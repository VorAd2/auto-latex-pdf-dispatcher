import os
import subprocess
import shutil
from pathlib import Path
import pandas as pd
import re
import unicodedata

from src import (
    LatexCompiler, get_dataframe, get_template, 
    LOG_FILE, OUTPUT_DIR, MODIFIED_SHEET_FILE, 
    summarize_and_log, ENABLE_EMAIL_SENDING, send_sucess_emails
)

def sanitize_tex_name(raw_name: str) -> str:
    name = raw_name.strip().replace(" ", "_")
    name = unicodedata.normalize('NFD', name)
    name = ''.join(c for c in name if unicodedata.category(c) != 'Mn')
    name = re.sub(r'[^a-zA-Z0-9_]', '', name)
    return name

def validate_required_fields(data: dict):
    empty_fields = [
        key
        for key, val in data.items()
        if pd.isna(val) or str(val).strip() == ""
    ]
    if empty_fields:
        raise ValueError(
            f"Campos obrigatórios ausentes: {', '.join(empty_fields)}"
        )

def clean_output(tex_path: str, output_dir: Path, success: bool):
    if os.path.exists(tex_path):
        os.remove(tex_path)
    root_name = os.path.splitext(os.path.basename(tex_path))[0]
    garbage = [".aux", ".log", ".out"]
    if not success:
        garbage.append(".pdf")
    for ext in garbage:
        file = output_dir / f"{root_name}{ext}"
        if file.exists():
            file.unlink()
    texput = output_dir / "texput.log"
    if texput.exists():
        texput.unlink()

def reset_output_dir(output_dir: Path):
    if output_dir.exists():
        shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=True)

##################################################################################

print(f"\n{40 * '='}ESCOLHA O FLUXO{40 * '='}")
print("1 - Processar Planilha Original")
print("2 - Processar Planilha de Correções")
answer = input("Digite o número da opção desejada (1 ou 2): ").strip()
use_modified = answer == "2"

try:
    df = get_dataframe(use_modified=use_modified)
except FileNotFoundError as e:
    print(f"\n\u274C Erro: {e}")
    exit(1)

print("\nLimpando o diretório de saída...")
reset_output_dir(OUTPUT_DIR)

template = get_template()

success = 0
fail = []
failed_indices = []

with LatexCompiler() as compiler:
    for index, row in df.iterrows():
        data = row.to_dict()

        tex_name_raw = str(row.get("nome", f"membro_{index+1}"))
        tex_name_clean = sanitize_tex_name(tex_name_raw)
        tex_path = f"{tex_name_clean}.tex"
        row_sheet = index + 2
        is_success = False 

        print(f"\U0001F4C4 [{row_sheet}] Compilando PDF para: {tex_name_raw}...")
        try:
            validate_required_fields(data)
            tex_content = template.render(data)
            with open(tex_path, "w", encoding="utf-8") as f:
                f.write(tex_content)

            #síncrona e bloqueante por conta do subprocess.run()
            compiler.compile(tex_path, OUTPUT_DIR)
            
            success += 1
            is_success = True
        except subprocess.CalledProcessError as e:
            print(f"\t \u274C Falha na linha {row_sheet}.")
            fail.append({
                "linha": row_sheet,
                "nome": tex_name_raw,
                "tipo": "Erro de Compilação no LaTeX / Docker.",
                "detalhes": e.stdout if e.stdout else e.stderr
            })
            failed_indices.append(index)
        except Exception as e:
            print(f"\t \u274C Falha na linha {row_sheet}.")
            fail.append({
                 "linha": row_sheet, 
                 "nome": tex_name_raw,
                 "tipo": "Python, Sistema Operacional ou Validação.", 
                 "detalhes": str(e)})
            failed_indices.append(index)
        finally:
             clean_output(tex_path, OUTPUT_DIR, success=is_success)

summarize_and_log(success, fail, LOG_FILE)

if ENABLE_EMAIL_SENDING:
    send_sucess_emails(OUTPUT_DIR, df, sanitize_tex_name)

print(f"\n{50 * '='}FINALIZAÇÃO{50 * '='}")
if fail:
    print(f"Gerando nova planilha com {len(fail)} erro(s) para correção...")
    df_errors = df.loc[failed_indices]
    #sobrescreve data_modified.xlsx a cada iteração
    df_errors.to_excel(MODIFIED_SHEET_FILE, index=False)
    print(f"Planilha de erros salva em: {MODIFIED_SHEET_FILE}\n")
else:
    print("\U0001F389 SUCESSO! Todas as linhas da planilha original foram processadas.")
    if MODIFIED_SHEET_FILE.exists():
       MODIFIED_SHEET_FILE.unlink()
    print("Planilha de correções deletada.\n")