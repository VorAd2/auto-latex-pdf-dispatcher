import os
import json
from pathlib import Path
from dotenv import load_dotenv
from functools import cache
from jinja2 import Environment, FileSystemLoader, Template
import pandas as pd

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = BASE_DIR / "config"
SHEET_FILE = BASE_DIR / "sheet" / "data.xlsx"
MODIFIED_SHEET_FILE = BASE_DIR / "sheet" / "data_modified.xlsx"
OUTPUT_DIR = BASE_DIR / "output"
LOG_FILE = OUTPUT_DIR / "errors.log"
TEMPLATE_DIR = BASE_DIR / "document_model"

_email_env = str(os.getenv('ENABLE_EMAIL_SENDING')).strip().lower()
ENABLE_EMAIL_SENDING = _email_env in ("true")

TAX_ID_FIELD = os.getenv('TAX_ID_FIELD').strip().lower()

# Trecho executado em Import Time, assim como tudo na identação 0
with open(CONFIG_PATH / "mapping.json", "r", encoding="utf-8") as f:
    COLUMN_MAPPING = json.load(f)

##################################################################################

 # df_raw.rename é tolerante ao "não matching" do data_modified.xlsx, 
 #portanto o mapping de colunas é corretamente ignorado nas iterações de correção.
 # @cache nasce e morre junto com o processo Python. Portanto, a cada nova iteração,
 #a persistência do dataframe é corretamente executada sobre o arquivo mais recente indicado.
@cache
def get_dataframe(use_modified: bool) -> pd.DataFrame:
    target_file = MODIFIED_SHEET_FILE if use_modified else SHEET_FILE
    if not os.path.exists(target_file):
        raise FileNotFoundError(
            f"Arquivo '{target_file}' não encontrado no caminho indicado."
        )
    df_raw = pd.read_excel(target_file)
    df_raw.columns = df_raw.columns.str.strip()
    return df_raw.rename(columns=COLUMN_MAPPING)

def get_template() -> Template:
    jinja_env = Environment(
        block_start_string=r"\block{",
        block_end_string=r"}",
        variable_start_string=r"\var{",
        variable_end_string=r"}",
        comment_start_string=r"\#{",
        comment_end_string=r"}",
        loader=FileSystemLoader(str(TEMPLATE_DIR)),
    )
    return jinja_env.get_template("main.tex")