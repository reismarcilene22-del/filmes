"""Ferramentas de producao: render do video, folha de contato e checagem de contato.

Todas recebem a mesma funcao do filme: desenhar(c, t), que desenha o instante t (em segundos) no canvas c.
"""
import os
import subprocess
from multiprocessing import Pool

import numpy as np
import skia

import cena
import personagem as pg
from desenho import W, H, FPS, P, S, fonte

_DESENHAR = [None]


def quadro(desenhar, t):
    """Um quadro pronto (RGB, com acabamento)."""
    s = skia.Surface(W, H)
    with s as c:
        desenhar(c, t)
    return cena.acabamento(cena.para_rgb(s))


_INICIO = [0.0]


def _trabalho(n):
    return quadro(_DESENHAR[0], _INICIO[0] + n / FPS).tobytes()


def render(desenhar, duracao, saida, audio=None, processos=None, celular=True, inicio=0.0):
    """Desenha todos os quadros em paralelo e entrega ao ffmpeg. Gera tambem uma copia 720p para celular.
    inicio: para renderizar so um trecho (previa de uma cena), de `inicio` ate `inicio + duracao`."""
    _DESENHAR[0] = desenhar
    _INICIO[0] = inicio
    total = int(round(duracao * FPS))
    cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-"]
    if audio:
        cmd += ["-i", audio, "-c:a", "aac", "-b:a", "256k", "-ac", "2", "-shortest"]
    cmd += ["-c:v", "libx264", "-crf", "17", "-preset", "medium", "-pix_fmt", "yuv420p", "-movflags", "+faststart", saida]
    ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    with Pool(processos or os.cpu_count()) as pool:
        for i, dados in enumerate(pool.imap(_trabalho, range(total), chunksize=4)):
            ff.stdin.write(dados)
            if i % (FPS * 5) == 0:
                print(f"  render: {i / FPS:5.1f} s de {duracao:.1f} s", flush=True)
    ff.stdin.close()
    if ff.wait() != 0:
        raise RuntimeError("ffmpeg falhou")
    if celular:
        menor = saida.replace(".mp4", "_celular.mp4")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", saida, "-vf", "scale=1280:720", "-c:v", "libx264", "-crf", "23",
                        "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", menor], check=True)
    return saida


def folha_de_contato(desenhar, inicio, fim, saida, n=12, de_video=None):
    """12 quadros de um trecho numa imagem so (4 x 3), cada um com o seu tempo.
    de_video: caminho de um mp4 pronto, para conferir o arquivo final em vez do codigo."""
    colunas, linhas = 4, 3
    w = W // colunas
    h = w * H // W                        # mesma proporcao do video: nada fica esticado
    folha = skia.Surface(W, 60 + h * linhas)
    fim = fim - 1.5 / FPS   # um pouco antes do fim: o ultimo quadro existente
    tempos = [inicio + (fim - inicio) * i / (n - 1) for i in range(n)]
    with folha as g:
        g.clear(skia.Color(0, 0, 0))
        for i, t in enumerate(tempos):
            if de_video:
                antes = max(t - 1.0, 0.0)   # pula rapido ate 1 s antes, depois anda quadro a quadro ate o instante exato
                bruto = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{antes:.3f}", "-i", de_video, "-ss", f"{t - antes:.3f}", "-frames:v", "1",
                                        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-"],
                                       capture_output=True, check=True).stdout
                rgb = np.frombuffer(bruto, np.uint8).reshape(H, W, 3)
            else:
                rgb = quadro(desenhar, t)
            img = skia.Image.fromarray(np.ascontiguousarray(np.dstack([rgb, np.full((H, W), 255, np.uint8)])),
                                       colorType=skia.kRGBA_8888_ColorType)
            x, y = (i % colunas) * w, 60 + (i // colunas) * h
            g.drawImageRect(img, skia.Rect(x + 3, y + 3, x + w - 3, y + h - 3), skia.SamplingOptions(skia.FilterMode.kLinear))
            rot = f"{int(t // 60)}:{t % 60:05.2f}"
            f = skia.Font(skia.Typeface('DejaVu Sans', skia.FontStyle.Bold()), 22)
            g.drawRect(skia.Rect(x + 3, y + 3, x + f.measureText(rot) + 20, y + 33), P((0, 0, 0), 200))
            g.drawString(rot, x + 11, y + 26, f, P((255, 255, 255)))
        f = skia.Font(skia.Typeface('DejaVu Sans', skia.FontStyle.Bold()), 30)
        origem = "do arquivo final" if de_video else "do codigo"
        g.drawString(f"Folha de contato  {inicio:.1f} s - {fim:.1f} s  ({origem})", 16, 42, f, P((235, 225, 255)))
    folha.makeImageSnapshot().save(saida, skia.kPNG)
    return saida


def checagem_de_contato(desenhar, duracao):
    """Passa por TODOS os quadros e lista cada momento em que uma mao ou pe nao alcanca o que deveria tocar."""
    pg.FALHAS.clear()
    rascunho = skia.Surface(64, 36)   # desenha num quadro minusculo: so queremos as contas, nao a imagem
    with rascunho as c:
        for n in range(int(round(duracao * FPS))):
            t = n / FPS
            pg.ROTULO[0] = f"{int(t // 60)}:{t % 60:05.2f}"
            c.save(); desenhar(c, t); c.restore()
    falhas = list(pg.FALHAS)
    pg.FALHAS.clear()
    if not falhas:
        print("checagem de contato: nenhuma falha")
        return []
    # agrupa quadros seguidos do mesmo membro num trecho so
    trechos = []
    for tempo, membro, gap in falhas:
        if trechos and trechos[-1]['membro'] == membro:
            trechos[-1]['fim'] = tempo; trechos[-1]['maior'] = max(trechos[-1]['maior'], gap); trechos[-1]['quadros'] += 1
        else:
            trechos.append({'membro': membro, 'inicio': tempo, 'fim': tempo, 'maior': gap, 'quadros': 1})
    print(f"checagem de contato: {len(falhas)} quadros com falha")
    for tr in trechos:
        print(f"  {tr['inicio']} - {tr['fim']}: {tr['membro']} nao alcanca (faltam ate {tr['maior']} px, {tr['quadros']} quadros)")
    return trechos
