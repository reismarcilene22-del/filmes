"""Parte 3: uma cena curta em movimento, para testar render, folha de contato e checagem de contato.

O personagem entra andando, o vilao acende, ele vai ate o interruptor, aperta, e o letreiro apaga.
Rode com ERRO=1 para ver a checagem pegando uma mao que nao encosta.
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import skia
import cena
import personagem as pg
import render
from desenho import W, H, LILAS, P, S, brilho, suave, entre

AQUI = os.path.dirname(__file__)
ERRO = os.environ.get("ERRO") == "1"
CHAO = 900
DURACAO = 10.0

# Todos os tempos num lugar so (imagem e musica usam os mesmos numeros).
TEMPOS = {
    'entra': (0.0, 2.6),        # anda da esquerda ate o meio
    'legenda1': (0.6, 3.4),
    'vilao_acende': 2.9,
    'anda_ate_interruptor': (5.0, 6.2),
    'estica_mao': (6.4, 6.9),
    'aperta': 7.0,
    'solta': (7.6, 8.0),
    'legenda2': (7.6, 10.0),
}

INTERRUPTOR = (1205, CHAO - 250) if not ERRO else (1300, CHAO - 330)   # com ERRO, longe demais


def interruptor(c, ligado):
    """Um poste com um botao. Devolve o ponto exato onde a mao deve apertar."""
    x, y = INTERRUPTOR
    c.drawLine(x + 22, y + 10, x + 22, CHAO, S((60, 55, 90), 10))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(x - 4, y - 26, x + 48, y + 26), 10, 10), P((90, 85, 130)))
    c.drawCircle(x + 22, y, 12, P((200, 195, 230) if ligado else (120, 115, 150)))
    return (x, y)


def posicao(t):
    """Onde o personagem esta e quanto ja andou (a trilha de som usa isto para os passos)."""
    T = TEMPOS
    x0, x1, x2 = -150, 820, 1080
    a, b = T['entra']; a2, b2 = T['anda_ate_interruptor']
    if t < b:
        x = x0 + (x1 - x0) * entre(t, a, b)
    elif t < a2:
        x = x1
    else:
        x = x1 + (x2 - x1) * suave(entre(t, a2, b2))
    return x, x - x0


def desenhar(c, t):
    T = TEMPOS
    cena.fundo(c, luz=(900, 640))
    zoom = cena.aproximar(t, T['vilao_acende'], T['vilao_acende'] + 2.0, 1.0, 1.06)
    zoom = zoom - 0.06 * suave(entre(t, T['aperta'] + 0.2, T['aperta'] + 1.4))
    cam = cena.Camera(zoom=zoom, foco=(W / 2, H / 2 + 30), tremor=1.0 if T['aperta'] < t < T['aperta'] + 0.25 else 0, t=t)
    c.save(); cam.aplica(c)
    cena.placa(c, 320, 300, 200, 80)
    cena.chao(c, CHAO)
    ponto = interruptor(c, ligado=t < T['aperta'])
    cena.letreiro(c, 1560, 520, "desiste.", t, acende=T['vilao_acende'], apaga=T['aperta'])

    x, andou = posicao(t)
    a, b = T['entra']; a2, b2 = T['anda_ate_interruptor']
    pose = pg.Pose(x, CHAO, 1.0, respiracao=__import__('math').sin(t * 2.2))
    for ini, fim in ((a, b), (a2, b2)):
        if ini <= t < fim:
            intensidade = min(entre(t, ini, ini + 0.3), 1 - entre(t, fim - 0.3, fim))
            pg.caminhar(pose, andou, intensidade=suave(intensidade))

    # expressao e olhar
    if t < T['vilao_acende'] + 0.1:
        pose.expressao, pose.olhar = 'neutro', (0.3, 0)
    elif t < a2:
        pose.expressao, pose.olhar = 'assustado', (0.8, -0.2)
    else:
        pose.expressao, pose.olhar = 'determinado', (0.8, 0)
    if T['aperta'] + 0.3 < t:
        pose.expressao = 'feliz'
    if 1.8 < t < 1.9 or 8.6 < t < 8.7:
        pose.piscar = 1.0

    # a mao vai ate o botao, aperta e volta
    e0, e1 = T['estica_mao']; s0, s1 = T['solta']
    if e0 <= t < s1:
        solta = pg.mao_solta(pose, 1)
        k = suave(entre(t, e0, e1)) * (1 - suave(entre(t, s0, s1)))
        alvo = (ponto[0] + (6 if T['aperta'] <= t < s0 else 0), ponto[1])
        pose.mao_dir = (solta[0] + (alvo[0] - solta[0]) * k, solta[1] + (alvo[1] - solta[1]) * k)
        if k < 0.999:
            pose.maos_livres = True     # ainda a caminho: nao e contato
    pg.desenha(c, pose)
    c.restore()

    cena.legenda(c, "Ele ia começar amanhã.", t, *T['legenda1'])
    cena.legenda(c, "Começa hoje.", t, *T['legenda2'], destaque=True)
    cena.mostrador(c, "DIA 1" if t < T['aperta'] else "DIA 2", t, mudou_em=T['aperta'])


if __name__ == "__main__":
    import time
    print("checando contato...")
    render.checagem_de_contato(desenhar, DURACAO)
    if ERRO:
        sys.exit()
    render.folha_de_contato(desenhar, 0, DURACAO, os.path.join(AQUI, "t3_folha.png"))
    t0 = time.time()
    saida = render.render(desenhar, DURACAO, os.path.join(AQUI, "t3_demo.mp4"))
    print(f"render em {time.time() - t0:.0f} s")
    render.folha_de_contato(desenhar, 0, DURACAO, os.path.join(AQUI, "t3_folha_do_video.png"), de_video=saida)
