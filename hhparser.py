# -*- coding: utf-8 -*-
"""
Created on Tue Aug  9 14:02:58 2016

@author: ThaiSSD
"""
import re
import numpy as np
import itertools

ACTIONS = {
    'calls': 'c',
    'raises': 'r',
    'folds': 'f',
    'bets': 'b',
    'checks': 'x'
}


class HHParser:
    PRIZE = []
    POSITIONS = ['BB', 'SB', 'BU', 'CO', 'MP2', 'MP1', 'UTG3', 'UTG2', 'UTG1']
    UNCALLED_REGEX = "Uncalled.*\((?P<bet>\d+)\).*to (?P<player>.*)"
    UNCALLED_DICT = {'player': 'bet'}
    CHIPWON_REGEX = "Seat \d: (?P<player>.*?) .*(?:and won|collected) \((?P<chipwon>.*)\)"
    CHIPWON_DICT = {'player': 'chipwon'}
    FINISHES_REGEX = "(?P<player>.*?) (?:finished.*in (?P<place>\d+)(?:nd|rd|th)|wins the tournament)"
    # {player: None} treats as 1st place

    def __init__(self, hh):
        #       todo проверка является ли строка hand history
        self.hand_history = hh

        #       split the original hand histoty into logical sections preflop flop ...
        hist_text = self.hand_history

        self.summary_str = hist_text[hist_text.find("*** SUMMARY ***"):]
        hist_text = hist_text[:hist_text.find("*** SUMMARY ***")]

        self.showdown_str = hist_text[hist_text.find("*** SHOW DOWN ***"):]
        hist_text = hist_text[:hist_text.find("*** SHOW DOWN ***")]

        self.river_str = hist_text[hist_text.find("*** RIVER ***"):]
        hist_text = hist_text[:hist_text.find("*** RIVER ***")]

        self.turn_str = hist_text[hist_text.find("*** TURN ***"):]
        hist_text = hist_text[:hist_text.find("*** TURN ***")]

        self.flop_str = hist_text[hist_text.find("*** FLOP ***"):]
        hist_text = hist_text[:hist_text.find("*** FLOP ***")]

        self.preflop_str = hist_text[hist_text.find("*** HOLE CARDS ***"):]
        hist_text = hist_text[:hist_text.find("*** HOLE CARDS ***")]

        self.caption_str = hist_text

        self.HeroCards = ""
        self.Hero = ""
        self.KnownCardsDict = {}
        self.bounty = 0.0
        self.rake = 0.0
        self.bi = 0.0
        self.sb = 0
        self.bb = 0
        self.stacks = []
        self.players = []
        self.ante = 0
        self.small_blind = 0
        self.big_blind = 0
        self.preflop_order = []  # чем больше число чем позже принимает решение
        self.flop = ""
        self.turn = ""
        self.river = ""
        self.winnings = {}
        self.chipwinnings = {}
        self.p_amounts = {}
        self.f_amounts = {}
        self.t_amounts = {}
        self.r_amounts = {}
        self.players_dict = {}
        self.p_actions = []
        self.blinds_ante = {}
        self.uncalled = {}
        self.bounty_won = {}
        self.prize_won = {}
        self.finishes = {}
        self.chip_won = {}

        #        regex_ps =  "\s?PokerStars\s+?Hand"
        #        regex_888 = "\s?888poker\s+?Hand"
        #        t = re.compile(regex_ps)
        #        if t.match(self.hand_history):
        #            print("poker stars hand detected")
        regex = "Seat\s?[0-9]:\s(.*)\s\(\s?\$?(\d*,?\d*)\s(?:in\schips)?"
        sbplayer_regex = "(.*)?:\sposts small"
        bbplayer_regex = "(.*)?:\sposts big"
        blinds_regex = "Level\s.+\s\((?P<sb>\d+)/(?P<bb>\d+)\)"
        bi_knock_regex = "Tournament\s#\d+,\s\$(?P<bi>\d+?\.\d+)\+\$(?P<bounty>\d+?\.\d+)\+\$(?P<rake>\d+?\.\d+)"
        #        t = re.search(regex)

        self.PRIZE = np.array([0.50, 0.50])

        tupples = re.findall(regex, self.hand_history)

        self.players = [x[0] for x in tupples]
        self.stacks = [float(x[1].replace(",", "")) for x in tupples]
        self.players_dict = {x[0]: float(x[1].replace(",", "")) for x in tupples}
        #       удаление нулевых стэков
        try:
            self.stacks.index(0.0)
            print(self.stacks.index(0.0))
            while self.stacks.index(0.0) + 1:
                n = self.stacks.index(0.0)
                self.stacks.remove(0.0)
                self.players.pop(n)
        except ValueError:
            pass
        finally:
            pass

        res = re.search(bbplayer_regex, self.hand_history)
        if res:
            self.big_blind = self.players.index(res.group(1))
            self.preflop_order = self.players[self.big_blind + 1:] + self.players[:self.big_blind + 1]
        else:
            res = re.search(sbplayer_regex, self.hand_history)
            if res:
                self.small_blind = self.players.index(res.group(1))
                self.preflop_order = self.players[self.small_blind + 1:] + self.players[:self.small_blind + 1]

        # в префлоп ордер теперь содержится порядок действия игроков как они сидят префлоп от утг до бб

        res = re.search(blinds_regex, self.hand_history)
        if res:
            self.sb = int(res.groupdict().get('sb', '10'))
            self.bb = int(res.groupdict().get('bb', '20'))

        res = re.search(bi_knock_regex, self.hand_history)
        if res:
            self.bounty = float(res.groupdict().get('bounty'))
            self.rake = float(res.groupdict().get('rake'))
            self.bi = float(res.groupdict().get('bi')) + self.bounty + self.rake

    def p1p(self, ind, place):
        #       вероятность place го места для игрока ind

        #       s - список стэков игроков
        #       ind - индекс стэка для которого считаестя вероятность
        #       place - место целое число, должно быть не больше чем длина списка s

        sz = self.getPlayersNumber()

        #
        if place > sz:
            return 0
        if ind + 1 > sz:
            return 0
        #       если стэк 0 сразу вернем 0

        if self.getStack(ind) == 0:
            if sz - 1 >= np.size(self.PRIZE):
                return 0
            else:
                return self.PRIZE[sz - 1]

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
                    si.append(self.getStack(j))
                #                    with Profiler() as pr:
                pi = 1
                for j in range(sz):
                    sum_ = sum(si[j:])
                    if sum_ != 0:
                        pi = pi * si[j] / sum_

                p.append(pi)

        result = sum(p)
        return result

    def icm_eq(self, stacks=None):
        if stacks is not None:
            SZ = np.size(stacks)
        else:
            SZ = np.size(self.stacks)
            stacks = np.copy(self.stacks)

        #        place_probe = np.zeros(SZ, 3)

        #       end p1p()

        #       perm = itertools.permutations(range(SZ), SZ)

        ind1 = range(0, SZ)

        min_place = min(SZ, np.size(self.PRIZE))
        p1 = np.zeros(shape=(min_place, SZ))
        ind2 = range(0, min_place)
        # p1 строка - занятое место, столбец - номер игрока
        for i in ind1:
            for j in ind2:
                p1[j, i] = self.p1p(i, j + 1)
                # в функции место нумеруются с 1 до 3, в матрице с 0 до 2  

        #
        eq = np.dot(self.PRIZE[:min_place], p1)
        return eq

    def icm_eq_dict(self, stacks=None):
        if stacks is not None:
            SZ = np.size(stacks)
        else:
            SZ = np.size(self.stacks)
            stacks = np.copy(self.stacks)
        ind1 = range(0, SZ)
        min_place = min(SZ, np.size(self.PRIZE))
        p1 = np.zeros(shape=(min_place, SZ))
        ind2 = range(0, min_place)
        # p1 строка - занятое место, столбец - номер игрока
        for i in ind1:
            for j in ind2:
                p1[j, i] = self.p1p(i, j + 1)
                # в функции место нумеруются с 1 до 3, в матрице с 0 до 2
        #
        eq = np.dot(self.PRIZE[:min_place], p1)
        return {self.players[i]: round(eq[i], 4) for i in range(SZ)}

    def tie_factor(self):
        eq = self.icm_eq()
        st = np.array(self.stacks)
        sz = np.size(st)
        result = np.zeros((sz, sz))
        for i in range(sz):
            for j in range(sz):
                if i == j:
                    continue

                stacks_win = np.copy(st)
                stacks_lose = np.copy(st)
                if st[i] > st[j]:
                    stacks_win[i] = st[i] + st[j]
                    stacks_win[j] = 0
                    stacks_lose[i] = st[i] - st[j]
                    stacks_lose[j] = st[j] * 2
                else:
                    stacks_win[i] = st[i] * 2
                    stacks_win[j] = st[j] - st[i]
                    stacks_lose[i] = 0
                    stacks_lose[j] = st[i] + st[j]
                eq_win = self.icm_eq(stacks_win)
                eq_lose = self.icm_eq(stacks_lose)
                #                print(stacks_win)
                #                print(stacks_lose)
                #                print(eq_win)
                #                print(eq_lose)
                #
                #                print(i, j)
                bubble_factor = (eq[i] - eq_lose[i]) / (eq_win[i] - eq[i])
                result[i, j] = bubble_factor / (1 + bubble_factor)
        #                if i > 1 and j > 1: return result
        return result

    def tournamentPosition(self, player):

        try:
            i = self.players.index(player)
        except ValueError:
            #            print("no player " + player)
            return -1

        sp = self.stacks[i]
        result = 1
        #
        for s in self.stacks:
            if s > sp:
                result += 1

        return result

    def tablePosition(self, player):
        # сколько еще игроков будут действовать на префлопе после игрока
        return self.preflop_order

    def isChipLeader(self, player):

        if self.tournamentPosition(player) == 1:
            return True
        else:
            return False

    def tournamentPositionL(self, player):
        # позиция игрока среди игроков сидящих слева т.е. действующих на префлопе после него

        if self.big_blind:
            if self.big_blind == self.players.index(player):
                return self.tournamentPosition(player)

        try:
            i = self.players.index(player)

        except ValueError:
            print("no player " + player)
            return -1

        sp = self.stacks[i]
        result = 1

        i = self.preflop_order.index(player)
        for s in [self.stacks[ind1] for ind1 in [self.players.index(p) for p in self.preflop_order[i:]]]:
            if s > sp:
                result += 1

        return result

    def getStack(self, player):
        #       возвращает стэк игрока
        #       player - номер игрока int или имя игрока str
        #
        sp = 0
        if type(player) is str:
            try:
                i = self.players.index(player)
            except ValueError:
                print("no player " + player)
                return -1

            sp = self.stacks[i]

        if type(player) is int:
            try:
                sp = self.stacks[player]
            except IndexError:
                print("no such index " + player)
                return -1

        return sp

    def getStacks(self):
        # returns dict {player: stack}
        return self.players_dict

    def getStackList(self):
        #       возвращает сисок стэков
        #
        return self.stacks

    def isChipLeaderL(self, player):

        if self.tournamentPositionL(player) == 1:
            return True
        else:
            return False

    def getPlayersNumber(self):
        #   возвращает число игроков
        #
        return len(self.stacks)

    def getPlayerDict(self):
        #   returns dict {position: playername}
        return {self.POSITIONS[i]: self.preflop_order[::-1][i] for i in range(len(self.preflop_order))}

    def getPlayersDict(self):
        return self.players_dict

    def isKnockoutTournament(self):
        try:
            if self.bounty:
                return True

        except AttributeError:
            return False
        return False

    def getStackDict(self):
        #       returns dict {position: stack}
        return {self.POSITIONS[i]: self.getStack(self.preflop_order[::-1][i]) for i in range(len(self.preflop_order))}

    def getBlinds(self):

        return [self.sb, self.bb]

    def getBI(self):

        return self.bi

    def flgRFIOpp(self, player):
        #       returns true if player has opportunity of first action
        rfi_regex = f'(folds\s{player}|]\s{player})'
        if re.search(rfi_regex, self.hand_history):
            return True
        return False

    def flgFacedAI(self, player):
        return False

    def getTournamentID(self):

        id_regex = "Tournament #(?P<tid>\d+)"
        res = re.search(id_regex, self.hand_history)
        if res:
            return res.groupdict().get('tid')

    def getHandID(self):

        id_regex = "Hand #(?P<hid>\d+)"
        res = re.search(id_regex, self.hand_history)
        if res:
            return res.groupdict().get('hid')
        else:
            return 0

    def getDateTimeET(self):

        datetime_regex = r"(?P<datetime>\d{4}/\d{2}/\d{2}\s\d{1,2}:\d{1,2}:\d{1,2})\sET"
        res = re.search(datetime_regex, self.hand_history)
        if res:
            return res.groupdict().get('datetime')
        else:
            return 0

    def getPActions(self):

        regex = r"(?P<player>.*):\s(?P<action>calls|raises|folds|checks)"
        res = re.findall(regex, self.preflop_str)
        if res:
            self.p_actions = [ACTIONS[x[1]] for x in res]
            return self.p_actions

    def getFActions(self):

        regex = r"(?P<player>.*):\s(?P<action>calls|raises|folds|checks|bets)"
        res = re.findall(regex, self.flop_str)
        self.FActions = []
        if res:
            self.FActions = [ACTIONS[x[1]] for x in res]

        return self.FActions

    def getTActions(self):

        regex = r"(?P<player>.*):\s(?P<action>calls|raises|folds|checks|bets)"
        res = re.findall(regex, self.turn_str)
        self.TActions = []
        if res:
            self.TActions = [ACTIONS[x[1]] for x in res]

        return self.TActions

    def getRActions(self):

        regex = r"(?P<player>.*):\s(?P<action>calls|raises|folds|checks|bets)"
        res = re.findall(regex, self.river_str)
        self.RActions = []
        if res:
            self.RActions = [ACTIONS[x[1]] for x in res]

        return self.RActions

    def getPAIPlayers(self):
        #       returns list of players which is all in preflop

        regex = r"(?P<player>.*):.* all-in"
        res = re.findall(regex, self.preflop_str)
        self.PAIPlayers = []
        if res:
            self.PAIPlayers = [x for x in res]

        return self.PAIPlayers

    def getFAIPlayers(self):

        regex = r"(?P<player>.*):.* all-in"
        res = re.findall(regex, self.flop_str)
        self.FAIPlayers = []
        if res:
            self.FAIPlayers = [x for x in res]

        return self.FAIPlayers

    def getTAIPlayers(self):

        regex = r"(?P<player>.*):.* all-in"
        res = re.findall(regex, self.turn_str)
        self.TAIPlayers = []
        if res:
            self.TAIPlayers = [x for x in res]

        return self.TAIPlayers

    def getRAIPlayers(self):

        regex = r"(?P<player>.*):.* all-in"
        res = re.findall(regex, self.river_str)
        self.RAIPlayers = []
        if res:
            self.RAIPlayers = [x for x in res]

        return self.RAIPlayers

    def getPotList(self):
        #       returns list with 1st item is total pot and all af the side pots if presents
        regex = r"(Total|Main|Side) (pot|pot-1|pot-2|pot-3|pot-4|pot-5)\s(?P<pot>\d*)"
        res = re.findall(regex, self.summary_str)
        self.PotList = []
        if res:
            self.PotList = [float(x[2]) for x in res]
        return self.PotList

    def getPActionsAmount(self):

        regex = "(?P<player>.*?): (?:calls|raises.*to|bets) (?P<amount>\d*)"
        res = re.findall(regex, self.preflop_str)

        if self.p_amounts:
            return self.p_amounts
        else:
            if res:
                for x in res:
                    if self.p_amounts.get(x[0]):
                        self.p_amounts[x[0]].append(int(x[1]))
                    else:
                        self.p_amounts[x[0]] = [int(x[1])]

        return self.p_amounts

    def getFActionsAmount(self):

        regex = "(?P<player>.*?): (?:calls|raises.*to|bets) (?P<amount>\d*)"
        res = re.findall(regex, self.flop_str)

        if self.f_amounts:
            return self.f_amounts
        else:
            if res:
                for x in res:
                    if self.f_amounts.get(x[0]):
                        self.f_amounts[x[0]].append(int(x[1]))
                    else:
                        self.f_amounts[x[0]] = [int(x[1])]

        return self.f_amounts

    def getTActionsAmount(self):

        regex = "(?P<player>.*?): (?:calls|raises.*to|bets) (?P<amount>\d*)"
        res = re.findall(regex, self.turn_str)

        if self.t_amounts:
            return self.t_amounts
        else:
            if res:
                for x in res:
                    if self.t_amounts.get(x[0]):
                        self.t_amounts[x[0]].append(int(x[1]))
                    else:
                        self.t_amounts[x[0]] = [int(x[1])]

        return self.t_amounts

    def getRActionsAmount(self):

        regex = "(?P<player>.*?): (?:calls|raises.*to|bets) (?P<amount>\d*)"
        res = re.findall(regex, self.river_str)

        if self.r_amounts:
            return self.r_amounts
        else:
            if res:
                for x in res:
                    if self.r_amounts.get(x[0]):
                        self.r_amounts[x[0]].append(int(x[1]))
                    else:
                        self.r_amounts[x[0]] = [int(x[1])]

        return self.r_amounts

    def getHero(self):
        #       returns hero name
        regex = r"Dealt to (?P<hero>.*)\s\["
        res = re.search(regex, self.preflop_str)

        if self.Hero:
            return self.Hero
        else:
            if res:
                self.Hero = res.groupdict().get('hero')

        return self.Hero

    def getHeroCards(self):

        regex = r"Dealt to .*\s\[(?P<cards>.*)]"
        res = re.search(regex, self.preflop_str)

        if self.HeroCards:
            return self.HeroCards
        else:
            if res:
                #               delete spaces
                self.HeroCards = re.sub(r'\s+', '', res.groupdict().get('cards'), flags=re.UNICODE)

        return self.HeroCards

    def getKnownCards(self):

        regex = "Seat \d: (?P<player>.*?)\s?(?:\(button\) showed|\(small blind\) showed|\(button\) \(small blind\) showed|\(big blind\) showed| showed)\s\[(?P<knowncards>.*)\]"
        res = re.findall(regex, self.summary_str)

        if self.KnownCardsDict:
            return self.KnownCardsDict
        else:
            if res:
                self.KnownCardsDict = {x[0]: re.sub(r'\s+', '', x[1], flags=re.UNICODE) for x in res}

        return self.KnownCardsDict

    def getFlop(self):
        regex = "FLOP.*\[(?P<flop>.*)\]"
        res = re.search(regex, self.flop_str)

        if self.flop:
            return self.flop
        else:
            if res:
                self.flop = re.sub(r'\s+', '', res.groupdict().get('flop'), flags=re.UNICODE)

        return self.flop

    def getTurn(self):
        regex = "TURN.*\[(?:.*)\] \[(?P<turn>.{2})\]"
        res = re.search(regex, self.turn_str)

        if self.turn:
            return self.turn
        else:
            if res:
                self.turn = res.groupdict().get('turn')

        return self.turn

    def getRiver(self):
        regex = "RIVER.*\[(?:.*)\] \[(?P<river>.{2})\]"
        res = re.search(regex, self.river_str)

        if self.river:
            return self.river
        else:
            if res:
                self.river = res.groupdict().get('river')

        return self.river
        pass

    def getBountyWon(self):
        #       winning in tournament
        regex = "(?P<player>.*) wins the \$(?P<bounty>.*) bounty"
        if self.bounty_won:
            return self.bounty_won
        else:
            self.bounty_won = self._process_regexp(regex, self.showdown_str, type_func=lambda x: float(x), **{'player':'bounty'})
            return self.bounty_won

    def getPrizeWon(self):
        regex = "(?P<player>.*?) .*and (?:received|receives) \$(?P<prize>\d+\.\d+)(?:.|\s)"
        if self.prize_won:
            return self.prize_won
        else:
            self.prize_won = self._process_regexp(regex, self.showdown_str, type_func=lambda x: float(x), **{'player':'prize'})
            return self.prize_won

    def getChipWon(self):

        if self.chip_won:
            return self.chip_won
        else:
            self.chip_won = self._process_regexp(self.CHIPWON_REGEX,
                                                 self.summary_str,
                                                 type_func=lambda x: int(x),
                                                 **self.CHIPWON_DICT)
            return self.chip_won

    def getFinishes(self):
        if self.finishes:
            return self.finishes
        else:
            self.finishes = self._process_regexp(self.FINISHES_REGEX,
                                                   self.showdown_str,
                                                   type_func=lambda x: int(x),
                                                   **{'player':'place'})
            return self.finishes

    def getBlidnsAnte(self):
        #returns dict {player: bet before preflop}
        regex = "(?P<player>.*): posts .*?(?P<bet>\d+)"

        if self.blinds_ante:
            return self.blinds_ante
        else:
            res = re.findall(regex, self.caption_str)
            if res:
                dic = {}
                for x in res:
                    if dic.get(x[0], 0) == 0:
                        dic[x[0]] = int(x[1])
                    else:
                        dic[x[0]] = dic.get(x[0]) + int(x[1])

                self.blinds_ante = dic

        return self.blinds_ante

    def getUncalled(self):
        #returns dict {player: bet}
        if self.uncalled:
            return self.uncalled
        else:
            self.uncalled = self._process_regexp(self.UNCALLED_REGEX,
                                                 self.hand_history,
                                                 type_func=lambda x: int(x),
                                                 **self.UNCALLED_DICT)
            return self.uncalled

    def positions(self):
    #     returns dict{player: position}
        return {self.preflop_order[::-1][i]: self.POSITIONS[i] for i in range(len(self.preflop_order))}

    def _process_regexp(self, pattern, text, type_func=lambda x:x, *args, **kwargs):
        # extracts named groups from result of re and converts it into dict or list
        it = re.finditer(pattern, text)

        res = []
        for x in args:
            for i in it:
                try:
                    res.append(type_func(i.groupdict().get(x)))
                    res = [type_func(i.groupdict().get(x)) for i in it]
                except TypeError:
                    res.append(i.groupdict().get(x))

        res = {}
        for k, v in kwargs.items():
            for i in it:
                try:
                    res[i.groupdict().get(k)] = type_func(i.groupdict().get(v))
                except TypeError:
                    res[i.groupdict().get(k)] = i.groupdict().get(v)

        return res

