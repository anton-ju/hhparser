# -*- coding: utf-8 -*-
"""
Created on Fri Jul 13 01:06:17 2018

@author: user
"""
from storage.hand_storage import HandStorage
from parsers import hhparser as hh
from calc import pokercalc as pc
import logging

logging.basicConfig(level = logging.INFO)
logger = logging.getLogger(__name__)

# hs = HandStorage('hands/debug/test_hand')
hs = HandStorage('hands/10')
icm = pc.Icm((0.50, 0.50))
ko = pc.Knockout(pc.KOModels.PROPORTIONAL)
diff_list = []
player = 'DiggErr555'
# player = 'Paartje2en'
for history in hs.read_hand():
    hand = hh.HHParser(history)
    # if hand.players_number() == 2:
    aiplayers = hand.p_ai_players() + hand.f_ai_players() + hand.t_ai_players() + hand.r_ai_players()
    # aiplayers
#         case only for preflop allins
#     print(hand.bi())
    if aiplayers and hand.flg_showdown():
        ev = pc.EV(hand, icm, ko)
        ev.calc(player)
        eq = ev.equities.get(player,0)
        chip_diff = ev.chip_diff.get(player,0)

        icm_diff = ev.icm_diff
        ev_diff = ev.ev_diff
        chip_fact = ev.chip_fact
        # icm_ev = ev.icm_ev
        # icm_ev_pct = ev.icm_ev_pct
        # icm_fact = ev.icm_fact
        # icm_fact_pct = ev.icm_fact_pct
        ko_diff = ev.ko_diff
        ko_diff_pct = ev.ko_diff_pct
        # ko_diff = ev.ko_diff.get(player, 0)
        ko_ev_pct = ev.ko_ev_pct
        ko_ev = ev.ko_ev
        ko_fact_pct = ev.ko_fact_pct
        ko_fact = ev.ko_fact
        chip_ev = ev.chip_ev
        chip_win = ev.chip_win
        chip_lose = ev.chip_lose
        # chip_sum = pc.EV.sum_dict_values(chip_fact)
        li = [hand.tid(), hand.datetime(), eq, ev_diff, icm_diff, ko_diff]
        diff_list.append(li)
        # logger.debug(f'ev.icm_ev_pct() {icm_ev_pct}')
        # logger.debug(f'ev.icm_ev() {icm_ev}')
        # logger.debug(f'ev.icm_ev_diff() {icm_diff}')
        # logger.debug(f'ev.eq() {icm_ev}')

        # logger.debug(f'ev.icm_fact_pct() { icm_fact_pct}')
        # logger.debug(f'ev.icm_fact() {icm_fact}')
        # logger.debug(f'ev.chip_win() {chip_win}')
        # logger.debug(f'ev.chip_lose() {chip_lose}')
        # logger.debug(f'ev.ko_ev_pct() {ko_ev_pct}')
        # logger.debug(f'ev.ko_ev() {ko_ev}')
        # logger.debug(f'ev.ko_fact_pct() {ko_fact_pct}')
        # logger.debug(f'ev.ko_fact() {ko_fact}')
        # logger.debug(f'ev.ko_diff_pct() {ko_diff_pct}')

        # logger.debug(f'ev.chip_ev() {chip_ev}')
        # logger.debug(f'ev.chip_fact() {chip_fact}')
        if eq != 0: logger.info(li)
        # if chip_sum != 3000:
        #     logger.debug(li)

    # logger.debug(diff_list)

# df = pd.DataFrame(diff_list)
# df.to_csv('results.csv')