# status: TODO
# progress: 0/7
# updated: 2026-10-29
# language: pt
Funcionalidade: Gravação da sessão e allowlist legível por máquina
  Cenário: Allowlist em JSON (sucesso)
    Quando o usuário roda "zenpilot allow --json"
    Então recebe a allowlist, as grants vigentes e allow_all_sites em JSON

  Cenário: Gravar e rever (sucesso)
    Dado que o usuário rodou "zenpilot record start"
    Quando o Claude navega, clica e digita no Zen
    E o usuário roda "zenpilot record stop"
    Então existe um recording.html com um frame por ação, sem o texto digitado

  Cenário: Parar sem gravar (erro)
    Quando o usuário roda "zenpilot record stop" sem gravação ativa
    Então a resposta é "Not recording"

  Cenário: GIF sem Pillow (desvio)
    Dado que o Pillow não está instalado
    Quando a gravação é parada
    Então só o HTML é gerado e a mensagem ensina "zenpilot[gif]"

  Cenário: Claude não age em aba alheia (erro)
    Dado que o usuário abriu uma aba logada no banco
    Quando o Claude tenta ler essa aba
    Então a chamada é bloqueada e o Claude é orientado a pedir com attach_tab

  Cenário: Usuário entrega uma aba (sucesso)
    Quando o Claude chama attach_tab nessa aba
    E o usuário escolhe "Allow"
    Então o Claude passa a ler e agir nela

  Cenário: Outra sessão Claude (desvio)
    Dado que a sessão A abriu uma aba
    Quando a sessão B tenta clicar nela
    Então a chamada é bloqueada mesmo se B pedir attach_tab
