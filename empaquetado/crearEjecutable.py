"""Genera el ejecutable de escritorio con PyInstaller."""

import os
from pathlib import Path
import subprocess
import sys


def principal():
    raizProyecto = Path(__file__).resolve().parents[1]
    ejecutableNucleo = raizProyecto / "nucleo" / "bin" / "simulador.exe"
    if not ejecutableNucleo.is_file():
        raise SystemExit(
            "No se encontro nucleo/bin/simulador.exe. Compile primero el nucleo; consulte README.md.")

    directorioEmpaquetado = raizProyecto / "empaquetado"
    comando = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--clean",
        "--onefile",
        "--windowed",
        "--name", "Simulador",
        "--distpath", str(directorioEmpaquetado / "dist"),
        "--workpath", str(directorioEmpaquetado / "build"),
        "--specpath", str(directorioEmpaquetado),
        "--add-binary", "{}{}.".format(ejecutableNucleo, os.pathsep),
        str(raizProyecto / "interfaz" / "main.py"),
    ]
    subprocess.run(comando, cwd=raizProyecto, check=True)


if __name__ == "__main__":
    principal()
