#! /usr/bin/env python3

from copy import deepcopy
from typing import *
from production import *

__all__ = ['Grammar', 'EOF']

EOF = '#'


class Grammar:
    __slots__ = ['target', 'production', 'first', 'follow', 'symbols']

    def __init__(self, target: str):
        self.target: str = target
        self.production: Dict[str, Set[Production]] = {}
        self.first: Dict[str, Set[str]] = {}
        self.follow: Dict[str, Set[str]] = {}
        self.symbols: Set[str] = set()

    @staticmethod
    def is_terminal(x: str) -> bool:
        return not x[0].isupper()

    def add_production(self, production: Production):
        if production.target not in self.production:
            self.production[production.target] = set()

        production = deepcopy(production)

        self.production[production.target].add(production)

        self.symbols.add(production.target)
        self.first[production.target] = set()
        self.follow[production.target] = set()
        for x in production.rule:
            self.symbols.add(x)
            self.first[x] = set()
            self.follow[x] = set()
        return self

    def calc_first(self):
        updated = True
        while updated:
            updated = False
            for symbol in self.symbols:
                if self.is_terminal(symbol):
                    if symbol not in self.first[symbol]:
                        self.first[symbol].add(symbol)
                        updated = True
                else:
                    for rule in self.production[symbol]:
                        if not rule.rule:
                            if '' not in self.first[symbol]:
                                self.first[symbol].add('')
                                updated = True
                        else:
                            for naive in rule.rule:
                                to_break = True
                                for item in self.first[naive]:
                                    if item:
                                        if item not in self.first[symbol]:
                                            self.first[symbol].add(item)
                                            updated = True
                                    else:
                                        to_break = False
                                if to_break:
                                    break
                            else:
                                self.first[symbol].add('')
                                updated = True

    def calc_follow(self):
        self.follow[self.target].add(EOF)
        updated = True

        while updated:
            updated = False

            for target, rules in self.production.items():
                for rule in rules:
                    for s1, s2 in zip(rule.rule[:-1], rule.rule[1:]):
                        for symbol in self.first[s2]:
                            if symbol and symbol not in self.follow[s1]:
                                self.follow[s1].add(symbol)
                                updated = True
                    for s1, s2, s3 in zip(rule.rule[:-2], rule.rule[1:-1], rule.rule[2:]):
                        if '' not in self.first[s2]:
                            continue
                        for symbol in self.first[s3]:
                            if symbol and symbol not in self.follow[s1]:
                                self.follow[s1].add(symbol)
                                updated = True

                    if len(rule.rule) >= 1:
                        last = rule.rule[-1]
                        for symbol in self.follow[target]:
                            if symbol not in self.follow[last]:
                                self.follow[last].add(symbol)
                                updated = True

                    if len(rule.rule) >= 2:
                        last1, last = rule.rule[-2:]
                        if '' in self.first[last]:
                            for symbol in self.follow[target]:
                                if symbol not in self.follow[last1]:
                                    self.follow[last1].add(symbol)
                                    updated = True


if __name__ == '__main__':
    grammar = Grammar('S') \
        .add_production(Production('S', ['a', 'F', 'S1'])) \
        .add_production(Production('S', ['+', 'a', 'F', 'S1'])) \
        .add_production(Production('S1', ['+', 'a', 'F', 'S1'])) \
        .add_production(Production('S1', [])) \
        .add_production(Production('F', ['*', 'a', 'F'])) \
        .add_production(Production('F', ['*', 'a']))

    grammar.calc_first()
    grammar.calc_follow()
    print(grammar.first)
    print(grammar.follow)
