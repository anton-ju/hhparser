import unittest
import pokercalc

th = """
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

class TestPokercalc(unittest.TestCase):
    def test_icm(self):
        pc = pokercalc.Icm((0.5,0.5))

    def test_calc(self):
        icm_ko = pokercalc.Icm((0.5,0.5))
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

    def test__p1p(self):
        pass

if __name__ == '__main__':
    unittest.main()