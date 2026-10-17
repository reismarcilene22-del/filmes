# Método

Os passos de todo filme, as conferências que sempre fazemos e cada erro que já custou tempo.

## As 8 etapas
1. **Ideia**: uma dor específica (não uma virtude), a frase do vilão e o "dispositivo" visual.
2. **História + linha do tempo**: cena a cena, com segundo de início e fim. Nada parado mais de ~6 s.
3. **Pasta do filme**: `filmes/<titulo>/`, reaproveitando personagem, efeitos e sons.
4. **Construir uma cena por vez** ✅ folha de contato (12 quadros) conferida antes de seguir.
5. **Checagem de contato** ✅ nenhuma mão ou pé flutuando perto do que deveria tocar.
6. **Música e som**: um tema de 4 acordes, um som para cada ação, nível medido como num celular.
7. **Render final** ✅ conferir quadros tirados do mp4 final, não do código.
8. **Capa, título e memória**: atualizar `estilo.md`, `metodo.md` e `filmes.md`.

## Conferências
- Toda cena: folha de contato, legenda fora de áreas movimentadas, sobrancelhas certas, regra das cores mantida.
- Antes do render: duração exata, checagem de contato limpa, volume das cenas dentro de ~5 dB.
- Depois do render: assistir inteiro no celular, com som.

## Ambiente (computador na nuvem)
- O computador é apagado depois de um tempo sem uso. **Tudo que importa vai para o GitHub** (`git push`).
- Numa sessão nova: `bash setup.sh` reinstala tudo (Python, ffmpeg, fontes, voz, bibliotecas).
- Voz sintética: `espeak-ng` (português: `-v pt-br`). Robótica — serve para o sussurro do vilão, não para narração.
- Vídeos grandes (`*.mp4`) não vão para o GitHub; só as cópias `*_celular.mp4`.

## Erros que já custaram tempo
- `skia` devolve as cores em ordem BGRA por padrão: ao converter para numpy, usar `toarray(colorType=skia.kRGBA_8888_ColorType)`, senão vermelho vira azul.
- O brilho neon (desfoque em 1080p) é a parte mais lenta do render. Grão de filme deixa o vídeo enorme (50 MB para 4 s) — por isso foi descartado.
- O efeito de traço tremidinho também deforma as letras; se voltar a ser usado, não aplicar em texto.
- Na caminhada, a perna aberta não alcança o chão se o quadril não descer: `caminhar` já calcula isso (a checagem de contato pegou).
- Joelhos: de frente abrem para os lados; andando apontam para onde ele vai (`Pose.joelhos`).
- O braço erguido passa por trás da cabeça, nunca na frente do rosto.
- Folha de contato do mp4: o último quadro existe em `fim - 1/30`, não em `fim`.
- Cada filme define `desenhar(c, t)` e um dicionário de TEMPOS; imagem e som leem os mesmos números (os passos saem da mesma função de posição).
- Render: ~5 s por segundo de filme nas 4 CPUs desta máquina.
