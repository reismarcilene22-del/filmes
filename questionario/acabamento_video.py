"""Teste do acabamento escolhido: vinheta + brilho neon (sem grao, sem faixas, sem traco tremidinho)."""
import subprocess, numpy as np, skia
from scipy.ndimage import gaussian_filter
import personagem as pg

W, H, FPS, SEG = 1920, 1080, 30, 4
GROUND = 900
RED = (255, 45, 60)
FONT = 'Comic Neue'

def boil(frame):
    # the outline is re-drawn slightly differently every 3 frames
    return None  # traco tremidinho desligado

def desenha(frame):
    t = frame / FPS
    s = skia.Surface(W, H)
    with s as c:
        pg.EFEITO = None
        c.clear(skia.Color(14, 10, 28))
        pg.glow(c, 320, 300, 340, (70, 55, 120)); pg.glow(c, 1660, 280, 300, (50, 70, 120))
        pg.glow(c, 660, 640, 440, (255, 240, 220), 35)
        pg.EFEITO = boil(frame)
        c.drawRect(skia.Rect(220, 260, 420, 340), pg.S((70, 55, 120), 8))
        c.drawLine(0, GROUND, W, GROUND, pg.S((70, 55, 120), 5))
        # breathing: a tiny rise and fall
        pg.personagem(c, 660, GROUND + 2 * np.sin(t * 2.2), 1.05)
        # villain sign flickers on at 1.5 s
        on = t > 1.5 and not (1.6 < t < 1.68 or 1.8 < t < 1.85)
        if on:
            pg.EFEITO = None; pg.glow(c, 1340, 640, 300, RED, 100); pg.EFEITO = boil(frame)
            c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(1140, 580, 1540, 700), 20, 20), pg.S(RED, 8))
            f = skia.Font(skia.Typeface(FONT, skia.FontStyle.Bold()), 66)
            c.drawString("desiste.", 1340 - f.measureText("desiste.") / 2, 662, f, pg.P(RED))
        pg.EFEITO = None
        f = skia.Font(skia.Typeface(FONT, skia.FontStyle.Bold()), 80)
        a = int(255 * min(1, t / 0.5))
        txt = "Ele ia começar amanhã."
        c.drawString(txt, W / 2 - f.measureText(txt) / 2, 250, f, pg.P((245, 242, 235), a))
    return s.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType)[:, :, :3].astype(np.float32)

yy, xx = np.mgrid[0:H, 0:W]
VINHETA = np.clip(1.15 - 0.45 * np.hypot((xx - W / 2) / (W / 2), (yy - H / 2) / (H / 2)) ** 2, 0, 1)[:, :, None]
BARRA = int(H * 0.09)

def acabamento(a, frame):
    a = a + gaussian_filter(np.clip(a - 160, 0, None), sigma=(28, 28, 0))          # brilho neon
    a = a * VINHETA                                                               # vinheta
    return np.clip(a, 0, 255).astype(np.uint8)

if __name__ == "__main__":
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                           "-i", "-", "-c:v", "libx264", "-crf", "17", "-pix_fmt", "yuv420p", "6_acabamento_final.mp4"], stdin=subprocess.PIPE)
    for fr in range(FPS * SEG):
        img = acabamento(desenha(fr), fr)
        ff.stdin.write(img.tobytes())
        if fr == 75:
            rgba = np.dstack([img, np.full((H, W), 255, np.uint8)])
            skia.Image.fromarray(rgba, colorType=skia.kRGBA_8888_ColorType).save("6_acabamento_final.png", skia.kPNG)
    ff.stdin.close(); ff.wait()
