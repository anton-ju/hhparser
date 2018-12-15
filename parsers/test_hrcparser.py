import unittest
import logging
from parsers.hrcparser import HRCParser

from datetime import datetime
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class TestHRCParser(unittest.TestCase):
    def setUp(self):

        with open("D:\\cloud\\disk.yandex\\prog\\python\\hhparser\\parsers\\hrc_output.html") as f:
            html = f.read()
        self.parser = HRCParser(html)

    def test_get_hand_ev(self):
        ev = '+0.18'
        hand = '22'
        players = 'DiggErr555'
        self.assertEqual(self.parser.get_hand_ev(hand, players), ev)

        ev = '-1.64'
        hand = 'JTs'
        players = 'DiggErr555,LikeTonyG'
        self.assertEqual(self.parser.get_hand_ev(hand, players), ev)

        ev = '-0.02'
        hand = 'A4s'
        players = 'LikeTonyG,larubirosa,rajs1984'
        self.assertEqual(self.parser.get_hand_ev(hand, players), ev)
        #
        # ev = '+0.18'
        # hand = '22'
        # players = 'DiggErr555'
        # self.assertEqual(self.parser.get_hand_ev(hand, players), ev)
        #
        # ev = '+0.18'
        # hand = '22'
        # players = 'DiggErr555'
        # self.assertEqual(self.parser.get_hand_ev(hand, players), ev)
        #
        # ev = '+0.18'
        # hand = '22'
        # players = 'DiggErr555'
        # self.assertEqual(self.parser.get_hand_ev(hand, players), ev)


if __name__ == '__main__':
    unittest.main()
