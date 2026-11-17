import os
import subprocess
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent / "src"
CODE = "import bloguero, os; print(os.environ.get('GTK_IM_MODULE', ''))"


def _run(value):
    env = {k: v for k, v in os.environ.items() if k != "GTK_IM_MODULE"}
    env["PYTHONPATH"] = str(SRC)
    if value is not None:
        env["GTK_IM_MODULE"] = value
    out = subprocess.run(
        [sys.executable, "-c", CODE], env=env, capture_output=True, text=True, check=True
    )
    return out.stdout.strip()


def test_ibus_pasa_a_simple():
    assert _run("ibus") == "simple"


def test_otro_valor_no_cambia():
    assert _run("fcitx") == "fcitx"


def test_sin_valor_no_cambia():
    assert _run(None) == ""
