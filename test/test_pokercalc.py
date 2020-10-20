import functools
import unittest
import logging
import random

from unittest import skip
from pypokertools.calc import pokercalc
from pypokertools.parsers import PSHandHistory as hhparser

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


def get_ev_calc(player, parsed_hand, prize=((1,0)), ko_model=pokercalc.KOModels.PROPORTIONAL):
        icm = pokercalc.Icm(prize)
        ko = pokercalc.Knockout(ko_model)
        ev_calc = pokercalc.EV(parsed_hand, icm, ko)
        ev_calc.calc(player)
        return ev_calc


class LoadCasesMixin:
    @classmethod
    def setUpClass(cls):
        icm = pokercalc.Icm((0.5, 0.5))
        icm1 = pokercalc.Icm((1,))
        ko = pokercalc.Knockout(pokercalc.KOModels.PROPORTIONAL)
        cls.case = {}
        cases = [()]
        fn_list = ['hh/th0.txt',
                   'hh/th1.txt',
                   'hh/th7.txt',
                   'hh/th8.txt',
                   'hh/sat16/round1/2way/hero-push-sb-call.txt',
                   'hh/sat16/round1/2way/sb-push-hero-call.txt',
                   'hh/sat16/round1/2way/hero-call-bvb.txt',
                   ]
        for fn in fn_list:
            with open(fn) as f:
                hh_text = f.read()
                # print(hh_text)
                parsed_hand = hhparser(hh_text)
                case = pokercalc.EV(parsed_hand, icm, ko)
                case.calc('DiggErr555')
                cls.case[fn] = case

    def get_params(self, params):
        expected = params.get('expected')
        case = self.case.get(params.get('fn'))
        return case, expected



class TestPokercalc(unittest.TestCase):
    @skip
    def test_icm(self):
        pc = pokercalc.Icm((0.5, 0.5))

    def test_calc(self):
        icm_ko = pokercalc.Icm((0.5, 0.5))
        self.assertListEqual(list(icm_ko.calc([954, 20, 466, 568, 496, 496])),
                             [0.2894, 0.0076, 0.1633, 0.1944, 0.1727, 0.1727])

        icm_ko = pokercalc.Icm((0.65, 0.35))
        self.assertListEqual(list(icm_ko.calc([954, 20, 466, 568, 496, 496])),
                             [0.2980, 0.0073, 0.1609, 0.1928, 0.1705, 0.1705])

        icm_ko = pokercalc.Icm((0.60, 0.40))
        self.assertListEqual(list(icm_ko.calc([954, 20, 466, 568, 496, 496])),
                             [0.2951, 0.0074, 0.1617, 0.1934, 0.1712, 0.1712])

        icm_ko = pokercalc.Icm((0.3333, 0.3333, 0.3333))
        self.assertListEqual(list(icm_ko.calc([954, 20, 466, 568, 496, 496])),
                             [0.2602, 0.0089, 0.1722, 0.1980, 0.1803, 0.1803])

        icm_ko = pokercalc.Icm((0.5, 0.5))
        self.assertDictEqual(icm_ko.calc({'da_mauso': 954,
                                          'DiggErr555': 466,
                                          'baluoteli': 20,
                                          'bigboyby': 568,
                                          '2Ran128': 496,
                                          'zaxar393': 496}),
                             {'da_mauso': 0.2894,
                              'DiggErr555': 0.1633,
                              'baluoteli': 0.0076,
                              'bigboyby': 0.1944,
                              '2Ran128': 0.1727,
                              'zaxar393': 0.1727})

        self.assertDictEqual(icm_ko.calc({'da_mauso': 974,
                                  'DiggErr555': 466,
                                  'baluoteli': 0,
                                  'bigboyby': 568,
                                  '2Ran128': 496,
                                  'zaxar393': 496}),
                             {'da_mauso': 0.2944,
                              'DiggErr555': 0.1639,
                              'baluoteli': 0,
                              'bigboyby': 0.1951,
                              '2Ran128': 0.1733,
                              'zaxar393': 0.1733})

        self.assertDictEqual(icm_ko.calc({'vIpEr9427': 299,
                                  'Denisov V.': 427,
                                  'Chang Chi': 477,
                                  'sabuco_2110': 850,
                                  'shagvaladyan': 447,
                                  'DiggErr555': 500}),
                             {'vIpEr9427': 0.1059,
                              'Denisov V.': 0.1473,
                              'Chang Chi': 0.1627,
                              'sabuco_2110': 0.2608,
                              'shagvaladyan': 0.1535,
                              'DiggErr555': 0.1697})

    def test__p1p(self):
        pass


class TestEV(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        icm = pokercalc.Icm((0.5, 0.5))
        icm1 = pokercalc.Icm((1,))
        ko = pokercalc.Knockout(pokercalc.KOModels.PROPORTIONAL)
        cls.case = {}
        cases = [()]
        fn_list = ['hh/th0.txt',
                   'hh/th1.txt',
                   'hh/th7.txt',
                   'hh/th8.txt',
                   'hh/sat16/round1/2way/hero-push-sb-call.txt',
                   'hh/sat16/round1/2way/sb-push-hero-call.txt',
                   'hh/sat16/round1/2way/hero-call-bvb.txt',
                   ]
        for fn in fn_list:
            with open(fn) as f:
                hh_text = f.read()
                # print(hh_text)
                parsed_hand = hhparser(hh_text)
                case = pokercalc.EV(parsed_hand, icm, ko)
                case.calc('DiggErr555')
                cls.case[fn] = case

    def get_params(self, params):
        expected = params.get('expected')
        case = self.case.get(params.get('fn'))
        return case, expected

    @add_params([
        {
         'fn': 'hh/sat16/round1/2way/hero-push-sb-call.txt',
         'expected': ['fozzzi', 'DiggErr555'],
        },
        {
         'fn':  'hh/sat16/round1/2way/sb-push-hero-call.txt',
         'expected': ['fozzzi', 'DiggErr555'],
        },
        {
         'fn': 'hh/sat16/round1/2way/hero-call-bvb.txt',
         'expected': ['bayaraa2222', 'DiggErr555'],
        },
    ])
    def test_detect_ai_players(self, params):
        expected = params.get('expected')
        hand = get_parsed_hand_from_file(params.get('fn'))
        ai_players, p_ai_players, f_ai_players, t_ai_players = pokercalc.EV.detect_ai_players(hand)
        self.assertListEqual(expected, ai_players)

    @skip
    @add_params([
        {
         'fn': 'hh/th1.txt',
         'expected': 0.4600,
         'player': 'vIpEr9427'
        },
        {
         'fn': 'hh/th8.txt',
         'expected': 0.02,
         'player': 'Hpak205'
        },
        {
         'fn': 'hh/sat16/round1/2way/hero-push-sb-call.txt',
         'expected': 0.3926,
         'player': 'DiggErr555'
        },
        {
         'fn':  'hh/sat16/round1/2way/sb-push-hero-call.txt',
         'expected': 0.5244,
         'player': 'DiggErr555'
        },
        {
         'fn': 'hh/sat16/round1/2way/hero-call-bvb.txt',
         'expected': 0.8428,
         'player': 'DiggErr555'
        },
        {
         'fn': 'hh/sat16/round1/2way/hero-call-bvb.txt',
         'expected': 0.1572,
         'player': 'bayaraa2222'
        },
           ])
    def test_equties(self, params):
        case, expected = self.get_params(params)
        result = case.equities().get(params.get('player'))
        self.assertAlmostEqual(result, expected, delta=0.005)

    @skip
    def test_chip_diff(self):
        chip_diff = self.case1.chip_diff()
        # self.assertEqual(chip_diff,{'vIpEr9427': -6,
        #                             'Denisov V.': -18,
        #                             'Chang Chi': 33,
        #                             'sabuco_2110': -3,
        #                             'shagvaladyan': -3,
        #                             'DiggErr555': -3})

        self.assertAlmostEqual(sum(chip_diff.values()), 0, delta=0.001)

    @skip
    def test_chip_win(self):
        pass

    @skip
    def test_chip_lose(self):
        case = self.case7.chip_lose()
        expected = {
            'sabuco_2110': 1668,
            'DiggErr555': 1332,
        }
        self.assertDictEqual(case, expected)

    @add_params([{'fn': 'hh/th1.txt',
             'expected':
             {
                 'vIpEr9427': 299,
                 'Denisov V.': 427,
                 'Chang Chi': 477,
                 'sabuco_2110': 850,
                 'shagvaladyan': 447,
                 'DiggErr555': 500
             }},
            {'fn': 'hh/th7.txt',
             'expected':
             {
                 'sabuco_2110': 0,
                 'DiggErr555': 3000
             }},
            {'fn': 'hh/sat16/round1/2way/hero-push-sb-call.txt',
             'expected':
             {
                 'fozzzi': 100,
                 'bayaraa2222': 270,
                 'apos87tolos': 460,
                 'DiggErr555': 1170
             }},
            {'fn': 'hh/sat16/round1/2way/sb-push-hero-call.txt',
             'expected':
             {
                 'fozzzi': 0,
                 'DiggErr555': 2000,
             }},
            {'fn': 'hh/sat16/round1/2way/hero-call-bvb.txt',
             'expected':
             {
                 'fozzzi': 90,
                 'bayaraa2222': 0,
                 'apos87tolos': 450,
                 'DiggErr555': 1460,
             }},
            {'fn': 'hh/sat16/round1/hero-fold.txt',
             'expected':
             {
                 'Aurade': 445,
                 'Joshje': 625,
                 'byStereo': 510,
                 'DiggErr555': 420,
             }},
            {'fn': 'hh/sat16/round1/hero-push-bb-fold.txt',
             'expected':
             {
                 'fozzzi': 710,
                 'bayaraa2222': 340,
                 'apos87tolos': 200,
                 'DiggErr555': 750,
             }},
            ])
    def test_chip_fact(self, params):
        hand = get_parsed_hand_from_file(params.get('fn'))
        ev_calc = get_ev_calc('DiggErr555', hand)
        expected = params.get('expected')
        result = ev_calc.chip_fact()
        self.assertDictEqual(result, expected)

    @add_params([{'fn': 'hh/th1.txt',
             'expected':
             {
                 'vIpEr9427': 299,
                 'Denisov V.': 427,
                 'Chang Chi': 477,
                 'sabuco_2110': 850,
                 'shagvaladyan': 447,
                 'DiggErr555': 500
             }},
            {'fn': 'hh/th7.txt',
             'expected':
             {
                 'sabuco_2110': 0,
                 'DiggErr555': 3000
             }},
            ])
    def test_chip_fact_chip_sum(self, params):
        case, expected = self.get_params(params)
        result = case.chip_fact()
        result = pokercalc.EV.sum_dict_values(result)
        self.assertEqual(result, 3000, 'Chip sum should be 3000')

    @add_params([{
             'fn': 'hh/th1.txt',
             'expected':
             {
                 'vIpEr9427': 0.1059,
                 'Denisov V.': 0.1473,
                 'Chang Chi': 0.1627,
                 'sabuco_2110': 0.2608,
                 'shagvaladyan': 0.1535,
                 'DiggErr555': 0.1697}
             },
            ])
    def test_icm_fact_pct(self, params):
        case, expected = self.get_params(params)
        result = case.icm_fact_pct()
        self.assertEqual(result, expected)

    @add_params([{
             'fn': 'hh/th1.txt',
             'expected':
             {
              'vIpEr9427': 7.63,
              'Denisov V.': 10.61,
              'Chang Chi': 11.72,
              'sabuco_2110': 18.79,
              'shagvaladyan': 11.06,
              'DiggErr555': 12.23
             }},
            ])
    def test_icm_fact(self, params):
        case, expected = self.get_params(params)
        result = case.icm_fact()
        result = round_dict(result, 2)
        self.assertEqual(result, expected)

    def test_non_zero_values(self):
        self.assertEqual(pokercalc.EV.non_zero_values({1: 1, 2: 2, 3: 0, 4: 0}), 2)

    def test_sum_dict_values(self):
        self.assertEqual(pokercalc.EV.sum_dict_values({1: 1, 2: 2, 3: 0, 4: 0}), 3)
        self.assertEqual(pokercalc.EV.sum_dict_values({1: 1, 2: 2, 3: 'sdf', 4: 0}), 0)
        self.assertEqual(pokercalc.EV.sum_dict_values([1, 2, 3]), 0)

class TestOutcome(LoadCasesMixin, unittest.TestCase):
    def test_add_cildren(self):
        aiplayers = ['DiggErr555', 'fozzzi']
        root = pokercalc.OutCome('root')
        pokercalc.add_children(root, aiplayers)

    @add_params([
            {'fn': 'hh/sat16/round1/2way/hero-push-sb-call.txt',
             'expected':
             {
                 'fozzzi': 100,
                 'bayaraa2222': 270,
                 'apos87tolos': 460,
                 'DiggErr555': 1170
             }},
            {'fn': 'hh/sat16/round1/2way/sb-push-hero-call.txt',
             'expected':
             {
                 'fozzzi': 0,
                 'DiggErr555': 2000,
             }},
            {'fn': 'hh/sat16/round1/2way/hero-call-bvb.txt',
             'expected':
             {
                 'fozzzi': 90,
                 'bayaraa2222': 0,
                 'apos87tolos': 450,
                 'DiggErr555': 1460,
             }},
    ])
    def test_build_outcome_tree(self, params):
        hand = get_parsed_hand_from_file(params.get('fn'))
        ev_calc = get_ev_calc('DiggErr555', hand, ((1,)), pokercalc.KOModels.PROPORTIONAL)
        expected = params.get('expected')
        aiplayers = ev_calc.ai_players
        chips = ev_calc.chips
        pots = ev_calc.pots
        uncalled = ev_calc.uncalled
        total_bets = ev_calc.total_bets
        winnings = ev_calc.winnings_chips
        path = params.get('path')
        result = pokercalc.build_outcome_tree(aiplayers, chips, pots, uncalled, total_bets, winnings)
        print(result)
        #self.assertEqual(result, expected)

    @add_params([
            {'fn': 'hh/sat16/round1/2way/hero-push-sb-call.txt',
             'path': ['DiggErr555', 'fozzzi'],
             'expected':
             {
                 'fozzzi': 100,
                 'bayaraa2222': 270,
                 'apos87tolos': 460,
                 'DiggErr555': 1170
             }},
            {'fn': 'hh/sat16/round1/2way/sb-push-hero-call.txt',
             'path': ['DiggErr555', 'fozzzi'],
             'expected':
             {
                 'fozzzi': 0,
                 'DiggErr555': 2000,
             }},
            {'fn': 'hh/sat16/round1/2way/hero-call-bvb.txt',
             'path': ['DiggErr555', 'bayaraa2222'],
             'expected':
             {
                 'fozzzi': 90,
                 'bayaraa2222': 0,
                 'apos87tolos': 450,
                 'DiggErr555': 1460,
             }},
            {'fn': 'hh/sat16/round1/hero-fold.txt',
             'expected':
             {
                 'Aurade': 445,
                 'Joshje': 625,
                 'byStereo': 510,
                 'DiggErr555': 420,
             }},
            {'fn': 'hh/sat16/round1/hero-push-bb-fold.txt',
             'expected':
             {
                 'fozzzi': 710,
                 'bayaraa2222': 340,
                 'apos87tolos': 200,
                 'DiggErr555': 750,
             }},
    ])
    def test_outcome_win(self, params):
        hand = get_parsed_hand_from_file(params.get('fn'))
        ev_calc = get_ev_calc('DiggErr555', hand, ((1,)), pokercalc.KOModels.PROPORTIONAL)
        expected = params.get('expected')
        aiplayers = ev_calc.ai_players
        chips = ev_calc.chips
        pots = ev_calc.pots
        uncalled = ev_calc.uncalled
        total_bets = ev_calc.total_bets
        winnings = ev_calc.winnings_chips
        path = params.get('path')
        result = pokercalc.build_outcome(path, aiplayers, chips, pots, uncalled, total_bets, winnings)
        self.assertDictEqual(result, expected)

    @add_params([
            {'fn': 'hh/sat16/round1/2way/hero-push-sb-call.txt',
             'path': ['fozzzi', 'DiggErr555'],
             'expected':
             {
                 'fozzzi': 1270,
                 'bayaraa2222': 270,
                 'apos87tolos': 460,
                 'DiggErr555':0,
             }},
            {'fn': 'hh/sat16/round1/2way/sb-push-hero-call.txt',
             'path': ['fozzzi', 'DiggErr555'],
             'expected':
             {
                 'fozzzi': 1420,
                 'DiggErr555': 580,
             }},
            {'fn': 'hh/sat16/round1/2way/hero-call-bvb.txt',
             'path': ['bayaraa2222', 'DiggErr555'],
             'expected':
             {
                 'fozzzi': 90,
                 'bayaraa2222': 560,
                 'apos87tolos': 450,
                 'DiggErr555': 900,
             }},
            {'fn': 'hh/sat16/round1/hero-fold.txt',
             'expected':
             {
                 'Aurade': 445,
                 'Joshje': 625,
                 'byStereo': 510,
                 'DiggErr555': 420,
             }},
            {'fn': 'hh/sat16/round1/hero-push-bb-fold.txt',
             'expected':
             {
                 'fozzzi': 710,
                 'bayaraa2222': 340,
                 'apos87tolos': 200,
                 'DiggErr555': 750,
             }},
    ])
    def test_outcome_lose(self, params):
        hand = get_parsed_hand_from_file(params.get('fn'))
        ev_calc = get_ev_calc('DiggErr555', hand, ((1,)), pokercalc.KOModels.PROPORTIONAL)
        expected = params.get('expected')
        aiplayers = ev_calc.ai_players
        chips = ev_calc.chips
        pots = ev_calc.pots
        uncalled = ev_calc.uncalled
        total_bets = ev_calc.total_bets
        winnings = ev_calc.winnings_chips
        path = params.get('path')
        result = pokercalc.build_outcome(path, aiplayers, chips, pots, uncalled, total_bets, winnings)
        self.assertDictEqual(result, expected)

class TestNumericDict(unittest.TestCase):
    def test_add(self):
        di1 = pokercalc.NumericDict(int)
        di1['a'] = 1
        di1['b'] = 2

        di2 = pokercalc.NumericDict(int)
        di2['a'] = 10
        di2['b'] = 20
        di1['c'] = 30

        di3 = di2+di1
        self.assertDictEqual(di3, {'a': 11, 'b': 22, 'c': 30})
        di4 = di1+di2
        self.assertDictEqual(di4, {'a': 11, 'b': 22, 'c': 30})

    def test_sub(self):
        di1 = pokercalc.NumericDict(int)
        di1['a'] = 1
        di1['b'] = 2

        di2 = pokercalc.NumericDict(int)
        di2['a'] = 10
        di2['b'] = 20
        di2['c'] = 30

        di3 = di2-di1
        self.assertDictEqual(di3, {'a': 9, 'b': 18, 'c': 30})
        di4 = di1-di2
        self.assertDictEqual(di4, {'a': -9, 'b': -18, 'c': -30})

    def test_mul(self):
        di1 = pokercalc.NumericDict(int)
        di1['a'] = 1
        di1['b'] = 2

        di3 = di1*5
        self.assertDictEqual(di3, {'a': 5, 'b': 10})
        di4 = 5*di1
        self.assertDictEqual(di4, {'a': 5, 'b': 10})

        di2 = pokercalc.NumericDict(int)
        di2['a'] = 88
        di2['c'] = 99
        di5 = di2 * di1
        self.assertDictEqual(di5, {'a': 88})

        di6 = di1 * di2
        self.assertDictEqual(di6, {'a': 88})

        di = {'a': 5, 'c': 10}
        with self.assertRaises(TypeError):
            di1 * di
        with self.assertRaises(TypeError):
            di * di1

    def test_truediv(self):
        di1 = pokercalc.NumericDict(int)
        di1['a'] = 1
        di1['b'] = 2

        di3 = di1/2
        self.assertDictEqual(di3, {'a': 0.5, 'b': 1})
        with self.assertRaises(TypeError):
            di4 = 2/di1

    def test_len(self):
        d = {'a': 1, 'b': 2, 'c': 3}
        di1 = pokercalc.NumericDict(int, d)
        self.assertDictEqual(di1, {'a': 1, 'b': 2, 'c': 3})
        self.assertEqual(len(di1), 3)

    def test_empty(self):
        d = pokercalc.NumericDict(int)
        self.assertFalse(d)


if __name__ == '__main__':
    unittest.main()
