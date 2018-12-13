from parsers.hhparser import HHParser
from parsers.hrcparser import HRCParcer
from storage import hand_storage

hs = hand_storage.HandStorage('hands/hrcparser/')




for hand_hist in hs.read_hand():
    hh = HHParser(hand_hist)
    players = ','.join([k for k, v in hh.p_actions.items() if v != ['f']])
    hand = hh.cards_to_hand(hh.hero_cards)

    with open('parsers/hrc_output.html') as f:
        html = f.read()

    parser = HRCParcer(html)
    print(hand, players)
    print(parser.get_hand_ev(hand, players))

    # print(cards_to_hand(cards))