# Fácil Click V1.2.5 — Ambiente Python Automático

Esta versão reúne a interface acessível, navegador controlado, jogos offline,
código comentado e encerramento protegido. O projeto não depende do PyCharm.

## Inicialização normal

Execute na pasta principal:

```text
INICIAR_FACIL_CLICK.bat
```

Na primeira execução, o próprio arquivo BAT:

1. localiza o Python 3.10 de 64 bits;
2. cria uma `.venv` exclusiva e relativa à pasta do aplicativo;
3. atualiza `pip`, `setuptools` e `wheel`;
4. instala Pillow, pyttsx3, pywebview e suas dependências;
5. verifica bibliotecas, Tkinter, ícones e módulos;
6. abre o Fácil Click sem manter o CMD na tela.

Nas execuções seguintes, a configuração é reutilizada e a abertura é direta.

## Arquivos de suporte

- `CONFIGURAR_AMBIENTE.bat`: cria ou atualiza a `.venv`;
- `REPARAR_AMBIENTE.bat`: apaga somente a `.venv` e a recria;
- `INICIAR_COM_DIAGNOSTICO.bat`: mantém o console aberto para testes;
- `BIBLIOTECAS_INSTALADAS.txt`: é gerado após a instalação;
- `logs/configuracao_ambiente.log`: relatório da instalação;
- `logs/facil_click.log`: histórico de execução do aplicativo.

## Dependência externa do Windows

O navegador incorporado utiliza o Microsoft Edge WebView2 Runtime, normalmente
presente em instalações atualizadas do Windows 10 e Windows 11.

## Encerramento protegido

Ao clicar em **Encerrar Aplicativo**, a autorização exige:

```text
Ctrl + Alt + Shift + E
```

O prazo é de 20 segundos. `Esc` cancela a operação.

## Observação sobre portabilidade

A pasta `.venv` é criada na própria máquina porque ambientes virtuais do
Windows registram referências ao interpretador instalado. Copiar uma `.venv`
pronta entre computadores pode quebrar esses vínculos. O BAT automatiza a
criação correta no local em que o pacote for extraído.
