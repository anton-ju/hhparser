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
        if  len(aiplayers) >= 2: 
            cards = hand.getKnownCards() 
            hand1 = cards.get(aiplayers[0])
            print(cards)
#             for player in aiplayers:
#                cards = hand.getKnownCards()
#                hand1 = cards.get(player)
#                stack1 = hand.getStack(cards[0])
#            hand = map(eval7.Card, (cards[0][:2], cards[0][2:]))
#            villian = eval7.HandRange(cards[1])
#            print(f'Hero: {cards[0]}\n')
#            print(f'Villian: {cards[1]}\n')
#            board = []
#            equity = eval7.py_hand_vs_range_monte_carlo(
#            hand, villian, board, 100000
#            )
#            print(equity * hand.getStack(cards[0]))