import numpy as np
import itertools
import hhparser as hh
import eval7
import logging
logging.basicConfig(level = logging.DEBUG)
logger = logging.getLogger(__name__)
from enum import Enum

class KOModels(Enum):
    PROPORTIONAL = 1
    FLAT = 2


class PlayerNotFoundException(Exception):
    pass


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
        if type(prize) in (type([]), type((0,1)), type({})):
            self.prize = prize
        else:
            exit(1)

    def calc(self, stacks_players):
        if stacks_players is None:
            exit(1)
        flg_dict = False
        if type(stacks_players)==type({}):
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
            return {players[i]: np.round(eq[i],4) for i in range(len(players))}
        else:
            return eq.round(4)

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


class EV:
    # todo use new class StacksDict to simplify add and sub operations over dicts
    def __init__(self, hand: hh.HHParser, icm: Icm, ko: Knockout=None, trials=1000000):
        # todo add param: player to filter results
        self.hand = hand
        self.icm = icm
        self.ko = ko
        self.aiplayers = hand.p_ai_players() + hand.f_ai_players() + hand.t_ai_players() + hand.r_ai_players()
        self.winnings_chips = self.hand.chip_won()
        self.chips = self.hand.stacks()
        self.players = self.chips.keys()
        self.uncalled = self.hand.uncalled()
        self.cards = self.hand.known_cards()
        self.pots = self.hand.pot_list()
        self._equities_ = {}
        self.trials = trials

        self._chip_fact_ = {}
        self._chip_ev_ = {}
        self._chip_diff_ = {}
        self._chip_lose_ = {}
        self._chip_win_ = {}

        self._icm_fact_ = {}
        self._icm_fact_pct_ = {}
        self._icm_ev_ = {}
        self._icm_ev_pct_ = 0.0
        self._icm_diff_ = {}
        self._icm_diff_pct_ = {}

        self._ko_fact_ = {}
        self._ko_fact_pct_ = {}
        self._ko_ev_ = {}
        self._ko_ev_pct_ = {}
        self._ko_diff_ = {}
        self._ko_diff_pct_ = {}

        self._ev_diff_ = {}
        self._ev_diff_pct = {}

        self.total_prizes = (self.hand.bi - self.hand.rake - self.hand.bounty) * 6
        self.player = str()
        self.flg_calculated = False


    def calc(self, player):
        if player not in self.players:
            raise PlayerNotFoundException()
        self.player = player
        self._equities_ = self._equities()
        self._chip_fact_ = self._chip_fact()
        self._chip_ev_ = self._chip_ev()
        self._chip_diff_ = self._chip_diff()
        self._chip_win_ = self._chip_win()
        self._icm_fact_pct_ = self._icm_fact_pct()
        self._icm_fact_ = self._icm_fact()
        self._icm_ev_pct_ = self._icm_ev_pct()
        self._icm_ev_ = self._icm_ev()
        if self.ko:
            self._ko_fact_pct_ = self._ko_fact_pct()
            self._ko_fact_ = self._ko_fact()
            self._ko_ev_pct_ = self._ko_ev_pct()
            self._ko_ev_ = self._ko_ev()
        self._ev_diff_ = self._ev_diff()
        self._chip_lose_ = self._chip_lose()
        self.flg_calculated = True

    @property
    def chip_lose(self):
        return self._chip_lose_

    @property
    def equities(self):
        return self._equities_

    @property
    def chip_fact(self):
        return self._chip_fact_

    @property
    def chip_ev(self):
        return self._chip_ev_
    @property
    def chip_diff(self):
        return self._chip_diff_

    @property
    def chip_win(self):
        return self._chip_win_

    @property
    def icm_ev_pct(self):
        # returns float
        return self._icm_ev_pct_

    @property
    def icm_ev(self):
        # returns float
        return self._icm_ev_

    @property
    def icm_fact(self):
        return self._icm_fact_

    @property
    def icm_fact_pct(self):
        return self._icm_fact_pct_

    @property
    def ko_ev_pct(self):
        return self._ko_ev_pct_

    @property
    def ko_ev(self):
        return self._ko_ev_

    @property
    def ko_fact(self):
        return self._ko_fact_

    @property
    def ko_fact_pct(self):
        return self._ko_fact_pct_

    @property
    def ev_diff(self):
        return self._ev_diff_

    def _chip_diff(self):
        res = {}
        for p in self.chip_fact.keys():
            res[p] = self.chip_ev[p] - self.chip_fact.get(p, 0)
        return res

    def _chip_lose(self):
        """
        returns stack distribution after self.player lose hand
        Если игрок не пошел алл ин результат тот же что и в функции chip_fact
        иначе уберем игрока из списка аллина,
        возьмем первого оставшегося игрока в списке (*пока считать для случая когда в аи больше 2 игроков не будем)
        todo расчет для случая когда в аи 3+ игроков
        допустим что он выиграл, отдалим ему все фишки из банка + анколед
        у остальных игроков :
            если игрок ставил олин, у него осталось только анколед
            если игрок не ставил олин, то вычтим из его стэка все расходы + анколед
        """
        players_went_to_shd = list(self.cards.keys())
        # logger.debug(players_went_to_shd)
        res = {}
        if self.player not in players_went_to_shd:
            # if player didnt go all in return fact distribution
            return self.chip_fact
        else:
            total_bets_amounts = self.hand.total_bets_amounts()
            # logger.debug(total_bets_amounts)
            # aiplayers = list(self.aiplayers)
            players = list(self.players)
            players_went_to_shd.pop(players_went_to_shd.index(self.player))
            # todo calculation if more then 2 players goes all-in
            # if len(aiplayers) == 1:
            # now consider fists player in list won hand
            # logger.debug(self.aiplayers)
            res[players_went_to_shd[0]] = sum(self.pots) + self.uncalled.get(players_went_to_shd[0] ,0)
            # logger.debug(res)
            players.pop(players.index(players_went_to_shd[0]))
            for p in players:
                if p in players_went_to_shd:
                    res[p] = self.uncalled.get(p, 0)
                else:
                    res[p] = self.chips.get(p, 0) \
                            - total_bets_amounts.get(p, 0) \
                            + self.uncalled.get(p, 0)
                # logger.debug(res)

        return res

    def _chip_win(self):
        # result int()
        # returns stack distribution after self.player won hand
        res = {}
        if self.player not in self.aiplayers:
            return self.chip_fact
        else:
            total_bets_amounts = self.hand.total_bets_amounts()

            for p in self.players:
                if p in self.aiplayers:
                    res[p] = self.uncalled.get(p, 0)
                else:
                    res[p] = self.chips.get(p, 0) \
                            - total_bets_amounts.get(p, 0) \
                            + self.uncalled.get(p, 0)
            res[self.player] = sum(self.pots) + self.uncalled.get(self.player,0)
            return res

    def _chip_fact(self):
        # returns dict {player: stack}
        res = {}
        total_bets_amounts = self.hand.total_bets_amounts()

        for p in self.players:
            if p in self.aiplayers:
                res[p] = sum(self.winnings_chips.get(p, [0]))+ self.uncalled.get(p, 0)
            else:
                res[p] = self.chips.get(p, 0) \
                         - total_bets_amounts.get(p, 0) \
                         + sum(self.winnings_chips.get(p, [0]))\
                         + self.uncalled.get(p, 0)
        return res

    def _chip_ev(self):
        # returns dict {player: stack}
        if not(self.hand.flg_showdown()):
            return self.chip_fact

        if not(self.aiplayers):
            return self.chip_fact

        res = {}
        eq = self.equities
        for p in self.chips.keys():
            if p in eq.keys():
                if p in self.aiplayers:
                    res[p] = int(round(self.pots[0] * eq[p] + self.uncalled.get(p, 0)))
                else:
                    res[p] = int(round(self.chips.get(p, 0) \
                             - self.hand.total_bets_amounts().get(p, 0) \
                             + self.pots[0] * eq[p]\
                             + self.uncalled.get(p, 0)))
            else:
                res[p] = self.chip_fact.get(p)

        return res

    def _ev_diff(self):
        total_diff = self.icm_diff + self.ko_diff
        return total_diff

    def _ev_diff_pct(self):
        total_diff = self.icm_diff + self.ko_diff
        return total_diff

    def _icm_ev(self):

        icm_exp = self.icm_ev_pct * self.total_prizes
        return icm_exp

    def _icm_ev_pct(self):

        p_win = self.equities.get(self.player, 0)
        ev_win = self.icm.calc(self.chip_win).get(self.player, 0)
        ev_lose = self.icm.calc(self.chip_lose).get(self.player, 0)

        ev = p_win * ev_win + (1 - p_win) * ev_lose

        return ev

    def _icm_fact(self):

        res = self.hand.prize_won()
        if res:
            return res
        else:
            res = {key: value * self.total_prizes for key, value in self._icm_fact_pct().items()}
            return res

    def _icm_fact_pct(self):
        prize_won = self.hand.prize_won()

        if prize_won:
            res = {key: value / self.total_prizes for key, value in prize_won.items()}
            return res
        else:
            res = {key: value for key, value in self.icm.calc(self.chip_fact).items()}
            return res

    def _ko_ev(self):
        res = self.ko_ev_pct * self.hand.bounty

        return res

    def _ko_ev_pct(self):
        # returns: float
        # how many bounties player expected to get
        # todo реализовать различные модели баунти
        # посчитаем также как и icm_ev
        # если игрок выиграл и выбил другого игрока, то добавим к его нокаутам количество игроков которых он выбил
        # ev = p_win * ko_ev(win) + (1 - p_win) * ko_ev(lose)
        if not self.ko:
            return 0

        p_win = self.equities.get(self.player, 0)
        ev_win = self.ko.calc(self.chip_win).get(self.player, 0)
        ko_get = self.non_zero_values(self.chips) - self.non_zero_values(self.chip_win)
        ev_win += ko_get
        ev_lose = self.ko.calc(self.chip_lose).get(self.player, 0)
        # logger.debug(p_win)
        # logger.debug(ev_win)
        # logger.debug(self.chip_lose)

        ev = p_win * ev_win + (1 - p_win) * ev_lose

        return ev

    def _ko_fact(self):
        res = {}
        for key, value in self.ko_fact_pct.items():
            res[key] = value * self.hand.bounty

        return res

    def _ko_fact_pct(self):
        res = {}
        who_won_bounty = self.hand.bounty_won().keys()
        chips = self.chip_fact
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

    def _equities(self):
        hands = list(self.cards.values())
        players = list(self.cards.keys())
        p_ai_players = []
        f_ai_players = []
        t_ai_players = []
        for p in players:
            if self.hand.p_ai_players():
                p_actions = self.hand.p_last_action()
                if p_actions.get(p, 'f') != 'f':
                    p_ai_players.append(p)

            if self.hand.f_ai_players():
                f_actions = self.hand.f_last_action()
                if f_actions.get(p, 'f') != 'f':
                    f_ai_players.append(p)

            if self.hand.t_ai_players():
                t_actions = self.hand.t_last_action()
                if t_actions.get(p, 'f') != 'f':
                    t_ai_players.append(p)

        if p_ai_players:
            if len(players) == 2:
                hand1 = self.cards.get(players[0])
                hand2 = self.cards.get(players[1])
                hand1 = map(eval7.Card, hand1.split())
                hand2 = eval7.HandRange(''.join(hand2.split()))
                board = []
                equity = eval7.py_hand_vs_range_monte_carlo(
                    hand1, hand2, board, self.trials
                )
                return {players[0]: equity, players[1]: 1-equity}

        if f_ai_players:
            players = f_ai_players
            if len(players) == 2:
                hand1 = self.cards.get(players[0])
                hand2 = self.cards.get(players[1])
                hand1 = map(eval7.Card, hand1.split())
                hand2 = eval7.HandRange(''.join(hand2.split()))
                board = tuple(map(eval7.Card, self.hand.flop().split()))
                equity = eval7.py_hand_vs_range_monte_carlo(
                    hand1, hand2, board, self.trials
                )
                return {players[0]: equity, players[1]: 1-equity}

        if t_ai_players:
            players = t_ai_players
            if len(players) == 2:
                hand1 = self.cards.get(players[0])
                hand2 = self.cards.get(players[1])
                hand1 = map(eval7.Card, hand1.split())
                hand2 = eval7.HandRange(''.join(hand2.split()))
                board = tuple(map(eval7.Card, (self.hand.flop() + ' ' + self.hand.turn()).split()))
                equity = eval7.py_hand_vs_range_monte_carlo(
                    hand1, hand2, board, self.trials
                )
                return {players[0]: equity, players[1]: 1-equity}
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

from collections import defaultdict

class StacksDict(defaultdict):

    @classmethod
    def newdict(cls):
        return cls()

    def __add__(self, other):
        res = StacksDict.newdict()
        for k, v in other.items():
            res[k] = v + self[k]
        return res

    def __sub__(self, other):
        res = StacksDict.newdict()
        for k, v in other.items():
            res[k] = v - self[k]
        return res

    def __mul__(self, other):
        pass

    def __repr__(self):

        res = '{'
        for k, v in self.items():
            res = res + f'{k}: {v}, '

        res = self.__class__.__name__ + '(' + res + '})'
        return res

    def __str__(self):
        res = '{'
        for k, v in self.items():
            res = res + f'{k}: {v}, '

        res = res + '}'
        return res