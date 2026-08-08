# Guia Didático — Fácil Click V1.2.5 Comentado

## 1. Visão geral

O projeto combina duas tecnologias de interface:

- **Tkinter**: constrói o menu principal, os cartões, a barra de status e a
  central lateral;
- **pywebview/WebView2**: exibe páginas web e os jogos HTML em janelas próprias.

A separação em processos evita que o loop de eventos de uma tecnologia bloqueie
ou interfira no loop da outra.

## 2. Responsabilidade de cada arquivo

### `facil_click_v1_2_5.py`

É o ponto de entrada principal. Ele:

1. configura DPI e dependências opcionais;
2. localiza os recursos do projeto;
3. cria a interface Tkinter;
4. associa cliques e atalhos;
5. inicia navegador e jogos por `subprocess.Popen`.

### `navegador_controlado.py`

Valida a URL, cria uma janela WebView2 e injeta uma barra de navegação por
JavaScript. O objeto `ApiNavegador` forma uma ponte restrita entre JavaScript e
Python.

### `jogos_controlados.py`

Valida o identificador do jogo, carrega o HTML local, substitui o marcador
`__JOGO_INICIAL__` e abre o conteúdo no pywebview.

### `jogos_offline.html`

Contém três camadas:

- HTML: estrutura básica da tela;
- CSS: aparência responsiva e acessível;
- JavaScript: estado, regras e renderização dos quatro jogos.

## 3. Fluxo de um clique em um site

1. O usuário clica no cartão.
2. A função `abrir_url` monta o comando.
3. `subprocess.Popen` cria outro processo Python.
4. `navegador_controlado.py` abre o WebView2.
5. Após a página carregar, a barra de controle é injetada.
6. O botão **VOLTAR AO FÁCIL CLICK** destrói somente essa janela.

## 4. Fluxo de um clique em um jogo

1. O botão lateral chama `abrir_jogo`.
2. O identificador, como `campo_minado`, é enviado ao processo separado.
3. `jogos_controlados.py` confirma que o identificador é permitido.
4. O HTML recebe o identificador e chama a inicializadora correspondente.
5. O jogo altera seu estado em memória e a função `render` atualiza a tela.

## 5. Conceitos importantes presentes no código

- **tratamento de exceções** com `try/except`;
- **dependências opcionais** com fallback;
- **programação orientada a eventos**;
- **funções internas** para encapsular o estado de cada jogo;
- **closures** e captura de valores em `lambda`;
- **comunicação Python–JavaScript** por `js_api`;
- **renderização baseada em estado**;
- **recursão** na abertura automática do Campo Minado;
- **algoritmo Fisher–Yates** para embaralhamento;
- **design responsivo** com `clamp` e `@media`.

## 6. Observação de segurança

O navegador limita downloads, protocolos externos, pop-ups e ferramentas de
desenvolvedor dentro da janela. Esse mecanismo melhora o controle da navegação,
mas não bloqueia sozinho os recursos gerais do Windows. Isolamento completo
exige configuração adicional do sistema operacional, como Modo Quiosque.

## Barreira de autorização para encerramento

A função `solicitar_encerramento()` demonstra controle de eventos de teclado,
janela modal, captura de foco e temporização não bloqueante com `after()`.
O encerramento ocorre somente após o evento `Ctrl + Alt + Shift + E` ser
reconhecido. A combinação é uma barreira operacional contra cliques acidentais;
não deve ser tratada como substituta das permissões e políticas do Windows.

## Ambiente Python automático

A versão atual acrescenta uma camada de inicialização independente do PyCharm.
O arquivo `INICIAR_FACIL_CLICK.bat` usa caminhos relativos (`%~dp0`), verifica a
`.venv` e chama `CONFIGURAR_AMBIENTE.bat` quando necessário.

O configurador localiza o Python 3.10, cria o ambiente com `python -m venv`,
instala as dependências do `requirements.txt` e executa
`verificar_ambiente.py`. O arquivo `iniciador_facil_click.py` utiliza `runpy`
para executar o módulo principal e grava exceções em `logs/facil_click.log`.
Essa arquitetura separa quatro responsabilidades: preparação, validação,
inicialização e aplicação gráfica.
