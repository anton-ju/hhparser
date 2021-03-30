from utils import EquityArray, str_to_cards, getEquityVsHandFast, pe_string2card, NUM_CARDS, pe_card2string
from utils import printProgressBar, py_equities_2hands_fast
from time import perf_counter
from eval7 import py_equities_2hands, py_hand_vs_range_monte_carlo, HandRange, py_outcome_breakdown
from itertools import permutations

# generates preflop array
ea = EquityArray()

RANKS = ['A', 'K', 'Q','J', 'T', '9', '8', '7', '6', '5', '4', '3', '2']
RANKS.reverse()

CARDS = ['2h', '3h', '4h', '5h', '6h', '7h', '8h', '9h', 'Th', 'Jh', 'Qh', 'Kh', 'Ah', 
         '2d', '3d', '4d', '5d', '6d', '7d', '8d', '9d', 'Td', 'Jd', 'Qd', 'Kd', 'Ad',
         '2c', '3c', '4c', '5c', '6c', '7c', '8c', '9c', 'Tc', 'Jc', 'Qc', 'Kc', 'Ac', 
         '2s', '3s', '4s', '5s', '6s', '7s', '8s', '9s', 'Ts', 'Js', 'Qs', 'Ks', 'As']

h1 = "Kd As"
h2 = "Th 2c"

hand1 = str_to_cards(h1)
hand2 = str_to_cards(h2)
board = str_to_cards("")

t1 = perf_counter()
result = py_equities_2hands(hand1, hand2, board)
t2 = perf_counter()

print(f"py_equities_2hands: {t2 - t1:0.8f} sec, result={result[0]:2.8f}")

t1 = perf_counter()
result = py_outcome_breakdown(board, hand1, hand2)
t2 = perf_counter()

print(f"py_outcome_breakdown: {t2 - t1:0.8f} sec, result={result}")

hand2 = HandRange(h2)
t1 = perf_counter()

result = py_hand_vs_range_monte_carlo(hand1, hand2, board, 200000)
t2 = perf_counter()

print(f"py_hand_vs_range_monte_carlj: {t2 - t1:0.8f} sec, result={result:2.8f}")

hand1 = h1.split()
hand2 = h2.split()

t1 = perf_counter()
result = getEquityVsHandFast(pe_string2card(hand1), pe_string2card(hand2), ea)
t2 = perf_counter()
print(f'{hand1} vs {hand2}')
print(f"getEquityFast: {t2 - t1:0.8f} sec, result={result:2.8f}")

t1 = perf_counter()
result = getEquityVsHandFast(pe_string2card(hand2), pe_string2card(hand1), ea)
t2 = perf_counter()
print(f'{hand2} vs {hand1}')
print(f"getEquityFast: {t2 - t1:0.8f} sec, result={result:2.8f}")

hand1 = sorted(hand1, key=lambda card: CARDS.index(card))
hand2 = sorted(hand2, key=lambda card: CARDS.index(card))
t1 = perf_counter()
result = getEquityVsHandFast(pe_string2card(hand1), pe_string2card(hand2), ea)
t2 = perf_counter()
print(f'{hand1} vs {hand2}')
print(f"sorted hand --- getEquityFast: {t2 - t1:0.8f} sec, result={result:2.8f}")

t1 = perf_counter()
result = getEquityVsHandFast(pe_string2card(hand2), pe_string2card(hand1), ea)
t2 = perf_counter()
print(f'{hand2} vs {hand1}')
print(f" sorted hand --- getEquityFast: {t2 - t1:0.8f} sec, result={result:2.8f}")

perm = permutations(CARDS, 4)
perm = list(perm)
total_len = len(perm)
print(f'Total hand vs hand : {total_len}')
counter = 0
#printProgressBar(counter, total_len)
#for p in perm:
#    hand1 = " ".join([p[0], p[1]])
#    hand2 = " ".join([p[2], p[3]])
#    result = py_equities_2hands_fast(hand1, hand2)
#    counter += 1
#    printProgressBar(counter, total_len)
#    if result == 0 or result is None:
#        print(f"result is {result} for {hand1} vs {hand2}")
#        break
# for i in range(NUM_CARDS):
#    for j in range(NUM_CARDS):
#        for a in range(NUM_CARDS):
#            for b in range(NUM_CARDS):
#                hand1 = pe_card2string([a, b])
#                hand2 = pe_card2string([i, j])
#                print(f'{hand1} vs {hand2} ::: {ea.eArray[a][b][i][j]} - {ea.eArray[i][j][a][b]}')
