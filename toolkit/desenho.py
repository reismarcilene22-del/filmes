"""Cores do estilo e pequenas ajudas de desenho usadas por todas as outras pecas."""
import skia

W, H, FPS = 1920, 1080, 30

# Paleta (ver estilo.md). Vermelho e verde sao reservados: so vilao/ruim e so bom.
FUNDO = (14, 10, 28)
ROXO = (70, 55, 120)
AZUL = (50, 70, 120)
CREME = (238, 232, 220)
LILAS = (150, 140, 190)
TINTA = (20, 14, 36)
BRANCO = (245, 242, 235)
VERMELHO = (255, 45, 60)
VERDE = (60, 230, 120)

FONTE = 'Comic Neue'


def P(cor, a=255):
    """Pincel de preenchimento."""
    return skia.Paint(Color=skia.Color(*(int(v) for v in cor), int(a)), AntiAlias=True)


def S(cor, largura, a=255):
    """Pincel de contorno, com pontas arredondadas."""
    return skia.Paint(Color=skia.Color(*(int(v) for v in cor), int(a)), AntiAlias=True, Style=skia.Paint.kStroke_Style,
                      StrokeWidth=largura, StrokeCap=skia.Paint.kRound_Cap, StrokeJoin=skia.Paint.kRound_Join)


def brilho(c, x, y, raio, cor, a=110):
    """Uma mancha de luz suave (lampada, letreiro, foco)."""
    p = skia.Paint(AntiAlias=True)
    cor = tuple(int(v) for v in cor)
    p.setShader(skia.GradientShader.MakeRadial((x, y), raio, [skia.Color(*cor, int(a)), skia.Color(*cor, 0)]))
    c.drawCircle(x, y, raio, p)


def fonte(tamanho, negrito=True):
    return skia.Font(skia.Typeface(FONTE, skia.FontStyle.Bold() if negrito else skia.FontStyle.Normal()), tamanho)


def suave(t):
    """Aceleracao e desaceleracao suaves (0..1 -> 0..1)."""
    t = min(max(t, 0.0), 1.0)
    return t * t * (3 - 2 * t)


def mola(t):
    """Passa um pouco do ponto e volta (para coisas que 'pulam')."""
    import math
    t = min(max(t, 0.0), 1.0)
    return 1 - math.cos(t * math.pi * 2.5) * math.exp(-t * 5) if t < 1 else 1.0


def entre(t, inicio, fim):
    """Progresso 0..1 de t dentro do intervalo [inicio, fim]."""
    if fim <= inicio:
        return 1.0 if t >= fim else 0.0
    return min(max((t - inicio) / (fim - inicio), 0.0), 1.0)
