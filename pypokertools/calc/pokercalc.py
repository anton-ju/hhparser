from decimal import Decimal
import numpy as np
import itertools
import copy
import logging
from collections import defaultdict

from pypokertools.parsers import PSHandHistory as hh
from pypokertools.utils import NumericDict, cached_property, py_equities_2hands_fast
import eval7
from eval7 import py_equities_2hands, py_equities_3hands, py_equities_4hands
from anytree import NodeMixin, RenderTree
from enum import Enum
from typing import Dict, List, Tuple, Union

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class KOModels(Enum):
    PROPORTIONAL = 1
    FLAT = 2


class PlayerNotFoundException(Exception):
    pass


def str_to_cards(hand_str):
    cards = tuple(map(eval7.Card, hand_str.split()))
    return cards


class Knockout:
    # todo add class knock to choose knock model
    def __init__(self, model: KOModels):
        self.model = model

    def calc(self, stacks_players):
        # todo проверка переменной stacks_players является ли она распределнием стэков игроков
        # здесь подразумевается, что stacks_players это словарь вида {player: stacks}
        # возвращает ожидаемое количество нокаутов которое игрок может получить в соответствии с моделью нокаутов
        # пока реализована только пропорциональная модель.
        # ko = total_players * stack / total_chips
        res = {}
        total_players = EV.non_zero_values(stacks_players)
        total_chips = EV.sum_dict_values(stacks_players)
        if self.model == KOModels.PROPORTIONAL:
            for player, stack in stacks_players.items():
                res[player] = total_players * stack / total_chips
        else:
            raise ValueError('Unknown knockout model')

        return res


class Icm:

    def __init__(self, payouts):
        if isinstance(payouts, (list, dict, tuple)):
            self.payouts = payouts
        else:
            raise RuntimeError("Invalid prize structure")

    def calc(self, chips_players: Union[List[int], Dict[str, int]]) -> Union[List[float], Dict[str, float]]:
        result: List[float] = []
        if isinstance(chips_players, dict):

            chips = list(chips_players.values())
        elif isinstance(chips_players, list):
            chips = chips_players[:]
        else:
            raise RuntimeError("Invalid type")

        total: int = sum(chips)
        for k, v in enumerate(chips):
            eq = round(self.get_equities(chips, total, k, 0), 4)
            result.append(eq)

        return result if isinstance(chips_players, list) else dict(zip(chips_players.keys(), result))

    def get_equities(self, chips: List[int], total: int, player, depth: int) -> float:
        result = chips[player] / total * self.payouts[depth]
        if depth + 1 < len(self.payouts):
            i: int = 0
            for stack in chips:
                if i != player and stack > 0.0:
                    chips[i] = 0.0
                    result += self.get_equities(chips, (total - stack), player, (depth + 1)) * (stack / total)
                    chips[i] = stack
                i += 1
        return result


class OutCome(NodeMixin, object):

    def __init__(self, name, parent=None, children=None, chips={}, probs={}, knocks={}, **kwargs):
        self.__dict__.update(kwargs)
        self.name = name
        self.chips = chips
        self.probs = probs
        self.knocks = knocks
        self.parent = parent
        if children:
            self.children = children

    def __repr__(self):
        res = []
        for pre, _, node in RenderTree(self):
            res.append("%s %s %s %s" % (pre, node.name, node.chips, node.knocks))
        return '\n'.join(res)


def add_children(root, children):
    if len(children) <= 1:
        return
    for i in range(len(children)):
        new_root = OutCome(children[i], parent=root, )
        add_children(new_root, children[:i])


def fill_knocks(node, stacks):
    """Fills node.knocks with dict
    """
    knocks = {}
    for n in node.path:
        knocks_sum = sum([stacks[n.name] >= stacks[s.name] for s in n.siblings])
        if knocks_sum:
            knocks[n.name] = knocks_sum
    node.knocks = knocks


def fill_probs(root, cards):
    """Fills node.probs
    """
    for pre, fill, node in RenderTree(root):
        if not node.is_leaf:
            pass

#  TODO:  <28-11-20, anton-ju> make class for this functions # 


def build_outcome(path: List[str],
                  aiplayers: List[str],
                  chips: Dict[str, int],
                  pots: List[float],
                  uncalled: Dict[str, int],
                  total_bets: Dict[str, int],
                  winnings: Dict[str, int]) -> Dict[str, int]:
    """
    Returns chipcount for outcome path
    :path: list of player names who win pots
        [player1, player2] means player1 wins, player2 lose
        [player1, player2, player3] means player1 wins main pot, player2 win side pot, player3 lose
    :aiplayers: players who went all in
    :chips: chipcount of original hand history
    :pots: pots from main to all side posts
    :uncalled: uncalled from hand history
    :total_bets: total bets on all streets for every player
    :winnings: total winnings for every player
    """

    # players with bigger stack first
    aiplayers.sort(key=lambda v: chips[v], reverse=True)
    not_aiplayers = [p for p in chips.keys() if p not in aiplayers]
    # [side2pot, side1pot, mainpot]
    # [players_in_pot[0] - corresponds to list of players in side2 pot
    # [players_in_pot[1] - corresponds to list of players in side1 pot and so on 
    players_in_pot = list(reversed([aiplayers[:l] for l in range(len(pots)+1, 1, -1)]))
    # uncalled for top1 player
    result = {}
    if len(aiplayers) < 2:
        # no all in in hand return fact resalts
        for p in chips.keys():
            result[p] = sum(winnings[p]) + uncalled[p] + chips[p] - total_bets[p]
        return result

    elif len(aiplayers) == 2:
        result[path[0]] = pots[0] + chips[path[0]] - total_bets[path[0]]
        result[path[1]] = chips[path[1]] - total_bets[path[1]]

    elif len(aiplayers) == 3:
        # players by chipcount
        p1, p2, p3 = aiplayers
        mainpot = pots[0]
        try:
            sidepot = pots[1]
        except IndexError:
            sidepot = 0
        # top1 player wins
        if path[0] == p1:
            result[p1] = mainpot + sidepot + chips[p1] - total_bets[p1]
            result[p2] = 0
            result[p3] = 0
        # top 2 player wins
        elif path[0] == p2:
            result[p1] = chips[p1] - total_bets[p1]
            result[p2] = mainpot + sidepot + chips[p2] - total_bets[p2]
            result[p3] = 0
        # top 3 player wins
        elif path[0] == p3:
            # top 3 gets main pot
            result[p3] = mainpot
            # who wins side pot
            result[path[1]] = sidepot + chips[path[1]] - total_bets[path[1]]
            try:
                result[path[2]] = chips[path[2]] - total_bets[path[2]]
            except IndexError:
                pass

    # stacks for players that is not take part in pots remains the same - blinds ante
    for p in not_aiplayers:
        result[p] = chips[p] - total_bets[p]

    # players who lose.
    for p in aiplayers:
        if p not in path:
            result[p] = 0

    # uncalled allways to top1 player
    try:
        result[aiplayers[0]] += uncalled[aiplayers[0]]
    except KeyError:
        result[aiplayers[0]] = uncalled[aiplayers[0]]

    return {p: int(v) for p, v in result.items()}


def build_outcome_tree(aiplayers: List[str],
                       chips: Dict[str, int],
                       pots: List[float],
                       uncalled: Dict[str, int],
                       total_bets: Dict[str, int],
                       winnings: Dict[str, int]) -> Dict[str, int]:
    """
    Returns tree, with leafs representing 1 posible outcome
    aiplayers: list of players in all-in
    stacks: dict with stack distribution {'player': chips}
    pots: list with amount of chips in pots that been playing from main pot to all side pots
    """
    root = OutCome('root')
    add_children(root, aiplayers)
    # creating all paths list if node is leaf
    for pre, fill, node in RenderTree(root):
        # leaf of the tree representing 1 outcome
        if node.is_leaf:
            path = []
            for p in node.path:
                # path looks like [node.name, node.name...]
                path.append(p.name)
            # not including first path element, because it is always root
            path = list(reversed(path[1:]))

            stack = build_outcome(path, aiplayers, chips, pots, uncalled, total_bets, winnings)
            node.chips = stack
            fill_knocks(node, chips)
            fill_probs(node, None)
    return root


class EV:
    def __init__(self,
                 hand: hh,
                 icm: Icm = None,
                 ko: KOModels = KOModels.PROPORTIONAL,
                 trials: int = 1000000):
        """
        hand: parsed hand object of HandHistoryParser subclass
        icm: icmcalc class
        ko: Knockout calculation model
        trials: trials for monte carlo algorithm

        Functions to calculate expected value of played hand
        """
        #  TODO:  deep copy? # 
        self.hand = hand
        # if no icm provided calculate as winner takes all case
        if not icm:
            icm = Icm((1, 0))
        self.icm = icm
        self.ko = ko
        # players who went all in on different streets
        self.ai_players: List[str] = []
        self.p_ai_players: List[str] = []
        self.f_ai_players: List[str] = []
        self.t_ai_players: List[str] = []

        # chip collected from pot total
        self.winnings_chips = NumericDict(list, hand.chip_won)

        self.total_bets = NumericDict(int, hand.total_bets_amounts())
        self.prize_won = hand.prize_won
        self.chips = NumericDict(int, hand.chips())
        self.players = self.chips.keys()
        self.uncalled = NumericDict(int, hand.uncalled)
        self.cards = hand.known_cards
        self.pots = hand.pot_list
        # not include total pot if multiway
        if len(self.pots) > 1:
            self.pots = self.pots[1:]
        self.trials = trials

        self.total_prizes = (self.hand.bi - self.hand.rake - self.hand.bounty) * 4
        # TODO tournament types detection?

        # default player for calculation is always hero
        self.player = self.hand.hero
        self._probs: Dict[str, int]
        self.flg_calculated = False

    @staticmethod
    def detect_ai_players(hand: hh)-> Tuple[List[str], List[str], List[str], List[str]]:
        """ returns tupple with players who went all in on every street
        :params: parsed hand
        """

        ai_players = list(hand.known_cards.keys())
        p_ai_players = []
        f_ai_players = []
        t_ai_players = []
        r_ai_players = []
        p_actions = hand.p_last_action()
        f_actions = hand.f_last_action()
        t_actions = hand.t_last_action()
        r_actions = hand.r_last_action()
        for p in ai_players:
            if hand.p_ai_players:
                if p_actions.get(p, 'c') != 'f':
                    p_ai_players.append(p)

            if hand.f_ai_players:
                if f_actions.get(p, 'f') != 'f':
                    f_ai_players.append(p)

            if hand.t_ai_players:
                if t_actions.get(p, 'f') != 'f':
                    t_ai_players.append(p)

            if hand.r_ai_players:
                if r_actions.get(p, 'f') != 'f':
                    r_ai_players.append(p)
        return ai_players, p_ai_players, f_ai_players, t_ai_players

    def sort_ai_players_by_chipcount(self) -> None:
        """
        sort players list by chip count
        change self.ai_players
        doc
        """
        self.ai_players.sort(key=lambda v: self.chips[v], reverse=True)

    def should_return_chip_fact(self) -> bool:
        if not(self.hand.flg_showdown()):
            return True

        if not(self.ai_players) or (len(self.ai_players) > 3):
            return True

        return False

    def get_probs(self, player: Union[str, List[str]], npot: int = 0) -> Union[float, Dict[str, float]]:
        """
        :npot: pot number - 0 for mainpot, 1 for side pot 1 and so on, default: 0
        :returns: probabilities of win on showdown for given player, or for a list of players
        returns 0 if player not participated in all in

        """
        if not self.flg_calculated:
            self._probs = self.calculate_probs()
            self.flg_calculated = True

        if isinstance(player, str):
            result = self._probs[npot].get(player, 0)
        elif isinstance(player, list):
            probs: dict = self._probs[npot]
            result = {p: probs.get(p, 0) for p in player}
        else:
            raise RuntimeError("Invalid parameter 'player'!")

        return result

    def calc(self, player: str) -> None:
        """
        calculates probabilities and detects all in players
        sets up active player for which results of calculations returns
        """
        if self.flg_calculated:
            self.player = player
        else:
            self.player = player
            self.ai_players, self.p_ai_players, self.f_ai_players, self.t_ai_players = self.detect_ai_players(self.hand)
            self.sort_ai_players_by_chipcount()
            self._probs = self.calculate_probs()
            self.flg_calculated = True

    def chip_diff_ev_adj(self) -> float:
        fact = self.chip_fact().get(self.player, 0.0)
        return self.chip_ev_adj() - fact

    def chip_net_won(self) -> Dict[str, int]:
        """Returns net chip won for every player in hand"""
        res = self.chip_fact() - self.chips
        return res

    def chip_fact(self) -> Dict[str, int]:
        """Return real outcome of played hand
        chip count after hand been played
        returns: NumericDict {player: stack}
        """
        res = NumericDict(int)
        total_bets_amounts = self.hand.total_bets_amounts()
        chips = self.chips
        winnings = self.winnings_chips
        uncalled = self.uncalled

        for p in self.players:
            res[p] = sum(winnings[p]) + uncalled[p] + chips[p] - total_bets_amounts[p]
        return res

    def chip_ev_adj(self) -> float:
        """expected to won chips All in adjusted
        returns: float
        """
        if self.should_return_chip_fact():
            return self.chip_fact().get(self.player, 0.0)

        ai_players = self.ai_players
        if len(ai_players) == 2:
            return self.chip_ev_2way()
        elif len(ai_players) == 3:
            return self.chip_ev_3way()

    def chip_ev_2way(self) -> float:
        """expected to won chips All in adjusted
        pwin - probabiliti for player to win on showdown
        sWin - chips in case player win
        sLose - chips in case player lose

        chip_ev_adj = pWin * sWin + (1 - pWin) * sLose

        calculates only for 2 players in all in
        returns: float
        """
        ai_players = self.ai_players
        player = self.player
        pwin = self.get_probs(player)
        hero_win_path = ai_players[:] if ai_players[0] == player else ai_players[::-1]
        hero_lose_path = hero_win_path[::-1]

        hero_win_outcome = build_outcome(hero_win_path,
                                         ai_players,
                                         self.chips,
                                         self.pots,
                                         self.uncalled,
                                         self.total_bets,
                                         self.winnings_chips)
        hero_lose_outcome = build_outcome(hero_lose_path,
                                          ai_players,
                                          self.chips,
                                          self.pots,
                                          self.uncalled,
                                          self.total_bets,
                                          self.winnings_chips)
        swin = hero_win_outcome[player]
        slose = hero_lose_outcome[player]

        res = pwin * swin + (1 - pwin) * slose
        return res

    def chip_ev_3way(self):
        """
        calculations for 3way spots
        P1 = top 1 player in all in by chips
        p1win - probabiliti for P1 to win on showdown
        p2win - probabiliti for P2 to win on showdown
        p3win - probabiliti for P3 to win on showdown
        p1sp1win - probabiliti between P1 and P2 for P1 to win on showdown
        sP1Win - chips in case P1 win
        sP2Win - chips in case P2 win
        sP3P1Win - chips in case P3 win main pot and P1 win side pot
        sP3P2Win - chips in case P3 win main pot and P2 win side pot = 1 - sP3P1Win

        chip_ev_3way =  P1Win * sP1Win + P2Win * sP2Win + P3Win * (P1WinSP * sP3P1Win + (1 - P1WinSP) * sP3P2Win)

        returns: float
        """
        player = self.player
        p1, p2, p3 = self.ai_players
        c_p1win = build_outcome([p1, p2, p3],
                                [p1, p2, p3],
                                self.chips,
                                self.pots,
                                self.uncalled,
                                self.total_bets,
                                self.winnings_chips)
        c_p1win = c_p1win[player]

        c_p2win = build_outcome([p2, p1, p3],
                                [p1, p2, p3],
                                self.chips,
                                self.pots,
                                self.uncalled,
                                self.total_bets,
                                self.winnings_chips)
        c_p2win = c_p2win[player]

        c_p3p1win = build_outcome([p3, p1, p2],
                                  [p1, p2, p3],
                                  self.chips,
                                  self.pots,
                                  self.uncalled,
                                  self.total_bets,
                                  self.winnings_chips)
        c_p3p1win = c_p3p1win[player]

        c_p3p2win = build_outcome([p3, p2, p1],
                                  [p1, p2, p3],
                                  self.chips,
                                  self.pots,
                                  self.uncalled,
                                  self.total_bets,
                                  self.winnings_chips)
        c_p3p2win = c_p3p2win[player]

        probs = self.get_probs([p1, p2, p3])
        p1win = probs.get(p1, 0.0)
        p2win = probs.get(p2, 0.0)
        p3win = probs.get(p3, 0.0)
        # probabilities for side pot
        p1sp1win = self.get_probs(player, 1)
        p1sp2win = 1 - p1sp1win
        result = p1win * c_p1win + p2win * c_p2win + p3win * (p1sp1win * c_p3p1win + p1sp2win * c_p3p2win)
        return result

    def ev_diff(self):
        total_diff = self.icm_diff + self.ko_diff
        return total_diff

    def ev_diff_pct(self):
        total_diff = self.icm_diff + self.ko_diff
        return total_diff

    def icm_ev_pct(self) -> float:
        """
        calculates expected value of stack in percents of prize fund according to the icm model
        pwin - probability for player to win on showdown
        icm_win - icm value for players stack in case player win
        icm_lose - icm value for players stack in case player lose
        icm_ev_pct = pwin * icm_win + (1 - pwin) * icm_lose
        """
        # TODO another conditions to return fact should be
        # TODO calculations for 3way all in
        if self.should_return_chip_fact():
            return self.icm_fact_pct()

        ai_players = self.ai_players

        if len(ai_players) == 2:
            return self.icm_ev_2way()
        elif len(ai_players) == 3:
            return self.icm_ev_3way()

    def icm_ev_2way(self):
        """
        :returns: TODO

        """
        ai_players = self.ai_players
        player = self.player
        eq = self._probs[0]
        pwin = eq.get(player, 0)
        hero_win_path = ai_players[:] if ai_players[0] == player else ai_players[::-1]
        hero_lose_path = hero_win_path[::-1]

        hero_win_outcome = build_outcome(hero_win_path,
                                         ai_players,
                                         self.chips,
                                         self.pots,
                                         self.uncalled,
                                         self.total_bets,
                                         self.winnings_chips)
        hero_lose_outcome = build_outcome(hero_lose_path,
                                          ai_players,
                                          self.chips,
                                          self.pots,
                                          self.uncalled,
                                          self.total_bets,
                                          self.winnings_chips)
        icm_win = self.icm.calc(hero_win_outcome)
        icm_win = icm_win.get(player, 0.0)
        icm_lose = self.icm.calc(hero_lose_outcome)
        icm_lose = icm_lose.get(player, 0.0)
        res = pwin * icm_win + (1 - pwin) * icm_lose
        return res

    def icm_ev_3way(self):
        """

        :f: TODO
        :returns: TODO

        """
        player = self.player
        p1, p2, p3 = self.ai_players
        c_p1win = build_outcome([p1, p2, p3],
                                [p1, p2, p3],
                                self.chips,
                                self.pots,
                                self.uncalled,
                                self.total_bets,
                                self.winnings_chips)
        icm_p1win = self.icm.calc(c_p1win)
        icm_p1win = icm_p1win.get(player, 0.0)

        c_p2win = build_outcome([p2, p1, p3],
                                [p1, p2, p3],
                                self.chips,
                                self.pots,
                                self.uncalled,
                                self.total_bets,
                                self.winnings_chips)
        icm_p2win = self.icm.calc(c_p2win)
        icm_p2win = icm_p2win.get(player, 0.0)

        c_p3p1win = build_outcome([p3, p1, p2],
                                  [p1, p2, p3],
                                  self.chips,
                                  self.pots,
                                  self.uncalled,
                                  self.total_bets,
                                  self.winnings_chips)
        icm_p3p1win = self.icm.calc(c_p3p1win)
        icm_p3p1win = icm_p3p1win.get(player, 0.0)

        c_p3p2win = build_outcome([p3, p2, p1],
                                  [p1, p2, p3],
                                  self.chips,
                                  self.pots,
                                  self.uncalled,
                                  self.total_bets,
                                  self.winnings_chips)
        icm_p3p2win = self.icm.calc(c_p3p2win)
        icm_p3p2win = icm_p3p2win.get(player, 0.0)

        probs = self.get_probs([p1, p2, p3])
        p1win = probs.get(p1, 0.0)
        p2win = probs.get(p2, 0.0)
        p3win = probs.get(p3, 0.0)
        p1sp1win = self.get_probs(player, 1)
        p1sp2win = 1 - p1sp1win
        print(p1win, p2win, p3win, icm_p1win, p1sp1win, icm_p3p1win)
        result = p1win * icm_p1win + p2win * icm_p2win + p3win * (p1sp1win * icm_p3p1win + p1sp2win * icm_p3p2win)
        return result

    def icm_ev_diff_pct(self) -> float:
        """
        calculates difference between EV and fact in percent according to the icm model

        icm_ev_diff_pct = icm_ev_pct - icm_fact
        """
        fact = self.icm_fact_pct()
        return self.icm_ev_pct() - fact

    def icm_ev(self) -> float:
        """
        calculates expected value of players stack in currency according to the icm model
        """
        return self.icm_ev_pct() * self.total_prizes

    def icm_ev_diff(self):
        """
        calculates difference between EV and fact in currency according to the icm model
        """
        return self.icm_ev_diff_pct() * self.total_prizes

    def icm_fact(self) -> float:
        """
        calculates fact value of players stack in currency according to the icm model
        returns actual amount player won if tournament finished in the hand
        """
        prize_won = self.prize_won
        icm_fact_pct = self.icm_fact_pct()
        if self.prize_won:
            res = prize_won
        else:
            res = self.total_prizes * icm_fact_pct
        return res.get(self.player, 0)

    def icm_fact_pct(self) -> float:
        """
        calculates fact value of players stack in percents according to the icm model
        returns actual amount player won in percents if tournament finished in the hand
        """
        chip_fact = self.chip_fact()
        prize_won = self.prize_won
        if prize_won:
            res = NumericDict(float, prize_won) / self.total_prizes
        else:
            res = NumericDict(float, self.icm.calc(chip_fact))

        return res.get(self.player, 0)

    def ko_ev(self):
        # res = self.ko_ev_pct() * self.hand.bounty

        # return res
        raise NotImplementedError

    def ko_ev_pct(self):
        # returns: float
        # how many bounties player expected to get
        # todo реализовать различные модели баунти
        # посчитаем также как и icm_ev
        # если игрок выиграл и выбил другого игрока, то добавим к его нокаутам количество игроков которых он выбил
        # ev = p_win * ko_ev(win) + (1 - p_win) * ko_ev(lose)
        # if not self.ko:
        #     return 0

        # p_win = self._probs.get(self.player, 0)
        # ev_win = self.ko.calc(self.chip_win()).get(self.player, 0)
        # ko_get = self.non_zero_values(self.chips) - self.non_zero_values(self.chip_win())
        # ev_win += ko_get
        # ev_lose = self.ko.calc(self.chip_lose()).get(self.player, 0)
        # logger.debug(p_win)
        # logger.debug(ev_win)
        # logger.debug(self.chip_lose)

        # ev = p_win * ev_win + (1 - p_win) * ev_lose

        # return ev
        raise NotImplementedError

    def ko_fact(self):

        # return self.hand.bounty * self.ko_fact_pct()
        raise NotImplementedError

    def ko_fact_pct(self):
        raise NotImplementedError
        res = {}
        who_won_bounty = self.hand.bounty_won.keys()
        chips = self.chip_fact()
        res = self.ko.calc(chips)
        for p in who_won_bounty:
            res[p] += 1

        return res

    @property
    def ko_diff(self):
        # returns: float
        # Возвращает разницу между ожиданием и факту по KO
        # return self.ko_diff_pct * self.hand.bounty
        raise NotImplementedError

    @property
    def ko_diff_pct(self):
        # returns: float
        # Возвращает разницу между ожиданием и факту по KO
        # if self.ko:
        #     return self.ko_ev_pct - self.ko_fact_pct.get(self.player, 0)
        # else:
        #     return 0
        raise NotImplementedError

    def calculate_probs(self) -> List[Dict[str, float]]:
        """
        calculates probabilities of win on showdown for 2 or 3 players,
        list index corresponds to number of pot, 0 for main pot, 1 for sidepot 1 and so on.
        returns 0.0 for every player in other cases
        """
        params = []
        shd_players = self.ai_players
        tasks: list = []
        tasks_result: list = []
        result: list = []
        if self.p_ai_players:
            board = str_to_cards("")
        elif self.f_ai_players:
            board = str_to_cards(self.hand.flop)
        elif self.t_ai_players:
            board = str_to_cards(self.hand.flop + ' ' + self.hand.turn)

        if len(shd_players) == 2:
            hand1 = str_to_cards(self.cards.get(shd_players[0]))
            hand2 = str_to_cards(self.cards.get(shd_players[1]))
            if board == '' or board is None:
                equity_func = py_equities_2hands_fast
                params = [hand1, hand2]
            else:
                equity_func = py_equities_2hands
                params = [hand1, hand2, board]

            tasks.append((equity_func, params))

        elif len(shd_players) == 3:
            hand1 = str_to_cards(self.cards.get(shd_players[0]))
            hand2 = str_to_cards(self.cards.get(shd_players[1]))
            hand3 = str_to_cards(self.cards.get(shd_players[2]))
            equity_func = py_equities_3hands
            params = [hand1, hand2, hand3, board]
            tasks.append((equity_func, params))

            # top 2 players in side pot 1 calculation
            if board == '' or board is None:
                equity_func = py_equities_2hands_fast
                params = [hand1, hand2]
            else:
                equity_func = py_equities_2hands
                params = [hand1, hand2, board]
            tasks.append((equity_func, params))
        else:
            return [{shd_players[i]: 0.0 for i in range(len(shd_players))}]

        for t in tasks:
            equity_func, params = t
            tasks_result.append(equity_func(*params))

        for r in tasks_result:
            i = 0
            d = {}
            for p in r:
                d[shd_players[i]] = p
                i += 1
            result.append(d)

        return result

    @staticmethod
    def non_zero_values(d: dict):
        #  TODO: move to utils <28-11-20, anton-ju> # 
        counter = 0
        for v in d.values():
            if v:
                counter += 1
        return counter

    @staticmethod
    def sum_dict_values(d: dict):
        try:
            res = sum([v for v in d.values()])
        except:
            res = 0
        return res


