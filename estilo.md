# Guia de estilo

As regras visuais e sonoras de todos os filmes. Curto de propósito: cada regra traz o motivo.

## Mundo
- Noturno, neon. Fundo quase preto-arroxeado (`#0E0A1C`).
- Letreiros e luzes do cenário em **roxo e azul apagados** — são ambiente, nunca chamam atenção.
- Só o que importa recebe luz. O personagem está sempre no lugar mais iluminado da cena.
- Cenário de perfil, como um corte de prédio: linha do chão, parede, poucos objetos.

## Cores com significado
- **Vermelho = coisas ruins**: o vilão, o fracasso, o perigo. Nada mais no filme é vermelho.
- **Verde = coisas boas**: esperança, crescimento, vitória. Nada mais no filme é verde.
- Todo o resto fica em roxo, azul e creme. Se vermelho ou verde aparecerem por engano, o público lê errado.

## Personagem
- Boneco simples: cabeça redonda, corpo arredondado, pernas de palito. Sem cabelo, sem roupa, sem nariz.
- Branco-creme (`#EEE8DC`) com contorno lilás (`#968CBE`). Olhos pretos redondos, boca de um traço.
- Proporções (em escala 1): cabeça raio 110, centro 380 px acima do chão; corpo 136 × 180, de 260 a 80 px acima do chão; pernas de 90 px até o chão. Código de referência: `questionario/personagem.py`.
- **Ainda precisa de braços**: bracinhos finos de palito, da mesma cor das pernas, que dobram no cotovelo e alcançam pontos exatos.
- Expressões só com olhos (abertos, meio, fechados), sobrancelhas e boca. Conferir sempre a direção das sobrancelhas.
- **O personagem nunca fala.** Tudo é contado com expressão, gesto e legenda.

## Vilão
- Um **letreiro neon vermelho** com moldura arredondada que acende (piscando, como neon de verdade) e escreve a frase ruim.
- Ele nasce de algo que já está na cena: um letreiro que estava apagado acende em vermelho. Nunca aparece do nada.
- Frases curtas (até 6 palavras), em minúsculas, com ponto final. Ex.: "desiste.", "só mais 5 minutos."
- É o único com voz: um sussurro grave, no mesmo instante em que o letreiro acende.

## Texto
- Uma única letra: **Comic Neue** (negrito), nas legendas e no letreiro do vilão.
- Legendas brancas, centralizadas, **no alto da tela**. Nunca sobre o rosto, um braço ou algo movimentado.
- Cerca de 10 legendas por filme. Elas nomeiam o sentimento, nunca descrevem o que se vê.

## Acabamento
- **Vinheta**: cantos mais escuros que o centro.
- **Brilho neon**: tudo que é claro brilha e vaza luz suavemente.
- Sem grão, sem faixas pretas, sem traço tremidinho — o traço é limpo e firme.
- Código de referência do acabamento: `questionario/acabamento_video.py`.

## Movimento
- Tudo com aceleração e desaceleração suaves, nunca velocidade constante.
- Em cena parada, o personagem respira (sobe e desce bem pouco).
- Câmera: aproximação lenta (~8%) para tensão; afastar para revelar; tremor curto para impacto.

## Formato
- 1920 × 1080, 30 quadros por segundo. Cópia de 1280 × 720 para o celular.
