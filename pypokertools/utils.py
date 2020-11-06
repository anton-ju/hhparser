from collections import defaultdict
import numpy
from eval7 import py_equities_2hands, Card
import os


def str_to_cards(hand_str):
    cards = tuple(map(Card, hand_str.split()))
    return cards
# code from https://github.com/hh2010/hunl.git
# Define some useful constants
NUM_CARDS = 52
NUM_RANKS = 13
NUM_SUITS = 4
NUM_HANDS = 1326 # nchoosek(52,2)
NUM_VILLAIN_HANDS = 1225 # nchoosek(50,2)

# Make some lists

SUITS = ['h', 'd', 'c', 's']
RANKS = ['A', 'K', 'Q','J', 'T', '9', '8', '7', '6', '5', '4', '3', '2']
CARDS = ['2h', '3h', '4h', '5h', '6h', '7h', '8h', '9h', 'Th', 'Jh', 'Qh', 'Kh', 'Ah', 
         '2d', '3d', '4d', '5d', '6d', '7d', '8d', '9d', 'Td', 'Jd', 'Qd', 'Kd', 'Ad',
         '2c', '3c', '4c', '5c', '6c', '7c', '8c', '9c', 'Tc', 'Jc', 'Qc', 'Kc', 'Ac', 
         '2s', '3s', '4s', '5s', '6s', '7s', '8s', '9s', 'Ts', 'Js', 'Qs', 'Ks', 'As']

CARDS_MAP = ['2h', '2d', '2c', '2s',
             '3h', '3d', '3c', '3s',
             '4h', '4d', '4c', '4s',
             '5h', '5d', '5c', '5s',
             '6h', '6d', '6c', '6s',
             '7h', '7d', '7c', '7s',
             '8h', '8d', '8c', '8s',
             '9h', '9d', '9c', '9s',
             'Th', 'Td', 'Tc', 'Ts',
             'Jh', 'Jd', 'Jc', 'Js',
             'Qh', 'Qd', 'Qc', 'Qs',
             'Kh', 'Kd', 'Kc', 'Ks',
             'Ah', 'Ad', 'Ac', 'As']

# Create formulas for converting string card names to nums (and vice versa)
def pe_string2card(cards_inp):
    newcards = []
    for i in cards_inp:
        if i in ['__', '_', '*']:
            newcards.append(255)
        else:
            newcards.append(CARDS.index(i))
    return newcards


def pe_card2string(cards_inp):
    newcards = []
    for i in cards_inp:
        if i == 255:
            newcards.append('__')
        else:
            newcards.append(CARDS[i])
    return newcards


# To avoid expensive equity calculations, we will pre-compute all 
#     equities for any board we are interested in.
# Essentially, we'll make a table that contains all hand-vs-hand 
#     matchups, and we'll computer the equity of every matchup once.  
#     And then if we need it in the future, we can just look it up.

# EquityArray class organizes hand vs hand equities for a board
class EquityArray:
    # Constructor
    # Input:
    #    b - list of numbers representing a board
    def __init__(self, b):
        self.board = b
        self.eArray = numpy.zeros((NUM_CARDS,NUM_CARDS,NUM_CARDS,NUM_CARDS))
        if os.path.isfile('eqarray/' + self.getFilename()):
            self.eArray = numpy.load('eqarray/' + self.getFilename())
        else:
            self.makeArray()

    def makeArray(self): #can you cut down on hand combos here through isomorphism?
#         x = 0
        for i in range(NUM_CARDS):
            for j in range(NUM_CARDS):
                for a in range(NUM_CARDS):
                    for b in range(NUM_CARDS):
#                         x += 1
                        hand = str_to_cards(" ".join([CARDS[i], CARDS[j]]))
                        villainHand = [a, b]
                        self.eArray[i][j][a][b] = py_equities_2hands(hand, villainHand, self.board)
#                         print x
        numpy.save(self.getFilename(), self.eArray)

    # Output: filename built from self.board
    # For example, if card2string(self.board) == ['Ah', 'Jd', '2c', '__','__']
    # then x return 'AhJd2c.ea.npy'.
    def getFilename(self):
        boardStr = ''
        boardAsStrings = pe_card2string(self.board)
        for i in boardAsStrings:
            if i != '__':
                boardStr = boardStr + i
            if boardStr == '': #this is the case when we have the preflop board
                boardStr = 'preflop'
        boardStr = boardStr + '.ea.npy'
        return boardStr


class cached_property(object):
    def __init__(self, func):
        self.func = func

    def __get__(self, instance, cls=None):
        result = instance.__dict__[self.func.__name__] = self.func(instance)
        return result


class NumericDict(defaultdict):
    """
    allows addiction, substraction, multiplication and divizion beetwen NumericDicts ind scalars
    """
    @classmethod
    def _NewDict(cls):
        return cls()

    def __add__(self, other):
        res = other.copy()
        for k, v in self.items():
            res[k] = v + other[k]
        return res

    def __sub__(self, other):
        res = self.copy()
        if isinstance(other, (int, float)):
            for k, v in self.items():
                res[k] = self[k] - other
        elif isinstance(other, self.__class__):
            for k, v in other.items():
                res[k] = self[k] - v
        else:
            raise TypeError('Invalid operand type')
        return res

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            res = self._NewDict()
            for k, v in self.items():
                res[k] = v * other
        elif isinstance(other, self.__class__):
            res = self._NewDict()
            keys = set(self.keys()) & set(other.keys())
            for k in keys:
                res[k] = self[k] * other[k]
        else:
            raise TypeError('Invalid operand type')
        return res

    def __rmul__(self, other):
        return self * other

    def __truediv__(self, other):
        if isinstance(other, (int, float)):
            res = self._NewDict()
            for k, v in self.items():
                res[k] = v / other
            return res
        raise TypeError('Invalid operand type: expected int or float')

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
