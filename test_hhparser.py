# -*- coding: utf-8 -*-
"""
Created on Sat Jun  2 23:24:47 2018

@author: user
"""
import importlib
import unittest

from hhparser import HHParser

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


class TestHHParser(unittest.TestCase):
    def test_getDateTimeET(self):
        hh = HHParser(th)
        dt = hh.getDateTimeET()
        self.assertEqual(dt, '2018/02/11 20:32:33')
        


    def test_getTournamentID(self):
        hh = HHParser(th)
        tid = hh.getTournamentID()
        self.assertEqual(tid, '2216721390')
        
        
    def test_getHandID(self):
        hh = HHParser(th)
        hid = hh.getHandID()
        self.assertEqual(hid, '182384621288')
 

    def test_isKnockoutTournament(self):
        hh= HHParser(th2)
        flg = hh.isKnockoutTournament()
        self.assertEqual(flg, True)
        
    def test_getBI(self):
        hh = HHParser(th2)
        bi = hh.getBI()
        self.assertEqual(bi, 10)
        
        hh = HHParser(th4)
        bi = hh.getBI()
        self.assertEqual(bi, 25)
        
        
    def test_getPActions(self):
        hh = HHParser(th4)
        actions = hh.getPActions()
        self.assertEqual(actions, ['f','f','f','r','c','f']) 
        
        hh = HHParser(th)
        actions = hh.getPActions()
        self.assertEqual(actions, ['c','r','c','r','r','f','c','f']) 
        
        hh = HHParser(th2)
        actions = hh.getPActions()
        self.assertEqual(actions, ['f','f','r','f']) 
    
    def test_getFActions(self):
       
        hh = HHParser(th4)
        actions = hh.getFActions()
        self.assertEqual(actions, ['x', 'b', 'c']) 
        
        hh = HHParser(th)
        actions = hh.getFActions()
        self.assertEqual(actions, []) 
        
        hh = HHParser(th2)
        actions = hh.getFActions()
        self.assertEqual(actions, []) 
        
    def test_getTActions(self):
           
        hh = HHParser(th4)
        actions = hh.getTActions()
        self.assertEqual(actions, ['x', 'x']) 
        
        hh = HHParser(th)
        actions = hh.getTActions()
        self.assertEqual(actions, []) 
        
        hh = HHParser(th2)
        actions = hh.getTActions()
        self.assertEqual(actions, []) 
            
    def test_getRActions(self):
           
        hh = HHParser(th4)
        actions = hh.getRActions()
        self.assertEqual(actions, ['b', 'c']) 
        
        hh = HHParser(th)
        actions = hh.getRActions()
        self.assertEqual(actions, []) 
        
        hh = HHParser(th2)
        actions = hh.getRActions()
        self.assertEqual(actions, []) 
    
    
    def test_getPAIPlayers(self):
           
        hh = HHParser(th4)
        players = hh.getPAIPlayers()
        self.assertEqual(players, []) 
        
        hh = HHParser(th2)
        players = hh.getPAIPlayers()
        self.assertEqual(players, []) 
        
        hh = HHParser(th)
        players = hh.getPAIPlayers()
        self.assertEqual(players, ['baluoteli', 'DiggErr555','bigboyby','zaxar393']) 
    
    def test_getPotList(self):
        hh = HHParser(th4)
        PotList = hh.getPotList()
        self.assertEqual(PotList, [550.0]) 
        
        hh = HHParser(th2)
        PotList = hh.getPotList()
        self.assertEqual(PotList, [96.0]) 

        hh = HHParser(th)
        PotList = hh.getPotList()
        self.assertEqual(PotList, [1542.0, 120.0, 1362.0, 60]) 
        
    def test_getPActionsAmount(self):

        hh = HHParser(th)
        res = hh.getPActionsAmount()
        self.assertEqual(res, {"zaxar393": [20, 474], "da_mauso": [40],"baluoteli":[18],  "DiggErr555": [464], "bigboyby": [566]})
        
        hh = HHParser(th2)
        res = hh.getPActionsAmount()
        self.assertEqual(res, {"yaniw777": [80]})
        
        hh = HHParser(th4)
        res = hh.getPActionsAmount()
        self.assertEqual(res, {"DiggErr555": [40], "epsilonmi27": [30]})         

    def test_getFActionsAmount(self):

        hh = HHParser(th)
        res = hh.getFActionsAmount()
        self.assertEqual(res, {})
        
        hh = HHParser(th2)
        res = hh.getFActionsAmount()
        self.assertEqual(res, {})
        
        hh = HHParser(th4)
        res = hh.getFActionsAmount()
        self.assertEqual(res, {"DiggErr555": [39], "epsilonmi27": [39]})
        
        hh = HHParser(th5)
        res = hh.getFActionsAmount()
        self.assertEqual(res, {"DiggErr555": [80, 458], "Udodov1988": [362, 96]})
    
    def test_getTActionsAmount(self):
        
        hh = HHParser(th)
        res = hh.getTActionsAmount()
        self.assertEqual(res, {})
        
        hh = HHParser(th2)
        res = hh.getTActionsAmount()
        self.assertEqual(res, {})
        
        hh = HHParser(th6)
        res = hh.getTActionsAmount()
        self.assertEqual(res, {"DiggErr555": [671]})
    
    def test_getRActionsAmount(self):
       
        hh = HHParser(th)
        res = hh.getRActionsAmount()
        self.assertEqual(res, {})
        
        hh = HHParser(th2)
        res = hh.getRActionsAmount()
        self.assertEqual(res, {})
        
        hh = HHParser(th4)
        res = hh.getRActionsAmount()
        self.assertEqual(res, {"epsilonmi27": [180], "DiggErr555": [180]})

    
    def test_getHero(self):
        hh = HHParser(th4)
        hero = hh.getHero()
        self.assertEqual(hero, "DiggErr555") 
        
        hh = HHParser(th2)
        hero = hh.getHero()
        self.assertEqual(hero, "") 

    def test_getHeroCards(self):
        hh = HHParser(th4)
        herocards = hh.getHeroCards()
        self.assertEqual(herocards, "Ad7h") 
        
        hh = HHParser(th)
        herocards = hh.getHeroCards()
        self.assertEqual(herocards, "AsAd")
        
        hh = HHParser(th2)
        herocards = hh.getHeroCards()
        self.assertEqual(herocards, "") 
    
    def test_getKnownCards(self):
        hh = HHParser(th4)
        knowncards = hh.getKnownCards()
        self.assertEqual(knowncards, {"DiggErr555": "Ad7h", "epsilonmi27": "Kd9h"})
        
        hh = HHParser(th)
        knowncards = hh.getKnownCards()
        self.assertEqual(knowncards, {"baluoteli": "JdQs", "DiggErr555": "AsAd", "bigboyby": "5d5h", "zaxar393": "9dKd"})
        
        hh = HHParser(th2)
        knowncards = hh.getKnownCards()
        self.assertEqual(knowncards, {})       
        hh = HHParser(th7)
        knowncards = hh.getKnownCards()
        self.assertEqual(knowncards, {"DiggErr555": "Ad4h", "sabuco_2110": "ThQs"})
        
        
    
    def test_getFlop(self):
        
        hh = HHParser(th)
        flop = hh.getFlop()
        self.assertEqual(flop, "3s2h7c") 
        
        hh = HHParser(th2)
        flop = hh.getFlop()
        self.assertEqual(flop, "") 
        
        hh = HHParser(th4)
        flop = hh.getFlop()
        self.assertEqual(flop, "5d4d4h") 

    
    def test_getTurn(self):
        
        hh = HHParser(th)  
        self.assertEqual(hh.getTurn(), "Jh") 
        
        hh = HHParser(th2)
        self.assertEqual(hh.getTurn(), "") 
        
        hh = HHParser(th4)
        self.assertEqual(hh.getTurn(), "2h") 
    
    def test_getRiver(self):
        
        hh = HHParser(th)  
        self.assertEqual(hh.getRiver(), "Ks") 
        
        hh = HHParser(th2)
        self.assertEqual(hh.getRiver(), "") 
        
        hh = HHParser(th4)
        self.assertEqual(hh.getRiver(), "5c") 
        

    def test_getWinnings(self):
        hh = HHParser(th)
        res = hh.getWinnings()
        self.assertEqual(res, {"DiggErr555": 4.79})
        
        hh = HHParser(th2)
        res = hh.getWinnings()
        self.assertEqual(res, {})
        
        hh = HHParser(th4)
        res = hh.getWinnings()
        self.assertEqual(res, {}) 
    
    def test_getChipWinnings(self):
        hh = HHParser(th)
        res = hh.getChipWinnings()
        self.assertEqual(res, {"DiggErr555": 1482, "zaxar393": 60})
        
        hh = HHParser(th2)
        res = hh.getChipWinnings()
        self.assertEqual(res, {"yaniw777": 96})
        
        hh = HHParser(th4)
        res = hh.getChipWinnings()
        self.assertEqual(res, {"DiggErr555": 550}) 
        
    
    def test_tournamentPosition(self):
        hh = HHParser(th)

        self.assertEqual(hh.tournamentPosition("DiggErr555"), 5)
        self.assertEqual(hh.tournamentPosition("baluoteli"), 6)
        self.assertEqual(hh.tournamentPosition("da_mauso"), 1)
        self.assertEqual(hh.tournamentPosition("bigboyby"), 2)
        self.assertEqual(hh.tournamentPosition("2Ran128"), 3)
        self.assertEqual(hh.tournamentPosition("zaxar393"), 3)#todo
        self.assertEqual(hh.tournamentPosition("error"), -1)#todo

    def test_getStacks(self):
        hh = HHParser(th)
        self.assertEqual(hh.getStacks(), {'da_mauso': 954,
                                          'baluoteli': 20,
                                          'DiggErr555': 466,
                                          'bigboyby': 568,
                                          '2Ran128': 496,
                                          'zaxar393': 496})

        hh = HHParser(th7)
        self.assertEqual(hh.getStacks(),{'sabuco_2110': 834,
                                         'DiggErr555': 2166})
        
    
    def test_tablePosition(self):
        
#        hh = HHParser(th)
#        self.assertEqual(hh.tablePosition("DiggErr555"), 2)
        pass
    
    def test_isChipLeader(self):
        pass


    def test_tournamentPositionL(self): 
        pass
        
    def test_getStack(self):
        pass
        
        
    def test_getStackList(self):
        pass
        
        
    def test_isChipLeaderL(self):
        pass

        
    def test_getPlayersNumber(self):
        pass
        
    def test_getPlayerDict(self):
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

if __name__ == '__main__':
    unittest.main()
