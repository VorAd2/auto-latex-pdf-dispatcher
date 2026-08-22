# Auto LaTeX Dispatcher

[![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](LICENSE)

Read this in: 󠁧󠁢󠁥🇺🇸 [English](README.md)

A princípio, este programa foi motivado pelo meu interesse em automatizar, usando ferramentas populares e sem a instalação local do ecossistema TeX, o preenchimento de Termos de Voluntariado no âmbito da minha experiência universitária enquanto membro de uma empresa júnior. Entretanto, por conta da arquitetura desacoplada e do uso de modelos LaTeX, o script também é bastante útil em diversos outros cenários, a saber:
- Geração e despache automático de certificados para participantes de workshops, de semanas acadêmicas e de minicursos de capacitação.
- Geração e despache automático de Termos de Posse e de Contratos de Confidencialidade para membros e diretorias de uma empresa.

Nesse sentido, este projeto trata-se de um gerador e (opcionalmente) um despachador automatizado de PDFs LaTeX local que, a partir de planilhas .xlsx e modelos .tex, utiliza informações como nome completo, número de identificação fiscal e email para preencher campos dinâmicos em um arquivo .tex, gerar o PDF correspondente e despachá-lo via e-mail para o destinatário associado.

---

## Sumário
- [Tecnologias](#tecnologias)
- [Limitações](#limitações)
- [Fluxo de Trabalho](#fluxo-de-trabalho)
- [Como Usar](#como-usar)
- [Licença](#licença)

## Tecnologias
- Google Forms para a coleta e exportação dos dados dos destinatários.
- Overleaf para a elaboração do modelo .tex.
- Python 3.11.5 para a orquestração do fluxo de automação, gerenciando desde a manipulação de planilhas até a compilação e despache dos PDFs.
- Docker Desktop para a compilação containerizada dos arquivos .tex e .pdf em qualquer máquina, livrando-se da compilação nativa. 

## Limitações
Este script foi desenvolvido assumindo premissas do ambiente em que é executado. Se você pretende utilizá-lo em circunstâncias diferentes daquelas testadas para este projeto, podem ser necessárias modificações associadas aos seguintes pontos:

1. Validação de Dados e Dependência da Coleta
    - O script assume que os dados de entrada (via planilha exportada) já passaram por uma validação forte do mecanismo de coleta. Nesse sentido, o script valida apenas a presença dos campos e, particularmente no campo 'Nome' (ou em campo de identificação análogo que venha a ser usado), realiza o tratamento agressivo (mantém apenas letras planas e underscores) para que esse dado possa ser utilizado na nomeação dos arquivos .pdf.
    - Caracteres especiais tais como '%' e underscores inseridos em demais campos que não sejam o de identificação podem acarretar problemas durante a compilação dos arquivos .pdf, pois não são retirados pelo script (o código assume que os demais campos são de escrita livre ou numéricos) e entram em conflito com as regras do compilador TeX.

2. Volume de Processamento
    - O projeto foi desenvolvido pensando no processamento de não mais do que algumas dezenas de registros por execução (e respeitando a cota do seu provedor SMTP). Nesse sentido, o envio automatizado dos e-mails é feito via SMTP direto usando a biblioteca `smtplib` e, por isso, para grandes volumes de disparo, é interessante implementar uma versão em nuvem deste script, delegando processamento de planilha e disparo de e-mails a serviços fora da sua máquina.

## Fluxo de Trabalho
Antes de utilizar o programa, é importante entender o seu fluxo, que, apesar de automatizado, ainda exige uma pequena participação humana, sobretudo em cenários onde a validação dos dados deixa escapar campos inválidos de alguma linha da planilha. Para detalhes de setup e dependência, consulte [Como usar](#como-usar) e para detalhes das limitações, [Limitações](#limitações).

A execução é dividida em duas etapas principais:

1. Geração de PDFs (Compilação em Lote)
   - O operador executa o `main.py` e seleciona no terminal o tipo de planilha a ser processada: **Original** ou de **Correções/Modificada** ([Ciclo Iterativo](#ciclo-iterativo)).
   - As linhas do arquivo `.xlsx` são validadas automaticamente.
   - **Sucesso:** Os registros válidos têm seus PDFs gerados na pasta `/output`.
   - **Falha:** Os registros com erro são salvos em uma nova planilha (`/sheet/data_modified.xlsx`) para **correção manual** e o detalhamento da falha é registrado em `/output/errors.log`.

2. Despacho por E-mail (Opcional)
   - Inicia-se automaticamente logo após a compilação em lote terminar, enviando cada PDF gerado ao respectivo e-mail do destinatário.
   - *Nota:* Esta etapa pode ser desativada definindo `ENABLE_EMAIL_SENDING=False` no arquivo `.env`.


### Ciclo Iterativo
Caso registros inválidos não consigam ser tratados durante o processamento, o sistema permite tratar e reprocessar **apenas as linhas que falharam** durante a compilação dos PDFs, evitando reprocessar dados já concluídos.

#### Fluxo de Reprocessamento

1. **1ª Execução (Planilha Original):**
   - Execute o script e selecione a **Opção 1** (Planilha Original).
   - Se houver falhas, verifique o arquivo de log `/output/errors.log` para entender os motivos.
   
2. **Correção Manual:**
   - Abra o arquivo `/sheet/data_modified.xlsx` gerado pelo script (contendo apenas as linhas com falhas).
   - Corrija os dados necessários (ex: ajuste de caracteres reservados do LaTeX como `%` ou `_`) e salve o arquivo com o mesmo nome.

3. **Reexecução (Planilha de Correções):**
   - Execute o script novamente e selecione a **Opção 2** (Planilha Modificada).
   - O processo se repete até que `/sheet/data_modified.xlsx` não contenha mais nenhuma pendência.



## Como Usar

### 1. Pré-requisitos
Este projeto foi desenvolvido e testado na versão 3.11.5 do Python.
O leitor deve ter instalado:
- **Git**
- **pyenv** (recomendado) ou **Python 3.11.5** instalado globalmente.
- **Docker Desktop**
    > Docker Desktop precisa estar aberto e rodando enquanto o script é executado.

**Nota**: Caso o leitor possua o Python 3.11.5 instalado globalmente em sua máquina, ignore os dois primeiros comandos do **Passo 2**. 

### 2. Configuração de Ambiente

1. Clone o Repositório
```bash
git clone https://github.com/VorAd2/je-document-generator
cd je-document-generator
```

2. Configure o Ambiente Virtual
```bash
pyenv install 3.11.5
pyenv local 3.11.5

python -m venv .venv

# Linux/macOS:
source .venv/bin/activate
# Windows (PowerShell):
.venv\Scripts\Activate.ps1
```

3. Instale as Dependências
```bash
# Opção A: Autonomia para o pip decidir as versões compatíveis mais recentes das dependências.

pip install -r requirements.txt

# Opção B: Reproduza exatamente o ambiente de pacotes no qual este projeto foi desenvolvido e testado.

pip install -r requirements-lock.txt
```

4. Configure as Variáveis de Ambiente

Verifique o arquivo [.env.template](.env.template) e siga as instruções.


## 3. Arquivos de Entrada

Antes de executar o script, certifique-se de que os seguintes arquivos estejam corretamente localizados no diretório do projeto:

1. Planilha de Dados
- Planilha original (`/sheet/data.xlsx`) exportada do seu mecanismo de coleta de dados ou planilha para correções (`/sheet/data_modified.xlsx`).

2. Template/Projeto LaTeX
- Todo o projeto LaTeX deve estar no diretório `/document_model`.
- O documento base `/document_model/main.tex` deve conter tags de modelo (`\var{nome_da_variável}`) com os nomes exatos das variáveis definidos no arquivo `mapping.json`.

3. Arquivo de Mapeamento (`mapping.json`)
- Arquivo de configuração (localizado em `config/mapping.json`) usado para mapear os cabeçalhos das colunas da planilha em formato bruto (por exemplo, títulos de perguntas do Google Forms) aos nomes das variáveis definidas no seu modelo LaTeX.
- Essa camada separa a fonte de dados do código, permitindo que as perguntas do formulário ou as tags do modelo LaTeX sejam atualizadas sem a necessidade de modificar os scripts em Python.
- **Exemplo:**
  ```json
  {
    "Qual é o seu nome completo?": "nome",
    "Digite seu CPF (somente números):": "cpf",
    "Endereço de E-mail": "email"
  }
  ```

---

## Licença
[MIT](LICENSE)