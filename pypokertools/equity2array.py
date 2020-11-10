from utils import EquityArray, str_to_cards, getEquityVsHandFast, pe_string2card, NUM_CARDS, pe_card2string
from time import perf_counter
from eval7 import py_equities_2hands, py_hand_vs_range_monte_carlo, HandRange

# generates preflop array
ea = EquityArray()

hand1 = str_to_cards("Ac 2d")
hand2 = str_to_cards("Js 2c")
board = str_to_cards("")

t1 = perf_counter()
result = py_equities_2hands(hand1, hand2, board)
t2 = perf_counter()

print(f"py_equities_2hands: {t2 - t1:0.4f} sec, result={result[0]:2.4f}")

hand2 = HandRange("Js 2c")
t1 = perf_counter()

result = py_hand_vs_range_monte_carlo(hand1, hand2, board, 200000)
t2 = perf_counter()

print(f"py_hand_vs_range_monte_carlj: {t2 - t1:0.4f} sec, result={result:2.4f}")

hand1 = "Ac 2d".split()
hand2 = "Js 2c".split()

t1 = perf_counter()
result = getEquityVsHandFast(pe_string2card(hand1), pe_string2card(hand2), ea)
t2 = perf_counter()
print(f'{hand1} vs {hand2}')
print(f"getEquityFast: {t2 - t1:0.4f} sec, result={result:2.4f}")

t1 = perf_counter()
result = getEquityVsHandFast(pe_string2card(hand2), pe_string2card(hand1), ea)
t2 = perf_counter()
print(f'{hand2} vs {hand1}')
print(f"getEquityFast: {t2 - t1:0.4f} sec, result={result:2.4f}")

hand1.reverse()
hand2.reverse()
t1 = perf_counter()
result = getEquityVsHandFast(pe_string2card(hand1), pe_string2card(hand2), ea)
t2 = perf_counter()
print(f'{hand1} vs {hand2}')
print(f"getEquityFast: {t2 - t1:0.4f} sec, result={result:2.4f}")

t1 = perf_counter()
result = getEquityVsHandFast(pe_string2card(hand2), pe_string2card(hand1), ea)
t2 = perf_counter()
print(f'{hand2} vs {hand1}')
print(f"getEquityFast: {t2 - t1:0.4f} sec, result={result:2.4f}")

# for i in range(NUM_CARDS):
#    for j in range(NUM_CARDS):
#        for a in range(NUM_CARDS):
#            for b in range(NUM_CARDS):
#                hand1 = pe_card2string([a, b])
#                hand2 = pe_card2string([i, j])
#                print(f'{hand1} vs {hand2} ::: {ea.eArray[a][b][i][j]} - {ea.eArray[i][j][a][b]}')
