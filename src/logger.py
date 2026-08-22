import os

def summarize_and_log(success: int, fail: list, log_file: str):
    print("\n" + "+" * 40)
    print("\U0001F4CA RESUMO DO PROCESSAMENTO")
    print(f"\u2705 PDFs gerados com sucesso: {success}")
    print(f"\u274C Falhas encontradas: {len(fail)}\n")
    print('Se aplicável, consulte o arquivo de logs.')
    print("+" * 40)
    print()
    if not fail:
        if os.path.exists(log_file):
            os.remove(log_file)
        return

    with open(log_file, "w", encoding="utf-8") as log:
        log.write("--- RELATÓRIO DE ERROS ---\n\n")
        for item in fail:
            log.write(f"Linha Planilha: {item['linha']}\n")
            log.write(f"Nome: {item['nome']}\n")
            tipo_erro = item.get("tipo", "Erro Genérico")
            log.write(f"Categoria: {tipo_erro}\n")
            log.write("Detalhes:\n")
            log.write(item["detalhes"])
            log.write("\n" + "-" * 70 + "\n\n")
