# status: TODO
# progress: 0/4
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
