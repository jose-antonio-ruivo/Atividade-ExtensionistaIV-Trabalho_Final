"""Inicializador com registro de falhas do Fácil Click.

Quando iniciado por ``pythonw.exe``, erros não aparecem em um console. Este
arquivo redireciona as mensagens para ``logs/facil_click.log`` e mostra uma
janela de aviso caso uma exceção impeça a abertura do programa principal.
"""

from __future__ import annotations

import contextlib
import datetime as dt
import os
import runpy
import sys
import traceback
from pathlib import Path


BASE = Path(__file__).resolve().parent
RAIZ = BASE.parent
LOGS = RAIZ / "logs"
LOG = LOGS / "facil_click.log"
PRINCIPAL = BASE / "facil_click_v1_2_5.py"


def mostrar_erro(mensagem: str) -> None:
    """Tenta apresentar uma mensagem gráfica sem criar nova dependência."""
    try:
        from tkinter import Tk, messagebox

        janela = Tk()
        janela.withdraw()
        messagebox.showerror("Fácil Click", mensagem)
        janela.destroy()
    except Exception:
        pass


def executar() -> int:
    LOGS.mkdir(parents=True, exist_ok=True)
    modo_console = "--console" in sys.argv

    with LOG.open("a", encoding="utf-8") as arquivo_log:
        arquivo_log.write("\n" + "=" * 70 + "\n")
        arquivo_log.write(f"Inicialização: {dt.datetime.now():%Y-%m-%d %H:%M:%S}\n")
        arquivo_log.write(f"Python: {sys.executable}\n")
        arquivo_log.write(f"Aplicativo: {PRINCIPAL}\n")
        arquivo_log.flush()

        destinos = contextlib.nullcontext() if modo_console else contextlib.ExitStack()
        try:
            if modo_console:
                runpy.run_path(str(PRINCIPAL), run_name="__main__")
            else:
                with contextlib.redirect_stdout(arquivo_log), contextlib.redirect_stderr(arquivo_log):
                    runpy.run_path(str(PRINCIPAL), run_name="__main__")
            return 0
        except SystemExit as saida:
            codigo = saida.code if isinstance(saida.code, int) else 0
            return codigo
        except Exception:
            detalhes = traceback.format_exc()
            arquivo_log.write(detalhes)
            arquivo_log.flush()
            if modo_console:
                print(detalhes)
            mostrar_erro(
                "O Fácil Click encontrou uma falha ao iniciar.\n\n"
                f"Consulte o relatório:\n{LOG}"
            )
            return 1


if __name__ == "__main__":
    raise SystemExit(executar())
