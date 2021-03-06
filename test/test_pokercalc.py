import functools
import unittest
import logging
import random
from profiler import profile
import pprint
import eval7

from unittest import skip
from pypokertools.calc import pokercalc
from pypokertools.parsers import PSHandHistory as hhparser
from pypokertools.calc.pokercalc import OutcomeBuilder
from pypokertools.calc.pokercalc import str_to_cards

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
                case.calc()
                cls.case[fn] = case

    def get_params(self, params):
        expected = params.get('expected')
        case = self.case.get(params.get('fn'))
        return case, expected


class TestPokercalc(unittest.TestCase):
    @skip
    def test_icm(self):
        pc = pokercalc.Icm((0.5, 0.5))

    @profile('test_calc.txt')
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

        icm_ko = pokercalc.Icm((0.3333, 0.3333, 0.3333))

        self.assertListEqual(list(icm_ko.calc([954, 0, 466])),
                             [0.3333, 0.3333])

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

        self.assertDictEqual(icm_ko.calc(
           {
            'da_mauso': 974,
            'DiggErr555': 466,
            'baluoteli': 0,
            'bigboyby': 568,
            '2Ran128': 496,
            'zaxar393': 496
           }),
           {
            'da_mauso': 0.2944,
            'DiggErr555': 0.1639,
            'bigboyby': 0.1951,
            '2Ran128': 0.1733,
            'zaxar393': 0.1733
            })

        self.assertDictEqual(icm_ko.calc(
           {
            'vIpEr9427': 299,
            'Denisov V.': 427,
            'Chang Chi': 477,
            'sabuco_2110': 850,
            'shagvaladyan': 447,
            'DiggErr555': 500
           }),
           {
            'vIpEr9427': 0.1059,
            'Denisov V.': 0.1473,
            'Chang Chi': 0.1627,
            'sabuco_2110': 0.2608,
            'shagvaladyan': 0.1535,
            'DiggErr555': 0.1697
           })

        icm_sat = pokercalc.Icm((0.4, 0.4, 0.2))
        self.assertDictEqual(icm_sat.calc(
           {
                 'FutureofMe': 990,
                 'DiggErr555': 1010,
                 'Sunwavebeach': 0,
           }),
           {
                 'FutureofMe': 0.4,
                 'DiggErr555': 0.4,
           })

    def test__p1p(self):
        pass

    def test__check_chips(self):
        """TODO: Docstring for test__remove_zeros.

        :params: TODO
        :returns: TODO

        """
        icm_sat = pokercalc.Icm((0.4, 0.4, 0.2))
        self.assertDictEqual(icm_sat._check_chips(
           {
                 'FutureofMe': 990,
                 'DiggErr555': 1010,
                 'Sunwavebeach': 0,
           }),
           {
                 'FutureofMe': 990,
                 'DiggErr555': 1010,
           })


class TestEqArray(unittest.TestCase):
    def test_eqarray(self):
        pass


class TestEV(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # icm = pokercalc.Icm((0.5, 0.5))
        # icm1 = pokercalc.Icm((1,))
        # ko = pokercalc.Knockout(pokercalc.KOModels.PROPORTIONAL)
        # cls.case = {}
        # cases = [()]
        # fn_list = ['hh/th0.txt',
        #            'hh/th1.txt',
        #            'hh/th7.txt',
        #            'hh/th8.txt',
        #            'hh/sat16/round1/2way/hero-push-sb-call.txt',
        #            'hh/sat16/round1/2way/sb-push-hero-call.txt',
        #            'hh/sat16/round1/2way/hero-call-bvb.txt',
        #            ]
        # for fn in fn_list:
        #     with open(fn) as f:
        #         hh_text = f.read()
        #         # print(hh_text)
        #         parsed_hand = hhparser(hh_text)
        #         case = pokercalc.EV(parsed_hand, icm, ko)
        #         case.calc(parsed_hand.hero)
        #         cls.case[fn] = case
        pass

    def setUp(self):
        """TODO: Docstring for setUp.
        :returns: TODO

        """
        pass

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
        {
         'fn': 'hh/sat16/round1/auto-ai.txt',
         'expected': ['Skrotnes', 'NL_Classic'],
        },
        {'fn': 'hh/sat16/round1/hu-noai-postflop.txt',
         'expected': [],
         },
        {'fn': 'hh/sat16/round1/hu-noai-postflop2.txt',
         'expected': [],
         },
        {'fn': 'hh/sat16/round2/3way-bu-call-sb-call.txt',
         'expected': ['wycioreks', 'slavikus555', 'DiggErr555'],
         },
    ])
    def test_detect_ai_players(self, params):
        expected = params.get('expected')
        hand = get_parsed_hand_from_file(params.get('fn'))
        ai_players, p_ai_players, f_ai_players, t_ai_players = pokercalc.EV.detect_ai_players(hand)
        #logger.debug((p_ai_players, f_ai_players, t_ai_players))
        try:
            expected.sort()
            ai_players.sort()
        except:
            pass
        self.assertListEqual(expected, ai_players)

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
        {
         'fn': 'hh/sat16/round1/auto-ai.txt',
         'expected': ['Skrotnes', 'NL_Classic'],
        },
        {'fn': 'hh/sat16/round1/hu-noai-postflop.txt',
         'expected': [],
         },
        {'fn': 'hh/sat16/round1/hu-noai-postflop2.txt',
         'expected': [],
         },
        {'fn': 'hh/sat16/round2/3way-bu-call-sb-call.txt',
         'expected': ['wycioreks', 'slavikus555', 'DiggErr555'],
         },
        {
         'fn': 'hh/sat16/round1/auto-ai.txt',
         'expected': ['Skrotnes', 'NL_Classic'],
        },
    ])
    def test_detect_preflop_ai_players(self, params):
        expected = params.get('expected')
        hand = get_parsed_hand_from_file(params.get('fn'))
        ai_players, p_ai_players, f_ai_players, t_ai_players = pokercalc.EV.detect_ai_players(hand)
        try:
            expected.sort()
            p_ai_players.sort()
        except:
            pass
        self.assertListEqual(expected, p_ai_players)

    @profile('test_get_probs.prof')
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
        {
         'fn': 'hh/sat16/round1/auto-ai.txt',
         'expected': 0.2795,
         'player': 'NL_Classic'
        },
           ])
    def test_get_probs(self, params):
        hand = get_parsed_hand_from_file(params.get('fn'))
        hero = hand.hero
        ev_calc = get_ev_calc(hero, hand)
        expected = params.get('expected')
        result = ev_calc.get_probs(params.get('player'))
        self.assertAlmostEqual(result, expected, delta=0.005)

    @profile('test_equities_3way.prof')
    @add_params([
        {'fn': 'hh/sat16/round1/3way/3way-ai-preflop.txt',
         'expected': 0.5038,
         'player': 'OrangemanXD'
         },
        {'fn': 'hh/sat16/round1/3way/3way-ai-preflop.txt',
         'expected': 0.2976,
         'player': 'DiggErr555'
         },
        ])
    def test_equities_3way(self, params):
        hand = get_parsed_hand_from_file(params.get('fn'))
        hero = hand.hero
        ev_calc = get_ev_calc(hero, hand)
        expected = params.get('expected')
        result = ev_calc.get_probs(params.get('player'))
        self.assertAlmostEqual(result, expected, delta=0.005)

    @add_params([
        {'fn': 'hh/sat16/round1/3way/3way-ai-preflop.txt',
         'expected': 0.0107,
         'outcome': '122'
         },
        {'fn': 'hh/sat16/round1/3way/3way-ai-preflop.txt',
         'expected': 0.1631,
         'outcome': '321'
         },
        ])
    def test_calculate_outcome_probs(self, params):
        hand = get_parsed_hand_from_file(params.get('fn'))
        hero = hand.hero
        ev_calc = get_ev_calc(hero, hand)
        outcome = params.get('outcome')
        expected = params.get('expected')
        probs = ev_calc.calculate_outcome_probs()
        result = probs.get(outcome)
        self.assertAlmostEqual(result, expected, delta=0.005)


#    @profile('test-hu-ai-postflop.prof')
#    @add_params([
#        {
#         'fn': 'hh/sat16/round1/hu-ai-postflop.txt',
#         'expected': 0.7879,
#         'player': 'NL_Classic'
#        },
#           ])
#    def test_equities_flop(self, params):
#        hand = get_parsed_hand_from_file(params.get('fn'))
#        hero = hand.hero
#        ev_calc = get_ev_calc(hero, hand)
#        expected = params.get('expected')
#        result = ev_calc.get_probs(params.get('player'))
#        self.assertAlmostEqual(result, expected, delta=0.005)

    @profile('test-chip-diff-ev-adj.prof')
    @add_params([
        {
         'fn': 'hh/sat16/round1/2way/hero-push-sb-call.txt',
         'expected': -711,
         'player': 'DiggErr555'
        },
        {
         'fn':  'hh/sat16/round1/2way/sb-push-hero-call.txt',
         'expected': -675,
         'player': 'DiggErr555'
        },
        {
         'fn': 'hh/sat16/round1/2way/hero-call-bvb.txt',
         'expected': -88,
         'player': 'DiggErr555'
        },
           ])
    def test_chip_diff_ev_adj(self, params):
        hand = get_parsed_hand_from_file(params.get('fn'))
        ev_calc = get_ev_calc('DiggErr555', hand)
        expected = params.get('expected')
        result = ev_calc.chip_diff_ev_adj()
        self.assertAlmostEqual(round(result, 0), expected, delta=2)

    @profile('test-chip-fact.prof')
    @add_params([
        {'fn': 'hh/th1.txt',
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
        {'fn': 'hh/sat16/round1/hu.txt',
         'expected':
         {
             'L.A.Ruseman': 2000,
             'DiggErr555': 0,
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
        {'fn': 'hh/sat16/round1/hu-noai-postflop.txt',
         'expected':
         {
             'benekIP': 1560,
             'DiggErr555': 440,
         }},
        ])
    def test_chip_fact(self, params):
        hand = get_parsed_hand_from_file(params.get('fn'))
        hero = hand.hero
        ev_calc = get_ev_calc(hero, hand)
        expected = params.get('expected')
        result = ev_calc.chip_fact()
        self.assertDictEqual(result, expected)

    @profile('test-chip-net-won.prof')
    @add_params([
        {'fn': 'hh/sat16/round1/2way/sb-push-hero-call.txt',
         'expected':
         {
             'fozzzi': -710,
             'DiggErr555': 710,
         }},
        {'fn': 'hh/sat16/round1/2way/hero-call-bvb.txt',
         'expected':
         {
             'fozzzi': -10,
             'bayaraa2222': -270,
             'apos87tolos': -10,
             'DiggErr555': 290,
         }},
        {'fn': 'hh/sat16/round1/hero-push-bb-fold.txt',
         'expected':
         {
             'fozzzi': -10,
             'bayaraa2222': -10,
             'apos87tolos': -60,
             'DiggErr555': 80,
         }},
        ])
    def test_chip_net_won(self, params):
        hand = get_parsed_hand_from_file(params.get('fn'))
        hero = hand.hero
        ev_calc = get_ev_calc(hero, hand)
        expected = params.get('expected')
        result = ev_calc.chip_net_won()
        self.assertDictEqual(result, expected)

    @profile('test-chip-fact-3way.prof')
    @add_params([
            {'fn': 'hh/sat16/round1/3way/3way-ai-preflop.txt',
             'expected':
             {
                 'mjanisz': 455,
                 'OrangemanXD': 1545,
                 'DiggErr555': 0,
                 'dreber@77': 0,
             }},
            ])
    def test_chip_fact_3way(self, params):
        hand = get_parsed_hand_from_file(params.get('fn'))
        hero = hand.hero
        ev_calc = get_ev_calc(hero, hand)
        expected = params.get('expected')
        result = ev_calc.chip_fact()
        self.assertDictEqual(result, expected)

    @skip
    @add_params([
            {'fn': 'hh/th1.txt',
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

    @profile('test-icm-ev-diff-pct.prof')
    @add_params([
            {'fn': 'hh/sat16/round1/2way/hero-push-sb-call.txt',
             'expected': -0.35533,
             },
            {'fn': 'hh/sat16/round1/2way/sb-push-hero-call.txt',
             'expected': -0.33768,
             },
            {'fn': 'hh/sat16/round1/2way/hero-call-bvb.txt',
             'expected': -0.04402,
             },
            {'fn': 'hh/sat16/round1/auto-ai.txt',
             'expected': 0.00978,
             },
            {'fn': 'hh/sat16/round1/hu.txt',
             'expected': 0.20073,
             },
            {'fn': 'hh/sat16/round1/hu-noai-postflop2.txt',
             'expected': 0,
             },
            ])
    def test_icm_ev_diff_pct(self, params):
        hand = get_parsed_hand_from_file(params.get('fn'))
        expected = params.get('expected')
        prize = params.get('prize', ((1,)))
        hero = hand.hero
        ev_calc = get_ev_calc(hero, hand, prize)
        result = ev_calc.icm_ev_diff_pct()
        self.assertAlmostEqual(result, expected, delta=0.001)

    @add_params([
            {'fn': 'hh/sat16/round1/hu-noai-postflop2.txt',
             'expected': True,
             },
            ])
    def test_should_return_chip_fact(self, params):
        hand = get_parsed_hand_from_file(params.get('fn'))
        expected = params.get('expected')
        prize = params.get('prize', ((1,)))
        hero = hand.hero
        ev_calc = get_ev_calc(hero, hand, prize)
        logger.debug(ev_calc.ai_players)
        result = ev_calc.should_return_chip_fact()
        self.assertTrue(result, expected)

    @add_params([
            {'fn': 'hh/sat16/diverror-icmcalc.txt',
             'expected': 0.3527,
             'prize': (0.4631, .4631, .0738),
             },
            ])
    def test_icm_calc(self, params):
        """

        :params: TODO
        :returns: TODO

        """
        hand = get_parsed_hand_from_file(params.get('fn'))
        expected = params.get('expected')
        payouts = params.get('prize', ((1,)))
        hero = hand.hero

        icm_calc = pokercalc.Icm(payouts)

        result = icm_calc.calc(hand.chips())
        self.assertAlmostEqual(result.get(hero, 0), expected, delta=0.001)

    @profile('test-icm-ev-diff-pct-3way.prof')
    @add_params([
            {'fn': 'hh/sat16/round1/3way/3way-ai-preflop.txt',
             'expected': 0.2202,
             },
            ])
    def test_icm_ev_diff_pct_3way(self, params):
        hand = get_parsed_hand_from_file(params.get('fn'))
        expected = params.get('expected')
        prize = params.get('prize', ((1,)))
        hero = hand.hero
        ev_calc = get_ev_calc(hero, hand, prize)
        result = ev_calc.icm_ev_diff_pct()
        #print(f'result: {result}')
        #print(f'expected: {expected}')
        self.assertAlmostEqual(result, expected, 3)

    @add_params([
            {'fn': 'hh/th1.txt',
            'expected':
            {
                'vIpEr9427': 0.1059,
                'Denisov V.': 0.1473,
                'Chang Chi': 0.1627,
                'sabuco_2110': 0.2608,
                'shagvaladyan': 0.1535,
                'DiggErr555': 0.1697
            },
            'prize': (0.5, 0.5)},
            {'fn': 'hh/sat16/round1/2way/hero-push-sb-call.txt',
             'expected':
             {
                 'fozzzi': 0.05,
                 'bayaraa2222': 0.135,
                 'DiggErr555': 0.585,
                 'apos87tolos': 0.23,
             }},
            {'fn': 'hh/sat16/round1/2way/sb-push-hero-call.txt',
             'expected':
             {
                 'fozzzi': 0,
                 'DiggErr555': 1,
             }},
            {'fn': 'hh/sat16/round1/2way/hero-call-bvb.txt',
             'expected':
             {
                 'fozzzi': 0.045,
                 'bayaraa2222': 0,
                 'apos87tolos': 0.225,
                 'DiggErr555': 0.73,
             }},
            ])
    def test_icm_fact_pct(self, params):
        hand = get_parsed_hand_from_file(params.get('fn'))
        hero = hand.hero
        expected = params.get('expected')
        prize = params.get('prize', ((1,)))
        ev_calc = get_ev_calc(hero, hand, prize)
        result = ev_calc.icm_fact_pct()
        self.assertEqual(result, expected.get(hero))

    @add_params([
            {'fn': 'hh/sat16/round1/3way/3way-ai-preflop.txt',
             'expected':
             {
                 'OrangemanXD': 1,
             }},
            ])
    def test_icm_fact_pct_3way(self, params):
        hand = get_parsed_hand_from_file(params.get('fn'))
        hero = hand.hero
        expected = params.get('expected')
        prize = params.get('prize', ((1,)))
        ev_calc = get_ev_calc(hero, hand, prize)
        result = ev_calc.icm_fact_pct()

        self.assertEqual(result, expected.get(hero, 0))

    @skip
    @add_params([
             # {'fn': 'hh/th1.txt',
             #  'expected':
             #  {
             #   'vIpEr9427': 7.63,
             #   'Denisov V.': 10.61,
             #   'Chang Chi': 11.72,
             #   'sabuco_2110': 18.79,
             #   'shagvaladyan': 11.06,
             #   'DiggErr555': 12.23
             #  }},
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

    @add_params([
            {'fn': 'hh/sat16/round1/2way/hero-call-bvb.txt',
             'expected': '',
             },
            ])
    def test_get_board_before_allin(self, params):
        """
        :returns: TODO

        """
        hand = get_parsed_hand_from_file(params.get('fn'))
        hero = hand.hero
        expected = params.get('expected')
        prize = params.get('prize', ((1,)))
        ev_calc = get_ev_calc(hero, hand, prize)
        result = ev_calc.get_board_before_allin()
        self.assertEqual(result, expected)


class TestOutcomeBuilder(unittest.TestCase):
    """
                {'fn': 'hh/sat16/round1/3way/3way-ai-preflop.txt',
    Seat 1: dreber@77 (490 in chips)
    Seat 2: mjanisz (465 in chips)
    Seat 3: OrangemanXD (555 in chips)
    Seat 4: DiggErr555 (490 in chips)
                {'fn': 'hh/sat16/round2/3way-bu-call-sb-call.txt',
    Seat 2: slavikus555 (730 in chips) 
    Seat 3: DiggErr555 (1175 in chips) 
    Seat 4: wycioreks (95 in chips) 
    """
    @add_params([
            {'fn': 'hh/sat16/round2/3way-bu-call-sb-call.txt',
             'expected':
             {
                 'slavikus555': 610,
                 'DiggErr555': 1390,
                 'wycioreks': 0,
             }},
            {'fn': 'hh/sat16/round1/3way/3way-ai-preflop.txt',
             'expected':
             {
                 'dreber@77': 0,
                 'DiggErr555': 0,
                 'mjanisz': 455,
                 'OrangemanXD': 1545,
             }},
    ])
    def test_outcome123(self, params):
        hand = get_parsed_hand_from_file(params.get('fn'))
        ev_calc = get_ev_calc('DiggErr555', hand, ((1,)), pokercalc.KOModels.PROPORTIONAL)
        expected = params.get('expected')
        aiplayers = ev_calc.ai_players
        chips = ev_calc.chips
        pots = ev_calc.pots
        uncalled = ev_calc.uncalled
        total_bets = ev_calc.total_bets
        winnings = ev_calc.winnings_chips
        ob = OutcomeBuilder(aiplayers, chips, pots, uncalled, total_bets, winnings)
        outcome = ob.outcome123()
        self.assertDictEqual(outcome, expected)
        totalchips = 2000
        result = sum(list(outcome.values()))
        self.assertEqual(result, totalchips)

    @add_params([
            {'fn': 'hh/sat16/round2/3way-bu-call-sb-call.txt',
             'expected':
             {
                 'slavikus555': 610,
                 'DiggErr555': 1390,
                 'wycioreks': 0,
             }},
            {'fn': 'hh/sat16/round1/3way/3way-ai-preflop.txt',
             'expected':
             {
                 'dreber@77': 0,
                 'DiggErr555': 0,
                 'mjanisz': 455,
                 'OrangemanXD': 1545,
             }},
    ])
    def test_outcome132(self, params):
        hand = get_parsed_hand_from_file(params.get('fn'))
        ev_calc = get_ev_calc('DiggErr555', hand, ((1,)), pokercalc.KOModels.PROPORTIONAL)
        expected = params.get('expected')
        aiplayers = ev_calc.ai_players
        chips = ev_calc.chips
        pots = ev_calc.pots
        uncalled = ev_calc.uncalled
        total_bets = ev_calc.total_bets
        winnings = ev_calc.winnings_chips
        ob = OutcomeBuilder(aiplayers, chips, pots, uncalled, total_bets, winnings)
        outcome = ob.outcome132()
        self.assertDictEqual(outcome, expected)
        totalchips = 2000
        result = sum(list(outcome.values()))
        self.assertEqual(result, totalchips)

    @add_params([
            {'fn': 'hh/sat16/round2/3way-bu-call-sb-call.txt',
             'expected':
             {
                 'slavikus555': 610,
                 'DiggErr555': 1390,
                 'wycioreks': 0,
             }},
             {'fn': 'hh/sat16/round1/3way/3way-ai-preflop.txt',
             'expected':
             {
                 'dreber@77': 0,
                 'DiggErr555': 0,
                 'mjanisz': 455,
                 'OrangemanXD': 1545,
             }},
    ])
    def test_outcome122(self, params):
        hand = get_parsed_hand_from_file(params.get('fn'))
        ev_calc = get_ev_calc('DiggErr555', hand, ((1,)), pokercalc.KOModels.PROPORTIONAL)
        expected = params.get('expected')
        aiplayers = ev_calc.ai_players
        chips = ev_calc.chips
        pots = ev_calc.pots
        uncalled = ev_calc.uncalled
        total_bets = ev_calc.total_bets
        winnings = ev_calc.winnings_chips
        ob = OutcomeBuilder(aiplayers, chips, pots, uncalled, total_bets, winnings)
        outcome = ob.outcome122()
        self.assertDictEqual(outcome, expected)
        totalchips = 2000
        result = sum(list(outcome.values()))
        self.assertEqual(result, totalchips)

    @add_params([
            {'fn': 'hh/sat16/round2/3way-bu-call-sb-call.txt',
             'expected':
             {
                 'slavikus555': 945,
                 'DiggErr555': 1055,
                 'wycioreks': 0,
             }},
             {'fn': 'hh/sat16/round1/3way/3way-ai-preflop.txt',
             'expected':
             {
                 'dreber@77': 1480,
                 'DiggErr555': 0,
                 'mjanisz': 455,
                 'OrangemanXD': 65,
             }},
    ])
    def test_outcome213(self, params):
        hand = get_parsed_hand_from_file(params.get('fn'))
        ev_calc = get_ev_calc('DiggErr555', hand, ((1,)), pokercalc.KOModels.PROPORTIONAL)
        expected = params.get('expected')
        aiplayers = ev_calc.ai_players
        chips = ev_calc.chips
        pots = ev_calc.pots
        uncalled = ev_calc.uncalled
        total_bets = ev_calc.total_bets
        winnings = ev_calc.winnings_chips
        ob = OutcomeBuilder(aiplayers, chips, pots, uncalled, total_bets, winnings)
        outcome = ob.outcome213()
        self.assertDictEqual(outcome, expected)
        totalchips = 2000
        result = sum(list(outcome.values()))
        self.assertEqual(result, totalchips)

    @add_params([
            {'fn': 'hh/sat16/round2/3way-bu-call-sb-call.txt',
             'expected':
             {
                 'slavikus555': 945,
                 'DiggErr555': 1055,
                 'wycioreks': 0,
             }},
            {'fn': 'hh/sat16/round1/3way/3way-ai-preflop.txt',
             'expected':
             {
                 'dreber@77': 1480,
                 'DiggErr555': 0,
                 'mjanisz': 455,
                 'OrangemanXD': 65,
             }},
    ])
    def test_outcome312(self, params):
        hand = get_parsed_hand_from_file(params.get('fn'))
        ev_calc = get_ev_calc('DiggErr555', hand, ((1,)), pokercalc.KOModels.PROPORTIONAL)
        expected = params.get('expected')
        aiplayers = ev_calc.ai_players
        chips = ev_calc.chips
        pots = ev_calc.pots
        uncalled = ev_calc.uncalled
        total_bets = ev_calc.total_bets
        winnings = ev_calc.winnings_chips
        ob = OutcomeBuilder(aiplayers, chips, pots, uncalled, total_bets, winnings)
        outcome = ob.outcome312()
        self.assertDictEqual(outcome, expected)
        totalchips = 2000
        result = sum(list(outcome.values()))
        self.assertEqual(result, totalchips)

    @add_params([
            {'fn': 'hh/sat16/round2/3way-bu-call-sb-call.txt',
             'expected':
             {
                 'slavikus555': 945,
                 'DiggErr555': 1055,
                 'wycioreks': 0,
             }},
            {'fn': 'hh/sat16/round1/3way/3way-ai-preflop.txt',
             'expected':
             {
                 'dreber@77': 1480,
                 'DiggErr555': 0,
                 'mjanisz': 455,
                 'OrangemanXD': 65,
             }},
    ])
    def test_outcome212(self, params):
        hand = get_parsed_hand_from_file(params.get('fn'))
        ev_calc = get_ev_calc('DiggErr555', hand, ((1,)), pokercalc.KOModels.PROPORTIONAL)
        expected = params.get('expected')
        aiplayers = ev_calc.ai_players
        chips = ev_calc.chips
        pots = ev_calc.pots
        uncalled = ev_calc.uncalled
        total_bets = ev_calc.total_bets
        winnings = ev_calc.winnings_chips
        ob = OutcomeBuilder(aiplayers, chips, pots, uncalled, total_bets, winnings)
        outcome = ob.outcome212()
        self.assertDictEqual(outcome, expected)
        totalchips = 2000
        result = sum(list(outcome.values()))
        self.assertEqual(result, totalchips)


    @add_params([
            {'fn': 'hh/sat16/round2/3way-bu-call-sb-call.txt',
             'expected':
             {
                 'slavikus555': 730,
                 'DiggErr555': 1175,
                 'wycioreks': 95,
             }},
            {'fn': 'hh/sat16/round1/3way/3way-ai-preflop.txt',
             'expected':
             {
                 'dreber@77': 493,
                 'DiggErr555': 494,
                 'mjanisz': 455,
                 'OrangemanXD': 558,
             }},
    ])
    def test_outcome111(self, params):
        hand = get_parsed_hand_from_file(params.get('fn'))
        ev_calc = get_ev_calc('DiggErr555', hand, ((1,)), pokercalc.KOModels.PROPORTIONAL)
        expected = params.get('expected')
        aiplayers = ev_calc.ai_players
        chips = ev_calc.chips
        pots = ev_calc.pots
        uncalled = ev_calc.uncalled
        total_bets = ev_calc.total_bets
        winnings = ev_calc.winnings_chips
        ob = OutcomeBuilder(aiplayers, chips, pots, uncalled, total_bets, winnings)
        outcome = ob.outcome111()
        self.assertDictEqual(outcome, expected)
        totalchips = 2000
        result = sum(list(outcome.values()))
        self.assertEqual(result, totalchips)

    @add_params([
            {'fn': 'hh/sat16/round2/3way-bu-call-sb-call.txt',
             'expected':
             {
                 'slavikus555': 778,
                 'DiggErr555': 1222,
                 'wycioreks': 0,
             }},
            {'fn': 'hh/sat16/round1/3way/3way-ai-preflop.txt',
             'expected':
             {
                 'dreber@77': 740,
                 'DiggErr555': 0,
                 'mjanisz': 455,
                 'OrangemanXD': 805,
             }},
    ])
    def test_outcome113(self, params):
        hand = get_parsed_hand_from_file(params.get('fn'))
        ev_calc = get_ev_calc('DiggErr555', hand, ((1,)), pokercalc.KOModels.PROPORTIONAL)
        expected = params.get('expected')
        aiplayers = ev_calc.ai_players
        chips = ev_calc.chips
        pots = ev_calc.pots
        uncalled = ev_calc.uncalled
        total_bets = ev_calc.total_bets
        winnings = ev_calc.winnings_chips
        ob = OutcomeBuilder(aiplayers, chips, pots, uncalled, total_bets, winnings)
        outcome = ob.outcome113()
        self.assertDictEqual(outcome, expected)
        totalchips = 2000
        result = sum(list(outcome.values()))
        self.assertEqual(result, totalchips)

    @add_params([
            {'fn': 'hh/sat16/round2/3way-bu-call-sb-call.txt',
             'expected':
             {
                 'slavikus555': 610,
                 'DiggErr555': 1247,
                 'wycioreks': 143,
             }},
            {'fn': 'hh/sat16/round1/3way/3way-ai-preflop.txt',
             'expected':
             {
                 'dreber@77': 0,
                 'DiggErr555': 740,
                 'mjanisz': 455,
                 'OrangemanXD': 805,
             }},
    ])
    def test_outcome131(self, params):
        hand = get_parsed_hand_from_file(params.get('fn'))
        ev_calc = get_ev_calc('DiggErr555', hand, ((1,)), pokercalc.KOModels.PROPORTIONAL)
        expected = params.get('expected')
        aiplayers = ev_calc.ai_players
        chips = ev_calc.chips
        pots = ev_calc.pots
        uncalled = ev_calc.uncalled
        total_bets = ev_calc.total_bets
        winnings = ev_calc.winnings_chips
        ob = OutcomeBuilder(aiplayers, chips, pots, uncalled, total_bets, winnings)
        outcome = ob.outcome131()
        self.assertDictEqual(outcome, expected)
        totalchips = 2000
        result = sum(list(outcome.values()))
        self.assertEqual(result, totalchips)

    @add_params([
            {'fn': 'hh/sat16/round2/3way-bu-call-sb-call.txt',
             'expected':
             {
                 'slavikus555': 802,
                 'DiggErr555': 1055,
                 'wycioreks': 143,
             }},
            {'fn': 'hh/sat16/round1/3way/3way-ai-preflop.txt',
             'expected':
             {
                 'dreber@77': 740,
                 'DiggErr555': 740,
                 'mjanisz': 455,
                 'OrangemanXD': 65,
             }},
    ])
    def test_outcome311(self, params):
        hand = get_parsed_hand_from_file(params.get('fn'))
        ev_calc = get_ev_calc('DiggErr555', hand, ((1,)), pokercalc.KOModels.PROPORTIONAL)
        expected = params.get('expected')
        aiplayers = ev_calc.ai_players
        chips = ev_calc.chips
        pots = ev_calc.pots
        uncalled = ev_calc.uncalled
        total_bets = ev_calc.total_bets
        winnings = ev_calc.winnings_chips
        ob = OutcomeBuilder(aiplayers, chips, pots, uncalled, total_bets, winnings)
        outcome = ob.outcome311()
        self.assertDictEqual(outcome, expected)
        totalchips = 2000
        result = sum(list(outcome.values()))
        self.assertEqual(result, totalchips)

    @add_params([
            {'fn': 'hh/sat16/round2/3way-bu-call-sb-call.txt',
             'expected':
             {
                 'slavikus555': 610,
                 'DiggErr555': 1105,
                 'wycioreks': 285,
             }},
            {'fn': 'hh/sat16/round1/3way/3way-ai-preflop.txt',
             'expected':
             {
                 'dreber@77': 0,
                 'DiggErr555': 1480,
                 'mjanisz': 455,
                 'OrangemanXD': 65,
             }},
    ])
    def test_outcome231(self, params):
        hand = get_parsed_hand_from_file(params.get('fn'))
        ev_calc = get_ev_calc('DiggErr555', hand, ((1,)), pokercalc.KOModels.PROPORTIONAL)
        expected = params.get('expected')
        aiplayers = ev_calc.ai_players
        chips = ev_calc.chips
        pots = ev_calc.pots
        uncalled = ev_calc.uncalled
        total_bets = ev_calc.total_bets
        winnings = ev_calc.winnings_chips
        ob = OutcomeBuilder(aiplayers, chips, pots, uncalled, total_bets, winnings)
        outcome = ob.outcome231()
        self.assertDictEqual(outcome, expected)
        totalchips = 2000
        result = sum(list(outcome.values()))
        self.assertEqual(result, totalchips)

    @add_params([
            {'fn': 'hh/sat16/round2/3way-bu-call-sb-call.txt',
             'expected':
             {
                 'slavikus555': 660,
                 'DiggErr555': 1055,
                 'wycioreks': 285,
             }},
            {'fn': 'hh/sat16/round1/3way/3way-ai-preflop.txt',
             'expected':
             {
                 'dreber@77': 0,
                 'DiggErr555': 1480,
                 'mjanisz': 455,
                 'OrangemanXD': 65,
             }},
    ])
    def test_outcome321(self, params):
        hand = get_parsed_hand_from_file(params.get('fn'))
        ev_calc = get_ev_calc('DiggErr555', hand, ((1,)), pokercalc.KOModels.PROPORTIONAL)
        expected = params.get('expected')
        aiplayers = ev_calc.ai_players
        chips = ev_calc.chips
        pots = ev_calc.pots
        uncalled = ev_calc.uncalled
        total_bets = ev_calc.total_bets
        winnings = ev_calc.winnings_chips
        ob = OutcomeBuilder(aiplayers, chips, pots, uncalled, total_bets, winnings)
        outcome = ob.outcome321()
        self.assertDictEqual(outcome, expected)
        totalchips = 2000
        result = sum(list(outcome.values()))
        self.assertEqual(result, totalchips)


    @add_params([
            {'fn': 'hh/sat16/round2/3way-bu-call-sb-call.txt',
             'expected':
             {
                 'slavikus555': 635,
                 'DiggErr555': 1080,
                 'wycioreks': 285,
             }},
            {'fn': 'hh/sat16/round1/3way/3way-ai-preflop.txt',
             'expected':
             {
                 'dreber@77': 0,
                 'DiggErr555': 1480,
                 'mjanisz': 455,
                 'OrangemanXD': 65,
             }},
    ])
    def test_outcome221(self, params):
        hand = get_parsed_hand_from_file(params.get('fn'))
        ev_calc = get_ev_calc('DiggErr555', hand, ((1,)), pokercalc.KOModels.PROPORTIONAL)
        expected = params.get('expected')
        aiplayers = ev_calc.ai_players
        chips = ev_calc.chips
        pots = ev_calc.pots
        uncalled = ev_calc.uncalled
        total_bets = ev_calc.total_bets
        winnings = ev_calc.winnings_chips
        ob = OutcomeBuilder(aiplayers, chips, pots, uncalled, total_bets, winnings)
        outcome = ob.outcome221()
        self.assertDictEqual(outcome, expected)
        totalchips = 2000
        result = sum(list(outcome.values()))
        self.assertEqual(result, totalchips)

    @skip
    @add_params([
            {'fn': 'hh/sat16/round1/3way/3way-ai-preflop.txt',
             'outcome': '312',
             'expected':
             {
                 'DiggErr555': 0,
                 'dreber@77': 1480,
                 'mjanisz': 455,
                 'OrangemanXD': 65,
             }},
            {'fn': 'hh/sat16/round1/3way/3way-ai-preflop.txt',
             'outcome': '123',
             'expected':
             {
                 'dreber@77': 0,
                 'DiggErr555': 0,
                 'mjanisz': 455,
                 'OrangemanXD': 1545,
             }},
            {'fn': 'hh/sat16/round1/3way/3way-ai-preflop.txt',
             'outcome': '312',
             'expected':
             {
                 'DiggErr555': 0,
                 'dreber@77': 1480,
                 'mjanisz': 455,
                 'OrangemanXD': 65,
             }},
            {'fn': 'hh/sat16/round1/3way/3way-ai-preflop.txt',
             'outcome': '321',
             'expected':
             {
                 'DiggErr555': 0,
                 'dreber@77': 1480,
                 'mjanisz': 455,
                 'OrangemanXD': 65,
             }},
            {'fn': 'hh/sat16/round1/3way/3way-ai-preflop.txt',
             'outcome': '123',
             'expected':
             {
                 'dreber@77': 0,
                 'DiggErr555': 1480,
                 'mjanisz': 455,
                 'OrangemanXD': 65,
             }},
    ])
    def test_build_outcome(self, params):
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
        ob = OutcomeBuilder(aiplayers, chips, pots, uncalled, total_bets, winnings)
        outcomes = ob.build_outcomes()
        self.assertDictEqual(outcomes[params.get('outcome')], expected)


class TestOutcome(unittest.TestCase):
    def test_add_cildren(self):
        aiplayers = ['DiggErr555', 'fozzzi']
        root = pokercalc.OutCome('root')
        pokercalc.add_children(root, aiplayers)
        print(root)

    @skip
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
            {'fn': 'hh/sat16/diverror-icmcalc.txt',
             'path': ['DiggErr555', 'Sunwavebeach'],
             'expected':
             {
                 'FutureofMe': 990,
                 'DiggErr555': 1010,
                 'Sunwavebeach': 0,
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
            {'fn': 'hh/sat16/round1/auto-ai.txt',
             'path': ['NL_Classic', 'Skrotnes'],
             'expected':
             {
                 'NL_Classic': 70,
                 'Skrotnes': 570,
                 'felipe goula': 395,
                 'DiggErr555': 965
             }},
    ])
    def test_outcome_win_auto_ai(self, params):
        hand = get_parsed_hand_from_file(params.get('fn'))
        hero = hand.hero
        ev_calc = get_ev_calc(hero, hand, ((1,)), pokercalc.KOModels.PROPORTIONAL)
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
            {'fn': 'hh/sat16/round1/auto-ai.txt',
             'path': ['Skrotnes', 'NL_Classic'],
             'expected':
             {
                 'NL_Classic': 0,
                 'Skrotnes': 640,
                 'felipe goula': 395,
                 'DiggErr555': 965
             }},
    ])
    def test_outcome_lose_auto_ai(self, params):
        hand = get_parsed_hand_from_file(params.get('fn'))
        hero = hand.hero
        ev_calc = get_ev_calc(hero, hand, ((1,)), pokercalc.KOModels.PROPORTIONAL)
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

    @add_params([
            {'fn': 'hh/sat16/round1/3way/3way-ai-preflop.txt',
             'path': ['dreber@77', 'OrangemanXD', 'DiggErr555'],
             'expected':
             {
                 'DiggErr555': 0,
                 'dreber@77': 1480,
                 'mjanisz': 455,
                 'OrangemanXD': 65,
             }},
            {'fn': 'hh/sat16/round1/3way/3way-ai-preflop.txt',
             'path': ['OrangemanXD', 'dreber@77', 'DiggErr555'],
             'expected':
             {
                 'dreber@77': 0,
                 'DiggErr555': 0,
                 'mjanisz': 455,
                 'OrangemanXD': 1545,
             }},
            {'fn': 'hh/sat16/round1/3way/3way-ai-preflop.txt',
             'path': ['dreber@77', 'DiggErr555', 'OrangemanXD', ],
             'expected':
             {
                 'DiggErr555': 0,
                 'dreber@77': 1480,
                 'mjanisz': 455,
                 'OrangemanXD': 65,
             }},
            {'fn': 'hh/sat16/round1/3way/3way-ai-preflop.txt',
             'path': ['dreber@77', 'OrangemanXD', 'DiggErr555', ],
             'expected':
             {
                 'DiggErr555': 0,
                 'dreber@77': 1480,
                 'mjanisz': 455,
                 'OrangemanXD': 65,
             }},
            {'fn': 'hh/sat16/round1/3way/3way-ai-preflop.txt',
             'path': ['DiggErr555', 'OrangemanXD', 'dreber@77', ],
             'expected':
             {
                 'dreber@77': 0,
                 'DiggErr555': 1480,
                 'mjanisz': 455,
                 'OrangemanXD': 65,
             }},
    ])
    def test_outcome_3way(self, params):
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
        
        scalar = 10
        di3 = di2-di1
        self.assertDictEqual(di3, {'a': 9, 'b': 18, 'c': 30})
        di4 = di1-di2
        self.assertDictEqual(di4, {'a': -9, 'b': -18, 'c': -30})
        di5 = di2-scalar
        self.assertDictEqual(di5, {'a': 0, 'b': 10, 'c': 20})

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
