"""Fácil Click V1.2.5 — módulo principal da interface.

Este arquivo cria a tela inicial em Tkinter, carrega os ícones, abre sites em um
navegador controlado, inicia programas do Windows e chama os jogos offline.

Organização didática do módulo:
1. importações e dependências opcionais;
2. definição dos caminhos do projeto;
3. funções auxiliares;
4. funções de navegação, jogos e emergência;
5. criação da interface gráfica;
6. associação dos eventos de mouse e teclado;
7. início do loop principal do Tkinter.

A interface foi projetada com foco em acessibilidade visual para pessoas idosas.
"""

import os
import sys
import webbrowser
import subprocess
import shutil
from datetime import datetime
from tkinter import Tk, Button, Toplevel, Entry, Label, Frame, StringVar, BOTH, LEFT, RIGHT, TOP, X

# -----------------------------------------------------------------------------
# AJUSTE DE DPI DO WINDOWS
# Evita que o Windows redimensione a aplicação de forma borrada em monitores
# com escala de 125%, 150% ou superior.
# -----------------------------------------------------------------------------
try:
    import ctypes
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

# Pillow é opcional. Quando disponível, permite redimensionar imagens com
# melhor qualidade. Caso contrário, o Tkinter usa PhotoImage diretamente.
try:
    from PIL import Image, ImageTk
    PIL_OK = True
except Exception:
    from tkinter import PhotoImage
    PIL_OK = False

# pyttsx3 é opcional e fornece retorno por voz das ações executadas.
try:
    import pyttsx3
except Exception:
    pyttsx3 = None

# -----------------------------------------------------------------------------
# CONSTANTES GLOBAIS
# -----------------------------------------------------------------------------
APP_TITLE = "Fácil Click V1.2.5 - Interface Sem Barra - RU:151561"

DIAS = {
    "Monday": "Segunda-feira",
    "Tuesday": "Terça-feira",
    "Wednesday": "Quarta-feira",
    "Thursday": "Quinta-feira",
    "Friday": "Sexta-feira",
    "Saturday": "Sábado",
    "Sunday": "Domingo",
}

janela_tela_cheia = True

# -----------------------------------------------------------------------------
# PROTEÇÃO DO ENCERRAMENTO
# A combinação abaixo funciona como uma barreira de uso para evitar que o
# usuário encerre o aplicativo por engano. Ela não substitui as políticas de
# segurança do Windows, mas é adequada para o controle operacional da interface.
# Para trocar a combinação, altere os eventos Tkinter e o texto de documentação.
# -----------------------------------------------------------------------------
COMBINACAO_ENCERRAR = "Ctrl + Alt + Shift + E"
EVENTOS_COMBINACAO_ENCERRAR = (
    "<Control-Alt-Shift-e>",
    "<Control-Alt-Shift-E>",
)
TEMPO_AUTORIZACAO_SEGUNDOS = 20
janela_autorizacao_encerramento = None

def app_base():
    """Retorna a pasta-base da aplicação.

    Quando o programa é empacotado com PyInstaller, ``sys._MEIPASS`` aponta
    para a pasta temporária onde os recursos foram extraídos. Durante o
    desenvolvimento, usa-se a pasta do próprio arquivo Python.
    """
    if getattr(sys, "frozen", False):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))

BASE = app_base()
ASSETS = os.path.join(BASE, "assets")

# Arquivos empacotados em modo ONEFILE ficam em uma pasta temporária e não
# devem receber dados persistentes. O número de emergência é salvo no perfil
# do usuário, permanecendo disponível nas próximas execuções do aplicativo.
DADOS_USUARIO = os.path.join(
    os.environ.get("APPDATA", os.path.expanduser("~")),
    "FacilClick",
)
os.makedirs(DADOS_USUARIO, exist_ok=True)
EMERGENCIA_PADRAO = os.path.join(BASE, "emergencia.txt")
EMERGENCIA_TXT = os.path.join(DADOS_USUARIO, "emergencia.txt")

if not os.path.exists(EMERGENCIA_TXT) and os.path.exists(EMERGENCIA_PADRAO):
    try:
        shutil.copyfile(EMERGENCIA_PADRAO, EMERGENCIA_TXT)
    except OSError:
        pass

NAVEGADOR_SCRIPT = os.path.join(BASE, "navegador_controlado.py")
JOGOS_SCRIPT = os.path.join(BASE, "jogos_controlados.py")

# Quando empacotado como executável, o próprio programa pode ser iniciado em
# modo navegador. No uso pelo código-fonte, o módulo é aberto em outro processo.
if "--navegador-controlado" in sys.argv:
    try:
        indice = sys.argv.index("--navegador-controlado")
        url_inicial = sys.argv[indice + 1]
        nome_inicial = sys.argv[indice + 2]
        from navegador_controlado import executar_navegador
        executar_navegador(url_inicial, nome_inicial)
    except Exception as erro:
        try:
            ctypes.windll.user32.MessageBoxW(
                0,
                f"Não foi possível abrir o navegador controlado.\n\n{erro}",
                "Fácil Click",
                0x10,
            )
        except Exception:
            print(f"Erro ao abrir navegador controlado: {erro}")
    sys.exit()

if "--jogo-controlado" in sys.argv:
    try:
        indice = sys.argv.index("--jogo-controlado")
        jogo_inicial = sys.argv[indice + 1]
        from jogos_controlados import executar_jogo
        executar_jogo(jogo_inicial)
    except Exception as erro:
        try:
            ctypes.windll.user32.MessageBoxW(
                0,
                f"Não foi possível abrir o jogo.\n\n{erro}",
                "Fácil Click",
                0x10,
            )
        except Exception:
            print(f"Erro ao abrir jogo: {erro}")
    sys.exit()

def caminho_icone(nome):
    """Procura um arquivo de ícone em diferentes pastas possíveis.

    A busca em vários locais permite executar o projeto pelo código-fonte, pelo
    PyCharm, pelo Prompt de Comando ou como executável empacotado.
    """
    nomes = [nome]
    if nome.endswith(".gif"):
        nomes.append(nome.replace(".gif", ".png"))
    for n in nomes:
        for p in [
            os.path.join(ASSETS, n),
            os.path.join(BASE, n),
            os.path.join(os.getcwd(), "assets", n),
            os.path.join(os.getcwd(), n),
        ]:
            if os.path.exists(p):
                return p
    return None

def carregar_icone(nome, largura=120, altura=120):
    """Carrega e redimensiona um ícone preservando sua proporção.

    O resultado é centralizado em uma tela transparente do tamanho solicitado,
    evitando deformação e mantendo todos os cartões visualmente uniformes.
    """
    caminho = caminho_icone(nome)
    if not caminho:
        return None
    try:
        if PIL_OK:
            img = Image.open(caminho).convert("RGBA")
            # Ajusta para cima ou para baixo preservando a proporção. O método
            # thumbnail não ampliava os arquivos menores e deixava os logos
            # visualmente reduzidos dentro dos cartões grandes.
            escala = min(largura / img.width, altura / img.height)
            nova_largura = max(1, int(img.width * escala))
            nova_altura = max(1, int(img.height * escala))
            img = img.resize((nova_largura, nova_altura), Image.LANCZOS)
            canvas = Image.new("RGBA", (largura, altura), (255, 255, 255, 0))
            x = (largura - img.width) // 2
            y = (altura - img.height) // 2
            canvas.paste(img, (x, y), img)
            return ImageTk.PhotoImage(canvas)
        return PhotoImage(file=caminho)
    except Exception:
        return None

def falar(texto):
    """Exibe uma mensagem no console e, quando possível, reproduz por voz."""
    print(texto)
    if pyttsx3 is None:
        return
    try:
        engine = pyttsx3.init()
        engine.say(texto)
        engine.runAndWait()
        engine.stop()
    except Exception:
        pass

def atualizar_status(texto):
    """Atualiza a barra de status e envia a mesma mensagem ao sintetizador."""
    status_var.set(texto)
    falar(texto)

def abrir_url(nome, url):
    """Abre um endereço no módulo de navegação controlada.

    O navegador é iniciado em outro processo para que o loop do pywebview não
    bloqueie o loop gráfico do Tkinter.
    """
    atualizar_status(f"Abrindo {nome} no navegador controlado")
    try:
        if getattr(sys, "frozen", False):
            comando = [sys.executable, "--navegador-controlado", url, nome]
        else:
            if not os.path.exists(NAVEGADOR_SCRIPT):
                raise FileNotFoundError("Módulo navegador_controlado.py não encontrado")
            comando = [sys.executable, NAVEGADOR_SCRIPT, url, nome]

        subprocess.Popen(comando, cwd=BASE)
    except Exception as erro:
        atualizar_status(f"Erro ao abrir {nome}: {erro}")

def abrir_programa(nome, comando):
    """Inicia um programa do Windows, como Calculadora ou Bloco de Notas."""
    atualizar_status(f"Abrindo {nome}")
    try:
        subprocess.Popen(comando, shell=True)
    except Exception:
        atualizar_status(f"Erro ao abrir {nome}")

def abrir_jogo(nome, identificador):
    """Abre um dos jogos locais em processo separado."""
    atualizar_status(f"Abrindo o jogo {nome}")
    try:
        if getattr(sys, "frozen", False):
            comando = [sys.executable, "--jogo-controlado", identificador]
        else:
            if not os.path.exists(JOGOS_SCRIPT):
                raise FileNotFoundError("Módulo jogos_controlados.py não encontrado")
            comando = [sys.executable, JOGOS_SCRIPT, identificador]

        subprocess.Popen(comando, cwd=BASE)
    except Exception as erro:
        atualizar_status(f"Erro ao abrir {nome}: {erro}")

def ler_numero_emergencia():
    """Lê e valida o telefone salvo no arquivo ``emergencia.txt``."""
    try:
        if os.path.exists(EMERGENCIA_TXT):
            with open(EMERGENCIA_TXT, "r", encoding="utf-8") as f:
                numero = f.read().strip()
            if numero.isdigit() and len(numero) >= 10:
                return numero
    except Exception:
        pass
    return None

def salvar_numero_emergencia(numero):
    """Grava o telefone de emergência em arquivo-texto UTF-8."""
    with open(EMERGENCIA_TXT, "w", encoding="utf-8") as f:
        f.write(numero)

def emergencia():
    """Abre uma conversa do WhatsApp com o contato de emergência configurado."""
    numero = ler_numero_emergencia()
    if not numero:
        atualizar_status("Número de emergência não configurado")
        configurar_emergencia()
        return
    atualizar_status("Emergência: abrindo WhatsApp")
    webbrowser.open("https://wa.me/" + numero, new=2)

def configurar_emergencia():
    """Mostra uma janela modal para cadastrar o telefone de emergência."""
    janela = Toplevel(root)
    janela.title("Configurar Emergência")
    janela.geometry("430x230")
    janela.resizable(False, False)
    janela.configure(bg="#ffffff")
    janela.transient(root)
    janela.grab_set()

    Label(janela, text="Número de Emergência", font=("Segoe UI", 15, "bold"), bg="#ffffff", fg="#1a252f").pack(pady=15)
    Label(janela, text="Digite o número com DDD, somente números:", font=("Segoe UI", 10), bg="#ffffff", fg="#7f8c8d").pack()

    entrada = Entry(janela, font=("Segoe UI", 17), justify="center", bd=1, relief="solid", fg="#2c3e50", bg="#f8f9fa")
    entrada.pack(pady=10, ipady=5, fill="x", padx=40)

    atual = ler_numero_emergencia()
    if atual:
        entrada.insert(0, atual)

    def salvar():
        """Valida o campo e encerra a janela após salvar o telefone."""
        numero = entrada.get().strip()
        if not (numero.isdigit() and len(numero) >= 10):
            status_var.set("Número inválido. Digite somente números com DDD.")
            return
        salvar_numero_emergencia(numero)
        status_var.set("Número de emergência salvo com sucesso.")
        janela.destroy()

    Button(janela, text="Salvar Configuração", font=("Segoe UI", 11, "bold"), bg="#2ecc71", fg="white",
           activebackground="#27ae60", activeforeground="white", bd=0, cursor="hand2", command=salvar).pack(pady=15, ipady=7, fill="x", padx=40)

def saudacao():
    """Retorna uma saudação de acordo com o horário atual."""
    hora = datetime.now().hour
    return "Bom dia" if hora < 12 else "Boa tarde" if hora < 18 else "Boa noite"

def atualizar_relogio():
    """Atualiza data e hora a cada segundo sem bloquear a interface.

    ``after`` agenda a próxima chamada dentro do próprio loop do Tkinter.
    """
    agora = datetime.now()
    dia = DIAS.get(agora.strftime("%A"), agora.strftime("%A"))
    data_hora_var.set(f"{dia}  |  {agora.strftime('%d/%m/%Y')}  |  {agora.strftime('%H:%M:%S')}")
    root.after(1000, atualizar_relogio)

# --- COMANDOS OCULTOS ---
def minimizar_app(event=None):
    """Minimiza a janela por um atalho oculto de teclado."""
    # Para minimizar janela sem borda, desativa temporariamente overrideredirect.
    root.overrideredirect(False)
    root.iconify()

def restaurar_borda_ao_voltar(event=None):
    """Restaura o modo sem borda depois que a janela volta da minimização."""
    # Reativa modo sem barra quando voltar da minimização.
    root.after(150, lambda: root.overrideredirect(True))

def alternar_tamanho(event=None):
    """Alterna entre tela cheia e uma janela centralizada de 1180 x 820."""
    global janela_tela_cheia
    janela_tela_cheia = not janela_tela_cheia
    root.overrideredirect(True)
    if janela_tela_cheia:
        root.geometry(f"{root.winfo_screenwidth()}x{root.winfo_screenheight()}+0+0")
        status_var.set("Tela cheia ativada.")
    else:
        largura = 1180
        altura = 820
        x = (root.winfo_screenwidth() - largura) // 2
        y = (root.winfo_screenheight() - altura) // 2
        root.geometry(f"{largura}x{altura}+{x}+{y}")
        status_var.set("Tamanho reduzido ativado.")

def solicitar_encerramento(event=None):
    """Solicita a combinação reservada antes de encerrar a aplicação.

    O botão de saída não fecha diretamente o programa. Primeiro é aberta uma
    janela modal, que captura o teclado e aguarda a combinação autorizada por
    um período limitado. Isso reduz encerramentos acidentais pelo usuário.
    """
    global janela_autorizacao_encerramento

    # Impede que várias janelas de autorização sejam abertas ao mesmo tempo.
    if (janela_autorizacao_encerramento is not None and
            janela_autorizacao_encerramento.winfo_exists()):
        janela_autorizacao_encerramento.lift()
        janela_autorizacao_encerramento.focus_force()
        return

    dialogo = Toplevel(root)
    janela_autorizacao_encerramento = dialogo
    dialogo.title("Autorização para encerrar")
    dialogo.geometry("600x330")
    dialogo.resizable(False, False)
    dialogo.configure(bg="#ffffff")
    dialogo.transient(root)
    dialogo.grab_set()

    # Centraliza o diálogo na tela, facilitando sua localização visual.
    dialogo.update_idletasks()
    x = (dialogo.winfo_screenwidth() - 600) // 2
    y = (dialogo.winfo_screenheight() - 330) // 2
    dialogo.geometry(f"600x330+{x}+{y}")

    Label(
        dialogo,
        text="ENCERRAMENTO PROTEGIDO",
        font=("Segoe UI", 20, "bold"),
        bg="#ffffff",
        fg="#c0392b",
    ).pack(pady=(30, 12))

    Label(
        dialogo,
        text=("Somente uma pessoa autorizada pode encerrar o Fácil Click.\n"
              "Pressione a combinação de segurança cadastrada."),
        font=("Segoe UI", 14),
        justify="center",
        bg="#ffffff",
        fg="#2c3e50",
    ).pack(pady=8)

    contagem_var = StringVar(value="")
    Label(
        dialogo,
        textvariable=contagem_var,
        font=("Segoe UI", 13, "bold"),
        bg="#ffffff",
        fg="#7f8c8d",
    ).pack(pady=(12, 4))

    Label(
        dialogo,
        text="A combinação não é exibida ao usuário comum.",
        font=("Segoe UI", 10, "italic"),
        bg="#ffffff",
        fg="#95a5a6",
    ).pack(pady=(0, 12))

    def limpar_referencia():
        """Libera a referência global quando o diálogo é fechado."""
        global janela_autorizacao_encerramento
        janela_autorizacao_encerramento = None

    def cancelar(evento=None):
        """Cancela o encerramento e devolve o foco à tela principal."""
        if dialogo.winfo_exists():
            dialogo.grab_release()
            dialogo.destroy()
        limpar_referencia()
        status_var.set("Encerramento cancelado.")
        root.focus_force()

    def confirmar(evento=None):
        """Fecha o aplicativo quando a combinação correta é detectada."""
        status_var.set("Autorização reconhecida. Encerrando o aplicativo.")
        if dialogo.winfo_exists():
            dialogo.grab_release()
            dialogo.destroy()
        limpar_referencia()
        root.after(120, root.destroy)
        return "break"

    # O diálogo aceita apenas a combinação definida nas constantes do módulo.
    for sequencia in EVENTOS_COMBINACAO_ENCERRAR:
        dialogo.bind(sequencia, confirmar)

    # Escape permite que o responsável desista sem encerrar o aplicativo.
    dialogo.bind("<Escape>", cancelar)
    dialogo.protocol("WM_DELETE_WINDOW", cancelar)

    Button(
        dialogo,
        text="CANCELAR E VOLTAR",
        font=("Segoe UI", 13, "bold"),
        bg="#34495e",
        fg="white",
        activebackground="#2c3e50",
        activeforeground="white",
        relief="flat",
        bd=0,
        cursor="hand2",
        command=cancelar,
    ).pack(fill="x", padx=110, pady=(8, 20), ipady=9)

    segundos_restantes = TEMPO_AUTORIZACAO_SEGUNDOS

    def atualizar_contagem():
        """Atualiza o limite de tempo sem bloquear o loop do Tkinter."""
        nonlocal segundos_restantes
        if not dialogo.winfo_exists():
            return
        if segundos_restantes <= 0:
            cancelar()
            status_var.set("Tempo de autorização encerrado.")
            return
        contagem_var.set(
            f"Aguardando autorização: {segundos_restantes} segundos"
        )
        segundos_restantes -= 1
        dialogo.after(1000, atualizar_contagem)

    dialogo.after(100, dialogo.focus_force)
    atualizar_contagem()


def fechar_app(event=None):
    """Compatibilidade: encaminha qualquer pedido de saída à autorização."""
    solicitar_encerramento(event)

# -----------------------------------------------------------------------------
# CRIAÇÃO DA JANELA PRINCIPAL
# -----------------------------------------------------------------------------
root = Tk()
root.title(APP_TITLE)
root.configure(bg="#eef2f7")

# Remove minimizar/restaurar/fechar da interface nativa
root.overrideredirect(True)

# Abre cobrindo a tela toda, sem barra superior
root.geometry(f"{root.winfo_screenwidth()}x{root.winfo_screenheight()}+0+0")

# Atalhos ocultos
root.bind_all("<Control-Alt-a>", minimizar_app)
root.bind_all("<Control-Alt-A>", minimizar_app)
root.bind_all("<Control-Alt-s>", alternar_tamanho)
root.bind_all("<Control-Alt-S>", alternar_tamanho)
# O atalho antigo agora abre a autorização; não existe encerramento direto.
root.bind_all("<Control-Alt-d>", solicitar_encerramento)
root.bind_all("<Control-Alt-D>", solicitar_encerramento)
root.bind("<Map>", restaurar_borda_ao_voltar)

# StringVar permite que o texto de um Label seja alterado automaticamente
# quando a variável recebe um novo valor.
status_var = StringVar(value=f"{saudacao()}! Sistema pronto para uso.")
data_hora_var = StringVar(value="")

# CABEÇALHO
header_frame = Frame(root, bg="#17202a", height=78)
header_frame.pack(fill=X, side=TOP)

left_header = Frame(header_frame, bg="#17202a")
left_header.pack(side=LEFT, padx=28, pady=10)

Label(left_header, text="FÁCIL CLICK", font=("Segoe UI", 25, "bold"), fg="#ffffff", bg="#17202a").pack(anchor="w")
Label(left_header, text="Inclusão Digital para a Terceira Idade", font=("Segoe UI", 11), fg="#d5dbdb", bg="#17202a").pack(anchor="w")

right_header = Frame(header_frame, bg="#17202a")
right_header.pack(side=RIGHT, padx=28, pady=10)

Label(right_header, text="RU: 151561 | Engenharia de Computação", font=("Segoe UI", 11, "italic"), fg="#d5dbdb", bg="#17202a").pack(anchor="e")
Label(right_header, textvariable=data_hora_var, font=("Segoe UI", 14, "bold"), fg="#ffffff", bg="#17202a").pack(anchor="e", pady=(6, 0))

# STATUS
status_frame = Frame(root, bg="#ffffff", height=44, bd=1, relief="solid")
status_frame.pack(fill=X, side=TOP)

Label(status_frame, textvariable=status_var, font=("Segoe UI", 12, "bold"), fg="#2c3e50", bg="#ffffff").pack(side=LEFT, padx=25, pady=9)

# PRINCIPAL
main_container = Frame(root, bg="#eef2f7")
main_container.pack(fill=BOTH, expand=True, padx=22, pady=18)

apps_frame = Frame(main_container, bg="#eef2f7")
apps_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 18))

sidebar_frame = Frame(main_container, bg="#eef2f7", width=350)
sidebar_frame.pack(side=RIGHT, fill=BOTH)
sidebar_frame.pack_propagate(False)

# Dimensionamento voltado à acessibilidade visual. Os limites mantêm a
# interface legível tanto em telas HD quanto em monitores Full HD/2K.
altura_tela = root.winfo_screenheight()
TAMANHO_ICONE = max(105, min(132, int(altura_tela * 0.145)))
FONTE_NOME_CARD = max(18, min(22, int(altura_tela / 43)))
FONTE_DESCRICAO_CARD = max(12, min(15, int(altura_tela / 62)))

# As imagens são mantidas neste dicionário para preservar suas referências.
# Sem uma referência Python ativa, o Tkinter pode liberar a imagem da memória.
imgs = {
    "google": carregar_icone("google_card.png", TAMANHO_ICONE, TAMANHO_ICONE),
    "gmail": carregar_icone("gmail_card.png", TAMANHO_ICONE, TAMANHO_ICONE),
    "instagram": carregar_icone("instagram_card.png", TAMANHO_ICONE, TAMANHO_ICONE),
    "facebook": carregar_icone("facebook_card.png", TAMANHO_ICONE, TAMANHO_ICONE),
    "cnn": carregar_icone("cnn_card.png", TAMANHO_ICONE, TAMANHO_ICONE),
    "youtube": carregar_icone("youtube_card.png", TAMANHO_ICONE, TAMANHO_ICONE),
    "netflix": carregar_icone("netflix_card.png", TAMANHO_ICONE, TAMANHO_ICONE),
    "whatsapp": carregar_icone("whatsapp_card.png", TAMANHO_ICONE, TAMANHO_ICONE),
    "meu_inss": carregar_icone("meu_inss_card.png", TAMANHO_ICONE, TAMANHO_ICONE),
    "gov": carregar_icone("gov_card.png", TAMANHO_ICONE, TAMANHO_ICONE),
    "calc": carregar_icone("calc_card.png", TAMANHO_ICONE, TAMANHO_ICONE),
    "notepad": carregar_icone("notepad_card.png", TAMANHO_ICONE, TAMANHO_ICONE),
}

botoes_config = [
    ("Google", "google.com", imgs["google"], "https://www.google.com"),
    ("Gmail", "google.com/gmail", imgs["gmail"], "https://www.google.com/intl/pt_br/gmail/about/"),
    ("Instagram", "instagram.com", imgs["instagram"], "https://www.instagram.com/"),
    ("Facebook", "facebook.com", imgs["facebook"], "https://facebook.com"),
    ("CNN Brasil", "cnnbrasil.com.br", imgs["cnn"], "https://www.cnnbrasil.com.br/"),
    ("YouTube", "youtube.com", imgs["youtube"], "https://www.youtube.com"),
    ("Netflix", "netflix.com/br/", imgs["netflix"], "https://www.netflix.com/br/"),
    ("WhatsApp", "web.whatsapp.com", imgs["whatsapp"], "https://web.whatsapp.com"),
    ("Meu INSS", "gov.br/inss", imgs["meu_inss"], "https://www.gov.br/inss/pt-br"),
    ("Gov.br Portal", "gov.br/pt-br", imgs["gov"], "https://www.gov.br/pt-br"),
    ("Calculadora", "Aplicativo do sistema", imgs["calc"], "calc"),
    ("Bloco de Notas", "Aplicativo do sistema", imgs["notepad"], "notepad"),
]

# Cada coluna e linha recebe o mesmo peso, formando uma grade uniforme 4 x 3.
for c in range(4):
    apps_frame.grid_columnconfigure(c, weight=1, uniform="grid_apps")
for r in range(3):
    apps_frame.grid_rowconfigure(r, weight=1, uniform="grid_apps")

def estilizar_card(card, elementos, ativo):
    """Altera as cores do cartão ao receber foco ou passagem do mouse."""
    cor = "#f2f8ff" if ativo else "#ffffff"
    borda = "#3498db" if ativo else "#d6dce2"
    card.config(bg=cor, highlightbackground=borda, highlightcolor=borda)
    for elemento in elementos:
        elemento.config(bg=cor)

# Cria dinamicamente os 12 cartões a partir da lista de configuração.
for i, (nome, descricao, img, destino) in enumerate(botoes_config):
    r, c = divmod(i, 4)

    # Os valores são capturados como argumentos-padrão da lambda. Isso evita o
    # problema de fechamento tardio, no qual todos os botões usariam o último
    # item percorrido pelo laço.
    if destino.startswith("http"):
        cmd = lambda n=nome, u=destino: abrir_url(n, u)
    else:
        cmd = lambda n=nome, prg=destino: abrir_programa(n, prg)

    # Moldura externa produz uma sombra discreta, semelhante aos cartões da referência.
    sombra = Frame(apps_frame, bg="#c7cdd3")
    sombra.grid(row=r, column=c, sticky="nsew", padx=7, pady=7)

    card = Frame(
        sombra,
        bg="#ffffff",
        bd=0,
        highlightthickness=1,
        highlightbackground="#d6dce2",
        cursor="hand2",
        takefocus=True,
    )
    card.pack(fill=BOTH, expand=True, padx=(0, 3), pady=(0, 3))

    # O conjunto ícone/textos permanece centralizado e aproveita melhor o card.
    conteudo_frame = Frame(card, bg="#ffffff", cursor="hand2")
    conteudo_frame.pack(expand=True)

    lbl_img = Label(conteudo_frame, image=img, bg="#ffffff", cursor="hand2")
    lbl_img.pack(side=LEFT, padx=(8, 16), pady=10)

    texto_frame = Frame(conteudo_frame, bg="#ffffff", cursor="hand2")
    texto_frame.pack(side=LEFT, fill=X, expand=True, padx=(0, 8), pady=8)

    lbl_texto = Label(
        texto_frame,
        text=nome,
        font=("Segoe UI", FONTE_NOME_CARD, "bold"),
        bg="#ffffff",
        fg="#111111",
        anchor="w",
        cursor="hand2",
    )
    lbl_texto.pack(fill=X, anchor="w")

    lbl_descricao = Label(
        texto_frame,
        text=descricao,
        font=("Segoe UI", FONTE_DESCRICAO_CARD),
        bg="#ffffff",
        fg="#34495e",
        anchor="w",
        cursor="hand2",
    )
    lbl_descricao.pack(fill=X, anchor="w", pady=(2, 0))

    elementos = (conteudo_frame, lbl_img, texto_frame, lbl_texto, lbl_descricao)
    # Todos os elementos internos recebem os mesmos eventos. Assim, clicar no
    # ícone, no título, na descrição ou no fundo executa a mesma ação.
    clicaveis = (card,) + elementos
    for widget in clicaveis:
        widget.bind("<Button-1>", lambda e, c=cmd: c())
        widget.bind("<Enter>", lambda e, ca=card, el=elementos: estilizar_card(ca, el, True))
        widget.bind("<Leave>", lambda e, ca=card, el=elementos: estilizar_card(ca, el, False))

    card.bind("<Return>", lambda e, c=cmd: c())
    card.bind("<space>", lambda e, c=cmd: c())
    card.bind("<FocusIn>", lambda e, ca=card, el=elementos: estilizar_card(ca, el, True))
    card.bind("<FocusOut>", lambda e, ca=card, el=elementos: estilizar_card(ca, el, False))

sidebar_frame.grid_columnconfigure(0, weight=1)
sidebar_frame.grid_rowconfigure(0, weight=3)
sidebar_frame.grid_rowconfigure(1, weight=1)
sidebar_frame.grid_rowconfigure(2, weight=4)
sidebar_frame.grid_rowconfigure(3, weight=1)

Button(sidebar_frame, text="🚨 EMERGÊNCIA\nChamar no WhatsApp", font=("Segoe UI", 15, "bold"), bg="#e74c3c", fg="white",
       activebackground="#c0392b", activeforeground="white", relief="flat", bd=0, cursor="hand2", command=emergencia).grid(row=0, column=0, sticky="nsew", padx=5, pady=8)

Button(sidebar_frame, text="⚙️ Configurar Contato", font=("Segoe UI", 12, "bold"), bg="#34495e", fg="white",
       activebackground="#2c3e50", activeforeground="white", relief="flat", bd=0, cursor="hand2", command=configurar_emergencia).grid(row=1, column=0, sticky="nsew", padx=5, pady=8)

games_frame = Frame(sidebar_frame, bg="#ffffff", bd=1, relief="solid")
games_frame.grid(row=2, column=0, sticky="nsew", padx=5, pady=8)

Label(games_frame, text="Central de Jogos", font=("Segoe UI", 13, "bold"), bg="#ffffff", fg="#34495e").pack(pady=(14, 10))

jogos_config = [
    ("Paciência", "paciencia", "#27ae60", "#219653"),
    ("FreeCell", "freecell", "#2980b9", "#2471a3"),
    ("Mahjong", "mahjong", "#d35400", "#ba4a00"),
    ("Campo Minado", "campo_minado", "#8e44ad", "#7d3c98"),
]

# O argumento-padrão da lambda também preserva o identificador de cada jogo.
for j_nome, j_id, j_cor, j_active in jogos_config:
    Button(games_frame, text=j_nome, font=("Segoe UI", 12, "bold"), bg=j_cor, fg="white",
           activebackground=j_active, activeforeground="white", relief="flat", bd=0, cursor="hand2",
           command=lambda n=j_nome, i=j_id: abrir_jogo(n, i)).pack(fill="x", expand=True, padx=22, pady=6)

Button(sidebar_frame, text="🚪 Encerrar Aplicativo", font=("Segoe UI", 12, "bold"), bg="#7f8c8d", fg="white",
       activebackground="#95a5a6", activeforeground="white", relief="flat", bd=0, cursor="hand2",
       command=solicitar_encerramento).grid(row=3, column=0, sticky="nsew", padx=5, pady=8)

# Mesmo que futuramente a barra nativa seja reativada, o botão X será
# encaminhado para a mesma rotina protegida.
root.protocol("WM_DELETE_WINDOW", solicitar_encerramento)

# Inicia o relógio e entrega o controle ao loop de eventos do Tkinter.
atualizar_relogio()
root.mainloop()
