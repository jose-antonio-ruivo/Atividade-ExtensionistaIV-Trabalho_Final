"""Verificação técnica do ambiente local do Fácil Click.

O script é chamado pelos arquivos BAT antes de abrir a interface. Ele testa a
versão do Python, os módulos externos, o Tkinter e os arquivos necessários.
Retorna código 0 quando o ambiente está íntegro e código 1 quando há falha.
"""

from __future__ import annotations

import importlib
import os
import sys
from pathlib import Path


BASE = Path(__file__).resolve().parent
SILENCIOSO = "--silencioso" in sys.argv


def informar(texto: str) -> None:
    """Imprime somente quando o modo silencioso não foi solicitado."""
    if not SILENCIOSO:
        print(texto)


def verificar_modulo(nome: str, rotulo: str | None = None) -> bool:
    """Importa um módulo e registra uma mensagem objetiva."""
    try:
        importlib.import_module(nome)
        informar(f"[OK] Biblioteca: {rotulo or nome}")
        return True
    except Exception as erro:  # A mensagem completa fica disponível no log.
        informar(f"[FALHA] Biblioteca {rotulo or nome}: {erro}")
        return False


def verificar_arquivo(caminho: Path) -> bool:
    """Confirma a presença de um arquivo essencial ao aplicativo."""
    if caminho.is_file():
        informar(f"[OK] Arquivo: {caminho.name}")
        return True
    informar(f"[FALHA] Arquivo ausente: {caminho}")
    return False


def main() -> int:
    resultados: list[bool] = []

    versao_ok = sys.version_info[:2] == (3, 10)
    informar(f"Python em uso: {sys.executable}")
    informar(f"Versão: {sys.version.split()[0]}")
    informar("[OK] Python 3.10" if versao_ok else "[FALHA] É necessário Python 3.10")
    resultados.append(versao_ok)

    # tkinter pertence ao Python oficial, mas é testado separadamente.
    resultados.append(verificar_modulo("tkinter", "Tkinter"))
    resultados.append(verificar_modulo("PIL", "Pillow"))
    resultados.append(verificar_modulo("pyttsx3", "pyttsx3"))
    resultados.append(verificar_modulo("webview", "pywebview"))

    essenciais = (
        BASE / "facil_click_v1_2_5.py",
        BASE / "navegador_controlado.py",
        BASE / "jogos_controlados.py",
        BASE / "jogos_offline.html",
        BASE / "emergencia.txt",
        BASE / "assets",
    )
    for item in essenciais:
        if item.name == "assets":
            ok = item.is_dir() and any(item.iterdir())
            informar("[OK] Pasta de ícones: assets" if ok else "[FALHA] Pasta assets ausente ou vazia")
            resultados.append(ok)
        else:
            resultados.append(verificar_arquivo(item))

    if all(resultados):
        informar("\nAmbiente validado com sucesso.")
        return 0

    informar("\nO ambiente possui uma ou mais falhas.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
