#! /usr/bin/env python3

from typing import *
from production import *
from grammar import *

__all__ = ['LL1Machine']


class LL1Machine:
    __slots__ = ['grammar', 'table', 'terminals', 'non_terminals']

    def __init__(self, target: str):
        self.grammar: Grammar = Grammar(target)
        self.table: Dict[str, Dict[str, Production]] = {}
        self.terminals: Set[str] = set()
        self.non_terminals: Set[str] = set()

    def add_production(self, *args, **kwargs):
        self.grammar.add_production(*args, **kwargs)
        return self

    def calc_table(self):
        self.grammar.calc_first()
        self.grammar.calc_follow()

        for symbol in self.grammar.first.keys():
            if Grammar.is_terminal(symbol):
                self.terminals.add(symbol)
            else:
                self.non_terminals.add(symbol)

        self.terminals.add(EOF)

        for target, rules in self.grammar.production.items():
            self.table[target] = {}
            for rule in rules:
                for term in rule.rule:
                    for sym in self.grammar.first[term]:
                        if sym:
                            if not (sym not in self.table[target] or str(self.table[target][sym]) == str(rule)):
                                print("Conflict at ", sym, rule, self.table, str(self.table[target][sym]), str(rule))
                                raise ValueError("LL conflict")
                            self.table[target][sym] = rule
                    if '' not in self.grammar.first[term]:
                        break
                else:
                    for sym in self.grammar.follow[target]:
                        if not (sym not in self.table[target] or str(self.table[target][sym]) == str(rule)):
                            print("Conflict at ", sym, rule, self.table, str(self.table[target][sym]), str(rule))
                            raise ValueError("LL conflict")
                        self.table[target][sym] = rule

    def table_to_string(self) -> str:
        align = 4
        for _, rules in self.grammar.production.items():
            for rule in rules:
                align = max(align, len(str(rule)))
        align += 2

        fit = lambda x: "%%-%ds" % align % x

        terminals = list(self.terminals)
        non_terminals = list(self.non_terminals)

        terminals.sort()
        non_terminals.sort()

        ret = [fit('') + ''.join(map(fit, terminals)), '\n']

        for nt in non_terminals:
            ret.append(fit(nt))
            for t in terminals:
                if t in self.table[nt]:
                    ret.append(fit(str(self.table[nt][t])))
                else:
                    ret.append(fit(''))
            ret.append('\n')

        return ''.join(ret)


if __name__ == '__main__':
    """
    ll1 = LL1Machine('S') \
        .add_production(Production('S', ['a', 'F', 'S1'])) \
        .add_production(Production('S', ['+', 'a', 'F', 'S1'])) \
        .add_production(Production('S1', ['+', 'a', 'F', 'S1'])) \
        .add_production(Production('S1', [])) \
        .add_production(Production('F', ['*', 'a', 'F1'])) \
        .add_production(Production('F1', ['F'])) \
        .add_production(Production('F1', []))"""

    ll1 = LL1Machine('E') \
        .add_production(Production("E", ["T", "E'"])) \
        .add_production(Production("E'", ["+", "T", "E'"])) \
        .add_production(Production("E'", [])) \
        .add_production(Production("T", ["F", "T'"])) \
        .add_production(Production("T'", ["*", "F", "T'"])) \
        .add_production(Production("T'", [])) \
        .add_production(Production("F", ["(", "E", ")"])) \
        .add_production(Production("F", ["id"]))
    ll1.calc_table()
    print(ll1.table_to_string())
