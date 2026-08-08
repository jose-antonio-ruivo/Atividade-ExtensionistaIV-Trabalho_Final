"""Navegador simplificado e controlado do Fácil Click.

Executado em processo separado para não conflitar com o loop do Tkinter.
No Windows, o pywebview utiliza o mecanismo Edge WebView2 disponível no sistema.

O controle implementado limita a navegação dentro da janela do aplicativo, mas
não substitui o Modo Quiosque do Windows. Portanto, atalhos do próprio sistema,
como Alt+Tab ou a tecla Windows, precisam de uma política adicional do sistema
operacional quando se deseja isolamento completo.
"""

import json
import os
import sys
from urllib.parse import urlparse


def _mensagem_erro(texto):
    """Exibe uma caixa de erro do Windows e usa o console como alternativa."""
    try:
        import ctypes

        ctypes.windll.user32.MessageBoxW(0, texto, "Fácil Click", 0x10)
    except Exception:
        print(texto)


def _url_segura(url):
    """Aceita somente endereços HTTP ou HTTPS com domínio definido."""
    try:
        resultado = urlparse(url)
        return resultado.scheme in ("http", "https") and bool(resultado.netloc)
    except Exception:
        return False


def _script_barra(url_inicial, nome_site):
    """Monta o JavaScript que injeta a barra de controle em cada página.

    ``json.dumps`` é usado para transportar texto Python para JavaScript sem
    quebrar aspas, acentos ou caracteres especiais.
    """
    url_json = json.dumps(url_inicial, ensure_ascii=False)
    nome_json = json.dumps(nome_site, ensure_ascii=False)

    return r"""
(() => {
    // IIFE: função executada imediatamente para não poluir o escopo global.
    const ID_BARRA = 'facil-click-barra-controlada';
    const ALTURA_BARRA = '88px';
    const URL_INICIAL = __URL_INICIAL__;
    const NOME_SITE = __NOME_SITE__;

    // Cancela uma ação padrão do navegador e impede sua propagação.
    const bloquearEvento = (evento) => {
        evento.preventDefault();
        evento.stopPropagation();
    };

    // Fábrica de botões acessíveis usada pela barra superior.
    function criarBotao(texto, cor, acao, rotulo) {
        const botao = document.createElement('button');
        botao.type = 'button';
        botao.textContent = texto;
        botao.setAttribute('aria-label', rotulo || texto);
        botao.style.cssText = [
            'all:initial',
            'box-sizing:border-box',
            'height:62px',
            'padding:0 28px',
            'border:3px solid rgba(255,255,255,.75)',
            'border-radius:12px',
            'background:' + cor,
            'color:#ffffff',
            'font-family:Segoe UI,Arial,sans-serif',
            'font-size:21px',
            'font-weight:800',
            'line-height:56px',
            'text-align:center',
            'cursor:pointer',
            'box-shadow:0 3px 8px rgba(0,0,0,.28)',
            'user-select:none',
            'white-space:nowrap'
        ].join(';');
        botao.addEventListener('click', acao);
        botao.addEventListener('focus', () => {
            botao.style.outline = '5px solid #ffd54f';
            botao.style.outlineOffset = '2px';
        });
        botao.addEventListener('blur', () => {
            botao.style.outline = 'none';
        });
        return botao;
    }

    // Insere a barra apenas uma vez em cada documento carregado.
    function instalarBarra() {
        if (!document.documentElement || document.getElementById(ID_BARRA)) return;

        const barra = document.createElement('div');
        barra.id = ID_BARRA;
        barra.setAttribute('role', 'navigation');
        barra.setAttribute('aria-label', 'Controles do navegador Fácil Click');
        barra.style.cssText = [
            'all:initial',
            'position:fixed',
            'top:0',
            'left:0',
            'right:0',
            'height:' + ALTURA_BARRA,
            'z-index:2147483647',
            'display:flex',
            'align-items:center',
            'gap:14px',
            'padding:10px 16px',
            'box-sizing:border-box',
            'background:#17202a',
            'border-bottom:4px solid #3498db',
            'box-shadow:0 4px 12px rgba(0,0,0,.38)',
            'font-family:Segoe UI,Arial,sans-serif'
        ].join(';');

        const anterior = criarBotao('← PÁGINA ANTERIOR', '#246b9e', () => history.back());
        const inicio = criarBotao('⌂ PÁGINA INICIAL', '#287d50', () => {
            window.pywebview.api.ir_inicio();
        });

        const titulo = document.createElement('div');
        titulo.textContent = 'Navegador Fácil Click  •  ' + NOME_SITE;
        titulo.style.cssText = [
            'all:initial',
            'flex:1',
            'color:#ffffff',
            'font-family:Segoe UI,Arial,sans-serif',
            'font-size:20px',
            'font-weight:700',
            'text-align:center',
            'overflow:hidden',
            'text-overflow:ellipsis',
            'white-space:nowrap'
        ].join(';');

        const voltar = criarBotao('⟵ VOLTAR AO FÁCIL CLICK', '#c0392b', () => {
            window.pywebview.api.voltar_facil_click();
        }, 'Voltar ao menu principal do Fácil Click');

        barra.append(anterior, inicio, titulo, voltar);
        document.documentElement.appendChild(barra);

        if (document.body) {
            document.body.style.setProperty('padding-top', ALTURA_BARRA, 'important');
            document.body.style.setProperty('box-sizing', 'border-box', 'important');
        }
    }

    // A marca global evita registrar os mesmos listeners repetidamente.
    if (!window.__facilClickProtecaoInstalada) {
        window.__facilClickProtecaoInstalada = true;

        // Intercepta links antes da página. Downloads e protocolos externos
        // são bloqueados; links de nova aba são redirecionados para a mesma tela.
        document.addEventListener('click', (evento) => {
            const link = evento.target && evento.target.closest
                ? evento.target.closest('a[href]')
                : null;
            if (!link) return;

            let destino;
            try {
                destino = new URL(link.href, window.location.href);
            } catch (_) {
                bloquearEvento(evento);
                return;
            }

            if (link.hasAttribute('download') || !['http:', 'https:'].includes(destino.protocol)) {
                bloquearEvento(evento);
                alert('Esta ação foi bloqueada para manter a navegação segura.');
                return;
            }

            if (link.target && link.target.toLowerCase() !== '_self') {
                bloquearEvento(evento);
                window.location.assign(destino.href);
            }
        }, true);

        // Obriga formulários a permanecerem na janela atual.
        document.addEventListener('submit', (evento) => {
            if (evento.target && evento.target.target) evento.target.target = '_self';
        }, true);

        // Remove recursos que poderiam facilitar saída, arraste ou download.
        document.addEventListener('contextmenu', bloquearEvento, true);
        document.addEventListener('dragstart', bloquearEvento, true);
        document.addEventListener('drop', bloquearEvento, true);

        // Bloqueia atalhos comuns de nova aba, salvar, imprimir, fonte e DevTools.
        document.addEventListener('keydown', (evento) => {
            const tecla = String(evento.key || '').toLowerCase();
            const atalhosBloqueados = ['l', 'n', 't', 'o', 's', 'p', 'u', 'j'];
            if ((evento.ctrlKey || evento.metaKey) && atalhosBloqueados.includes(tecla)) {
                bloquearEvento(evento);
            }
            if (tecla === 'f12') bloquearEvento(evento);
        }, true);

        // Substitui window.open para que pop-ups naveguem na própria janela.
        try {
            window.open = function(destino) {
                if (destino) {
                    const url = new URL(destino, window.location.href);
                    if (['http:', 'https:'].includes(url.protocol)) window.location.assign(url.href);
                }
                return window;
            };
        } catch (_) {}

        // Reinstala a barra caso uma aplicação web altere completamente o DOM.
        const observador = new MutationObserver(() => instalarBarra());
        observador.observe(document.documentElement, {childList:true, subtree:true});
    }

    instalarBarra();
})();
""".replace("__URL_INICIAL__", url_json).replace("__NOME_SITE__", nome_json)


def executar_navegador(url_inicial, nome_site="Internet"):
    """Cria e executa a janela de navegação controlada.

    A função configura o pywebview, expõe somente dois métodos ao JavaScript
    (voltar ao menu e ir à página inicial) e injeta a barra após cada carregamento.
    """
    if not _url_segura(url_inicial):
        raise ValueError("Endereço de internet inválido ou não permitido")

    try:
        import webview
    except ImportError:
        _mensagem_erro(
            "O componente do navegador controlado ainda não está instalado.\n\n"
            "Execute o arquivo INSTALAR_NAVEGADOR_CONTROLADO.bat e tente novamente."
        )
        return

    # Restrições globais do pywebview.
    webview.settings["ALLOW_DOWNLOADS"] = False
    webview.settings["ALLOW_FILE_URLS"] = False
    webview.settings["OPEN_EXTERNAL_LINKS_IN_BROWSER"] = False
    webview.settings["OPEN_DEVTOOLS_IN_DEBUG"] = False
    webview.settings["REMOTE_DEBUGGING_PORT"] = None

    # A referência da janela permanece fora do objeto exposto ao JavaScript.
    # Se ela for um atributo público da API, o pywebview tenta serializar a
    # árvore nativa de acessibilidade do Windows e entra em recursão infinita.
    janela_ref = {"valor": None}

    class ApiNavegador:
        """Ponte mínima entre o JavaScript da página e o código Python."""

        def voltar_facil_click(self):
            """Fecha somente o navegador e revela novamente o menu principal."""
            janela_atual = janela_ref["valor"]
            if janela_atual:
                janela_atual.destroy()
            return True

        def ir_inicio(self):
            """Recarrega o endereço originalmente associado ao cartão."""
            janela_atual = janela_ref["valor"]
            if janela_atual:
                janela_atual.load_url(url_inicial)
            return True

    api = ApiNavegador()
    # A janela é sem moldura e em tela cheia para manter uma experiência simples.
    janela = webview.create_window(
        f"Fácil Click — {nome_site}",
        url=url_inicial,
        js_api=api,
        fullscreen=True,
        frameless=True,
        easy_drag=False,
        on_top=True,
        resizable=False,
        background_color="#17202a",
        text_select=True,
        zoomable=True,
    )
    janela_ref["valor"] = janela

    script = _script_barra(url_inicial, nome_site)

    def pagina_carregada():
        """Injeta a barra de controle depois que o documento termina de carregar."""
        try:
            janela.run_js(script)
        except Exception as erro:
            print(f"Não foi possível inserir a barra de controle: {erro}")

    janela.events.loaded += pagina_carregada

    # Perfil separado: cookies e sessões do Fácil Click não usam o perfil normal
    # do Microsoft Edge instalado no computador.
    pasta_dados = os.path.join(
        os.environ.get("LOCALAPPDATA", os.path.expanduser("~")),
        "FacilClick",
        "Navegador",
    )
    os.makedirs(pasta_dados, exist_ok=True)

    webview.start(
        debug=False,
        private_mode=False,
        storage_path=pasta_dados,
    )


# Permite executar este módulo diretamente pelo Prompt de Comando.
if __name__ == "__main__":
    if len(sys.argv) < 2:
        _mensagem_erro("Nenhum endereço foi informado ao navegador controlado.")
        sys.exit(2)

    endereco = sys.argv[1]
    nome = sys.argv[2] if len(sys.argv) > 2 else "Internet"
    executar_navegador(endereco, nome)
