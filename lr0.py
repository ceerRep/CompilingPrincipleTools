#! /usr/bin/env python3

from copy import deepcopy
from typing import *
from grammar import *
from production import *


class State:
    __slots__ = ['productions', 'str']

    def __init__(self, production: Optional[Production] = None):
        self.productions: List[ProductionWithPos] = list()

        if production:
            self.productions.append(ProductionWithPos(production.target, production.rule, 0))

        self.str: str = ''

    def add_production(self, production: Production):
        if isinstance(production, ProductionWithPos):
            self.productions.append(production)
        else:
            self.productions.append(
                ProductionWithPos(production.target,
                                  production.rule,
                                  0))

    def closure(self, grammar: Grammar):
        for production in self.productions:
            if production.is_shift():
                next_t = production.rule[production.pos]

                if not grammar.is_terminal(next_t):
                    for p in grammar.production[next_t]:
                        p_pos = ProductionWithPos(p.target, p.rule, 0)
                        if p_pos not in self.productions:
                            self.productions.append(p_pos)

        self.productions.sort(key=lambda x: str(x))
        self.str = '[' + '; '.join(map(str, self.productions)) + ']'

    def next(self, grammar: Grammar):
        results: Dict[str, State] = {}

        for production in self.productions:
            if production.is_shift():
                next_t = production.rule[production.pos]

                if next_t not in results:
                    results[next_t] = State()

                results[next_t].add_production(
                    ProductionWithPos(production.target,
                                      production.rule,
                                      production.pos + 1))

        for _, state in results.items():
            state.closure(grammar)

        return results

    def __eq__(self, other):
        return self.str == other.str

    def __str__(self):
        return self.str

    def __repr__(self):
        return str(self)


class LR0Machine:
    __slots__ = ['grammar', 'table', 'states']

    def __init__(self, target: str):
        self.grammar: Grammar = Grammar(target)
        self.states: List[State] = []
        self.table: Dict[int, Dict[str, int]] = {}

    def add_production(self, *args, **kwargs):
        self.grammar.add_production(*args, **kwargs)
        return self

    def get_state(self, s: State):
        try:
            return self.states.index(s)
        except ValueError:
            self.states.append(s)
            return len(self.states) - 1

    def calc(self):
        self.grammar.calc_first()
        self.grammar.calc_follow()

        begin_state: State = State()

        for production in self.grammar.production[self.grammar.target]:
            begin_state.add_production(production)

        begin_state.closure(self.grammar)
        self.states.append(begin_state)

        for ind, state in enumerate(self.states):
            nexts = state.next(self.grammar)

            self.table[ind] = {}

            for term, next_state in nexts.items():
                ind1 = self.get_state(next_state)

                self.table[ind][term] = ind1

    def to_string(self):
        ret = []

        for ind, state in enumerate(self.states):
            ret.append(str(ind))
            ret.append(' ')
            ret.append(str(state))
            ret.append('\n')

        for begin, turns in self.table.items():
            ret.append(str(begin))
            ret.append(' ')
            for term, end in turns.items():
                ret.append(term + '->' + str(end) + ' ')
            ret.append('\n')
        return ''.join(ret)


if __name__ == '__main__':
    grammar = LR0Machine('S\'') \
        .add_production(Production('S\'', ['S'])) \
        .add_production(Production('S', ['S', 'S', '+'])) \
        .add_production(Production('S', ['S', 'S', '*'])) \
        .add_production(Production('S', ['(', 'S', ')'])) \
        .add_production(Production('S', ['a']))

    grammar.calc()
    print(grammar.to_string())
    print(grammar.grammar.first)
    print(grammar.grammar.follow)
