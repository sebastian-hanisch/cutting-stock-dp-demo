"""Unabhängiges Orakel: Teilmengen-DP über Einzelstücke (Bin Packing) und breadth-first
erreichbare Zustände mit itertools-Mustern - statt der memoisierten Bedarfsvektor-Rekursion."""

import itertools
import random

from csdp_patterns import feasible_patterns
from csdp_scenario import CuttingStockInstance
from csdp_solver import solve
from csdp_trace import build_trace


def _subset_dp(pieces, width):
    n = len(pieces)
    inf = 10 ** 9
    dp = [(inf, 0)] * (1 << n)
    dp[0] = (1, 0)
    for mask in range(1 << n):
        bins, fill = dp[mask]
        if bins == inf:
            continue
        for i in range(n):
            if mask >> i & 1:
                continue
            cand = (bins, fill + pieces[i]) if fill + pieces[i] <= width else (bins + 1, pieces[i])
            if cand < dp[mask | 1 << i]:
                dp[mask | 1 << i] = cand
    return dp[(1 << n) - 1][0]


def _patterns(inst, state):
    ranges = [range(min(s, inst.roll_width // w) + 1) for s, w in zip(state, inst.item_widths)]
    return {p for p in itertools.product(*ranges)
            if any(p) and sum(a * b for a, b in zip(p, inst.item_widths)) <= inst.roll_width}


def _reachable_states(inst):
    zero = tuple(0 for _ in inst.item_demands)
    seen, stack = set(), [inst.item_demands]
    while stack:
        s = stack.pop()
        if s in seen or s == zero:
            continue
        seen.add(s)
        for p in _patterns(inst, s):
            stack.append(tuple(a - b for a, b in zip(s, p)))
    return len(seen)


def test_dp_matches_subset_dp_state_count_patterns_and_trace():
    rng = random.Random(3)
    checked = 0
    while checked < 60:
        width = rng.choice([10, 20, 50, 100])
        n = rng.randint(1, 4)
        widths = tuple(rng.choice([1, width // 4, width // 3, width // 2, width - 1, width, rng.randint(1, width)])
                       for _ in range(n))
        demands = tuple(rng.randint(1, 3) for _ in range(n))
        inst = CuttingStockInstance(width, widths, demands)
        pieces = sorted((w for w, q in zip(widths, demands) for _ in range(q)), reverse=True)
        if len(pieces) > 9:
            continue
        checked += 1
        res = solve(inst)
        assert res.reached
        assert res.best_value == _subset_dp(pieces, width), inst
        assert res.states_explored == _reachable_states(inst), inst
        assert set(feasible_patterns(inst, demands)) == _patterns(inst, demands)
        trace = build_trace(res)
        assert len(trace) == res.best_value
        totals = [sum(step.pattern[i] for step in trace) for i in range(n)]
        assert tuple(totals) == demands
