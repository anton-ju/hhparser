from bs4 import BeautifulSoup as bs


class HRCParcer():
    def __init__(self, html):
        self.html_source = html

        self.hrc_output = bs(html, features="html.parser")
        self.stacks_table = self.get_stacks_table()

        self.strategy_table = self.get_strategy_table()

        self.ev_table = self.get_ev_table('o25-1')

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
        return rows

    def get_ev_table(self, ref):
        name_attr = ref.replace('o', 'r')
        ev_table = self.hrc_output.find('a', attrs={'name': name_attr}).find_next('table')

        rows = []
        for td in ev_table.find_all('td'):
            rows.append((td.text.replace(td.ev.text, '').replace(td.pl.text, ''), td.ev.text, td.pl.text))

        return rows


if __name__ == '__main__':

    def read_html(path):
        with open(path) as f:
            html = f.read()

        return html
    
    html = read_html('hrc_output.html')

    parser = HRCParcer(html)
    for r in parser.ev_table:
        print(r)


