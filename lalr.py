#! /usr/bin/env python3

from copy import deepcopy
from typing import *
from grammar import *
from production import *

from lr1 import *


class LALRMachine(LR1Machine):

    def calc(self):
        super(LALRMachine, self).calc()
        self.merge()

    def merge(self):
        now_counter = 0
        state_list: List[State] = []
        state_map: Dict[int, int] = {}
        state_id_map: Dict[int, int] = {}

        for oid, state in enumerate(self.states):
            if hash(state) not in state_map:
                state_list.append(state)
                state_map[hash(state)] = now_counter
                state_id_map[oid] = now_counter
                now_counter += 1
            else:
                for p1, p2 in zip(state.productions, state_list[state_map[hash(state)]].productions):
                    p2.merge(p1)
                state_id_map[oid] = state_map[hash(state)]

        for state in state_list:
            state.update_str()

        new_table: Dict[int, Dict[str, int]] = {}

        for begin, turns in self.table.items():
            nid = state_id_map[begin]
            if nid not in new_table:
                new_table[nid] = {}
            for term, end in turns.items():
                eid = state_id_map[end]
                new_table[nid][term] = eid

        self.states = state_list
        self.table = new_table


if __name__ == '__main__':
    lalr = LALRMachine('S\'') \
        .add_production(Production('S\'', ['S'])) \
        .add_production(Production('S', ['S', 'S', '+'])) \
        .add_production(Production('S', ['S', 'S', '*'])) \
        .add_production(Production('S', ['(', 'S', ')'])) \
        .add_production(Production('S', ['a']))

    lalr.calc()

    print(lalr.to_string())
