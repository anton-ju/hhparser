from utils import EquityArray, str_to_cards
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

#hand2 = str_to(("Js 2c"))
t1 = perf_counter()

result = py_hand_vs_range_monte_carlo(hand1, hand2, board, 200000)
t2 = perf_counter()

print(f"py_hand_vs_range_monte_carlj: {t1 - t2:0.4f} sec, result={result:2.4f}")


