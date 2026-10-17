"""Todos os tempos do filme ZERO. num lugar so. Imagem e som leem estes mesmos numeros."""

DURACAO = 85.0

CENAS = [
    # nome, inicio, fim
    ("1 salario", 0.0, 6.0),
    ("2 contas", 6.0, 17.0),
    ("3 promessa", 17.0, 25.0),
    ("4 meses", 25.0, 39.0),
    ("5 fundo do poco", 39.0, 47.0),
    ("6 virada", 47.0, 54.0),
    ("7 luta final", 54.0, 66.0),
    ("8 recompensa", 66.0, 77.0),
    ("9 titulo", 77.0, 85.0),
]

SALARIO = 2400
CONTAS = [("ALUGUEL", 1200), ("LUZ", 250), ("MERCADO", 650), ("CARTÃO", 300)]
GUARDA = 20

# Cena 1
PLIM = 0.6               # notificacao: o celular acende
SALDO_ENTRA = 1.0        # o saldo pula para 2.400
SORRI = 1.4
LEGENDA_1 = (1.2, 5.6)

# Cena 2: cada conta acende (a moeda sai do saldo 0,6 s antes)
CONTA_ACENDE = [7.0, 8.6, 10.2, 11.8]
VOO_MOEDA = 0.6
VILAO_NASCE = 13.6
LEGENDA_2 = (6.4, 12.4)
