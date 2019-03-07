import unittest
from calc import pokercalc
from parsers import hhparser
import logging
import random
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
random.seed(42)
th0 = """
PokerStars Hand #182384621288: Tournament #2216721390, $4.79+$4.79+$0.42 USD Hold'em No Limit - Level I (10/20) - 2018/02/12 4:32:33 MSK [2018/02/11 20:32:33 ET]
Table '2216721390 1' 6-max Seat #3 is the button
Seat 1: da_mauso (954 in chips)
Seat 2: baluoteli (20 in chips)
Seat 3: DiggErr555 (466 in chips)
Seat 4: bigboyby (568 in chips)
Seat 5: 2Ran128 (496 in chips)
Seat 6: zaxar393 (496 in chips)
da_mauso: posts the ante 2
baluoteli: posts the ante 2
DiggErr555: posts the ante 2
bigboyby: posts the ante 2
2Ran128: posts the ante 2
zaxar393: posts the ante 2
bigboyby: posts small blind 10
2Ran128: posts big blind 20
*** HOLE CARDS ***
Dealt to DiggErr555 [As Ad]
zaxar393: calls 20
da_mauso: raises 20 to 40
baluoteli: calls 18 and is all-in
DiggErr555: raises 424 to 464 and is all-in
bigboyby: raises 102 to 566 and is all-in
2Ran128: folds
zaxar393: calls 474 and is all-in
da_mauso: folds
Uncalled bet (72) returned to bigboyby
*** FLOP *** [3s 2h 7c]
*** TURN *** [3s 2h 7c] [Jh]
*** RIVER *** [3s 2h 7c Jh] [Ks]
*** SHOW DOWN ***
bigboyby: shows [5d 5h] (a pair of Fives)
zaxar393: shows [9d Kd] (a pair of Kings)
zaxar393 collected 60 from side pot-2
DiggErr555: shows [As Ad] (a pair of Aces)
DiggErr555 collected 1362 from side pot-1
baluoteli: shows [Jd Qs] (a pair of Jacks)
DiggErr555 collected 120 from main pot
DiggErr555 wins the $4.79 bounty for eliminating baluoteli
baluoteli finished the tournament in 6th place
*** SUMMARY ***
Total pot 1542 Main pot 120. Side pot-1 1362. Side pot-2 60. | Rake 0
Board [3s 2h 7c Jh Ks]
Seat 1: da_mauso folded before Flop
Seat 2: baluoteli showed [Jd Qs] and lost with a pair of Jacks
Seat 3: DiggErr555 (button) showed [As Ad] and won (1482) with a pair of Aces
Seat 4: bigboyby (small blind) showed [5d 5h] and lost with a pair of Fives
Seat 5: 2Ran128 (big blind) folded before Flop
Seat 6: zaxar393 showed [9d Kd] and won (60) with a pair of Kings

"""

th1 = """
PokerStars Hand #188549132928: Tournament #2352975270, $12.01+$12.01+$0.98 USD Hold'em No Limit - Level II (15/30) - 2018/07/10 1:52:37 MSK [2018/07/09 18:52:37 ET]
Table '2352975270 1' 6-max Seat #1 is the button
Seat 1: vIpEr9427 (524 in chips)
Seat 2: Denisov V. (445 in chips)
Seat 3: Chang Chi (225 in chips)
Seat 4: sabuco_2110 (853 in chips)
Seat 5: shagvaladyan (450 in chips)
Seat 6: DiggErr555 (503 in chips)
vIpEr9427: posts the ante 3
Denisov V.: posts the ante 3
Chang Chi: posts the ante 3
sabuco_2110: posts the ante 3
shagvaladyan: posts the ante 3
DiggErr555: posts the ante 3
Denisov V.: posts small blind 15
Chang Chi: posts big blind 30
*** HOLE CARDS ***
Dealt to DiggErr555 [Jc 7d]
sabuco_2110: folds
shagvaladyan: folds
DiggErr555: folds
vIpEr9427: raises 491 to 521 and is all-in
Denisov V.: folds
Chang Chi: calls 192 and is all-in
Uncalled bet (299) returned to vIpEr9427
*** FLOP *** [5d Td 6d]
*** TURN *** [5d Td 6d] [Ad]
*** RIVER *** [5d Td 6d Ad] [Ts]
*** SHOW DOWN ***
Chang Chi: shows [4s 4d] (a flush, Ace high)
vIpEr9427: shows [Ah 8s] (two pair, Aces and Tens)
Chang Chi collected 477 from pot
*** SUMMARY ***
Total pot 477 | Rake 0
Board [5d Td 6d Ad Ts]
Seat 1: vIpEr9427 (button) showed [Ah 8s] and lost with two pair, Aces and Tens
Seat 2: Denisov V. (small blind) folded before Flop
Seat 3: Chang Chi (big blind) showed [4s 4d] and won (477) with a flush, Ace high
Seat 4: sabuco_2110 folded before Flop (didn't bet)
Seat 5: shagvaladyan folded before Flop (didn't bet)
Seat 6: DiggErr555 folded before Flop (didn't bet)
"""

th8 = """
PokerStars Hand #186690380861: Tournament #2311064390, $4.79+$4.79+$0.42 USD Hold'em No Limit - Level VIII (75/150) - 2018/05/21 17:40:26 MSK [2018/05/21 10:40:26 ET]
Table '2311064390 1' 6-max Seat #5 is the button
Seat 1: DiggErr555 (302 in chips)
Seat 4: LikeTonyG (2496 in chips)
Seat 5: SHAOLINWH (202 in chips)
DiggErr555: posts the ante 15
LikeTonyG: posts the ante 15
SHAOLINWH: posts the ante 15
DiggErr555: posts small blind 75
LikeTonyG: posts big blind 150
*** HOLE CARDS ***
Dealt to DiggErr555 [9c 3d]
SHAOLINWH: raises 37 to 187 and is all-in
DiggErr555: calls 112
LikeTonyG: raises 2294 to 2481 and is all-in
DiggErr555: calls 100 and is all-in
Uncalled bet (2194) returned to LikeTonyG
*** FLOP *** [3s 5c 5h]
*** TURN *** [3s 5c 5h] [Kh]
*** RIVER *** [3s 5c 5h Kh] [7s]
*** SHOW DOWN ***
DiggErr555: shows [9c 3d] (two pair, Fives and Threes)
LikeTonyG: shows [6c Kc] (two pair, Kings and Fives)
LikeTonyG collected 200 from side pot
SHAOLINWH: shows [9s Jd] (a pair of Fives)
LikeTonyG collected 606 from main pot
LikeTonyG wins the $4.79 bounty for eliminating DiggErr555
LikeTonyG wins the $4.79 bounty for eliminating SHAOLINWH
DiggErr555 finished the tournament in 2nd place and received $14.37.
SHAOLINWH finished the tournament in 3rd place
LikeTonyG wins the tournament and receives $14.37 - congratulations!
*** SUMMARY ***
Total pot 806 Main pot 606. Side pot 200. | Rake 0
Board [3s 5c 5h Kh 7s]
Seat 1: DiggErr555 (small blind) showed [9c 3d] and lost with two pair, Fives and Threes
Seat 4: LikeTonyG (big blind) showed [6c Kc] and won (806) with two pair, Kings and Fives
Seat 5: SHAOLINWH (button) showed [9s Jd] and lost with a pair of Fives
"""
th7 = """
PokerStars Hand #188547377183: Tournament #2352932023, $12.01+$12.01+$0.98 USD Hold'em No Limit - Level VIII (75/150) - 2018/07/10 1:04:19 MSK [2018/07/09 18:04:19 ET]
Table '2352932023 1' 6-max Seat #6 is the button
Seat 4: sabuco_2110 (834 in chips)
Seat 6: DiggErr555 (2166 in chips)
sabuco_2110: posts the ante 15
DiggErr555: posts the ante 15
DiggErr555: posts small blind 75
sabuco_2110: posts big blind 150
*** HOLE CARDS ***
Dealt to DiggErr555 [Ad 4h]
DiggErr555: raises 2001 to 2151 and is all-in
sabuco_2110: calls 669 and is all-in
Uncalled bet (1332) returned to DiggErr555
*** FLOP *** [3c 9h Jc]
*** TURN *** [3c 9h Jc] [2s]
*** RIVER *** [3c 9h Jc 2s] [7d]
*** SHOW DOWN ***
sabuco_2110: shows [Th Qs] (high card Queen)
DiggErr555: shows [Ad 4h] (high card Ace)
DiggErr555 collected 1668 from pot
DiggErr555 wins the $12.01 bounty for eliminating sabuco_2110
sabuco_2110 finished the tournament in 2nd place and received $36.03.
DiggErr555 wins the tournament and receives $36.03 - congratulations!
*** SUMMARY ***
Total pot 1668 | Rake 0
Board [3c 9h Jc 2s 7d]
Seat 4: sabuco_2110 (big blind) showed [Th Qs] and lost with high card Queen
Seat 6: DiggErr555 (button) (small blind) showed [Ad 4h] and won (1668) with high card Ace
"""
th8 = """
PokerStars Hand #188548991725: Tournament #2352974684, $4.79+$4.79+$0.42 USD Hold'em No Limit - Level I (10/20) - 2018/07/10 1:48:39 MSK [2018/07/09 18:48:39 ET]
Table '2352974684 1' 6-max Seat #3 is the button
Seat 1: DiggErr555 (496 in chips)
Seat 2: MichelGiang (568 in chips)
Seat 3: Karagunis (466 in chips)
Seat 4: Phil_hardy92 (478 in chips)
Seat 5: Hpak205 (496 in chips)
Seat 6: Luchok123 (496 in chips)
DiggErr555: posts the ante 2
MichelGiang: posts the ante 2
Karagunis: posts the ante 2
Phil_hardy92: posts the ante 2
Hpak205: posts the ante 2
Luchok123: posts the ante 2
Phil_hardy92: posts small blind 10
Hpak205: posts big blind 20
*** HOLE CARDS ***
Dealt to DiggErr555 [7h 9d]
Luchok123: folds
DiggErr555: folds
MichelGiang: folds
Karagunis: raises 20 to 40
Phil_hardy92: folds
Hpak205: calls 20
*** FLOP *** [Qs 4h 6h]
Hpak205: checks
Karagunis: bets 40
Hpak205: raises 182 to 222
Karagunis: raises 202 to 424 and is all-in
Hpak205: calls 202
*** TURN *** [Qs 4h 6h] [Ah]
*** RIVER *** [Qs 4h 6h Ah] [Qh]
*** SHOW DOWN ***
Hpak205: shows [Kc Qc] (three of a kind, Queens)
Karagunis: shows [4d 4s] (a full house, Fours full of Queens)
Karagunis collected 950 from pot
*** SUMMARY ***
Total pot 950 | Rake 0
Board [Qs 4h 6h Ah Qh]
Seat 1: DiggErr555 folded before Flop (didn't bet)
Seat 2: MichelGiang folded before Flop (didn't bet)
Seat 3: Karagunis (button) showed [4d 4s] and won (950) with a full house, Fours full of Queens
Seat 4: Phil_hardy92 (small blind) folded before Flop
Seat 5: Hpak205 (big blind) showed [Kc Qc] and lost with three of a kind, Queens
Seat 6: Luchok123 folded before Flop (didn't bet)
"""

class TestPokercalc(unittest.TestCase):
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
    def setUp(self):
        # self.cases = []
        # self.cases.append(hhparser.HHParser(th0))
        #
        # self.results = []
        # self.results.append({'test_chip_diff': {}})
        icm = pokercalc.Icm((0.5, 0.5))
        ko = pokercalc.Knockout(pokercalc.KOModels.PROPORTIONAL)
        self.case0 = pokercalc.EV(hhparser.HHParser(th0), icm, ko)
        self.case0.calc('DiggErr555')
        self.case1 = pokercalc.EV(hhparser.HHParser(th1), icm, ko)
        self.case1.calc('DiggErr555')
        self.case7 = pokercalc.EV(hhparser.HHParser(th7), icm, ko)
        self.case7.calc('DiggErr555')
        self.case8 = pokercalc.EV(hhparser.HHParser(th8), icm, ko)
        self.case8.calc('DiggErr555')
    #   HU allin preflop knock


    def test_equties(self):
        self.assertAlmostEqual(self.case1.equities.get('vIpEr9427'), 0.4600, delta=0.005)
        self.assertAlmostEqual(self.case7.equities.get('DiggErr555'), 0.5566, delta=0.005)
        self.assertAlmostEqual(self.case8.equities.get('Hpak205'), 0.02, delta=0.005)

    def test_chip_diff(self):
        chip_diff = self.case1.chip_diff
        # self.assertEqual(chip_diff,{'vIpEr9427': -6,
        #                             'Denisov V.': -18,
        #                             'Chang Chi': 33,
        #                             'sabuco_2110': -3,
        #                             'shagvaladyan': -3,
        #                             'DiggErr555': -3})

        self.assertAlmostEqual(sum(chip_diff.values()), 0, delta=0.001)

    def test_chip_win(self):
        pass

    def test_chip_lose(self):
        case = self.case7.chip_lose
        expected = {
            'sabuco_2110': 1668,
            'DiggErr555': 1332,
        }
        self.assertDictEqual(case, expected)


    def test_chip_fact(self):
        chip_fact = self.case1.chip_fact
        self.assertDictEqual(chip_fact, {'vIpEr9427': 299,
                                     'Denisov V.': 427,
                                     'Chang Chi': 477,
                                     'sabuco_2110': 850,
                                     'shagvaladyan': 447,
                                     'DiggErr555': 500})
        case = self.case7.chip_fact
        expected = {
            'sabuco_2110': 0,
            'DiggErr555': 3000,
        }
        chip_sum = pokercalc.EV.sum_dict_values(expected)
        self.assertDictEqual(case, expected)
        self.assertEqual(chip_sum, 3000, 'Chip sum should be 3000')

    def test_icm_fact_pct(self):
        icm_fact_pct = self.case1.icm_fact_pct
        # logger.debug(icm_fact_pct)
        self.assertEqual(icm_fact_pct, {'vIpEr9427': 0.1059,
                                        'Denisov V.': 0.1473,
                                        'Chang Chi': 0.1627,
                                        'sabuco_2110': 0.2608,
                                        'shagvaladyan': 0.1535,
                                        'DiggErr555': 0.1697})

    def test_icm_fact(self):
        icm_fact = self.case1.icm_fact
        # logger.debug(icm_fact)
        self.assertEqual(icm_fact, {'vIpEr9427': 7.63,
                                    'Denisov V.': 10.61,
                                    'Chang Chi': 11.72,
                                    'sabuco_2110': 18.79,
                                    'shagvaladyan': 11.06,
                                    'DiggErr555': 12.23})

    def test_icm_ev(self):
        case = self.case1
        res = case.icm_ev
        logger.debug(f'{case.hand.hid()}->{res}')
    #     self.assertEqual(res, {'vIpEr9427': 12.61,
    #                                 'Denisov V.': 10.63,
    #                                 'Chang Chi': 6.67,
    #                                 'sabuco_2110': 18.82,
    #                                 'shagvaladyan': 11.08,
    #                                 'DiggErr555': 12.24})

    def test_icm_ev_pct(self):
        case = self.case1
        res = case.icm_ev_pct
        logger.debug(f'{case.hand.hid()}->{res}')
    #     self.assertEqual(res, {'vIpEr9427': 0.175,
    #                                 'Denisov V.': 0.1475,
    #                                 'Chang Chi': 0.0926,
    #                                 'sabuco_2110': 0.2612,
    #                                 'shagvaladyan': 0.1538,
    #                                 'DiggErr555': 0.1699})

    def test_ko_ev_pct(self):
        case = self.case1
        res = case.ko_ev_pct
        logger.debug(f'{case.hand.hid()}->{res}')
    #     self.assertEqual(ko_ev_pct, {'vIpEr9427': 1.03,
    #                                     'Denisov V.': 0.85,
    #                                     'Chang Chi': 0.52,
    #                                     'sabuco_2110': 1.7,
    #                                     'shagvaladyan': 0.89,
    #                                     'DiggErr555': 1})

    def test_ko_ev(self):
        case = self.case1
        res = case.ko_ev
        logger.debug(f'{case.hand.hid()}->{res}')
    #     self.assertEqual(ko_ev, {'vIpEr9427': 12.43,
    #                                     'Denisov V.': 10.26,
    #                                     'Chang Chi': 6.21,
    #                                     'sabuco_2110': 20.42,
    #                                     'shagvaladyan': 10.74,
    #                                     'DiggErr555': 12.01})

    def test_ko_fact(self):
        ko_fact = self.case1.ko_fact
        # logger.debug(ko_fact)
        self.assertEqual(ko_fact, {'vIpEr9427': 7.18,
                                   'Denisov V.': 10.26,
                                   'Chang Chi': 11.46,
                                   'sabuco_2110': 20.42,
                                   'shagvaladyan': 10.74,
                                   'DiggErr555': 12.01})

    def test_ko_fact_pct(self):
        ko_fact_pct = self.case1.ko_fact_pct
        # logger.debug(ko_fact_pct)
        self.assertEqual(ko_fact_pct, {
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


# class TestStacksDict(unittest.TestCase):
#     def test_add(self):
#         di1 = pokercalc.StacksDict(int)
#         di1['a'] = 1
#         di1['b'] = 2
#
#         di2 = pokercalc.StacksDict(int)
#         di2['a'] = 10
#         di2['b'] = 20
#         di1['c'] = 30
#
#         di3 = di1+di2
#         logger.debug(di3)

if __name__ == '__main__':
    unittest.main()
