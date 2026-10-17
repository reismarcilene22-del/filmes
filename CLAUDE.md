# Filmes animados em Python

Curtas animados em que cada quadro é desenhado com código (skia-python), música e sons feitos com numpy/scipy, e o vídeo montado com ffmpeg.

A dona do projeto não é programadora e fala português: explicar tudo em palavras simples, mostrar imagens como prova em vez de só dizer "pronto", e nunca pedir que ela leia código.

## Antes de qualquer trabalho, leia
- `estilo.md` — o guia de estilo (mundo neon, vermelho = ruim, verde = bom, personagem, vilão, letra, acabamento).
- `metodo.md` — as 8 etapas, as conferências e os erros que já custaram tempo.
- `filmes.md` — os filmes já feitos.

## Ambiente
- Numa sessão nova, rode `bash setup.sh` antes de tudo. Use sempre `.venv/bin/python`.
- O computador é temporário: faça commit e push no `main` ao fim de cada etapa.

## Situação atual
- Questionário de estilo concluído (rascunhos e escolhas em `questionario/`).
- Fundação pronta em `toolkit/` (testes e exemplos em `toolkit/testes/`, a cena `t3_demo.py` mostra como tudo se encaixa):
  - `desenho.py` — paleta, letra, pincéis, suavizações (`suave`, `mola`, `entre`)
  - `personagem.py` — `Pose`, `desenha`, `caminhar`, `mao_solta`; mãos/pés vão a pontos exatos e as faltas vão para `FALHAS`
  - `cena.py` — fundo neon, placas, `letreiro` (vilão), `legenda`, `mostrador`, `Camera`, `acabamento`
  - `render.py` — `render` (paralelo + cópia celular), `folha_de_contato` (do código ou do mp4), `checagem_de_contato`
  - `som.py` — instrumentos, `musica` (tema em 6 papéis), efeitos, `sussurro` (voz do vilão), `Mixagem` com `tabela`/`nivelar`
- Filme em andamento: **ZERO.** em `filmes/zero/` — roteiro aprovado em `roteiro.md`, tempos em `tempos.py`, cenas em `filme.py`.
  - Comandos (rodar dentro de `filmes/zero/`): `../../.venv/bin/python filme.py folha A B` (folha de contato), `... previa A B` (vídeo de um trecho), `... contato` (checagem de contato).
  - Cenas 1 e 2 (0:00–0:17) feitas; prévia enviada, aguardando a opinião dela (ritmo das contas a cada 1,6 s; se ele deve fazer algum gesto).
  - Próximo: cena 3 (a irmãzinha e a promessa da praia). Som só depois de todas as cenas aprovadas.

## Ao terminar um filme
Atualize `estilo.md`, `metodo.md` e `filmes.md` com o que aprendemos. Mantenha cada arquivo curto e não registre nada que só valha para aquele filme.
