# -*- coding: utf-8 -*-
"""
Created on Sat Jun  2 23:24:47 2018

@author: user
"""
import unittest
import logging
from parsers.hhparser import HHParser, TournamentSummary

from datetime import datetime
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

th10 = """
PokerStars Hand #194070989781: Tournament #2473317509, $12.01+$12.01+$0.98 USD Hold'em No Limit - Level VIII (75/150) - 2018/12/04 23:02:20 MSK [2018/12/04 15:02:20 ET]
Table '2473317509 1' 6-max Seat #2 is the button
Seat 2: FoodProm (46 in chips) is sitting out
Seat 5: DiggErr555 (2954 in chips)
FoodProm: posts the ante 15
DiggErr555: posts the ante 15
FoodProm: posts small blind 31 and is all-in
DiggErr555: posts big blind 150
*** HOLE CARDS ***
Dealt to DiggErr555 [5s Ts]
FoodProm: folds
Uncalled bet (119) returned to DiggErr555
DiggErr555 collected 92 from pot
DiggErr555 wins the $12.01 bounty for eliminating FoodProm
FoodProm finished the tournament in 2nd place and received $36.03.
DiggErr555 wins the tournament and receives $36.03 - congratulations!
DiggErr555: doesn't show hand
*** SUMMARY ***
Total pot 92 | Rake 0
Seat 2: FoodProm (button) (small blind) folded before Flop
Seat 5: DiggErr555 (big blind) collected (92)
"""

tts1 = """
PokerStars Tournament #2447891935, No Limit Hold'em
Buy-In: $48.04/$1.96 USD
6 players
Total Prize Pool: $144.12 USD 
Tournament started 2018/11/04 21:58:21 MSK [2018/11/04 13:58:21 ET]

  1: DiggErr555 (Russia), $72.06 (50%)
  2: Alex.i1off (Russia), $72.06 (50%)
  3: sdykuzbass (Russia), 
  4: Anhuhn (Germany), 
  5: Mailo2001 (Germany), 
  6: vjla (Belgium), 

You finished in 1st place (eliminated at hand #192956292599).

"""

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

th2 = """

PokerStars Hand #185633993066: Tournament #2288022169, $4.79+$4.79+$0.42 USD Hold'em No Limit - Level III (20/40) - 2018/04/24 17:00:00 ET
Table '2288022169 1' 6-max Seat #5 is the button
Seat 1: yaniw777 (851 in chips) 
Seat 2: Bee_Lou81 (1256 in chips) 
Seat 4: Archi801 (546 in chips) 
Seat 5: Garnas (347 in chips) 
yaniw777: posts the ante 4
Bee_Lou81: posts the ante 4
Archi801: posts the ante 4
Garnas: posts the ante 4
yaniw777: posts small blind 20
Bee_Lou81: posts big blind 40
*** HOLE CARDS ***
Archi801: folds 
Garnas: folds 
yaniw777: raises 40 to 80
Bee_Lou81: folds 
Uncalled bet (40) returned to yaniw777
yaniw777 collected 96 from pot
*** SUMMARY ***
Total pot 96 | Rake 0 
Seat 1: yaniw777 (small blind) collected (96)
Seat 2: Bee_Lou81 (big blind) folded before Flop
Seat 4: Archi801 folded before Flop (didn't bet)
Seat 5: Garnas (button) folded before Flop (didn't bet)


"""

th4 ="""
PokerStars Hand #187378182457: Tournament #2326475439, $12.01+$12.01+$0.98 USD Hold'em No Limit - Level I (10/20) - 2018/06/08 19:33:37 MSK [2018/06/08 12:33:37 ET]
Table '2326475439 1' 6-max Seat #3 is the button
Seat 1: yhterhulryk (518 in chips)
Seat 2: TH0090 (486 in chips)
Seat 3: DiggErr555 (446 in chips)
Seat 4: epsilonmi27 (558 in chips)
Seat 5: bull901 (496 in chips)
Seat 6: dini619 (496 in chips)
yhterhulryk: posts the ante 2
TH0090: posts the ante 2
DiggErr555: posts the ante 2
epsilonmi27: posts the ante 2
bull901: posts the ante 2
dini619: posts the ante 2
epsilonmi27: posts small blind 10
bull901: posts big blind 20
*** HOLE CARDS ***
Dealt to DiggErr555 [Ad 7h]
dini619: folds
yhterhulryk: folds
TH0090: folds
DiggErr555: raises 20 to 40
epsilonmi27: calls 30
bull901: folds
*** FLOP *** [5d 4d 4h]
epsilonmi27: checks
DiggErr555: bets 39
epsilonmi27: calls 39
*** TURN *** [5d 4d 4h] [2h]
epsilonmi27: checks
DiggErr555: checks
*** RIVER *** [5d 4d 4h 2h] [5c]
epsilonmi27: bets 180
DiggErr555: calls 180
*** SHOW DOWN ***
epsilonmi27: shows [Kd 9h] (two pair, Fives and Fours)
DiggErr555: shows [Ad 7h] (two pair, Fives and Fours - Ace kicker)
DiggErr555 collected 550 from pot
*** SUMMARY ***
Total pot 550 | Rake 0
Board [5d 4d 4h 2h 5c]
Seat 1: yhterhulryk folded before Flop (didn't bet)
Seat 2: TH0090 folded before Flop (didn't bet)
Seat 3: DiggErr555 (button) showed [Ad 7h] and won (550) with two pair, Fives and Fours
Seat 4: epsilonmi27 (small blind) showed [Kd 9h] and lost with two pair, Fives and Fours
Seat 5: bull901 (big blind) folded before Flop
Seat 6: dini619 folded before Flop (didn't bet)
"""

th5 = """
PokerStars Hand #186816489075: Tournament #2314060953, $24.02+$24.02+$1.96 USD Hold'em No Limit - Level I (10/20) - 2018/05/24 22:24:42 MSK [2018/05/24 15:24:42 ET]
Table '2314060953 1' 6-max Seat #1 is the button
Seat 1: muchpain (500 in chips)
Seat 2: IIackydal (500 in chips)
Seat 3: dimagog 434 (500 in chips)
Seat 4: DiggErr555 (500 in chips)
Seat 5: DaWmiZ (500 in chips)
Seat 6: Udodov1988 (500 in chips)
muchpain: posts the ante 2
IIackydal: posts the ante 2
dimagog 434: posts the ante 2
DiggErr555: posts the ante 2
DaWmiZ: posts the ante 2
Udodov1988: posts the ante 2
IIackydal: posts small blind 10
dimagog 434: posts big blind 20
*** HOLE CARDS ***
Dealt to DiggErr555 [Qc Kc]
DiggErr555: raises 20 to 40
DaWmiZ: folds
Udodov1988: calls 40
muchpain: folds
IIackydal has timed out
IIackydal: folds
IIackydal is sitting out
dimagog 434: folds
*** FLOP *** [Ac Jh Td]
IIackydal has returned
DiggErr555: bets 80
Udodov1988: raises 282 to 362
DiggErr555: raises 96 to 458 and is all-in
Udodov1988: calls 96 and is all-in
*** TURN *** [Ac Jh Td] [Kh]
*** RIVER *** [Ac Jh Td Kh] [7s]
*** SHOW DOWN ***
DiggErr555: shows [Qc Kc] (a straight, Ten to Ace)
Udodov1988: shows [8s Ah] (a pair of Aces)
DiggErr555 collected 1038 from pot
DiggErr555 wins the $24.02 bounty for eliminating Udodov1988
Udodov1988 finished the tournament in 6th place
*** SUMMARY ***
Total pot 1038 | Rake 0
Board [Ac Jh Td Kh 7s]
Seat 1: muchpain (button) folded before Flop (didn't bet)
Seat 2: IIackydal (small blind) folded before Flop
Seat 3: dimagog 434 (big blind) folded before Flop
Seat 4: DiggErr555 showed [Qc Kc] and won (1038) with a straight, Ten to Ace
Seat 5: DaWmiZ folded before Flop (didn't bet)
Seat 6: Udodov1988 showed [8s Ah] and lost with a pair of Aces
"""

th6 = """
PokerStars Hand #188404296549: Tournament #2349710032, $12.01+$12.01+$0.98 USD Hold'em No Limit - Level III (20/40) - 2018/07/06 3:22:54 MSK [2018/07/05 20:22:54 ET]
Table '2349710032 1' 6-max Seat #4 is the button
Seat 2: NL_Classic (518 in chips)
Seat 3: Mikson92 (399 in chips)
Seat 4: DiggErr555 (825 in chips)
Seat 5: zeus-yukiko (995 in chips)
Seat 6: alfpapa1992 (263 in chips)
NL_Classic: posts the ante 4
Mikson92: posts the ante 4
DiggErr555: posts the ante 4
zeus-yukiko: posts the ante 4
alfpapa1992: posts the ante 4
zeus-yukiko: posts small blind 20
alfpapa1992: posts big blind 40
*** HOLE CARDS ***
Dealt to DiggErr555 [Ac 5c]
NL_Classic: folds
Mikson92: folds
DiggErr555: raises 40 to 80
zeus-yukiko: folds
alfpapa1992: calls 40
*** FLOP *** [6c 2c 9c]
alfpapa1992: checks
DiggErr555: bets 70
alfpapa1992: calls 70
*** TURN *** [6c 2c 9c] [Qc]
alfpapa1992: checks
DiggErr555: bets 671 and is all-in
alfpapa1992: folds
Uncalled bet (671) returned to DiggErr555
DiggErr555 collected 340 from pot
DiggErr555: doesn't show hand
*** SUMMARY ***
Total pot 340 | Rake 0
Board [6c 2c 9c Qc]
Seat 2: NL_Classic folded before Flop (didn't bet)
Seat 3: Mikson92 folded before Flop (didn't bet)
Seat 4: DiggErr555 (button) collected (340)
Seat 5: zeus-yukiko (small blind) folded before Flop
Seat 6: alfpapa1992 (big blind) folded on the Turn
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

th9 = """
PokerStars Hand #193060609321: Tournament #2450141436, $2.38+$2.38+$0.24 USD Hold'em No Limit - Level II (15/30) - 2018/11/07 19:34:11 MSK [2018/11/07 11:34:11 ET]
Table '2450141436 1' 6-max Seat #6 is the button
Seat 1: saklari (560 in chips)
Seat 2: nikos98b (42 in chips)
Seat 3: DiggErr555 (1409 in chips)
Seat 5: HardnDeep (546 in chips)
Seat 6: BoOHP (443 in chips)
saklari: posts the ante 3
nikos98b: posts the ante 3
DiggErr555: posts the ante 3
HardnDeep: posts the ante 3
BoOHP: posts the ante 3
saklari: posts small blind 15
nikos98b: posts big blind 30
*** HOLE CARDS ***
Dealt to DiggErr555 [5c Ah]
DiggErr555: raises 1376 to 1406 and is all-in
HardnDeep: folds
BoOHP: calls 440 and is all-in
saklari: folds
nikos98b: calls 9 and is all-in
Uncalled bet (966) returned to DiggErr555
*** FLOP *** [Qd 7h 3d]
*** TURN *** [Qd 7h 3d] [Ac]
*** RIVER *** [Qd 7h 3d Ac] [8h]
*** SHOW DOWN ***
DiggErr555: shows [5c Ah] (a pair of Aces)
BoOHP: shows [9s Js] (high card Ace)
DiggErr555 collected 802 from side pot
nikos98b: shows [Ks 8c] (a pair of Eights)
DiggErr555 collected 147 from main pot
DiggErr555 wins the $2.38 bounty for eliminating nikos98b
DiggErr555 wins the $2.38 bounty for eliminating BoOHP
BoOHP finished the tournament in 4th place
nikos98b finished the tournament in 5th place
*** SUMMARY ***
Total pot 949 Main pot 147. Side pot 802. | Rake 0
Board [Qd 7h 3d Ac 8h]
Seat 1: saklari (small blind) folded before Flop
Seat 2: nikos98b (big blind) showed [Ks 8c] and lost with a pair of Eights
Seat 3: DiggErr555 showed [5c Ah] and won (949) with a pair of Aces
Seat 5: HardnDeep folded before Flop (didn't bet)
Seat 6: BoOHP (button) showed [9s Js] and lost with high card Ace"""


class TestHHParser(unittest.TestCase):
    def setUp(self):
        self.case0 = HHParser(th)
        # self.case1 = HHParser(th1)
        self.case2 = HHParser(th2)
        # self.case3 = HHParser(th3)
        self.case4 = HHParser(th4)
        self.case5 = HHParser(th5)
        self.case6 = HHParser(th6)
        self.case7 = HHParser(th7)
        self.case8 = HHParser(th8)
        self.case9 = HHParser(th9)  #2 bounty won case
        self.case10 = HHParser(th10) #3 bounty won case

    def test_datetime(self):
        hh = self.case0
        dt = hh.datetime
        self.assertEqual(dt, datetime(2018, 2, 11, 20, 32, 33))
        


    def test_tid(self):
        hh = self.case0
        tid = hh.tid
        self.assertEqual(tid, '2216721390')
        
        
    def test_hid(self):
        hh = self.case0
        hid = hh.hid
        self.assertEqual(hid, '182384621288')
 

    def test_isKnockoutTournament(self):
        hh= self.case2
        flg = hh.flg_knockout()
        self.assertEqual(flg, True)
        
    def test_bi(self):
        hh = self.case2
        bi = hh.bi
        self.assertEqual(bi, 10)
        
        hh = self.case4
        bi = hh.bi
        self.assertEqual(bi, 25)
        
        

    def test_p_actions(self):
        case = self.case0.p_actions
        res = {
            'da_mauso': ['r', 'f'],
            'baluoteli': ['c'],
            'DiggErr555': ['r'],
            'bigboyby': ['r'],
            '2Ran128': ['f'],
            'zaxar393': ['c', 'c'],
        }
        self.assertDictEqual(case, res)

    def test_f_actions(self):
        case = self.case4.f_actions
        res = {
            'epsilonmi27': ['x', 'c'],
            'DiggErr555': ['b']
        }
        self.assertDictEqual(case, res)

        case = self.case0.f_actions
        res = {}
        self.assertDictEqual(case, res)

    def test_last_actions(self):
        case = self.case0.last_actions()
        res = {
            'da_mauso': ['r', 'f'],
            'baluoteli': ['c'],
            'DiggErr555': ['r'],
            'bigboyby': ['r'],
            '2Ran128': ['f'],
            'zaxar393': ['c', 'c'],
        }
        self.assertDictEqual(case, res)

        case = self.case4.last_actions()
        res = {
            'epsilonmi27': ['b'],
            'DiggErr555': ['c']
        }
        self.assertDictEqual(case, res)

    def test_p_actions_amounts(self):
        case = self.case0.p_actions_amounts
        res = {
            "zaxar393": [20, 474],
            "da_mauso": [40],
            "baluoteli": [18],
            "DiggErr555": [464],
            "bigboyby": [566]
        }

        self.assertDictEqual(case, res)

        case = self.case2.p_actions_amounts
        res = {
            "yaniw777": [80]
        }
        self.assertDictEqual(case, res)


        case = self.case4.p_actions_amounts
        res = {
            "DiggErr555": [40],
            "epsilonmi27": [30]
        }
        self.assertDictEqual(case, res)

    def test_f_actions_amounts(self):
        case = self.case4.f_actions_amounts
        res = {
            "DiggErr555": [39],
            "epsilonmi27": [39]
        }
        self.assertDictEqual(case, res)

    def test_t_actions_amounts(self):
        case = self.case6.t_actions_amounts
        res = {
            "DiggErr555": [671]
        }
        self.assertDictEqual(case, res)

    def test_r_actions_amounts(self):
        case = self.case4.r_actions_amounts
        res = {
            "epsilonmi27": [180],
            "DiggErr555": [180]
        }
        self.assertDictEqual(case, res)

    def test_total_bets_amounts(self):
        case = self.case0.total_bets_amounts()
        res = {
            'da_mauso': 42,
            'baluoteli': 20,
            'DiggErr555': 466,
            'bigboyby': 568,
            '2Ran128': 22,
            'zaxar393': 496,
        }
        self.assertDictEqual(case, res)

        case = self.case4.total_bets_amounts()
        res = {
            'yhterhulryk': 2,
            'TH0090': 2,
            'DiggErr555': 261,
            'epsilonmi27': 261,
            'bull901': 22,
            'dini619': 2,
        }
        self.assertDictEqual(case, res)

    def test_p_ai_players(self):
           
        hh = self.case4
        players = hh.p_ai_players
        self.assertEqual(players, [])
        
        hh = self.case2
        players = hh.p_ai_players
        self.assertEqual(players, [])
        
        hh = self.case0
        players = hh.p_ai_players
        self.assertEqual(players, ['baluoteli', 'DiggErr555','bigboyby','zaxar393']) 
    
    def test_pot_list(self):
        hh = self.case4
        PotList = hh.pot_list
        self.assertEqual(PotList, [550])
        
        hh = self.case2
        PotList = hh.pot_list
        self.assertEqual(PotList, [96])

        hh = self.case0
        PotList = hh.pot_list
        self.assertEqual(PotList, [1542, 120, 1362, 60])
        

    def test_hero(self):
        hh = self.case4
        hero = hh.hero
        self.assertEqual(hero, "DiggErr555") 
        
        hh = self.case2
        hero = hh.hero
        self.assertEqual(hero, 0)

    def test_hero_cards(self):
        hh = self.case4
        herocards = hh.hero_cards
        self.assertEqual(herocards, "Ad 7h")
        
        hh = self.case0
        herocards = hh.hero_cards
        self.assertEqual(herocards, "As Ad")
        
        hh = self.case2
        herocards = hh.hero_cards
        self.assertEqual(herocards, 0)
    
    def test_known_cards(self):
        hh = self.case4
        knowncards = hh.known_cards
        self.assertEqual(knowncards, {"DiggErr555": "Ad 7h", "epsilonmi27": "Kd 9h"})
        
        hh = self.case0
        knowncards = hh.known_cards
        self.assertEqual(knowncards, {"baluoteli": "Jd Qs", "DiggErr555": "As Ad", "bigboyby": "5d 5h", "zaxar393": "9d Kd"})
        
        hh = self.case2
        knowncards = hh.known_cards
        self.assertEqual(knowncards, {})       
        hh = self.case7
        knowncards = hh.known_cards
        self.assertEqual(knowncards, {"DiggErr555": "Ad 4h", "sabuco_2110": "Th Qs"})
        
        
    
    def test_getFlop(self):
        
        hh = self.case0
        flop = hh.flop
        self.assertEqual(flop, "3s 2h 7c")
        
        hh = self.case2
        flop = hh.flop
        self.assertEqual(flop, 0)
        
        hh = self.case4
        flop = hh.flop
        self.assertEqual(flop, "5d 4d 4h")

    
    def test_getTurn(self):
        
        hh = self.case0  
        self.assertEqual(hh.turn, "Jh")
        
        hh = self.case2
        self.assertEqual(hh.turn, 0)
        
        hh = self.case4
        self.assertEqual(hh.turn, "2h")
    
    def test_getRiver(self):
        
        hh = self.case0  
        self.assertEqual(hh.river, "Ks")
        
        hh = self.case2
        self.assertEqual(hh.river, 0)
        
        hh = self.case4
        self.assertEqual(hh.river, "5c")
        

    # def test_getWinnings(self):
    #     hh = self.case0
    #     res = hh.getWinnings()
    #     self.assertEqual(res, {"DiggErr555": 4.79})
    #
    #     hh = self.case2
    #     res = hh.getWinnings()
    #     self.assertEqual(res, {})
    #
    #     hh = self.case4
    #     res = hh.getWinnings()
    #     self.assertEqual(res, {})
    
    def test_chip_won(self):
        hh = self.case2
        res = hh.chip_won
        self.assertEqual(res, {'yaniw777': [96]})

        hh = self.case0
        res = hh.chip_won
        self.assertEqual(res, {'DiggErr555': [1362, 120], 'zaxar393': [60]})

        hh = self.case4
        res = hh.chip_won
        self.assertEqual(res, {'DiggErr555': [550]})
        
    
    def test_tournamentPosition(self):
        hh = self.case0

        self.assertEqual(hh.tournamentPosition("DiggErr555"), 5)
        self.assertEqual(hh.tournamentPosition("baluoteli"), 6)
        self.assertEqual(hh.tournamentPosition("da_mauso"), 1)
        self.assertEqual(hh.tournamentPosition("bigboyby"), 2)
        self.assertEqual(hh.tournamentPosition("2Ran128"), 3)
        self.assertEqual(hh.tournamentPosition("zaxar393"), 3)#todo
        self.assertEqual(hh.tournamentPosition("error"), -1)#todo

    def test_stacks(self):
        hh = self.case0
        self.assertEqual(hh.stacks(), {'da_mauso': 954,
                                          'baluoteli': 20,
                                          'DiggErr555': 466,
                                          'bigboyby': 568,
                                          '2Ran128': 496,
                                          'zaxar393': 496})

        hh = self.case7
        self.assertEqual(hh.stacks(),{'sabuco_2110': 834,
                                         'DiggErr555': 2166})
    def test_blinds_antes(self):        
        self.assertEqual(self.case0.blinds_antes, {'da_mauso': 2,
                                          'baluoteli': 2,
                                          'DiggErr555': 2,
                                          'bigboyby': 12,
                                          '2Ran128': 22,
                                          'zaxar393': 2})
        hh = self.case7
        self.assertEqual(self.case7.blinds_antes, {'sabuco_2110': 165,
                                              'DiggErr555': 90})
    def test_uncalled(self):
        hh = self.case0
        self.assertEqual(hh.uncalled, {'bigboyby': 72,})
        hh = self.case2
        self.assertEqual(hh.uncalled, {'yaniw777': 40,})
        hh = self.case4
        self.assertEqual(hh.uncalled, {})
        hh = self.case6
        self.assertEqual(hh.uncalled, {'DiggErr555': 671,})

    def test_prize_won(self):
        hh = self.case7
        self.assertEqual(hh.prize_won, {'sabuco_2110': 36.03,
                                            'DiggErr555': 36.03})

    def test_bounty_won(self):
        hh = self.case7
        self.assertEqual(hh.bounty_won, {'DiggErr555': 24.02})
        hh = self.case6
        self.assertEqual(hh.bounty_won, {})
        hh = self.case5
        self.assertEqual(hh.bounty_won, {'DiggErr555': 24.02})
        hh = self.case0
        self.assertEqual(hh.bounty_won, {'DiggErr555': 4.79})
        hh = self.case9
        self.assertEqual(hh.bounty_won, {'DiggErr555': 4.76})
        hh = self.case10
        self.assertEqual(hh.bounty_won, {'DiggErr555': 24.02})

    def test_finishes(self):

        hh = self.case8
        self.assertEqual(hh.finishes, {'DiggErr555': 2,
                                            'SHAOLINWH': 3,
                                         'LikeTonyG': 1})
        hh = self.case7
        self.assertEqual(hh.finishes, {'sabuco_2110': 2,
                                            'DiggErr555': 1})

        hh = self.case10
        self.assertEqual(hh.finishes, {'FoodProm': 2, 'DiggErr555': 1})


    def test_icm_eq(self):
        hh = self.case8
        self.assertDictEqual(hh.icm_eq_dict(), {'DiggErr555': 0.3032,
                                            'SHAOLINWH': 0.2042,
                                         'LikeTonyG': 0.4926})
        hh = self.case7
        self.assertDictEqual(hh.icm_eq_dict(), {'sabuco_2110': 0.500,
                                            'DiggErr555': 0.500})
        hh = self.case0
        self.assertDictEqual(hh.icm_eq_dict(), {'da_mauso': 0.2894,
                                           'DiggErr555': 0.1633,
                                           'baluoteli': 0.0076,
                                           'bigboyby': 0.1944,
                                           '2Ran128': 0.1727,
                                            'zaxar393': 0.1727})
    def test_positions(self):
        hh = self.case8
        self.assertDictEqual(hh.positions(), {'DiggErr555': 'SB',
                                            'SHAOLINWH': 'BU',
                                         'LikeTonyG': 'BB'})
        hh = self.case7
        self.assertDictEqual(hh.positions(), {'sabuco_2110': 'BB',
                                            'DiggErr555': 'SB'})

        hh = self.case0
        self.assertDictEqual(hh.positions(), {'da_mauso': 'MP2',
                                           'DiggErr555': 'BU',
                                           'baluoteli': 'CO',
                                           'bigboyby': 'SB',
                                           '2Ran128': 'BB',
                                            'zaxar393': 'MP1'})


    def test_tablePosition(self):
       # hh = self.case0
       # self.assertEqual(hh.tablePosition("DiggErr555"), 2)
        pass

    def test_antes(self):
        self.assertDictEqual(self.case0.antes, {'da_mauso': 2,
                                           'DiggErr555': 2,
                                           'baluoteli': 2,
                                           'bigboyby': 2,
                                           '2Ran128': 2,
                                            'zaxar393': 2})

    def test_blinds(self):
        self.assertDictEqual(self.case0.blinds, {'bigboyby': 10,
                                                   '2Ran128': 20})

    def test_flg_showdown(self):
        case = self.case0.flg_showdown()
        res = True
        self.assertEqual(case, res)

        case = self.case2.flg_showdown()
        res = False
        logging.debug(self.case2.showdown_str)
        self.assertEqual(case, res)



    def test_flg_chiplead(self):
        pass


    def test_tournamentPositionL(self): 
        pass
        
    def test_getStack(self):
        pass
        
        
    def test_stacks(self):
        pass
        
        
    def test_flg_chiplead_left(self):
        pass

        
    def test_players_number(self):
        pass
        
    def test_isKnockoutTournament(self):
        pass
        
    def test_getStackDict(self):
        pass
        
    def test_getBlinds(self):
        pass
        
    def test_flgRFIOpp(self):
        pass
        
    
    def test_flgFacedAI(self):
        pass

    def test_p_last_action(self):
        case = self.case0.p_last_action()
        res = {
            'da_mauso': 'f',
            'baluoteli': 'c',
            'DiggErr555': 'r',
            'bigboyby': 'r',
            '2Ran128': 'f',
            'zaxar393': 'c',
        }
        self.assertDictEqual(case, res)

    def test_f_last_action(self):
        case = self.case4.f_last_action()
        res = {
            'epsilonmi27': 'c',
            'DiggErr555': 'b'
        }

    def test_t_last_action(self):
        pass

    def test_r_last_action(self):
        pass


class TestTournamentSummary(unittest.TestCase):
    def setUp(self):
        self.case0 = TournamentSummary(tts1)

    def test_tid(self):
        ts = self.case0
        tid = ts.tid
        self.assertEqual(tid, '2447891935')

    def test_finishes(self):
        ts = self.case0
        finishes = ts.finishes
        self.assertEqual(finishes, 1)

    def test_prize_won(self):
        ts = self.case0
        res = ts.prize_won
        self.assertEqual(res, {'DiggErr555': 72.06, 'Alex.i1off': 72.06})

    def test__str__(self):
        ts = self.case0
        res = ts.__str__()
        self.assertEqual(res,f"Tournament: #{ts.tid} Finish: {ts.finishes} Prize:{ts.prize_won}")

if __name__ == '__main__':
    unittest.main()
