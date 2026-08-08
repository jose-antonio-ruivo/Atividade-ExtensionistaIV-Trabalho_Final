"""Controlador dos jogos offline incorporados ao Fácil Click.

Este módulo não contém as regras dos jogos. Sua responsabilidade é validar o
jogo solicitado, carregar o arquivo HTML local e exibi-lo em uma janela
pywebview isolada. As regras e a renderização estão em ``jogos_offline.html``.
"""

import json
import os
import sys


# Dicionário de permissão: somente estes identificadores podem ser iniciados.
JOGOS_VALIDOS = {
    "paciencia": "Paciência",
    "freecell": "FreeCell",
    "mahjong": "Mahjong",
    "campo_minado": "Campo Minado",
}


def _base_aplicacao():
    """Localiza a pasta dos recursos no código-fonte ou no executável."""
    if getattr(sys, "frozen", False):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))


def _mensagem_erro(texto):
    """Apresenta uma mensagem visual de erro no Windows."""
    try:
        import ctypes

        ctypes.windll.user32.MessageBoxW(0, texto, "Fácil Click", 0x10)
    except Exception:
        print(texto)


def executar_jogo(identificador):
    """Carrega e exibe o jogo indicado em uma janela controlada."""
    if identificador not in JOGOS_VALIDOS:
        raise ValueError("Jogo não reconhecido")

    try:
        import webview
    except ImportError:
        _mensagem_erro(
            "O componente dos jogos ainda não está instalado.\n\n"
            "Instale o pywebview e tente novamente."
        )
        return

    caminho_html = os.path.join(_base_aplicacao(), "jogos_offline.html")
    if not os.path.exists(caminho_html):
        raise FileNotFoundError("Arquivo jogos_offline.html não encontrado")

    # O HTML é lido como texto para receber o identificador do jogo inicial.
    with open(caminho_html, "r", encoding="utf-8") as arquivo:
        html = arquivo.read()
    # json.dumps produz um literal JavaScript válido e evita problemas de aspas.
    html = html.replace("__JOGO_INICIAL__", json.dumps(identificador))

    # Como os jogos são totalmente locais, downloads e links externos são
    # desnecessários e permanecem desativados.
    webview.settings["ALLOW_DOWNLOADS"] = False
    webview.settings["ALLOW_FILE_URLS"] = False
    webview.settings["OPEN_EXTERNAL_LINKS_IN_BROWSER"] = False
    webview.settings["OPEN_DEVTOOLS_IN_DEBUG"] = False
    webview.settings["REMOTE_DEBUGGING_PORT"] = None

    # O dicionário mutável permite que a API acesse a janela depois da criação,
    # sem expor o objeto nativo ao mecanismo de serialização do pywebview.
    janela_ref = {"valor": None}

    class ApiJogos:
        """Ponte segura usada pelo botão VOLTAR AO FÁCIL CLICK."""

        def voltar_facil_click(self):
            """Fecha somente a janela do jogo atual."""
            janela_atual = janela_ref["valor"]
            if janela_atual:
                janela_atual.destroy()
            return True

    api = ApiJogos()
    # A interface HTML é fornecida diretamente pela memória, sem servidor web.
    janela = webview.create_window(
        f"Fácil Click — {JOGOS_VALIDOS[identificador]}",
        html=html,
        js_api=api,
        fullscreen=True,
        frameless=True,
        easy_drag=False,
        on_top=True,
        resizable=False,
        background_color="#0d3b2e",
        text_select=False,
        zoomable=False,
    )
    janela_ref["valor"] = janela
    webview.start(gui="edgechromium", debug=False, private_mode=True)


# Entrada usada quando o módulo é chamado como processo separado.
if __name__ == "__main__":
    if len(sys.argv) < 2:
        _mensagem_erro("Nenhum jogo foi informado.")
        sys.exit(2)
    executar_jogo(sys.argv[1])
