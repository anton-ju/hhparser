import functools
import unittest
import logging
import random
from profiler import profile
import pprint

from unittest import skip
from pypokertools.calc import pokercalc
from pypokertools.parsers import PSHandHistory as hhparser
from pypokertools.calc.pokercalc import OutcomeBuilder

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
random.seed(42)
th0 = """
"""

th1 = """
"""
th7 = """
"""
th8 = """
"""


def add_params(params):
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args):
            for c in params:
                new_args = args + (c if isinstance(c, tuple) else (c,))
                f(*new_args)
        return wrapper
    return decorator


def round_dict(d, n):
    return {k: round(v, n) for k, v in d.items()}


def get_parsed_hand_from_file(fn):
    with open(fn) as f:
        hh_text = f.read()
        parsed_hand = hhparser(hh_text)
        return parsed_hand


def get_ev_calc(player, parsed_hand, prize=((1, 0)), ko_model=pokercalc.KOModels.PROPORTIONAL) -> pokercalc.EV:
    icm = pokercalc.Icm(prize)
    ko = pokercalc.Knockout(ko_model)
    ev_calc = pokercalc.EV(parsed_hand, icm, ko)
    ev_calc.calc(player)
    return ev_calc


class Test1hand(unittest.TestCase):

    @add_params([
       {'fn': 'hh/sat16/round1/3way/3way-ai-preflop.txt',
         'expected': 0.2976,
         'player': 'DiggErr555'
         },
        ])

    def test_1hand(self, params):
        hand = get_parsed_hand_from_file(params.get('fn'))
        hero = 'DiggErr555'
        ev_calc = get_ev_calc(hero, hand)
        expected = params.get('expected')
        probs = ev_calc.get_outcome_probs()
        outcomes = ev_calc.get_outcome()
        fact = ev_calc.chip_fact()
        chip_ev = ev_calc.chip_ev_3way()
#        chip_ev_diff = ev_calc.chip_diff_ev_adj()
        icm_ev= ev_calc.icm_ev_diff()
        pprint.pprint(probs)
        pprint.pprint(outcomes)
        pprint.pprint(fact)
        pprint.pprint(chip_ev)
        pprint.pprint(icm_ev)
        # self.assertAlmostEqual(result, expected, delta=0.005)

