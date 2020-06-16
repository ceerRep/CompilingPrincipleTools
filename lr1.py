#! /usr/bin/env python3

from copy import deepcopy
from typing import *
from grammar import *
from production import *


class State:
    __slots__ = ['productions', 'str']

    def __init__(self, production: Optional[Production] = None):
        self.productions: List[ProductionWithPosAndTail] = list()

        if production:
            self.productions.append(ProductionWithPosAndTail(production.target, production.rule, 0).add_tail(['#']))

        self.str: str = ''

    def add_production(self, production: Production):
        if isinstance(production, ProductionWithPosAndTail):
            to_add = production
        else:
            to_add = ProductionWithPosAndTail(production.target,
                                              production.rule,
                                              0).add_tail(['#'])

        try:
            ind = self.productions.index(to_add)
            self.productions[ind].merge(to_add)
        except ValueError:
            self.productions.append(to_add)

    def closure(self, grammar: Grammar):
        updated = True
        while updated:
            updated = False
            for production in self.productions:
                if production.is_shift():
                    next_t = production.rule[production.pos]

                    if not grammar.is_terminal(next_t):
                        tails: Set[str] = set()

                        for t in production.rule[production.pos + 1:]:
                            tails = tails.union(grammar.first[t])
                            if '' not in grammar.first[t]:
                                break
                        else:
                            tails = tails.union(production.tail)

                        tails: List[str] = list(tails)

                        for p in grammar.production[next_t]:
                            p_pos = ProductionWithPosAndTail(p.target, p.rule, 0)
                            p_pos.add_tail(tails)
                            try:
                                ind = self.productions.index(p_pos)
                                l1 = len(self.productions[ind].tail)
                                self.productions[ind].add_tail(tails)
                                if l1 != len(self.productions[ind].tail):
                                    updated = True
                            except ValueError:
                                self.productions.append(p_pos)
                                updated = True
        self.productions.sort(key=lambda x: str(x))
        self.update_str()

    def next(self, grammar: Grammar):
        results: Dict[str, State] = {}

        for production in self.productions:
            if production.is_shift():
                next_t = production.rule[production.pos]

                if next_t not in results:
                    results[next_t] = State()

                results[next_t].add_production(
                    ProductionWithPosAndTail(production.target,
                                             production.rule,
                                             production.pos + 1).add_tail(production.tail))

        for _, state in results.items():
            state.closure(grammar)

        return results

    def update_str(self):
        self.str = '[' + '; '.join(map(str, self.productions)) + ']'

    def __eq__(self, other):
        return self.str == other.str

    def __str__(self):
        return self.str

    def __repr__(self):
        return str(self)

    def __hash__(self):
        return hash(tuple(self.productions))


class LR1Machine:
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
    grammar = LR1Machine('S\'') \
        .add_production(Production('S\'', ['S'])) \
        .add_production(Production('S', ['S', 'S', '+'])) \
        .add_production(Production('S', ['S', 'S', '*'])) \
        .add_production(Production('S', ['(', 'S', ')'])) \
        .add_production(Production('S', ['a']))

    grammar.calc()

    print(grammar.to_string())
