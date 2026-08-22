import subprocess
from pathlib import Path
import uuid
from .config import BASE_DIR

class LatexCompiler:
    def __init__(self):
        self.container_name = f"latex_compiler_{uuid.uuid4().hex[:8]}"

    # Chama o Docker e cria o container em modo detached quando main.py entra no with
    def __enter__(self):
        comando_docker_run = [
            "docker", "run",
            "-d", "--rm",
            "--name", self.container_name,
            "-v", f"{BASE_DIR}:/workdir",
            "-w", "/workdir",
            "-e", "TEXINPUTS=./document_model//:",
            "texlive/texlive",
            "tail", "-f", "/dev/null"
        ]
        subprocess.run(comando_docker_run, check=True, capture_output=True)
        return self

    def compile(self, tex_path: str, output_dir: Path):
        comando_docker_exec = [
            "docker", "exec",
            self.container_name,
            "pdflatex",
            "-interaction=nonstopmode",
            f"-output-directory=./{output_dir.name}",
            tex_path
        ]
        subprocess.run(comando_docker_exec, check=True, capture_output=True, text=True)

    # Destrói o container quando o main.py termina o with
    def __exit__(self, exc_type, exc_val, exc_tb):
        subprocess.run(["docker", "kill", self.container_name], capture_output=True)