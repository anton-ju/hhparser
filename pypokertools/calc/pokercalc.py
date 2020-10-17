import numpy as np
import itertools
import copy
import logging
from collections import defaultdict

from pypokertools.parsers import PSHandHistory as hh
from pypokertools.utils import NumericDict, cached_property
import eval7
from eval7 import py_equities_2hands, py_equities_3hands, py_equities_4hands
from anytree import NodeMixin, RenderTree

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

from enum import Enum

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


def build_outcome(path, aiplayers, stacks, pots, uncalled, total_bets):
    """returns outcome
    path: list of players in order of winning
    """
    
    # players with bigger stack first
    aiplayers.sort(key=lambda v: stacks[v], reverse=True)
    not_aiplayers = [p for p in stacks.keys() if p not in aiplayers]
    # [side2pot, side1pot, mainpot]
    # [players_in_pot[0] - corresponds to list of players in side2 pot
    # [players_in_pot[1] - corresponds to list of players in side1 pot and so on 
    players_in_pot = list(reversed([aiplayers[:l] for l in range(len(pots)+1, 1, -1)]))
    # uncalled for top1 player
    stack = {}
    if len(aiplayers) == 2:
        stack[path[0]] = pots[0] + stacks[path[0]] - total_bets[path[0]]
        stack[path[1]] = stacks[path[1]] - total_bets[path[1]]
    else:
        p_index = 0
        for i, pot in enumerate(pots):
            if path[p_index] in players_in_pot[i]:
                try:
                    stack[path[p_index]] += pots[i]
                except KeyError:
                    stack[path[p_index]] = pots[i]
                p_index = p_index + 1 if p_index < len(path) - 1 else p_index
            else:
                stack[path[p_index-1]] = stack[path[p_index-1]] + pots[i]

    # stacks for players that is not take part in pots remains the same - blinds ante
    for p in not_aiplayers:
        stack[p] = stacks[p] - total_bets[p]

    # players who lose.
    for p in aiplayers:
        if p not in path:
            stack[p] = 0

    # uncalled allways to top1 player
    try:
        stack[aiplayers[0]] += uncalled[aiplayers[0]]
    except KeyError:
        stack[aiplayers[0]] = uncalled[aiplayers[0]]

    return {p: int(v) for p, v in stack.items()}


def build_outcome_tree(aiplayers, stacks, pots, uncalled):
    """Returns tree, with leafs representing 1 posible outcome
    aiplayers: list of players in all-in
    stacks: dict with stack distribution {'player': chips}
    pots: list with amount of chips in pots that been playing from main pot to all side pots
    """
    not_aiplayers = [p for p in stacks.keys() if p not in aiplayers]
    # [side2pot, side1pot, mainpot]
    # [players_in_pot[0] - corresponds to list of players in side2 pot
    # [players_in_pot[1] - corresponds to list of players in side1 pot and so on 
    players_in_pot = list(reversed([aiplayers[:l] for l in range(len(pots)+1, 1, -1)]))
    # uncalled for top1 player
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

            stack = {}
            p_index = 0
            for i, pot in enumerate(pots):
                if path[p_index] in players_in_pot[i]:
                    try:
                        stack[path[p_index]] += pots[i]
                    except KeyError:
                        stack[path[p_index]] = pots[i]
                    p_index = p_index + 1 if p_index < len(path) - 1 else p_index
                else:
                    stack[path[p_index-1]] = stack[path[p_index-1]] + pots[i]

            # stacks for players that is not take part in pots remains the same
            for p in not_aiplayers:
                stack[p] = stacks[p]

            # players who lose.
            for p in aiplayers:
                if p not in path:
                    stack[p] = 0

            # uncalled allways to top1 player
            try:
                stack[aiplayers[0]] += uncalled[aiplayers[0]]
            except KeyError:
                stack[aiplayers[0]] = uncalled[aiplayers[0]]

            node.chips = stack
            fill_knocks(node, stacks)
            fill_probs(node, None)
    return root


class EV:
    def __init__(self, hand, icm, ko=None, trials=1000000):
        """
        hand: parsed hand object of HandHistoryParser subclass
        icm: icmcalc class
        ko: ko calc
        trials: trials for monte carlo algorithm
        #todo add param: player to filter results
        """
        self.hand = hand
        self.icm = icm
        self.ko = ko
        self.ai_players = []
        self.p_ai_players = []
        self.f_ai_players = []
        self.t_ai_players = []
        self.winnings_chips = NumericDict(list, hand.chip_won)
        self.total_bets = NumericDict(int, hand.total_bets_amounts())
        self.prize_won = hand.prize_won
        self.chips = NumericDict(int, hand.stacks())
        self.players = self.chips.keys()
        self.uncalled = NumericDict(int, hand.uncalled)
        self.cards = NumericDict(int, hand.known_cards)
        self.pots = hand.pot_list
        # not include total pot if multiway
        if len(self.pots) > 1:
            self.pots = self.pots[1:]
        self.trials = trials

        self.total_prizes = (self.hand.bi - self.hand.rake - self.hand.bounty) * 6
        self.player = str()
        self.flg_calculated = False
        self.detect_ai_players()
        self.ai_players = hand.p_ai_players+hand.f_ai_players+hand.t_ai_players+hand.r_ai_players
        self.sort_ai_players_by_chipcount()

    @staticmethod
    def outcome(self, players):
        """players: list of players in winnig order
        hand: parsed hand object of HandHistoryParser subclass
        returns chipcount for given outcome
        """
        pass

    def detect_ai_players(self):

        self.ai_players = list(self.cards.keys())
        for p in self.ai_players:
            if self.hand.p_ai_players:
                p_actions = self.hand.p_last_action()
                if p_actions.get(p, 'f') != 'f':
                    self.p_ai_players.append(p)

            if self.hand.f_ai_players:
                f_actions = self.hand.f_last_action()
                if f_actions.get(p, 'f') != 'f':
                    self.f_ai_players.append(p)

            if self.hand.t_ai_players:
                t_actions = self.hand.t_last_action()
                if t_actions.get(p, 'f') != 'f':
                    self.t_ai_players.append(p)

    def sort_ai_players_by_chipcount(self):
        # sort players list by chip count
        self.ai_players.sort(key=lambda v: self.chips[v], reverse=True)

    def calc(self, player):
        if player not in self.players:
            raise PlayerNotFoundException()
        self.player = player
        self.flg_calculated = True
        #if self.ai_players:
            # print(self.ai_players, self.chips, self.pots, self.uncalled)
            #root = build_outcome_tree(self.ai_players, self.chips, self.pots, self.uncalled)
            #for pre, _, node in RenderTree(root):
            #    pass
                #print("%s %s %s %s" % (pre, node.name, node.chips, node.knocks))
        #else:
            #print(self.chip_fact())

    def chip_diff(self):
        return self.chip_ev() - self.chip_fact()

    def chip_lose(self):
        pass

    def chip_win(self):
        pass

    def chip_outcome(self, winners):
        """ returns outcome with winners
        raise error if winners not in aiplayers
        returns: NumericDict {player: stack}
        """
        res = NumericDict(int)

    def chip_fact(self):
        """Return real outcome of played hand
        chip count after hand been played
        returns: NumericDict {player: stack}
        """
        res = NumericDict(int)
        total_bets_amounts = self.hand.total_bets_amounts()

        for p in self.players:
            if p in self.ai_players:
                res[p] = sum(self.winnings_chips[p]) + self.uncalled[p]
            else:
                res[p] = self.chips[p] \
                         - total_bets_amounts.get(p, 0) \
                         + sum(self.winnings_chips.get(p, [0]))\
                         + self.uncalled[p]
        return res

    def chip_ev(self):
        """Net won chips All in EV adjasted
        returns: dict {player: stack}
        """
        if not(self.hand.flg_showdown()):
            return self.chip_fact

        if not(self.ai_players):
            return self.chip_fact

        res = NumericDict(int)
        eq = self.equities()
        for p in self.chips.keys():
            if p in eq.keys():
                if p in self.aiplayers:
                    res[p] = int(round(self.pots[0] * eq[p] + self.uncalled[p]))
                else:
                    res[p] = int(round(self.chips[p] \
                             - self.hand.total_bets_amounts().get(p, 0) \
                             + self.pots[0] * eq[p]\
                             + self.uncalled[p]))
            else:
                res[p] = self.chip_fact().get(p)

        return res

    def ev_diff(self):
        total_diff = self.icm_diff + self.ko_diff
        return total_diff

    def ev_diff_pct(self):
        total_diff = self.icm_diff + self.ko_diff
        return total_diff

    def icm_ev(self):
        return self.icm_ev_pct() * self.total_prizes

    def icm_ev_pct(self):

        p_win = self.equities().get(self.player, 0)
        ev_win = self.icm.calc(self.chip_win()).get(self.player, 0)
        ev_lose = self.icm.calc(self.chip_lose()).get(self.player, 0)

        return p_win * ev_win + (1 - p_win) * ev_lose

    def icm_fact(self):
        icm_fact_pct = self.icm_fact_pct()
        if self.prize_won:
            res = self.prize_won
        else:
            res = self.total_prizes * icm_fact_pct
        return res

    def icm_fact_pct(self):
        chip_fact = self.chip_fact()
        if self.prize_won:
            res = self.prize_won / self.total_prizes
        else:
            res = NumericDict(int, self.icm.calc(chip_fact))

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

        p_win = self.equities().get(self.player, 0)
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
    def icm_diff(self):
        # returns: float
        # Возвращает разницу между ожиданием и факту по ICM

        return self.icm_diff_pct * self.total_prizes

    @property
    def icm_diff_pct(self):
        # returns: float
        # Возвращает разницу между ожиданием и факту по ICM

        return self.icm_ev_pct - self.icm_fact_pct.get(self.player, 0)

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

    def equities(self):

        if self.p_ai_players:
            players = self.p_ai_players
            if len(players) == 2:
                hand1 = self.cards.get(players[0])
                hand2 = self.cards.get(players[1])
                hand1 = str_to_cards(hand1)
                hand2 = str_to_cards(hand2)
                board = str_to_cards("")
                equity = py_equities_2hands(hand1, hand2, board)
                return {players[0]: equity[0], players[1]: equity[1]}

        if self.f_ai_players:
            players = self.f_ai_players
            if len(players) == 2:
                hand1 = self.cards.get(players[0])
                hand2 = self.cards.get(players[1])
                hand1 = str_to_cards(hand1)
                hand2 = str_to_cards(hand2)
                board = str_to_cards(self.hand.flop)
                equity = py_equities_2hands(hand1, hand2, board)
                return {players[0]: equity[0], players[1]: equity[1]}

        if self.t_ai_players:
            players = self.t_ai_players
            if len(players) == 2:
                hand1 = self.cards.get(players[0])
                hand2 = self.cards.get(players[1])
                hand1 = str_to_cards(hand1)
                hand2 = str_to_cards(hand2)
                board = str_to_cards(self.hand.flop + ' ' + self.hand.turn)
                equity = py_equities_2hands(hand1, hand2, board)
                return {players[0]: equity[0], players[1]: equity[1]}
        return {}

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


