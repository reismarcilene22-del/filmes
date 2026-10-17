"""O personagem: cabeca redonda, corpo arredondado, bracos e pernas de palito.

Maos e pes vao a pontos exatos. Quando nao alcancam, a falta fica registrada em FALHAS
(e a checagem de contato usa isso para achar maos flutuando).
"""
import math
from dataclasses import dataclass, field

import skia

from desenho import CREME, LILAS, TINTA, P, S

# Medidas em escala 1 (pixels), a partir do chao.
CABECA_R = 110
CABECA_Y = 380
CORPO = (136, 180, 260)        # largura, altura, topo acima do chao
QUADRIL_Y = 92
BRACO = (78, 74)               # braco, antebraco
PERNA = (46, 46)               # coxa, canela (somam a altura do quadril: em pe fica reta)
GROSSURA_BRACO = 20
GROSSURA_PERNA = 28
TOLERANCIA = 3.0               # px: abaixo disso conta como encostado

FALHAS = []                    # (rotulo, membro, distancia_em_px)
ROTULO = ['']                  # quem esta desenhando agora (ex.: "cena 3, quadro 120")

EXPRESSOES = ('neutro', 'feliz', 'triste', 'determinado', 'assustado', 'cansado')


@dataclass
class Pose:
    x: float                          # centro do personagem
    chao: float                       # linha do chao
    escala: float = 1.0
    mao_esq: tuple = None             # ponto exato para a mao (None = braco solto)
    mao_dir: tuple = None
    pe_esq: tuple = None              # ponto exato para o pe (None = em pe parado)
    pe_dir: tuple = None
    inclinacao: float = 0.0           # graus; positivo inclina para a direita
    respiracao: float = 0.0           # -1..1, sobe e desce um pouco
    agachar: float = 0.0              # px que o quadril desce (dobra os joelhos)
    expressao: str = 'neutro'
    olhar: tuple = (0.0, 0.0)         # para onde os olhos apontam (-1..1, -1..1)
    piscar: float = 0.0               # 0 aberto, 1 fechado
    lagrima: float = 0.0              # 0..1, usar uma vez so
    cor: tuple = CREME
    joelhos: int = 0                  # 0 = abrem para os lados (de frente); +1/-1 = apontam para direita/esquerda (andando)
    maos_livres: bool = False         # True: maos soltas (caminhada), nao checar contato
    contorno: tuple = LILAS


def alcance(raiz, alvo, l1, l2, dobra):
    """Dois ossos (braco+antebraco ou coxa+canela). Devolve cotovelo, ponta e quanto faltou."""
    dx, dy = alvo[0] - raiz[0], alvo[1] - raiz[1]
    d = math.hypot(dx, dy)
    falta = max(0.0, d - (l1 + l2))
    d = min(max(d, abs(l1 - l2) + 1e-3), l1 + l2 - 1e-3)
    a = math.atan2(dy, dx)
    b = math.acos(max(-1.0, min(1.0, (l1 * l1 + d * d - l2 * l2) / (2 * l1 * d))))
    ang = a + b * dobra
    meio = (raiz[0] + math.cos(ang) * l1, raiz[1] + math.sin(ang) * l1)
    ponta = (raiz[0] + math.cos(a) * d, raiz[1] + math.sin(a) * d)
    return meio, ponta, falta


def pontos(p: Pose):
    """Onde ficam ombros e quadris (util para a cena posicionar objetos)."""
    s = p.escala
    sobe = p.respiracao * 3 * s
    topo = p.chao - (CORPO[2] - 0) * s + p.agachar - sobe
    ombro_y = topo + 34 * s
    return {
        'ombro_esq': (p.x - 50 * s, ombro_y),
        'ombro_dir': (p.x + 50 * s, ombro_y),
        'quadril_esq': (p.x - 28 * s, p.chao - QUADRIL_Y * s + p.agachar),
        'quadril_dir': (p.x + 28 * s, p.chao - QUADRIL_Y * s + p.agachar),
        'cabeca': (p.x, p.chao - CABECA_Y * s + p.agachar - sobe * 1.3),
    }


def _membro(c, raiz, alvo, padrao, l1, l2, dobra, grossura, cor, nome, ponta_raio):
    """dobra: +1/-1 forca o lado do joelho; 0 escolhe o cotovelo mais baixo (o natural)."""
    if alvo is None:
        alvo = padrao
        checar = False
    else:
        checar = True
    if dobra == 0:
        a = alcance(raiz, alvo, l1, l2, 1); b = alcance(raiz, alvo, l1, l2, -1)
        meio, ponta, falta = a if a[0][1] >= b[0][1] else b
    else:
        meio, ponta, falta = alcance(raiz, alvo, l1, l2, dobra)
    if checar and nome and falta > TOLERANCIA:
        FALHAS.append((ROTULO[0], nome, round(falta, 1)))
    path = skia.Path()
    path.moveTo(*raiz); path.lineTo(*meio); path.lineTo(*ponta)
    c.drawPath(path, S(cor, grossura))
    if ponta_raio:
        c.drawCircle(ponta[0], ponta[1], ponta_raio, P(cor))
    return ponta


def _rosto(c, cx, cy, s, p: Pose):
    e = p.expressao
    ox, oy = p.olhar[0] * 14 * s, p.olhar[1] * 8 * s
    abertura = {'cansado': 0.45, 'assustado': 1.25}.get(e, 1.0) * (1 - p.piscar)
    for lado in (-1, 1):
        ex, ey = cx + lado * 28 * s + ox, cy + oy
        r = 12 * s
        if abertura > 0.15:
            c.save()
            c.scale(1, 1)
            c.drawOval(skia.Rect(ex - r, ey - r * abertura, ex + r, ey + r * abertura), P(TINTA))
            c.drawCircle(ex + 3.5 * s, ey - 4 * s * abertura, 3.2 * s, P((255, 255, 255)))
            c.restore()
        else:
            c.drawLine(ex - r, ey, ex + r, ey, S(TINTA, 4 * s))
        if e == 'cansado':  # olheiras
            olheira = skia.Path(); olheira.moveTo(ex - 11 * s, ey + 16 * s)
            olheira.quadTo(ex, ey + 22 * s, ex + 11 * s, ey + 16 * s)
            c.drawPath(olheira, S(p.contorno, 3 * s, 160))
        # sobrancelhas: para baixo no meio = bravo/determinado; para cima no meio = triste/preocupado
        inclina = {'determinado': -1, 'triste': 1, 'assustado': 0.6, 'cansado': 0.5}.get(e, 0)
        alto = {'assustado': -10, 'feliz': -4}.get(e, 0) * s
        by = ey - 30 * s + alto
        dentro, fora = ex - lado * 13 * s, ex + lado * 13 * s
        c.drawLine(dentro, by - inclina * 7 * s, fora, by + inclina * 5 * s, S(TINTA, 5 * s))
    # boca
    mx, my = cx + ox * 0.5, cy + 42 * s
    boca = skia.Path()
    if e == 'feliz':
        boca.moveTo(mx - 24 * s, my - 4 * s); boca.quadTo(mx, my + 22 * s, mx + 24 * s, my - 4 * s)
        c.drawPath(boca, S(TINTA, 5 * s))
    elif e == 'triste':
        boca.moveTo(mx - 18 * s, my + 8 * s); boca.quadTo(mx, my - 8 * s, mx + 18 * s, my + 8 * s)
        c.drawPath(boca, S(TINTA, 5 * s))
    elif e == 'assustado':
        c.drawOval(skia.Rect(mx - 11 * s, my - 8 * s, mx + 11 * s, my + 16 * s), P(TINTA))
    elif e == 'determinado':
        c.drawLine(mx - 16 * s, my + 2 * s, mx + 16 * s, my, S(TINTA, 5 * s))
    elif e == 'cansado':
        boca.moveTo(mx - 14 * s, my + 4 * s); boca.quadTo(mx, my, mx + 14 * s, my + 5 * s)
        c.drawPath(boca, S(TINTA, 4 * s))
    else:
        boca.moveTo(mx - 18 * s, my - 2 * s); boca.quadTo(mx, my + 12 * s, mx + 18 * s, my - 2 * s)
        c.drawPath(boca, S(TINTA, 5 * s))
    if p.lagrima > 0:
        lx, ly = cx + 34 * s + ox, cy + 16 * s + p.lagrima * 40 * s
        gota = skia.Path(); gota.moveTo(lx, ly - 12 * s)
        gota.quadTo(lx + 8 * s, ly, lx, ly + 6 * s); gota.quadTo(lx - 8 * s, ly, lx, ly - 12 * s)
        c.drawPath(gota, P((200, 225, 255), 230 * (1 - max(0, p.lagrima - 0.8) * 5)))


def desenha(c, p: Pose):
    s = p.escala
    pt = pontos(p)
    sobe = p.respiracao * 3 * s

    c.save()
    c.rotate(p.inclinacao, p.x, p.chao)

    # pernas (atras do corpo)
    for lado, alvo, nome in ((-1, p.pe_esq, 'pe esquerdo'), (1, p.pe_dir, 'pe direito')):
        quadril = pt['quadril_esq' if lado < 0 else 'quadril_dir']
        padrao = (quadril[0] + lado * p.agachar * 0.4, p.chao)
        _membro(c, quadril, alvo, padrao, PERNA[0] * s, PERNA[1] * s, -p.joelhos if p.joelhos else -lado, GROSSURA_PERNA * s,
                p.cor, nome, 0)

    # corpo
    larg, alt, topo = CORPO
    y0 = p.chao - topo * s + p.agachar - sobe
    corpo = skia.RRect.MakeRectXY(skia.Rect(p.x - larg / 2 * s, y0, p.x + larg / 2 * s, y0 + alt * s), 56 * s, 56 * s)
    c.drawRRect(corpo, P(p.cor)); c.drawRRect(corpo, S(p.contorno, 6 * s))

    # bracos: na frente do corpo, mas atras da cabeca (um braco erguido nunca cobre o rosto)
    for lado, alvo, nome in ((-1, p.mao_esq, 'mao esquerda'), (1, p.mao_dir, 'mao direita')):
        ombro = pt['ombro_esq' if lado < 0 else 'ombro_dir']
        padrao = (ombro[0] + lado * 24 * s, ombro[1] + 146 * s)
        if p.maos_livres:
            nome = None
        _membro(c, ombro, alvo, padrao, BRACO[0] * s, BRACO[1] * s, 0, GROSSURA_BRACO * s,
                p.cor, nome, 13 * s)
    # cabeca
    hx, hy = pt['cabeca']
    c.drawCircle(hx, hy, CABECA_R * s, P(p.cor)); c.drawCircle(hx, hy, CABECA_R * s, S(p.contorno, 6 * s))
    _rosto(c, hx, hy, s, p)

    c.restore()


def mao_solta(p: Pose, lado):
    """Onde a mao fica com o braco solto (lado -1 esquerda, +1 direita)."""
    s = p.escala
    ombro = pontos(p)['ombro_esq' if lado < 0 else 'ombro_dir']
    return (ombro[0] + lado * 24 * s, ombro[1] + 146 * s)


def caminhar(p: Pose, distancia, passo=70, levanta=22, balanco=26, intensidade=1.0):
    """Coloca pes e maos numa caminhada. `distancia` = quanto ele ja andou (px, cresce para a direita).
    O pe de apoio fica parado no chao enquanto o corpo passa: o pe nunca escorrega.
    intensidade: 1 = andando, 0 = parado (use para comecar e terminar a caminhada sem pulo)."""
    s = p.escala
    L = passo * s
    perna = (PERNA[0] + PERNA[1]) * s
    pes = []
    for lado, offset in ((-1, 0.0), (1, L)):
        u = (distancia + offset) % (2 * L)
        if u < L:                       # apoio: pe no chao, indo para tras em relacao ao corpo
            rel, y = L / 2 - u, 0.0
        else:                           # balanco: pe no ar, indo para a frente
            rel = u - 1.5 * L
            y = -math.sin(math.pi * (u - L) / L) * levanta * s
        pes.append((lado, rel * intensidade, y * intensidade))
    # o quadril desce o suficiente para a perna de apoio alcancar o chao (mais 1 px de folga)
    precisa = max(perna - math.sqrt(max(perna * perna - rel * rel, 0)) for _, rel, y in pes if y == 0) if any(y == 0 for _, _, y in pes) else 0
    p.agachar = max(p.agachar, precisa + 1.0 * s * intensidade)
    pt = pontos(p)
    for lado, rel, y in pes:
        quadril = pt['quadril_esq' if lado < 0 else 'quadril_dir']
        alvo = (quadril[0] + rel, p.chao + y)
        if lado < 0: p.pe_esq = alvo
        else: p.pe_dir = alvo
        # bracos balancam ao contrario das pernas
        mx, my = mao_solta(p, lado)
        alvo_mao = (mx - rel * balanco / (L / 2) * 0.9, my - abs(rel) * 0.15)
        if lado < 0: p.mao_esq = alvo_mao
        else: p.mao_dir = alvo_mao
    p.maos_livres = True
    p.joelhos = 1 if passo > 0 else -1   # joelho aponta para onde ele anda
    return p
