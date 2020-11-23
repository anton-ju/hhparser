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
from typing import Dict

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

    def __init__(self, prize):
        if isinstance(prize, (list, dict, tuple)):
            self.prize = prize
        else:
            raise RuntimeError("Invalid prize structure")

    def calc(self, stacks_players):
        if stacks_players is None:
            exit(1)
        flg_dict = False
        if isinstance(stacks_players, (dict, NumericDict)):
            flg_dict = True
            stacks = list(stacks_players.values())
            players = list(stacks_players.keys())
        else:
            stacks = stacks_players
        sz = np.size(stacks)
        stacks = np.copy(stacks)
        ind1 = range(0, sz)

        min_place = min(sz, np.size(self.prize))
        p1 = np.zeros(shape=(min_place, sz))
        ind2 = range(0, min_place)
        # p1 строка - занятое место, столбец - номер игрока
        for i in ind1:
            for j in ind2:
                p1[j, i] = self._p1p(i, j + 1, stacks)
                # в функции место нумеруются с 1 до 3, в матрице с 0 до 2
       #
        eq = np.dot(self.prize[:min_place], p1)

        if flg_dict:
            res = {players[i]: np.round(eq[i],4) for i in range(len(players))}
        else:
            res = eq.round(4)
        return res

    def _p1p(self, ind, place, stacks):
        #       вероятность place го места для игрока ind
        #       s - список стэков игроков
        #       ind - индекс стэка для которого считаестя вероятность
        #       place - место целое число, должно быть не больше чем длина списка s

        sz = len(stacks)
        if place > sz:
            return 0
        if ind + 1 > sz:
            return 0
        #       если стэк 0 сразу вернем 0

        if stacks[ind] == 0:
            if sz - 1 >= np.size(self.prize):
                return 0
            else:
                return self.prize[sz - 1]

        p = []
        # получаем все возможные варианты распределения мест
        #           индекс в списке соответствует месту игрока
        for i in itertools.permutations(range(sz), sz):
            #               выбираем только те распределения где игрок ind на месте place
            if i[place - 1] == ind:
                #                    из списка издексов с распределением мест,
                #                    формируем список со значениями стеков
                si = []
                for j in i:
                    si.append(stacks[j])
                #                    with Profiler() as pr:
                pi = 1
                for j in range(sz):
                    sum_ = sum(si[j:])
                    if sum_ != 0:
                        pi = pi * si[j] / sum_

                p.append(pi)

        result = sum(p)
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


def build_outcome(path, aiplayers, chips, pots, uncalled, total_bets, winnings):
    """returns chipcount for outcome path: list of players in order of winning
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
    if len (aiplayers) < 2:
        # no all in in hand return fact resalts
        for p in chips.keys():
            result[p] = sum(winnings[p]) + uncalled[p] + chips[p] - total_bets[p]
        return result

    elif len(aiplayers) == 2:
        result[path[0]] = pots[0] + chips[path[0]] - total_bets[path[0]]
        result[path[1]] = chips[path[1]] - total_bets[path[1]]
    else:
        p_index = 0
        for i, pot in enumerate(pots):
            if path[p_index] in players_in_pot[i]:
                try:
                    result[path[p_index]] += pots[i]
                except KeyError:
                    result[path[p_index]] = pots[i]
                p_index = p_index + 1 if p_index < len(path) - 1 else p_index
            else:
                result[path[p_index-1]] = result[path[p_index-1]] + pots[i]

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


def build_outcome_tree(aiplayers, stacks, pots, uncalled, total_bets, winnings):
    """Returns tree, with leafs representing 1 posible outcome
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

            stack = build_outcome(path, aiplayers, stacks, pots, uncalled, total_bets, winnings) 
            node.chips = stack
            fill_knocks(node, stacks)
            fill_probs(node, None)
    return root


class EV:
    def __init__(self,
                 hand: hh,
                 icm: Icm = None,
                 ko: int = KOModels.PROPORTIONAL,
                 trials: int = 1000000):
        """
        hand: parsed hand object of HandHistoryParser subclass
        icm: icmcalc class
        ko: Knockout calculation model
        trials: trials for monte carlo algorithm
        #todo add param: player to filter results

        Functions to calculate expected value of played hand for hero
        """
        self.hand = hand
        #if no icm provided calculate as winner takes all case
        if not icm:
            icm = Icm((1,0))
        self.icm = icm
        self.ko = ko
        # players who went all in on different streets
        self.ai_players = []
        self.p_ai_players = []
        self.f_ai_players = []
        self.t_ai_players = []

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

        self.total_prizes = (self.hand.bi - self.hand.rake - self.hand.bounty) * 4 #TODO tour types
        self.player = self.hand.hero
        self.flg_calculated = False

    @staticmethod
    def outcome(self, players):
        """players: list of players in winnig order
        hand: parsed hand object of HandHistoryParser subclass
        returns chipcount for given outcome
        """
        pass

    @staticmethod
    def detect_ai_players(hand):
        """ returns tupple with players who went all in on every street
        params::: parsed hand
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

    def sort_ai_players_by_chipcount(self):
        # sort players list by chip count
        self.ai_players.sort(key=lambda v: self.chips[v], reverse=True)

    def should_return_chip_fact(self) -> bool:

        if not(self.hand.flg_showdown()):
            return True

        if not(self.ai_players) or (len(self.ai_players) >2):
            return True

    def calc(self):
        self.ai_players, self.p_ai_players, self.f_ai_players, self.t_ai_players = self.detect_ai_players(self.hand)
        self.sort_ai_players_by_chipcount()
        self.probs = self.calculate_probs()
        self.flg_calculated = True

    def chip_diff_ev_adj(self) -> float:
        fact = self.chip_fact().get(self.player)
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
        pwin - probabiliti for player to win on showdown
        sWin - chips in case player win
        sLose - chips in case player lose

        chip_ev_adj = pWin * sWin + (1 - pWin) * sLose

        calculates only for 2 players in all in
        returns: float
        """
        if self.should_return_chip_fact():
            return self.chip_fact().get(player)

        ai_players = self.ai_players
        player = self.player
        #  TODO: if hand has not been calculated yet raise exception, or what??
        # <24-11-20, yourname> # 
        eq = self.probs
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
        swin = hero_win_outcome[player]
        slose = hero_lose_outcome[player]

        res = pwin * swin + (1 - pwin) * slose
        return res

    def ev_diff(self):
        total_diff = self.icm_diff + self.ko_diff
        return total_diff

    def ev_diff_pct(self):
        total_diff = self.icm_diff + self.ko_diff
        return total_diff

    def icm_ev_pct(self, player):
        if self.should_return_chip_fact():
            return self.icm_fact_pct().get(player, 0)  # TODO another conditions to return fact should be

        ai_players = self.ai_players
        if not player:
            player = self.hand.hero

        eq = self.probs
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
        icm_lose = self.icm.calc(hero_lose_outcome)
        res = pwin * icm_win[player] \
            + (1 - pwin) * icm_lose[player]
        return res

    def icm_ev_diff_pct(self, player):
        """ ICM ev all in adjasted in percents
        """
        fact = self.icm_fact_pct().get(player, 0)
        return self.icm_ev_pct(player) - fact

    def icm_ev(self, player):
        return self.icm_ev_pct(player) * self.total_prizes

    def icm_ev_diff(self, player):
        return self.icm_ev_diff_pct(player) * self.total_prizes

    def icm_fact(self):
        prize_won = self.prize_won
        icm_fact_pct = self.icm_fact_pct()
        if self.prize_won:
            res = prize_won
        else:
            res = self.total_prizes * icm_fact_pct
        return res

    def icm_fact_pct(self):
        chip_fact = self.chip_fact()
        prize_won = self.prize_won
        if prize_won:
            res = NumericDict(float, prize_won) / self.total_prizes
        else:
            res = NumericDict(float, self.icm.calc(chip_fact))

        return res

    def ko_ev(self):
        res = self.ko_ev_pct() * self.hand.bounty

        return res

    def ko_ev_pct(self):
        # returns: float
        # how many bounties player expected to get
        # todo реализовать различные модели баунти
        # посчитаем также как и icm_ev
        # если игрок выиграл и выбил другого игрока, то добавим к его нокаутам количество игроков которых он выбил
        # ev = p_win * ko_ev(win) + (1 - p_win) * ko_ev(lose)
        if not self.ko:
            return 0

        p_win = self.probs.get(self.player, 0)
        ev_win = self.ko.calc(self.chip_win()).get(self.player, 0)
        ko_get = self.non_zero_values(self.chips) - self.non_zero_values(self.chip_win())
        ev_win += ko_get
        ev_lose = self.ko.calc(self.chip_lose()).get(self.player, 0)
        # logger.debug(p_win)
        # logger.debug(ev_win)
        # logger.debug(self.chip_lose)

        ev = p_win * ev_win + (1 - p_win) * ev_lose

        return ev

    def ko_fact(self):

        return self.hand.bounty * self.ko_fact_pct()

    def ko_fact_pct(self):
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
        return self.ko_diff_pct * self.hand.bounty

    @property
    def ko_diff_pct(self):
        # returns: float
        # Возвращает разницу между ожиданием и факту по KO
        if self.ko:
            return self.ko_ev_pct - self.ko_fact_pct.get(self.player, 0)
        else:
            return 0

    def calculate_probs(self):

        params = []
        shd_players = list(self.cards.keys())
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
        elif len(shd_players) == 3:
            hand1 = str_to_cards(self.cards.get(shd_players[0]))
            hand2 = str_to_cards(self.cards.get(shd_players[1]))
            hand3 = str_to_cards(self.cards.get(shd_players[2]))
            equity_func = py_equities_3hands
            params = [hand1, hand2, hand3, board]
        else:
            return {}

        result = equity_func(*params)
        return {shd_players[i]: result[i] for i in range(len(shd_players))}

    @staticmethod
    def non_zero_values(d: dict):
        counter = 0
        for v in d.values():
            if v: counter+=1
        return counter

    @staticmethod
    def sum_dict_values(d: dict):
        try:
            res = sum([v for v in d.values()])
        except:
            res = 0
        return res


