import os
import smtplib
from collections.abc import Callable
from dotenv import load_dotenv
from pathlib import Path
from email.message import EmailMessage
from ssl import create_default_context
import pandas as pd


load_dotenv()
EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')

port = 465
smtp_server = "smtp.gmail.com"

EMAIL_SUBJECT = 'TERMO VOLUNTARIADO - Empresa Júnior'

def get_email_content(name: str) -> str:
    return f'''
        Olá, {name}. Segue o termo de voluntariado com suas informações preenchidas.
        \nComo resposta a este email, ficamos no aguardo da devolução do documento devidamente assinado.
        '''
#########################################################################

def send_sucess_emails(output_dir: Path, df: pd.DataFrame, generate_filename_wrapper: Callable):
    pdf_list = list(output_dir.glob('*.pdf'))

    if not pdf_list:
        print('Nenhum PDF encontrado para envio.\n')
        return

    print(f"\n\U0001F4E9 Iniciando o envio de {len(pdf_list)} email(s)...")

    df['sanitized_name'] = df.apply(generate_filename_wrapper, axis=1)

    try:
        with smtplib.SMTP_SSL(smtp_server, port ,context=create_default_context()) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)

            for pdf in pdf_list:
                pdf_filename = pdf.stem
                row = df[df['sanitized_name'] == pdf_filename]

                if row.empty: continue

                row_email = row.iloc[0].get('email')
                row_name = row.iloc[0].get('nome')

                msg = EmailMessage()
                msg['From'] = EMAIL_ADDRESS
                msg['To'] = row_email
                msg['Subject'] = EMAIL_SUBJECT
                msg.set_content(get_email_content(row_name))

                with open(pdf, 'rb') as f:
                    msg.add_attachment(
                        f.read(),
                        maintype='application',
                        subtype='pdf',
                        filename=pdf_filename
                    )

                smtp.send_message(msg)
                print(f"\t\u2705 E-mail enviado com sucesso para: {row_name} ({row_email})")
    except Exception as e:
        print('Erro durante conexão com servidor de email: ' + e)
