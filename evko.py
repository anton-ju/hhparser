# -*- coding: utf-8 -*-
"""
Created on Fri Jul 13 01:06:17 2018

@author: user
"""
import os
from hand_storage import HandStorage
import hhparser as hh
import eval7
import pokercalc as pc
import logging

logging.basicConfig(level = logging.DEBUG)
logger = logging.getLogger(__name__)

hs = HandStorage('/home/ant/evroi/hhparser/hands/debug')
icm = pc.Icm((0.5,0.5))
total_diff = []
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
            exp_chips = {aiplayers[0]: round(equity*pot[0] + uncalled.get(aiplayers[0], 0)), 
                         aiplayers[1]: round((1-equity)*pot[0] + uncalled.get(aiplayers[1], 0))}
            fact_chips = {}

            player_pos = hand.positions()
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

            icm_exp_dict = icm.calc(exp_chips)
            icm_exp = {key: value * (hand.bi - hand.rake)*6/2 for key,value in icm_exp_dict.items()}
#            icm_exp = {hand.icm_eq(list(exp_chips.values()))*(hand.bi-hand.rake)*6/2 for i in aiplayers}
            ko_exp = {p: hand.bounty*(hand.getPlayersNumber()*chips[p])/3000 for p in aiplayers}
#            ko_exp = [ko_exp[_] * hand.bounty for _ in range(len(ko_exp))]
            icm_fact = hand.getPrizeWon() or hand.icm_eq_dict()
            ko_fact = hand.getBountyWon()#todo ko_fact
            finish = hand.getFinishes()
            for ko in ko_fact.keys():
                if finish[ko]==None: #player finishes 1st place gets his own bounty
                    ko_fact[ko] = ko_fact[ko]*2 

#            logger.debug(type(ko_fact))
            logger.debug(f'eq - {eq}')
            logger.debug(f'pot - {pot}')
            logger.debug(f'exp_chips - {exp_chips}')
            logger.debug(f'winnings_chips - {winnings_chips}')
            logger.debug(f'loose_chips - {loose_chips}')
            logger.debug(f'chips - {chips}')
            logger.debug(f'bets_before - {bets_before}')
            logger.debug(f'bets_preflop - {bets_preflop}')
            logger.debug(f'uncalled - {uncalled}')
            logger.debug(f'fact_chips - {fact_chips}')
            logger.debug(f'icm_exp - {icm_exp}')
            logger.debug(f'ko_exp - {ko_exp}')
            logger.debug(f'icm_fact - {icm_fact}')
            logger.debug(f'ko_fact - {ko_fact}')
            logger.debug(f'finish - {ko_fact}')
            
            
            
            li = []
            for p in aiplayers:
                
                li.append(hand.getTournamentID())
                li.append(p)
                li.append(round(icm_exp.get(p, 0)
                        - icm_fact.get(p, 0)
                        + ko_exp.get(p, 0)
                        - ko_fact.get(p, 0), 2))
            total_diff.append(li)
            
#            logger.info(total_diff)
                
print(total_diff)
            
            
            
 