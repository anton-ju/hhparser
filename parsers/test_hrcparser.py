import unittest
import logging
from parsers.hrcparser import HRCParser
import os
from datetime import datetime
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class TestHRCParser(unittest.TestCase):
    def setUp(self):
        with open("hrc_output.html") as f:
            html = f.read()
        self.case1 = HRCParser(html)
        with open("debug_hrcparser.html") as f:
            html = f.read()
        self.case2 = HRCParser(html)

    def test_get_hand_ev(self):
        ev = '+0.18'
        hand = '22'
        players = 'DiggErr555'
        self.assertEqual(self.case1.get_hand_ev(hand, players), ev)

        ev = '-1.64'
        hand = 'JTs'
        players = 'DiggErr555,LikeTonyG'
        self.assertEqual(self.case1.get_hand_ev(hand, players), ev)

        ev = '-0.02'
        hand = 'A4s'
        players = 'LikeTonyG,larubirosa,rajs1984'
        self.assertEqual(self.case1.get_hand_ev(hand, players), ev)

        ev = '+1.28'
        hand = 'A7s'
        players = '$kill Game,DiggErr555'
        self.assertEqual(self.case2.get_hand_ev(hand, players), ev)
        #
        # ev = '+0.18'
        # hand = '22'
        # players = 'DiggErr555'
        # self.assertEqual(self.case2.get_hand_ev(hand, players), ev)
        #
        # ev = '+0.18'
        # hand = '22'
        # players = 'DiggErr555'
        # self.assertEqual(self.case2.get_hand_ev(hand, players), ev)

    def test_get_range(self):
        players = 'DiggErr555'
        res = '21.3%,22+ A2s+ A8o+ K9s+ KJo+ Q9s+ QJo J9s+ T8s+ 98s'
        self.assertEqual(self.case1.get_range(players), res)

        players = 'DiggErr555'
        res = '21.3%,22+ A2s+ A8o+ K9s+ KJo+ Q9s+ QJo J9s+ T8s+ 98s'
        self.assertEqual(self.case1.get_range(players), res)

        players = 'LikeTonyG,yaniw777'
        res = '15.1%,33+ A5s+ A9o+ KTs+ KQo QTs+'
        self.assertEqual(self.case1.get_range(players), res)

        players = 'LikeTonyG,yaniw777,rajs1984'
        res = '7.9%,66+ ATs+ AJo+ KQs'
        self.assertEqual(self.case1.get_range(players), res)


if __name__ == '__main__':
    unittest.main()
