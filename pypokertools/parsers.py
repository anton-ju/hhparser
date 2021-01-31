"""
Created on Tue Aug  9 14:02:58 2016

@author: anton-ju
"""

import re
import numpy as np
import itertools
from datetime import datetime
from bs4 import BeautifulSoup as bs
from typing import List, Dict

ACTIONS = {
    'calls': 'c',
    'raises': 'r',
    'folds': 'f',
    'bets': 'b',
    'checks': 'x'
}


class HRCOutput():
    STRATEGY_TABLE_COLUMNS = ('strategy',
                              'amount',
                              'player',
                              'range_pct',
                              'range_txt',
                              'ev_ref')

    def __init__(self, html):
        self.html_source = html

        self.hrc_output = bs(html, features="html.parser")
        self.stacks_table = self.get_stacks_table()

        self.strategy_table = self.get_strategy_table()

    def get_stacks_table(self):

        stacks_table = self.hrc_output.find_all('table', attrs={'class': 'stackstable'})

        chips = stacks_table[0].find_all('td', attrs={'class': 'chips'})
        players = stacks_table[0].find_all('td', attrs={'class': 'player'})
        blinds = stacks_table[0].find_all('td', attrs={'class': 'blinds'})

        res = []
        for player, chip, blind in zip(players, chips, blinds):
            res.append((player.text, chip.text, blind.text))

        return res

    def get_strategy_table(self):

        strategy_table = self.hrc_output.find_all('table',
                                                  attrs={'class': 'strategyoverview'})
        refs = [tag.attrs.get('name') for tag in strategy_table[0].find_all(lambda tag: 'name' in tag.attrs)]
        refs.insert(0, '')

        rows = []
        for tr, ref in zip(strategy_table[0].find_all('tr'), refs):
            row = []
            for td in tr:
                row.append(str.strip(td.text))
            row.append(ref)
            rows.append(row)
        rows[0] = ['action_1',
                   'action_2',
                   'action_3',
                   'amount',
                   'player',
                   'range_pct', 'range_txt', 'ev_ref']
        result = []

        def format_table(st):
            for number, row in enumerate(st):
                strategy, amount, player, range_pct, range_txt, ev_ref = row
                if strategy.startswith('--'):
                    for r in st[number-1::-1]:
                        s, _, p, _, _, _ = r
                        if not s.startswith('--'):
                            player = ','.join([p, player])
                            break
                elif strategy.startswith('-'):
                    for r in st[number-1::-1]:
                        s, _, p, _, _, _ = r
                        if not s.startswith('-'):
                            player = ','.join([p, player])
                            break

                st[number] = strategy, amount, player, range_pct, range_txt, ev_ref

        def replace_empty(s: str):
            if len(str.strip(s)) == 0:
                s = '-'

            return s

        for row in rows:
            result.append([replace_empty(row[0]) +
                           replace_empty(row[1]) + replace_empty(row[2]),
                           row[3], row[4], row[5], row[6], row[7]])

        format_table(result)

        result[0] = self.STRATEGY_TABLE_COLUMNS
        return result

    def get_ev_table_by_ref(self, ref):
        name_attr = ref.replace('o', 'r')
        ev_table = self.hrc_output.find('a', attrs={'name': name_attr}).find_next('table')

        rows = []
        for td in ev_table.find_all('td'):
            rows.append((td.text.replace(td.ev.text, '').replace(td.pl.text, ''),
                         td.ev.text, td.pl.text))
        return rows

    def get_ref_by_player(self, player: str):
        """
        :param player: string player or players e.x. 'player1,player2', 'BU'
        :return: reference is a string for get_ev_table_by_ref function
        """
        for row in self.strategy_table:
            strategy, amount, players, range_pct, range_txt, ev_ref = row
            if player == players:
                return ev_ref

    def get_hand_ev(self, hand, player):
        ref = self.get_ref_by_player(player)
        if ref:
            ev_table = self.get_ev_table_by_ref(ref)

            for row in ev_table:
                hand_str, ev, pct = row
                if hand_str == hand:
                    return ev

    def get_range(self, player: str):
        """
        :param player: string player or players e.x. 'player1,player2', 'BU'
        :return: tuple (range % , range text)
        """
        for row in self.strategy_table:
            strategy, amount, players, range_pct, range_txt, ev_ref = row
            if player == players:
                return ','.join([range_pct, range_txt])


class cached_property(object):
    def __init__(self, func):
        self.func = func

    def __get__(self, instance, cls=None):
        result = instance.__dict__[self.func.__name__] = self.func(instance)
        return result


class Actions(enumerate):
    pass


class HandHistoryParser:
    PRIZE = []
    POSITIONS = ['BB', 'SB', 'BU', 'CO', 'MP2', 'MP1', 'UTG3', 'UTG2', 'UTG1']
    UNCALLED_REGEX = "Uncalled.*\((?P<bet>\d+)\).*to (?P<player>.*)"
    UNCALLED_DICT = {'player': 'bet'}
    CHIPWON_REGEX = "(?P<player>.*) collected (?P<chipwon>\d+)"
    CHIPWON_DICT = {'player': 'chipwon'}
    FINISHES_REGEX = "(?P<player>.*?) (?:finished.*in (?P<place>\d+)(?:nd|rd|th)|wins the tournament)"
    PRIZE_WON_REGEX = "(?P<player>.*) (?:wins|finished).*and (?:received|receives) \$(?P<prize>\d+\.?\d+)(?:.|\s)"
    BLINDS_ANTE_REGEX = "(?P<player>.*): posts .*?(?P<bet>\d+)"
    BOUNTY_WON_REGEX = "(?P<player>.*) wins the \$(?P<bounty>.*) bounty"
    RIVER_REGEX = "RIVER.*\[(?:.*)\] \[(?P<river>.{2})\]"
    TURN_REGEX = "TURN.*\[(?:.*)\] \[(?P<turn>.{2})\]"
    ANTE_REGEX = "(?P<player>.*): posts the ante (?P<bet>\d+)"
    BLINDS_REGEX = "(?P<player>.*): posts (?:small|big) blind (?P<bet>\d+)"
    BLINDS_ANTE_DICT = {'player': 'bet'}
    SB_PLAYER_REGEX = "(?P<player>.*):\sposts small"
    BB_PLAYER_REGEX = "(?P<player>.*):\sposts big"
    P_ACTIONS_REGEX = "(?P<player>.*):\s(?P<action>calls|raises|folds|checks)"
    ACTIONS_REGEX = "(?P<player>.*):\s(?P<action>calls|raises|bets|folds|checks)"
    ACTIONS_DICT = {'player': 'action'}
    ACTIONS_AMOUNTS_REGEX = "(?P<player>.*?): (?:calls|raises.*to|bets|checks) (?P<amount>\d+)?"
    ACTIONS_AMOUNTS_DICT = {'player': 'amount'}
    AI_PLAYERS_REGEX = "(?P<player>.*):.* all-in"
    KNOWN_CARDS_REGEX = "Seat \d: (?P<player>.*?)\s?(?:\(button\) showed|\(small blind\) showed|\(button\) \(small blind\) showed|\(big blind\) showed| showed)\s\[(?P<knowncards>.*)\]"
    KNOWN_CARDS_DICT = {'player': 'knowncards'}
    FLOP_REGEX = "FLOP.*\[(?P<flop>.*)\]"
    POT_LIST_REGEX = "(Total|Main|Side) (pot|pot-1|pot-2|pot-3|pot-4|pot-5)\s(?P<pot>\d*)"
    DATETIME_REGEX = "(?P<datetime>\d{4}/\d{2}/\d{2}\s\d{1,2}:\d{1,2}:\d{1,2})\sET"
    TID_REGEX = "Tournament #(?P<tid>\d+)"
    HID_REGEX = "Hand #(?P<hid>\d+)"
    HERO_REGEX = r"Dealt to (?P<hero>.*)\s\["
    HERO_CARDS_REGEX = r"Dealt to .*\s\[(?P<cards>.*)]"
    BI_BOUNTY_RAKE_REGEX = "Tournament\s#\d+,\s\$(?P<bi>\d+?\.\d+)(?:\+\$)?(?P<bounty>\d+?\.\d+)?\+\$(?P<rake>\d+?\.\d+)"

    def _process_regexp(
            self,
            pattern,
            text,
            *args,
            type_func=lambda x: x,
            reslist=False,
            default_value=0,
            replace_none=True,
            **kwargs):
        """

        :param pattern: regex
        :param text: text
        :param args: list with group name to extract,
        if you want to extract values into list
        :param type_func: function for type casting
        :param reslist: boolean -> if you want to get dict with list values
        else same key will results will be added
        :param default_value: for reslist
        :param kwargs: dict with group names to extract
        :return:
        extracts named groups from result of re
        and converts it into dict or list
        """
        it = re.finditer(pattern, text)

        res = []
        for x in args:
            for i in it:
                try:
                    res.append(type_func(i.groupdict().get(x)))
                except TypeError:
                    res.append(i.groupdict().get(x))
            if reslist:
                return res
            else:
                return default_value if len(res) == 0 else res[0]
        res = {}
        for k, v in kwargs.items():
            for i in it:
                key = i.groupdict().get(k)
                value = i.groupdict().get(v, default_value)
                if replace_none and value is None:
                    value = default_value
                try:
                    if reslist:
                        if res.get(key):
                            res[key].append(type_func(value))
                        else:
                            res[key] = [type_func(value)]
                    else:
                        if res.get(key):
                            res[key] += type_func(value)
                        else:
                            res[key] = type_func(value)
                except TypeError:
                    if reslist:
                        if res.get(key):
                            res[key].append(value)
                        else:
                            res[key] = [value]
                    else:
                        res[key] = value
            return res


class PSTournamentSummary(HandHistoryParser):

    FINISHES_REGEX = "You finished in (?P<place>\d+)(?:nd|rd|th|st)"
    PRIZE_WON_REGEX = "(?:\d+):\s(?P<player>.*)\s\(.*\),\s\$(?P<prize>\d+\.\d+)"

    def __init__(self, ts_text):
        self.ts_text = ts_text

    def __str__(self):
        return f"Tournament: #{self.tid} Finish: {self.finishes} Prize: {self.prize_won}"

    @cached_property
    def tid(self):
        return self._process_regexp(self.TID_REGEX, self.ts_text, 'tid')

    @cached_property
    def finishes(self):
        return self._process_regexp(self.FINISHES_REGEX,
                                    self.ts_text,
                                    type_func=lambda x: int(x),
                                    *['place'])

    @cached_property
    def prize_won(self):
        return self._process_regexp(self.PRIZE_WON_REGEX,
                                    self.ts_text,
                                    type_func=lambda x: float(x),
                                    **{'player': 'prize'})


class PSHandHistory(HandHistoryParser):

    def __str__(self):
        return f"Hand: #{self.hid} Tournament: #{self.tid} \${self.bi} [{self.datetime}]"

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

        self.sb = 0
        self.bb = 0
        self._chips_list = []
        self.players = []
        self.small_blind = 0
        self.big_blind = 0
        self.preflop_order = []  # чем больше число чем позже принимает решение

        regex = "Seat\s?[0-9]:\s(.*)\s\(\s?\$?(\d*,?\d*)\s(?:in\schips)?"
        sbplayer_regex = "(.*)?:\sposts small"
        bbplayer_regex = "(.*)?:\sposts big"
        blinds_regex = "Level\s.+\s\((?P<sb>\d+)/(?P<bb>\d+)\)"
        self.PRIZE = np.array([0.50, 0.50])

        tuples = re.findall(regex, self.hand_history)

        self.players = [x[0] for x in tuples]
        self._chips_list = [float(x[1].replace(",", "")) for x in tuples]
        self._chips = {x[0]: float(x[1].replace(",", "")) for x in tuples}
        #       удаление нулевых стэков
        try:
            self._chips_list.index(0.0)
            print(self._chips_list.index(0.0))
            while self._chips_list.index(0.0) + 1:
                n = self._chips_list.index(0.0)
                self._chips_list.remove(0.0)
                self.players.pop(n)
        except ValueError:
            pass
        finally:
            pass

        res = re.search(bbplayer_regex, self.hand_history)
        if res:
            self.big_blind = self.players.index(res.group(1))
            self.preflop_order = (self.players[self.big_blind + 1:]
                                  + self.players[:self.big_blind + 1])
        else:
            res = re.search(sbplayer_regex, self.hand_history)
            if res:
                self.small_blind = self.players.index(res.group(1))
                self.preflop_order = (self.players[self.small_blind + 1:]
                                      + self.players[:self.small_blind + 1])

        # в префлоп ордер теперь содержится порядок действия игроков как они
        # сидят префлоп от утг до бб

        res = re.search(blinds_regex, self.hand_history)
        if res:
            self.sb = int(res.groupdict().get('sb', '10'))
            self.bb = int(res.groupdict().get('bb', '20'))

    def tournamentPosition(self, player):

        try:
            i = self.players.index(player)
        except ValueError:
            return -1

        sp = self._chips_list[i]
        result = 1
        #
        for s in self._chips_list:
            if s > sp:
                result += 1

        return result

    def tablePosition(self, player):
        # сколько еще игроков будут действовать на префлопе после игрока
        return self.preflop_order

    def flg_chiplead(self, player):

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

        sp = self._chips_list[i]
        result = 1

        i = self.preflop_order.index(player)
        for s in [self._chips_list[ind1]
                  for ind1 in [self.players.index(p)
                               for p in self.preflop_order[i:]]]:
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

            sp = self._chips_list[i]

        if type(player) is int:
            try:
                sp = self._chips_list[player]
            except IndexError:
                print("no such index " + player)
                return -1

        return sp

    def chips(self):
        # returns dict {player: stack}
        return self._chips

    def stack_list(self):
        #       возвращает сисок стэков
        #
        return self._chips_list

    def flg_chiplead_left(self, player):

        if self.tournamentPositionL(player) == 1:
            return True
        else:
            return False

    def players_number(self):
        #   возвращает число игроков
        #
        return len(self._chips_list)

    def flg_knockout(self):
        return True if self.bounty > 0 else False

    def getBlinds(self):
        return [self.sb, self.bb]

    @cached_property
    def bi(self):
        res = self._process_regexp(
            self.BI_BOUNTY_RAKE_REGEX,
            self.caption_str,
            'bi',
            type_func=lambda x: float(x),
        )
        res = res + self.bounty + self.rake
        return res

    @cached_property
    def bounty(self):
        res = self._process_regexp(
            self.BI_BOUNTY_RAKE_REGEX,
            self.caption_str,
            'bounty',
            type_func=lambda x: float(x),
        )
        return res if res else 0

    @cached_property
    def rake(self):
        return self._process_regexp(
            self.BI_BOUNTY_RAKE_REGEX,
            self.caption_str,
            'rake',
            type_func=lambda x: float(x),
        )

    def flgRFIOpp(self, player):
        #       returns true if player has opportunity of first action
        rfi_regex = f'(folds\s{player}|]\s{player})'
        if re.search(rfi_regex, self.hand_history):
            return True
        return False

    def flgFacedAI(self, player):
        return False

    @cached_property
    def tid(self):
        return self._process_regexp(self.TID_REGEX, self.caption_str, 'tid')

    @cached_property
    def hid(self):
        return self._process_regexp(
            self.HID_REGEX,
            self.caption_str,
            'hid'
        )

    @cached_property
    def datetime(self):
        res = self._process_regexp(
            self.DATETIME_REGEX,
            self.caption_str,
            'datetime'
        )
        dt_str_format = '%Y/%m/%d %H:%M:%S'
        try:
            res = datetime.strptime(res, dt_str_format)
        except ValueError:
            pass
        return res

    @cached_property
    def p_actions(self) -> Dict[str, List[str]]:
        """returns list of preflop actions for every player"""
        return self._process_regexp(
            self.ACTIONS_REGEX,
            self.preflop_str,
            type_func=lambda x: ACTIONS[x],
            reslist=True,
            **self.ACTIONS_DICT
        )

    @cached_property
    def f_actions(self) -> Dict[str, List[str]]:
        """returns list of flop actions for every player"""
        return self._process_regexp(
            self.ACTIONS_REGEX,
            self.flop_str,
            type_func=lambda x: ACTIONS[x],
            reslist=True,
            **self.ACTIONS_DICT
        )

    @cached_property
    def t_actions(self) -> Dict[str, List[str]]:
        """returns list of turn actions for every player"""
        return self._process_regexp(
            self.ACTIONS_REGEX,
            self.turn_str,
            type_func=lambda x: ACTIONS[x],
            reslist=True,
            **self.ACTIONS_DICT
        )

    @cached_property
    def r_actions(self) -> Dict[str, List[str]]:
        """returns list of river actions for every player"""
        return self._process_regexp(self.ACTIONS_REGEX,
                                    self.river_str,
                                    type_func=lambda x: ACTIONS[x],
                                    reslist=True,
                                    **self.ACTIONS_DICT)

    @cached_property
    def p_ai_players(self) -> Dict[str, List[str]]:
        # TODO сюда не попадают игроки которые заколили или поставили игрока 
        # под аи оставив в своем стэке фишки

        #       returns list of players which is all in preflop
        return self._process_regexp(self.AI_PLAYERS_REGEX,
                                    self.caption_str + self.preflop_str,
                                    'player',
                                    reslist=True)

    @cached_property
    def f_ai_players(self) -> Dict[str, List[str]]:
        #       returns list of players which is all in flop 
        return self._process_regexp(self.AI_PLAYERS_REGEX,
                                    self.flop_str,
                                    'player',
                                    reslist=True)

    @cached_property
    def t_ai_players(self) -> Dict[str, List[str]]:
        #       returns list of players which is all in turn 
        return self._process_regexp(self.AI_PLAYERS_REGEX,
                                    self.turn_str,
                                    'player',
                                    reslist=True)

    @cached_property
    def r_ai_players(self) -> Dict[str, List[str]]:
        #       returns list of players which is all in river 
        return self._process_regexp(self.AI_PLAYERS_REGEX,
                                    self.river_str,
                                    'player',
                                    reslist=True)

    @cached_property
    def pot_list(self):
        """
        returns list with 1st item is total pot and all
        the side pots if presents
        """
        return self._process_regexp(self.POT_LIST_REGEX,
                                    self.summary_str,
                                    'pot',
                                    reslist=True,
                                    type_func=lambda x: int(x)
                                    )

    @cached_property
    def p_actions_amounts(self):
        return self._process_regexp(self.ACTIONS_AMOUNTS_REGEX,
                                    self.preflop_str,
                                    type_func=lambda x: int(x),
                                    reslist=True,
                                    **self.ACTIONS_AMOUNTS_DICT)

    @cached_property
    def f_actions_amounts(self):
        return self._process_regexp(self.ACTIONS_AMOUNTS_REGEX,
                                    self.flop_str,
                                    type_func=lambda x: int(x),
                                    reslist=True,
                                    **self.ACTIONS_AMOUNTS_DICT)

    @cached_property
    def t_actions_amounts(self):
        return self._process_regexp(self.ACTIONS_AMOUNTS_REGEX,
                                    self.turn_str,
                                    type_func=lambda x: int(x),
                                    reslist=True,
                                    **self.ACTIONS_AMOUNTS_DICT)

    @cached_property
    def r_actions_amounts(self):
        return self._process_regexp(self.ACTIONS_AMOUNTS_REGEX,
                                    self.river_str,
                                    type_func=lambda x: int(x),
                                    reslist=True,
                                    **self.ACTIONS_AMOUNTS_DICT)

    def total_bets_amounts(self) -> Dict[str, int]:
        """ total bets sum on every street including blinds and antes, for every player
        """
        res = {}

        for k in list(self._chips.keys()):

            actions = self.p_actions.get(k, [0])
            if 'r' in actions:
                last_raise_pos = -actions[::-1].index('r') - 1
                p_total_bets = sum(self.p_actions_amounts.get(k, [0])[last_raise_pos:])
            else:
                p_total_bets = (sum(self.p_actions_amounts.get(k, [0]))
                                + self.blinds.get(k, 0))

            actions = self.f_actions.get(k, [0])
            if 'r' in actions:
                last_raise_pos = - actions[::-1].index('r') - 1
                f_total_bets = sum(self.f_actions_amounts.get(k, [0])[last_raise_pos:])
            else:
                f_total_bets = sum(self.f_actions_amounts.get(k, [0]))

            actions = self.t_actions.get(k, [0])
            if 'r' in actions:
                last_raise_pos = - actions[::-1].index('r') - 1
                t_total_bets = sum(self.t_actions_amounts.get(k, [0])[last_raise_pos:])
            else:
                t_total_bets = sum(self.t_actions_amounts.get(k, [0]))

            actions = self.r_actions.get(k, [0])
            if 'r' in actions:
                last_raise_pos = - actions[::-1].index('r') - 1
                r_total_bets = sum(self.r_actions_amounts.get(k, [0])[last_raise_pos:])
            else:
                r_total_bets = sum(self.r_actions_amounts.get(k, [0]))

            res[k] = (p_total_bets + f_total_bets
                      + t_total_bets + r_total_bets + self.antes.get(k, 0))

        return res

    def p_last_action(self):
        res = {}
        for k in list(self._chips.keys()):
            p_actions = self.p_actions.get(k, '')
            if p_actions:
                res[k] = p_actions[len(p_actions) - 1]
        return res

    def f_last_action(self):
        res = {}
        for k in list(self._chips.keys()):
            actions = self.f_actions.get(k, '')
            if actions:
                res[k] = actions[len(actions) - 1]
        return res

    def t_last_action(self):
        res = {}
        for k in list(self._chips.keys()):
            actions = self.t_actions.get(k, '')
            if actions:
                res[k] = actions[len(actions) - 1]
        return res

    def r_last_action(self):
        res = {}
        for k in list(self._chips.keys()):
            actions = self.r_actions.get(k, '')
            if actions:
                res[k] = actions[len(actions) - 1]
        return res

    @cached_property
    def hero(self) -> str:
        """returns hero name
        """
        return self._process_regexp(
                self.HERO_REGEX,
                self.preflop_str,
                'hero'
            )

    @cached_property
    def hero_cards(self) -> str:
        """returns pocket cards
        """
        return self._process_regexp(
                self.HERO_CARDS_REGEX,
                self.preflop_str,
                'cards'
            )

    @cached_property
    def known_cards(self) -> Dict[str, str]:
        """returns known cards, if there are showdown in hand, for every player
        """
        return self._process_regexp(self.KNOWN_CARDS_REGEX,
                                    self.summary_str,
                                    **self.KNOWN_CARDS_DICT,
                                    )

    @cached_property
    def flop(self) -> str:
        """ flop cards
        """
        return self._process_regexp(self.FLOP_REGEX,
                                    self.flop_str,
                                    'flop',
                                    # type_func=lambda x: ''.join(x.split()),
                                    )

    @cached_property
    def turn(self) -> str:
        """ turn cards
        """
        return self._process_regexp(self.TURN_REGEX,
                                    self.turn_str,
                                    'turn')

    @cached_property
    def river(self) -> str:
        """ river cards
        """
        return self._process_regexp(self.RIVER_REGEX,
                                    self.river_str,
                                    'river')

    @cached_property
    def bounty_won(self):
        #   bounty won in hand

        if str.strip(self.showdown_str) == '':
            # in case if where no showdown
            search_str = self.preflop_str
        else:
            search_str = self.showdown_str

        res = self._process_regexp(self.BOUNTY_WON_REGEX,
                                   search_str,
                                   type_func=lambda x: float(x),
                                   **{'player': 'bounty'})
        # 1 more bounty for the 1st place
        for player, place in self.finishes.items():
            if place == 1:
                res[player] = res.get(player, 0) + self.bounty
        return res

    @cached_property
    def prize_won(self) -> Dict[str, float]:
        """ returns prize player won
        """
        if str.strip(self.showdown_str) == '':
            # in case if where no showdown
            search_str = self.preflop_str
        else:
            search_str = self.showdown_str

        return self._process_regexp(self.PRIZE_WON_REGEX,
                                    search_str,
                                    type_func=lambda x: float(x),
                                    **{'player': 'prize'})

    @cached_property
    def chip_won(self) -> Dict[str, List[int]]:
        """ returns how much chips total player collected from pot
        """
        return self._process_regexp(self.CHIPWON_REGEX,
                                    self.showdown_str + self.preflop_str + self.flop_str + self.turn_str + self.river_str,
                                    type_func=lambda x: int(x),
                                    reslist=True,
                                    **self.CHIPWON_DICT)

    @cached_property
    def finishes(self):
        if str.strip(self.showdown_str) == '':
            # in case if where no showdown
            search_str = self.preflop_str
        else:
            search_str = self.showdown_str
        # replace None with default_value=1 
        # means that if no message about player finishes treats as 
        # player finished in 1st plase
        res = self._process_regexp(self.FINISHES_REGEX,
                                   search_str,
                                   type_func=lambda x: int(x),
                                   default_value=1,
                                   **{'player': 'place'})
        return res

    @cached_property
    def blinds_antes(self):
        # returns dict {player: bet before preflop}
        res = re.findall(self.BLINDS_ANTE_REGEX, self.caption_str)
        dic = {}
        if res:
            for x in res:
                if dic.get(x[0], 0) == 0:
                    dic[x[0]] = int(x[1])
                else:
                    dic[x[0]] = dic.get(x[0]) + int(x[1])

        return dic

    @cached_property
    def blinds(self):
        # returns dict {player: blind bet}
        return self._process_regexp(self.BLINDS_REGEX,
                                    self.caption_str,
                                    type_func=lambda x: int(x),
                                    **self.BLINDS_ANTE_DICT)

    @cached_property
    def antes(self):
        # returns dict {player: ante}

        return self._process_regexp(self.ANTE_REGEX,
                                    self.caption_str,
                                    type_func=lambda x: int(x),
                                    **self.BLINDS_ANTE_DICT)

    @cached_property
    def uncalled(self):
        """
        returns dict {player: bet}
        """
        return self._process_regexp(self.UNCALLED_REGEX,
                                    self.hand_history,
                                    type_func=lambda x: int(x),
                                    **self.UNCALLED_DICT)

    def positions(self):
        # returns dict{player: position}
        return {self.preflop_order[::-1][i]: self.POSITIONS[i]
                for i in range(len(self.preflop_order))}

    def flg_showdown(self):
        return True if self.showdown_str.strip() else False

    def last_actions(self):
        # returns last actions
        if self.r_actions:
            return self.r_actions
        elif self.t_actions:
            return self.t_actions
        elif self.f_actions:
            return self.f_actions
        else:
            return self.p_actions

    def last_actions_amounts(self):
        if self.r_actions_amounts():
            return self.r_actions_amounts()
        elif self.t_actions_amounts():
            return self.t_actions_amounts()
        elif self.f_actions_amounts():
            return self.f_actions_amounts()
        else:
            return self.p_actions_amounts()

    @staticmethod
    def cards_to_hand(cards):
        if not isinstance(cards, str):
            raise ValueError('String expected!')

        if len(cards.split()) != 2:
            raise ValueError(f'Invalid card format: {cards}')

        ranks = sorted([card[0] for card in cards.split()],
                       key=lambda x: "23456789TJQKA".index(x), reverse=True)
        suits = [card[1] for card in cards.split()]
        if suits[0] == suits[1]:
            res = ''.join([ranks[0], ranks[1], 's'])
        elif ranks[0] == ranks[1]:
            res = ''.join([ranks[0], ranks[1]])
        else:
            res = ''.join([ranks[0], ranks[1], 'o'])

        return res

    def tie_factor(self):
        eq = self.icm_eq()
        st = np.array(self._chips_list)
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
                bubble_factor = (eq[i] - eq_lose[i]) / (eq_win[i] - eq[i])
                result[i, j] = bubble_factor / (1 + bubble_factor)
        return result
