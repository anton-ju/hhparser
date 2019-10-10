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


def cases(cases):
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args):
            for c in cases:
                new_args = args + (c if isinstance(c, tuple) else (c,))
                f(*new_args)
        return wrapper
    return decorator


def round_dict(d, n):
    return {k: round(v, n) for k, v in d.items()}


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
        ko = pokercalc.Knockout(pokercalc.KOModels.PROPORTIONAL)
        cls.case = {}
        fn_list = ['hh/th0.txt', 'hh/th1.txt', 'hh/th7.txt', 'hh/th8.txt']
        for fn in fn_list:
            with open(fn) as f:
                hh_text = f.read()
                print(hh_text)
                parsed_hand = hhparser(hh_text)
                case = pokercalc.EV(parsed_hand, icm, ko)
                case.calc('DiggErr555')
                cls.case[fn] = case

    def get_params(self, params):
        expected = params.get('expected')
        case = self.case.get(params.get('fn'))
        return case, expected

    @cases([
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
         'fn': 'hh/th7.txt',
         'expected': 0.5566,
         'player': 'DiggErr555'
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

    @cases([{'fn': 'hh/th1.txt',
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
             }}])
    def test_chip_fact(self, params):
        case, expected = self.get_params(params)
        result = case.chip_fact()
        self.assertDictEqual(result, expected)

    @cases([{'fn': 'hh/th1.txt',
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
             }}])
    def test_chip_fact_chip_sum(self, params):
        case, expected = self.get_params(params)
        result = case.chip_fact()
        result = pokercalc.EV.sum_dict_values(result)
        self.assertEqual(result, 3000, 'Chip sum should be 3000')

    @cases([{
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

    @cases([{
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

    @skip
    def test_icm_ev(self):
        case = self.case1
        res = case.icm_ev()
        logger.debug(f'{case.hand.hid}->{res}')
    #     self.assertEqual(res, {'vIpEr9427': 12.61,
    #                                 'Denisov V.': 10.63,
    #                                 'Chang Chi': 6.67,
    #                                 'sabuco_2110': 18.82,
    #                                 'shagvaladyan': 11.08,
    #                                 'DiggErr555': 12.24})

    @skip
    def test_icm_ev_pct(self):
        case = self.case1
        res = case.icm_ev_pct()
        logger.debug(f'{case.hand.hid}->{res}')
    #     self.assertEqual(res, {'vIpEr9427': 0.175,
    #                                 'Denisov V.': 0.1475,
    #                                 'Chang Chi': 0.0926,
    #                                 'sabuco_2110': 0.2612,
    #                                 'shagvaladyan': 0.1538,
    #                                 'DiggErr555': 0.1699})

    @skip
    def test_ko_ev_pct(self):
        case = self.case1
        res = case.ko_ev_pct()
        logger.debug(f'{case.hand.hid}->{res}')
    #     self.assertEqual(ko_ev_pct, {'vIpEr9427': 1.03,
    #                                     'Denisov V.': 0.85,
    #                                     'Chang Chi': 0.52,
    #                                     'sabuco_2110': 1.7,
    #                                     'shagvaladyan': 0.89,
    #                                     'DiggErr555': 1})

    @skip
    def test_ko_ev(self):
        case = self.case1
        res = case.ko_ev()
        logger.debug(f'{case.hand.hid}->{res}')
    #     self.assertEqual(ko_ev, {'vIpEr9427': 12.43,
    #                                     'Denisov V.': 10.26,
    #                                     'Chang Chi': 6.21,
    #                                     'sabuco_2110': 20.42,
    #                                     'shagvaladyan': 10.74,
    #                                     'DiggErr555': 12.01})

    @skip
    def test_ko_fact(self):
        ko_fact = self.case1.ko_fact()
        # logger.debug(ko_fact)
        ko_fact = round_dict(ko_fact, 2)
        self.assertDictEqual(ko_fact, {'vIpEr9427': 7.18,
                                   'Denisov V.': 10.26,
                                   'Chang Chi': 11.46,
                                   'sabuco_2110': 20.42,
                                   'shagvaladyan': 10.74,
                                   'DiggErr555': 12.01})

    @skip
    def test_ko_fact_pct(self):
        ko_fact_pct = self.case1.ko_fact_pct()
        ko_fact_pct = round_dict(ko_fact_pct, 333)
        # logger.debug(ko_fact_pct)
        self.assertDictEqual(ko_fact_pct, {
                                       'vIpEr9427': 0.598,
                                       'Denisov V.': 0.854,
                                       'Chang Chi': 0.954,
                                       'sabuco_2110': 1.7,
                                       'shagvaladyan': 0.894,
                                       'DiggErr555': 1.0
                                        })

    def test_non_zero_values(self):
        self.assertEqual(pokercalc.EV.non_zero_values({1: 1, 2: 2, 3: 0, 4: 0}), 2)

    def test_sum_dict_values(self):
        self.assertEqual(pokercalc.EV.sum_dict_values({1: 1, 2: 2, 3: 0, 4: 0}), 3)
        self.assertEqual(pokercalc.EV.sum_dict_values({1: 1, 2: 2, 3: 'sdf', 4: 0}), 0)
        self.assertEqual(pokercalc.EV.sum_dict_values([1, 2, 3]), 0)


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
