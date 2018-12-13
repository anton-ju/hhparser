from bs4 import BeautifulSoup as bs


class HRCParcer():
    STRATEGY_TABLE_COLUMNS = ('strategy', 'amount', 'player', 'range_pct', 'range_txt', 'ev_ref')

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

        strategy_table = self.hrc_output.find_all('table', attrs={'class': 'strategyoverview'})
        refs = [tag.attrs.get('name') for tag in strategy_table[0].find_all(lambda tag: 'name' in tag.attrs)]
        refs.insert(0, '')

        rows = []
        for tr, ref in zip(strategy_table[0].find_all('tr'), refs):
            row = []
            for td in tr:
                row.append(td.text)
            row.append(ref)
            rows.append(row)
        rows[0] = ['action_1', 'action_2', 'action_3', 'amount', 'player', 'range_pct', 'range_txt', 'ev_ref']
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
            result.append([replace_empty(row[0]) + replace_empty(row[1]) + replace_empty(row[2]),
                           row[3], row[4], row[5], row[6], row[7]])

        format_table(result)

        result[0] = self.STRATEGY_TABLE_COLUMNS
        return result

    def get_ev_table_by_ref(self, ref):
        name_attr = ref.replace('o', 'r')
        ev_table = self.hrc_output.find('a', attrs={'name': name_attr}).find_next('table')

        rows = []
        for td in ev_table.find_all('td'):
            rows.append((td.text.replace(td.ev.text, '').replace(td.pl.text, ''), td.ev.text, td.pl.text))
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


if __name__ == '__main__':

    def read_html(path):
        with open(path) as f:
            html = f.read()

        return html

    html = read_html('hrc_output.html')
    parser = HRCParcer(html)
    print(parser.get_hand_ev('22', 'TH0090,DiggErr555'))

