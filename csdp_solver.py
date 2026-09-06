"""Memoisierte Rekursion über Bedarfsvektoren - siehe app.py's "Mathematische
Formulierung" für die Herleitung. Anders als ein Suchbaum liefert diese Rekursion
KEIN Zwischenergebnis, solange nicht alle nötigen Zustände berechnet sind - wird
die Sicherheitsgrenze überschritten, wird deshalb gar nicht erst gerechnet (wie in
dynamic-programming-demo), nur ehrlich erklärt, wie groß der Zustandsraum gewesen
wäre."""

from dataclasses import dataclass

from csdp_constants import MAX_STATES_EXPLORED
from csdp_patterns import feasible_patterns


class _StatesLimitExceeded(Exception):
    pass


@dataclass
class DPResult:
    best_value: object  # int, oder None falls die Sicherheitsgrenze überschritten wurde
    reached: bool
    states_explored: int
    theoretical_max_states: int
    memo: dict  # Zustand -> bester Wert
    best_pattern: dict  # Zustand -> gewähltes Muster
    full_state: tuple


def solve(instance, max_states=MAX_STATES_EXPLORED):
    memo = {}
    best_pattern = {}
    full_state = instance.item_demands
    zero_state = tuple(0 for _ in full_state)

    def f(state):
        if state == zero_state:
            return 0
        if state in memo:
            return memo[state]
        if len(memo) >= max_states:
            raise _StatesLimitExceeded()

        best = None
        chosen_pattern = None
        for pattern in feasible_patterns(instance, state):
            new_state = tuple(s - p for s, p in zip(state, pattern))
            value = 1 + f(new_state)
            if best is None or value < best:
                best = value
                chosen_pattern = pattern

        memo[state] = best
        best_pattern[state] = chosen_pattern
        return best

    theoretical_max_states = 1
    for d in full_state:
        theoretical_max_states *= d + 1

    try:
        best_value = f(full_state)
        reached = True
    except _StatesLimitExceeded:
        best_value = None
        reached = False

    return DPResult(
        best_value=best_value,
        reached=reached,
        states_explored=len(memo),
        theoretical_max_states=theoretical_max_states,
        memo=memo,
        best_pattern=best_pattern,
        full_state=full_state,
    )
