# -*- coding: utf-8 -*-
"""
Created on Fri Jul 13 01:06:17 2018

@author: user
"""
import os
from hand_storage import HandStorage
import hhparser as hh
import eval7

hs = HandStorage('/home/ant/evroi/hhparser/')

for history in hs.read_hand():
    hand = hh.HHParser(history)
    if hand.getPlayersNumber() == 2:
        aiplayers = hand.getPAIPlayers()
#hu
        if  len(aiplayers) == 2: 
            cards = hand.getKnownCards() 
#            print(cards)
            hand1 = cards.get(aiplayers[0])
            hand2 = cards.get(aiplayers[1])
            stack1 = hand.getStack(aiplayers[0])
            stack2 = hand.getStack(aiplayers[1])
            hand1 = map(eval7.Card, (hand1[:2], hand1[2:]))
            hand2 = eval7.HandRange(hand2)
            board = []
            equity = eval7.py_hand_vs_range_monte_carlo(
            hand1, hand2, board, 100000
            )
            eq = {aiplayers[0]: equity, aiplayers[1]: 1-equity}
#            print(eq)
            pot = hand.getPotList()
#            print(pot)
            exp_chips = {aiplayers[0]: round(equity*pot[0]), 
                         aiplayers[1]: round((1-equity)*pot[0])}
#            print(exp_chips)
            winnings_chips = hand.getChipWon()
            loose_chips = hand.getPActionsAmount()
            chips = hand.getStacks()
            bets_before = hand.getBlidnsAnte()
            bets_preflop = hand.getPActionsAmount()
            bets_flop = hand.getFActionsAmount()
            bets_turn = hand.getTActionsAmount()
            bets_river= hand.getRActionsAmount()
            uncalled = hand.getUncalled()

            fact_chips = {}

            player_pos = {hand.preflop_order[::-1][i]: 
                hand.POSITIONS[i] for i in range(len(hand.preflop_order))}
            fact_chips = {player: chips[player] - 
                          bets_before.get(player,0) - 
                          sum(bets_preflop.get(player,[0])) - 
                          sum(bets_flop.get(player,[0])) - 
                          sum(bets_turn.get(player,[0])) -
                          sum(bets_river.get(player,[0])) +
                          winnings_chips.get(player,0) +
                          uncalled.get(player, 0) +
                          (player_pos.get(player,0)=='SB')*hand.sb for player in aiplayers
                    }
            print(fact_chips)
            icm_exp_dict = hand.icm_eq(list(exp_chips.values()))
            icm_exp = {hand.icm_eq(list(exp_chips.values()))*(hand.bi-hand.rake)*6/2 for i in aiplayers}
            ko_exp = [(hand.getPlayersNumber()*chips[p])/3000 for p in aiplayers]
            ko_exp = [ko_exp[_] * hand.bounty for _ in range(len(ko_exp))]
            icm_fact = hand.getPrizeWon() or hand.icm_eq()
            ko_fact = hand.getBountyWon()
            finish = hand.getFinishes()
            for ko in ko_fact.keys():
                if finish[ko]==None: #player finishes 1st place gets his own bounty
                    ko_fact[ko] = ko_fact[ko]*2 
            print(finish)
#            print(icm_exp)
            print(ko_exp)
            print(icm_fact)
            print(ko_fact)
            
            
            
 