# Auto LaTeX Dispatcher

[![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](LICENSE)

Read this in: 🇧🇷 [Português do Brasil](README.pt-br.md)

Initially, this program was motivated by my interest in automating the process of filling out Volunteer Agreements — using popular tools and without having to install the TeX ecosystem locally — as part of my college experience as a member of a junior enterprise. However, thanks to its decoupled architecture, the script is also quite useful in various other scenarios, namely:
- Automatic generation and issuance of certificates for participants in workshops, academic weeks, and short-term training courses.
- Automatic generation and issuance of Letters of Appointment and Non-Disclosure Agreements for a company’s employees and executives.

In this regard, this project is a local LaTeX PDF generator and (optionally) an automated PDF dispatcher that, using .xlsx spreadsheets and .tex templates, utilizes information such as full name, national ID number and e-mail address to populate dynamic fields in a .tex file, generate the corresponding PDF and send it via e-mail to the associated recipient.

---

## Table of Contents
- [Technologies](#technologies)
- [Limitations](#limitations)
- [Workflow](#workflow)
- [Usage](#usage)
- [License](#license)

## Technologies
- Google Forms for collecting and exporting recipient data.
- Overleaf for creating the .tex template.
- Python 3.11.5 for automating workflow orchestration, handling everything from spreadsheet manipulation to PDF compilation and distribution.
- Docker Desktop for containerized compilation of .tex and .pdf files on any machine, eliminating the need for native compilation. 

## Limitations
This script was developed based on certain assumptions about the environment in which it runs. If you intend to use it in circumstances other than those tested for this project, you may need to make modifications related to the following points:

1. Data Validation and Data Collection Dependencies
    - The script assumes that the input data (from the exported spreadsheet) has already undergone rigorous validation by the data collection mechanism. As such, the script only validates the presence of the fields and, specifically in the 'Name' field (or any analogous identification field that may be used), performs aggressive sanitization (retaining only plain letters and underscores) so that this data can be used to name the .pdf files.
    - Special characters such as `%` and `_` entered in fields other than the identification field may cause problems during the compilation of the .pdf files, as they are not removed by the script (the code assumes that the other fields are free-text or numeric) and conflict with the TeX compiler’s rules.

2. Processing Volume
    - The project was designed to process no more than a few dozen records per run (while adhering to your SMTP provider’s quota). As such, emails are sent automatically via direct SMTP using the `smtplib` library; therefore, for large volumes of emails, it’s a good idea to implement a cloud-based version of this script, delegating spreadsheet processing and email sending to services outside your machine.

## Workflow
Before using the program, it is important to understand its workflow, which, although automated, still requires a small amount of human intervention—especially in scenarios where data validation fails to catch invalid fields in a row of the spreadsheet. For details on setup and dependencies, see [Usage](#usage), and for details on limitations, see [Limitations](#limitations).

The process is divided into two main stages:

1. Batch PDF Generation
   - The operator runs `main.py` and selects the type of spreadsheet to be processed in the terminal: **Original** or **Corrections/Modified** ([Iterative Cycle](#iterative-cycle)).
   - The rows in the `.xlsx` file are validated automatically.
   - **Success:** PDFs for valid records are generated in the `/output` folder.
   - **Error:** Records with errors are saved in a new spreadsheet (`/sheet/data_modified.xlsx`) for **manual correction** and the error details are logged in `/output/errors.log`.

2. Email Dispatch (Optional)
   - It starts automatically as soon as the batch compilation is complete, sending each generated PDF to the recipient's email address.
   - *Note:* This step can be disabled by setting `ENABLE_EMAIL_SENDING=False` in the `.env` file.


### Iterative Cycle
If invalid records cannot be handled during processing, the system allows you to handle and reprocess **only the rows that failed** during PDF compilation, thereby avoiding the reprocessing of data that has already been completed.

#### Reprocessing Workflow

1. **1st Run (Original Spreadsheet):**
   - Run the script and select **Option 1** (Original Spreadsheet).
   - If there are any errors, check the log file `/output/errors.log` to understand the reasons.
   
2. **Manual Correction:**
   - Open the file `/sheet/data_modified.xlsx` generated by the script (which contains only the rows with errors).
   - Correct the necessary data (e.g., adjust LaTeX reserved characters such as `%` or `_`) and save the file with the same name.

3. **Re-run (Corrections Spreadsheet):**
   - Run the script again and select **Option 2** (Modified Spreadsheet).
   - The process repeats until `/sheet/data_modified.xlsx` no longer contains any pending items.



## Usage

### 1. Prerequisites
This project was developed and tested using Python version 3.11.5.
The reader must have the following installed:
- **Git**
- **pyenv** (recomended) ou **Python 3.11.5** installed globally.
- **Docker Desktop**
    > Docker Desktop must be open and running while the script is executing.

**Note**: If you have Python 3.11.5 installed globally on your machine, skip the first two commands in **Step 2**.

### 2. Environment Setup

1. Clone the Repository
```bash
git clone https://github.com/VorAd2/je-document-generator
cd je-document-generator
```

2. Configure Virtual Env
```bash
pyenv install 3.11.5
pyenv local 3.11.5

python -m venv .venv

# Linux/macOS:
source .venv/bin/activate
# Windows (PowerShell):
.venv\Scripts\Activate.ps1
```

3. Install Dependencies
```bash
# Option A: Allow pip to decide which are the most recent compatible versions of the dependencies.

pip install -r requirements.txt

# Option B: Exactly replicate the package environment in which this project was developed and tested.

pip install -r requirements-lock.txt
```

4. Setup Environment Variables

Check the [.env.template](.env.template) file and follow the instructions.


## 3. Input Files

Before running the script, make sure the following files are correctly located in the project directory:

1. Data Spreadsheet
- Original sheet (`/sheet/data.xlsx`) exported from your data collection mechanism or updated after corrections sheet (`/sheet/data_modified.xlsx`).

2. LaTeX template/project
- All the LaTeX project must be in `/document_model` directory.
- Base `/document_model/main.tex` document containing template tags (`\var{variable_name}`) with the exact var names in the `mapping.json`.

3. Mapping File (`mapping.json`)
- Configured file (located in `config/mapping.json`) used to map raw spreadsheet column headers (e.g., Google Forms question titles) to the variable names defined in your LaTeX template.
- This layer decouples the data source from the code, allowing form questions or LaTeX template tags to be updated without modifying Python scripts.
- **Example structure:**
  ```json
  {
    "Type your full name": "name",
    "Type your SSN": "ssn",
    "Type your e-mail": "email"
  }
  ```

---

## License
[MIT](LICENSE)