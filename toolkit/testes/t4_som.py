"""Parte 4: catalogo de todos os sons do kit e a trilha sonora da cena de teste."""
import os, sys, subprocess
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import numpy as np
import som
import t3_demo as demo

AQUI = os.path.dirname(__file__)
ACORDES = ['Dm', 'Bb', 'F', 'C']


def catalogo():
    itens = [
        ("Tema: quieto (início)", som.musica(ACORDES, 70, 2, 'quieto')),
        ("Tema: quente (rotina)", som.musica(ACORDES, 80, 2, 'quente')),
        ("Tema: cansado (fundo do poço)", som.musica(ACORDES, 70, 2, 'cansado')),
        ("Tema: abrindo (virada)", som.musica(ACORDES, 96, 2, 'abrindo')),
        ("Tema: luta (batidas)", som.musica(ACORDES, 120, 2, 'luta')),
        ("Tema: cheio (final)", som.musica(ACORDES, 96, 2, 'cheio')),
        ("Violão", np.concatenate([som.violao(m, 0.5) for m in (50, 53, 57, 62)])),
        ("Passos", np.concatenate([np.pad(som.passo(i), (0, 9000)) for i in range(4)])),
        ("Respiração + expiração", np.concatenate([som.respiracao(), som.expiracao()])),
        ("Batimento do coração", np.concatenate([som.batimento()] * 3)),
        ("Papel", som.papel()), ("Amassar papel", som.amassar()), ("Lápis", som.lapis()),
        ("Clique", som.clique()), ("Tique do mostrador", som.tique()), ("Vidro quebrando", som.vidro()),
        ("Cerâmica quebrando", som.ceramica()), ("Água", som.agua()),
        ("Sala (silêncio de fundo)", som.ambiente('sala', 2) * 4), ("Chuva", som.ambiente('chuva', 2.5)),
        ("Rua", som.ambiente('rua', 2.5)), ("Grilos", som.ambiente('grilos', 2.5)), ("Pássaros", som.ambiente('passaros', 2.5)),
        ("Conversa ao fundo", som.ambiente('conversa', 2.5)), ("Aplausos", som.ambiente('aplausos', 2.5)),
        ("Whoosh", som.whoosh()), ("Thud (pancada)", som.thud()), ("Boom", som.boom()), ("Subida (tensão)", som.subida()),
        ("Cintilar (momento mágico)", som.cintilar()), ("Drone de medo", som.drone_medo(3)), ("Prato", som.prato()),
        ("Neon acendendo", som.neon_liga()), ("Neon zumbindo", som.neon_zumbido(2)), ("Neon apagando", som.neon_desliga()),
        ("Voz do vilão: 'desiste.'", som.sussurro("desiste.")),
        ("Voz do vilão: 'só mais 5 minutos.'", som.sussurro("só mais 5 minutos.")),
        ("Voz do vilão: 'você não está pronto.'", som.sussurro("você não está pronto.")),
    ]
    total = sum(len(x) / som.SR + 0.8 for _, x in itens)
    mix = som.Mixagem(total)
    t, lista = 0.0, []
    for nome, x in itens:
        x = x / (np.max(np.abs(x)) or 1) * 0.6
        mix.poe(x, t)
        lista.append(f"{int(t // 60)}:{t % 60:04.1f}  {nome}")
        t += len(x) / som.SR + 0.8
    wav = mix.salvar(os.path.join(AQUI, "t4_catalogo.wav"))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", wav, "-b:a", "192k", wav.replace(".wav", ".mp3")], check=True)
    open(os.path.join(AQUI, "t4_catalogo.txt"), "w").write("\n".join(lista) + "\n")
    print("\n".join(lista))


def trilha():
    T = demo.TEMPOS
    D = demo.DURACAO
    mix = som.Mixagem(D)
    mix.poe(som.ambiente('sala', D), 0, -6)
    acende, aperta = T['vilao_acende'], T['aperta']
    # musica: quieta no inicio; medo enquanto o vilao esta aceso; silencio antes do botao; abre no final
    mix.poe(som.musica(ACORDES, 80, 2, 'quieto')[: int((acende + 0.3) * som.SR)], 0.0, -4)
    mix.poe(som.drone_medo(aperta - 0.6 - acende), acende, -2)
    for i, quando in enumerate(np.cumsum([0.95 - 0.04 * k for k in range(8)]) + acende + 0.5):
        if quando < aperta - 0.6:                      # coracao acelerando, e some antes do grande momento
            mix.poe(som.batimento(), quando, -3)
    mix.poe(som.musica(ACORDES, 96, 2, 'cheio'), aperta + 0.15, -5)
    mix.poe(som.cintilar(2.4), T['legenda2'][0], -6)
    # vilao
    mix.poe(som.neon_liga(), acende, -2)
    mix.poe(som.neon_zumbido(aperta - acende - 0.4), acende + 0.4, -4)
    mix.poe(som.sussurro("desiste."), acende + 0.4, 0, pan=0.4)
    # o botao
    mix.poe(som.clique(), aperta, 0, pan=0.3)
    mix.poe(som.thud(), aperta, -2)
    mix.poe(som.neon_desliga(), aperta + 0.05, -2, pan=0.4)
    mix.poe(som.tique(), aperta, -4, pan=0.6)
    mix.poe(som.expiracao(), aperta + 0.5, -4)
    # passos: cada vez que um pe toca o chao
    L = 70
    anterior = None
    for n in range(int(D * 30)):
        t = n / 30
        x, andou = demo.posicao(t)
        andando = T['entra'][0] <= t < T['entra'][1] or T['anda_ate_interruptor'][0] <= t < T['anda_ate_interruptor'][1]
        passo = int(andou // L)
        if andando and anterior is not None and passo != anterior:
            mix.poe(som.passo(passo % 4), t, -6, pan=(x - 960) / 960 * 0.6)
        anterior = passo
    cenas = [("1 entrada", 0, acende), ("2 vilao aceso", acende, T['estica_mao'][0]),
             ("3 botao", T['estica_mao'][0], T['legenda2'][0]), ("4 final", T['legenda2'][0], D)]
    print("ANTES de nivelar:\n" + mix.tabela(cenas))
    mix.nivelar(cenas, 5.0)
    print("\nDEPOIS de nivelar:\n" + mix.tabela(cenas))
    wav = mix.salvar(os.path.join(AQUI, "t4_trilha.wav"))
    video = os.path.join(AQUI, "t3_demo.mp4")
    for entrada, saida in ((video, "t4_demo_com_som.mp4"), (video.replace('.mp4', '_celular.mp4'), "t4_demo_com_som_celular.mp4")):
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", entrada, "-i", wav, "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                        "-c:a", "aac", "-b:a", "256k", "-shortest", os.path.join(AQUI, saida)], check=True)


if __name__ == "__main__":
    catalogo()
    print()
    trilha()
