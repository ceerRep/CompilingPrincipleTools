#! /usr/bin/env python3

import copy
from itertools import chain
from typing import *

__all__ = ['Production', 'ProductionWithPos', 'ProductionWithPosAndTail']


class Production:
    __slots__ = ['target', 'rule', 'str']

    def __init__(self, target: str, rule: List[str]):
        self.target: str = target
        self.rule: List[str] = rule
        self.update_str()

    def update_str(self):
        self.str = ' '.join(chain([self.target, ':'], self.rule))

    def __str__(self) -> str:
        return self.str

    def __repr__(self) -> str:
        return "'" + str(self) + "'"

    def __hash__(self):
        return hash(self.str)


class ProductionWithPos(Production):
    __slots__ = ['pos']

    def __init__(self, target: str, rule: List[str], pos: int):
        self.pos: int = pos
        super(ProductionWithPos, self).__init__(target, rule)

    def update_str(self):
        self.str = ' '.join(chain([self.target, ':'], self.rule[:self.pos], ['·'], self.rule[self.pos:]))

    def is_shift(self):
        return not self.is_reduce()

    def is_reduce(self):
        return self.pos == len(self.rule)

    def __eq__(self, other):
        return self.str == other.str

    def next(self):
        assert self.is_shift()
        ret = copy.deepcopy(self)
        ret.pos += 1
        ret.update_str()
        return ret


class ProductionWithPosAndTail(ProductionWithPos):
    __slots__ = ['tail', 'str1']

    def __init__(self, target: str, rule: List[str], pos: int):
        self.tail: List[str] = []
        super(ProductionWithPosAndTail, self).__init__(target, rule, pos)

    def update_str(self):
        self.str = ' '.join(chain([self.target, ':'], self.rule[:self.pos], ['·'], self.rule[self.pos:]))
        self.str1 = self.str + ' {' + '/'.join(self.tail) + '}'

    def add_tail(self, tails: List[str]):
        for t in tails:
            if t not in self.tail:
                self.tail.append(t)
        self.tail.sort()
        self.update_str()
        return self

    def merge(self, other):
        if self.str != other.str:
            raise ValueError('invalid argument')
        self.add_tail(other.tail)
        return self

    def __hash__(self):
        return hash(self.str)

    def __str__(self):
        return self.str1


if __name__ == '__main__':
    a = ProductionWithPosAndTail('A', ['B'], 0).add_tail(['2', '3', '4'])
    print(a)
    a = a.next()
    print(a)
    print(a.next())
