"""Kit de som: instrumentos, efeitos, a voz do vilao, mixagem e medicao de volume como num celular.

Tudo feito com matematica (numpy/scipy), sem gravacoes. Nada e aleatorio de verdade: o mesmo som sai sempre igual.
"""
import os
import subprocess
import tempfile

import numpy as np
from scipy import signal
from scipy.io import wavfile

SR = 48000


# ---------- basico ----------

def _t(dur):
    return np.arange(int(dur * SR)) / SR


def _ruido(dur, semente):
    return np.random.default_rng(semente).standard_normal(int(dur * SR))


def _filtro(x, tipo, freq, ordem=2):
    sos = signal.butter(ordem, freq, btype=tipo, fs=SR, output='sos')
    return signal.sosfilt(sos, x)


def _env(n, ataque=0.005, queda=0.3, sustenta=0.0, solta=0.05):
    """Envelope: sobe em `ataque`, cai exponencialmente com `queda` (s) ate `sustenta`, e solta no fim."""
    t = np.arange(n) / SR
    e = np.minimum(t / max(ataque, 1e-4), 1.0)
    e *= sustenta + (1 - sustenta) * np.exp(-np.maximum(t - ataque, 0) / max(queda, 1e-4))
    r = int(solta * SR)
    if r and n > r:
        e[-r:] *= np.linspace(1, 0, r)
    return e


def _norm(x, pico=0.9):
    m = np.max(np.abs(x)) or 1.0
    return x / m * pico


def eco(x, tamanho=1.2, mistura=0.25, semente=7):
    """Reverberacao simples (sala escura e grande)."""
    ir = _ruido(tamanho, semente) * np.exp(-np.arange(int(tamanho * SR)) / SR * (6.0 / tamanho))
    ir = _filtro(ir, 'lowpass', 5000)
    molhado = signal.fftconvolve(x, ir)[: len(x) + int(tamanho * SR)]
    seco = np.concatenate([x, np.zeros(len(molhado) - len(x))])
    return seco + _norm(molhado, np.max(np.abs(x)) or 1) * mistura


def db(v):
    return 10 ** (v / 20)


# ---------- notas e acordes ----------

_NOMES = {'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3, 'E': 4, 'F': 5, 'F#': 6, 'Gb': 6, 'G': 7,
          'G#': 8, 'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11}


def freq(midi):
    return 440.0 * 2 ** ((midi - 69) / 12)


def acorde(nome, oitava=3):
    """'Dm' -> notas MIDI da triade (fundamental, terca, quinta)."""
    menor = nome.endswith('m')
    raiz = nome[:-1] if menor else nome
    base = 12 * (oitava + 1) + _NOMES[raiz]
    return [base, base + (3 if menor else 4), base + 7]


# ---------- instrumentos ----------

def piano(midi, dur=1.5, forca=0.8):
    f = freq(midi); t = _t(dur + 0.3)
    x = sum((forca ** (k * 0.5)) / k ** 1.4 * np.sin(2 * np.pi * f * k * (1 + 0.0004 * k * k) * t) * np.exp(-t * (1.2 + k * 0.6))
            for k in range(1, 9))
    martelo = _filtro(_ruido(0.02, midi), 'bandpass', [1500, 5000]) * 0.15
    x[: len(martelo)] += martelo
    return x * _env(len(t), 0.003, 3.0, 0, 0.3) * forca * 0.5


def caixinha(midi, dur=1.2):
    """Caixinha de musica."""
    f = freq(midi); t = _t(dur)
    x = np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * f * 3.01 * t) * np.exp(-t * 6)
    return x * _env(len(t), 0.002, 0.5, 0, 0.1) * 0.35


def sino(midi, dur=3.0):
    f = freq(midi); t = _t(dur)
    x = sum(a * np.sin(2 * np.pi * f * r * t) * np.exp(-t * d) for r, a, d in
            ((1, 1, 1.0), (2.76, 0.5, 2.0), (5.4, 0.25, 3.5), (8.93, 0.12, 5)))
    return x * _env(len(t), 0.002, 4.0, 0, 0.3) * 0.25


def violao(midi, dur=2.0):
    """Corda dedilhada (Karplus-Strong)."""
    f = freq(midi); n = int(dur * SR); p = int(SR / f)
    buf = np.random.default_rng(midi).uniform(-1, 1, p)
    out = np.empty(n)
    for i in range(n):
        out[i] = buf[i % p]
        buf[i % p] = 0.996 * 0.5 * (buf[i % p] + buf[(i + 1) % p])
    return _filtro(out, 'lowpass', 4000) * 0.4


def pad(notas, dur, brilho=1500):
    """Fundo macio e continuo (varias ondas levemente desafinadas)."""
    t = _t(dur); x = np.zeros(len(t))
    for m in notas:
        for desafina in (-0.12, 0.0, 0.11):
            f = freq(m) * 2 ** (desafina / 12)
            x += sum(np.sin(2 * np.pi * f * k * t + k) / k for k in range(1, 10))
    x = _filtro(x, 'lowpass', brilho)
    return _norm(x, 0.25) * _env(len(t), min(1.0, dur / 3), 99, 1.0, min(1.0, dur / 3))


def bumbo(forca=1.0):
    """Bumbo com 'clique' em cima: o grave some no celular, o clique nao."""
    t = _t(0.5)
    f = 45 + 80 * np.exp(-t * 30)
    corpo = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7)
    clique = _filtro(_ruido(0.5, 1), 'bandpass', [1500, 4000]) * np.exp(-t * 120) * 0.5
    return (corpo + clique) * forca * 0.8


def caixa(forca=1.0):
    t = _t(0.3)
    x = _filtro(_ruido(0.3, 2), 'bandpass', [1200, 7000]) * np.exp(-t * 18) * 0.6 + np.sin(2 * np.pi * 185 * t) * np.exp(-t * 25) * 0.5
    return x * forca * 0.6


def chimbal(forca=1.0):
    t = _t(0.08)
    return _filtro(_ruido(0.08, 3), 'highpass', 7000) * np.exp(-t * 60) * forca * 0.35


# ---------- efeitos: corpo ----------

def passo(semente=0, forca=1.0):
    t = _t(0.18)
    x = _filtro(_ruido(0.18, 10 + semente), 'bandpass', [300, 2500]) * np.exp(-t * 35)
    return x * forca * 0.5


def respiracao(dur=1.2):
    t = _t(dur)
    return _filtro(_ruido(dur, 11), 'bandpass', [400, 3000]) * np.sin(np.pi * t / dur) ** 2 * 0.12


def expiracao(dur=0.9):
    t = _t(dur)
    return _filtro(_ruido(dur, 12), 'bandpass', [300, 2000]) * np.exp(-t * 3) * np.minimum(t / 0.05, 1) * 0.2


def batimento(forca=1.0):
    """Tum-tum. Cada batida tem um 'toc' medio para ser ouvida no alto-falante do celular."""
    t = _t(0.7); x = np.zeros(len(t))
    for atraso, a in ((0.0, 1.0), (0.22, 0.7)):
        i = int(atraso * SR); tt = t[: len(t) - i]
        golpe = np.sin(2 * np.pi * 55 * tt) * np.exp(-tt * 18) + 0.35 * _filtro(_ruido(len(tt) / SR, 13), 'bandpass', [500, 1500]) * np.exp(-tt * 60)
        x[i:] += golpe * a
    return x * forca * 0.7


# ---------- efeitos: objetos ----------

def papel(forca=1.0):
    t = _t(0.25)
    return _filtro(_ruido(0.25, 20), 'bandpass', [800, 6000]) * np.exp(-t * 30) * forca * 0.6


def amassar(dur=0.8):
    t = _t(dur); r = np.random.default_rng(21)
    estalos = (r.random(len(t)) > 0.996) * r.uniform(0.3, 1, len(t))
    return _filtro(signal.lfilter([1], [1, -0.9], estalos), 'highpass', 1500) * np.sin(np.pi * t / dur) * 0.4


def lapis(dur=1.0):
    t = _t(dur)
    return _filtro(_ruido(dur, 22), 'bandpass', [2000, 7000]) * (0.6 + 0.4 * np.sin(2 * np.pi * 7 * t)) * 0.15


def clique():
    t = _t(0.05)
    return _filtro(_ruido(0.05, 23), 'bandpass', [2000, 6000]) * np.exp(-t * 200) * 0.6


def tique():
    """O 'tic' do mostrador mudando."""
    t = _t(0.12)
    return (np.sin(2 * np.pi * 2200 * t) + 0.5 * np.sin(2 * np.pi * 3300 * t)) * np.exp(-t * 45) * 0.3


def vidro():
    t = _t(1.2); x = np.zeros(len(t))
    for i, f in enumerate((2400, 3150, 4100, 5300, 6900)):
        x += np.sin(2 * np.pi * f * t + i) * np.exp(-t * (4 + i))
    return (x * 0.15 + _filtro(_ruido(1.2, 24), 'highpass', 3000) * np.exp(-t * 12) * 0.5) * 0.5


def ceramica():
    t = _t(0.8)
    x = _filtro(_ruido(0.8, 25), 'bandpass', [600, 4000]) * np.exp(-t * 14)
    x += sum(np.sin(2 * np.pi * f * t) * np.exp(-t * 10) for f in (900, 1350, 2100)) * 0.1
    return x * 0.6


def agua(dur=1.5):
    t = _t(dur); r = np.random.default_rng(26); x = np.zeros(len(t))
    for i in range(int(dur * 25)):
        ini = int(r.uniform(0, dur - 0.05) * SR); f0 = r.uniform(400, 1200); tt = _t(0.04)
        x[ini: ini + len(tt)] += np.sin(2 * np.pi * np.cumsum(f0 * (1 + 2 * tt / 0.04)) / SR) * np.exp(-tt * 80)
    return (x * 0.15 + _filtro(_ruido(dur, 27), 'bandpass', [500, 3000]) * 0.05) * np.minimum(1, np.sin(np.pi * t / dur) * 3)


# ---------- efeitos: lugares ----------

def ambiente(tipo, dur):
    """'sala', 'chuva', 'rua', 'grilos', 'passaros', 'conversa' ou 'aplausos' (em loop do tamanho pedido)."""
    t = _t(dur); r = np.random.default_rng(30)
    if tipo == 'sala':
        x = _filtro(_ruido(dur, 31), 'bandpass', [150, 900]) * 0.03
    elif tipo == 'chuva':
        x = _filtro(_ruido(dur, 32), 'bandpass', [800, 8000]) * 0.12
        gotas = (r.random(len(t)) > 0.9993) * r.uniform(0.2, 1, len(t))
        x += _filtro(signal.lfilter([1], [1, -0.97], gotas), 'bandpass', [1500, 5000]) * 0.15
    elif tipo == 'rua':
        x = _filtro(_ruido(dur, 33), 'lowpass', 600) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.07 * t)) * 0.12
    elif tipo == 'grilos':
        x = np.sin(2 * np.pi * 4300 * t) * (np.sin(2 * np.pi * 30 * t) > 0.3) * (np.sin(2 * np.pi * 0.9 * t) > 0) * 0.04
    elif tipo == 'passaros':
        x = np.zeros(len(t))
        for i in range(int(dur * 1.5)):
            ini = r.uniform(0, max(dur - 0.4, 0.01)); tt = _t(0.25); f0 = r.uniform(2500, 4500)
            canto = np.sin(2 * np.pi * np.cumsum(f0 + 900 * np.sin(2 * np.pi * 12 * tt)) / SR) * np.sin(np.pi * tt / 0.25) ** 2
            a = int(ini * SR); x[a: a + len(tt)] += canto[: len(x) - a] * 0.06
    elif tipo == 'conversa':
        x = _filtro(_ruido(dur, 34), 'bandpass', [250, 2500]) * (0.5 + 0.5 * np.abs(np.sin(2 * np.pi * 2.3 * t + np.sin(2 * np.pi * 0.7 * t) * 3))) * 0.08
    elif tipo == 'aplausos':
        palmas = (r.random(len(t)) > 0.995) * r.uniform(0.3, 1, len(t))
        x = _filtro(signal.lfilter([1], [1, -0.6], palmas), 'bandpass', [800, 6000]) * 0.5
    else:
        raise ValueError(tipo)
    borda = min(int(0.3 * SR), len(x) // 2)
    x[:borda] *= np.linspace(0, 1, borda); x[-borda:] *= np.linspace(1, 0, borda)
    return x


# ---------- efeitos: drama ----------

def whoosh(dur=0.5):
    t = _t(dur)
    x = np.zeros(len(t)); bloco = 512
    ruido = _ruido(dur, 40)
    for i in range(0, len(t), bloco):     # filtro que varre do grave ao agudo e volta
        k = i / len(t); fc = 300 + 3500 * np.sin(np.pi * k)
        x[i: i + bloco] = _filtro(ruido[i: i + bloco], 'bandpass', [fc * 0.6, fc * 1.4])
    return x * np.sin(np.pi * t / dur) ** 2 * 0.5


def thud(forca=1.0):
    t = _t(0.6)
    x = np.sin(2 * np.pi * 60 * t) * np.exp(-t * 10)
    x += _filtro(_ruido(0.6, 41), 'bandpass', [400, 2000]) * np.exp(-t * 40) * 0.6   # parte media: ouvida no celular
    return x * forca * 0.8


def boom(forca=1.0):
    t = _t(2.5)
    f = 35 + 40 * np.exp(-t * 3)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 1.5)
    x += _filtro(_ruido(2.5, 42), 'bandpass', [600, 3000]) * np.exp(-t * 12) * 0.7      # o 'crack'
    return eco(x * forca * 0.8, 1.5, 0.3)[: len(t)]


def subida(dur=2.0):
    """Riser: tensao subindo ate o grande momento."""
    t = _t(dur)
    f = 200 * 2 ** (3 * t / dur)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.3 + _filtro(_ruido(dur, 43), 'highpass', 2000) * 0.2
    return x * (t / dur) ** 2 * 0.6


def cintilar(dur=2.0):
    """Shimmer: momento magico (usar com o verde)."""
    t = _t(dur); x = np.zeros(len(t)); r = np.random.default_rng(44)
    for i in range(18):
        ini = r.uniform(0, dur * 0.7); m = r.choice([84, 86, 88, 91, 93, 96])
        nota = sino(int(m), dur - ini) * 0.4
        a = int(ini * SR); x[a: a + len(nota)] += nota[: len(x) - a]
    return x * np.minimum(1, (dur - t) / 0.5)


def drone_medo(dur=4.0):
    t = _t(dur)
    x = sum(np.sin(2 * np.pi * f * t + np.sin(2 * np.pi * 0.3 * t) * 2) for f in (55, 58.3, 110.5))
    x += _filtro(_ruido(dur, 45), 'bandpass', [300, 900]) * 0.4       # textura media, audivel no celular
    return x * _env(len(t), 1.0, 99, 1.0, 1.0) * 0.12


def prato():
    t = _t(3.0)
    return _filtro(_ruido(3.0, 46), 'highpass', 4000) * np.exp(-t * 1.6) * 0.4


# ---------- efeitos do nosso estilo: neon ----------

def neon_liga():
    """O letreiro do vilao acendendo: estalos eletricos no mesmo ritmo do pisca da imagem."""
    t = _t(0.6); x = np.zeros(len(t))
    for ini, fim in ((0.00, 0.06), (0.14, 0.18), (0.30, 0.34), (0.40, 0.6)):
        a, b = int(ini * SR), int(fim * SR)
        x[a:a + 600] += _filtro(_ruido(600 / SR, 50), 'bandpass', [1000, 6000])[: len(x[a:a + 600])] * 0.8
        tt = t[a:b] - ini
        x[a:b] += (np.sin(2 * np.pi * 120 * tt) + 0.5 * np.sin(2 * np.pi * 240 * tt) + 0.3 * np.sin(2 * np.pi * 960 * tt)) * 0.15
    return x


def neon_zumbido(dur):
    t = _t(dur)
    x = np.sin(2 * np.pi * 120 * t) + 0.6 * np.sin(2 * np.pi * 240 * t) + 0.4 * np.sin(2 * np.pi * 480 * t) + 0.25 * np.sin(2 * np.pi * 960 * t)
    return x * (0.8 + 0.2 * np.sin(2 * np.pi * 3.1 * t)) * _env(len(t), 0.05, 99, 1, 0.1) * 0.04


def neon_desliga():
    t = _t(0.5)
    return (np.sin(2 * np.pi * 120 * t) * 0.15 * np.exp(-t * 8) + _filtro(_ruido(0.5, 51), 'bandpass', [800, 4000]) * np.exp(-t * 40) * 0.5)


# ---------- a voz do vilao ----------

def sussurro(texto, voz='pt-br'):
    """Voz sintetica sussurrando, mais grave, dobrada com uma copia ainda mais grave por baixo."""
    with tempfile.TemporaryDirectory() as d:
        arq = os.path.join(d, 'v.wav')
        subprocess.run(['espeak-ng', '-v', f'{voz}+whisper', '-s', '125', '-p', '25', '-a', '160', '-w', arq, texto], check=True)
        sr, v = wavfile.read(arq)
    v = v.astype(np.float64) / 32768
    v = signal.resample_poly(v, SR, sr)

    def grave(x, fator):     # mais lento = mais grave
        return signal.resample(x, int(len(x) * fator))
    a, b = grave(v, 1.12), grave(v, 1.3) * 0.5
    n = max(len(a), len(b)); x = np.zeros(n); x[: len(a)] += a; x[: len(b)] += b
    x = _filtro(x, 'highpass', 250)
    return eco(_norm(x, 0.7), 1.0, 0.3)


# ---------- musica ----------

def musica(acordes, bpm, compassos, papel, oitava=3, melodia=True):
    """Toca o tema (4 acordes, um por compasso de 4 tempos) num 'papel':
    'quieto', 'quente', 'cansado', 'abrindo', 'luta' ou 'cheio'."""
    beat = 60 / bpm
    if papel == 'cansado':
        beat *= 1.15
    total = compassos * 4 * beat
    x = np.zeros(int((total + 4) * SR))

    def poe(som, quando, ganho=1.0):
        a = int(quando * SR); x[a: a + len(som)] += som[: len(x) - a] * ganho

    for c in range(compassos):
        nome = acordes[c % len(acordes)]
        notas = acorde(nome, oitava)
        ini = c * 4 * beat
        if papel in ('quente', 'cansado', 'abrindo', 'luta', 'cheio'):
            poe(pad(notas, 4 * beat + 0.5, 900 if papel == 'cansado' else 1600), ini, 0.7)
        if papel in ('quieto', 'cansado'):
            poe(piano(notas[0] + 12, 3 * beat, 0.5), ini, 0.8)
        if papel in ('quente', 'abrindo', 'cheio'):
            for i, n in enumerate([notas[0], notas[1], notas[2], notas[1]]):
                poe(piano(n + 12, 1.5 * beat, 0.6), ini + i * beat, 0.7)
        if papel in ('abrindo', 'cheio'):
            poe(sino(notas[2] + 24, 3), ini, 0.5)
        if papel in ('luta', 'cheio'):
            for i in range(4):
                poe(bumbo(), ini + i * beat, 0.8 if papel == 'luta' else 0.5)
                poe(chimbal(), ini + (i + 0.5) * beat, 0.6)
            poe(caixa(), ini + 1 * beat, 0.5); poe(caixa(), ini + 3 * beat, 0.5)
        if melodia and papel != 'luta':
            frase = [notas[2] + 12, notas[1] + 12, notas[0] + 12, notas[1] + 12] if c % 2 == 0 else [notas[1] + 12, notas[2] + 12, notas[2] + 14, notas[2] + 12]
            instr = caixinha if papel in ('quieto', 'cansado') else piano
            passos_mel = (0, 1, 2, 3) if papel != 'quieto' else (0, 2)
            for i in passos_mel:
                poe(instr(frase[i] + 12, 1.2 * beat) if instr is caixinha else instr(frase[i] + 12, 1.2 * beat, 0.7), ini + i * beat, 0.6)
    return x[: int(total * SR)]


# ---------- mixagem ----------

class Mixagem:
    """Linha do tempo de audio em estereo. poe(som, segundo, ganho_db, pan -1..1)."""

    def __init__(self, duracao):
        self.duracao = duracao
        self.x = np.zeros((int(duracao * SR), 2))

    def poe(self, som, quando, ganho_db=0.0, pan=0.0):
        if som.ndim == 1:
            som = np.stack([som * np.sqrt((1 - pan) / 2) * 1.414, som * np.sqrt((1 + pan) / 2) * 1.414], axis=1)
        a = int(max(quando, 0) * SR); n = min(len(som), len(self.x) - a)
        if n > 0:
            self.x[a: a + n] += som[:n] * db(ganho_db)

    def volume_por_cena(self, cenas):
        """Volume de cada cena como um celular ouve (filtro passa-alta em 300 Hz). Devolve [(nome, dB)]."""
        celular = _filtro(self.x.mean(axis=1), 'highpass', 300, 4)
        out = []
        for nome, ini, fim in cenas:
            trecho = celular[int(ini * SR): int(fim * SR)]
            rms = np.sqrt(np.mean(trecho ** 2)) if len(trecho) else 0
            out.append((nome, 20 * np.log10(rms + 1e-9)))
        return out

    def nivelar(self, cenas, limite_db=5.0):
        """Sobe as cenas baixas demais para ficarem a no maximo `limite_db` abaixo da mais alta. A mais alta continua a maior."""
        vols = self.volume_por_cena(cenas)
        alvo = max(v for _, v in vols)
        ganho = np.ones(len(self.x))
        for (nome, ini, fim), (_, v) in zip(cenas, vols):
            if v > -80 and alvo - v > limite_db:
                ganho[int(ini * SR): int(fim * SR)] = db(alvo - v - limite_db)
        ganho = signal.filtfilt(*signal.butter(1, 2, fs=SR), ganho)     # transicao suave entre cenas
        self.x *= ganho[:, None]
        return vols

    def tabela(self, cenas):
        vols = self.volume_por_cena(cenas)
        alto = max(v for _, v in vols)
        linhas = [f"{'cena':<24}{'volume (celular)':>18}{'abaixo da mais alta':>22}"]
        for nome, v in vols:
            linhas.append(f"{nome:<24}{v:>15.1f} dB{alto - v:>19.1f} dB")
        return "\n".join(linhas)

    def salvar(self, caminho):
        x = self.x / (np.max(np.abs(self.x)) or 1) * db(-1)      # pico em -1 dB
        wavfile.write(caminho, SR, (x * 32767).astype(np.int16))
        return caminho
