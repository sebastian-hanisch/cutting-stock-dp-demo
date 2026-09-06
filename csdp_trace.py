"""Rekonstruiert die Rollenplan-Sequenz vom vollen Bedarfsvektor bis zum
Nullvektor entlang der in csdp_solver.solve gewählten Muster - die Entsprechung zu
dynamic-programming-demo's Rückverfolgung, hier als lineare Sequenz statt als Pfad
durch eine 2D-Tabelle, da der Zustand hier ein Vektor ist."""

from dataclasses import dataclass


@dataclass(frozen=True)
class TraceStep:
    roll_number: int  # 1-basiert
    from_state: tuple
    pattern: tuple
    to_state: tuple


def build_trace(result):
    if not result.reached:
        return ()

    steps = []
    state = result.full_state
    zero_state = tuple(0 for _ in state)
    roll_number = 1
    while state != zero_state:
        pattern = result.best_pattern[state]
        new_state = tuple(s - p for s, p in zip(state, pattern))
        steps.append(TraceStep(roll_number, state, pattern, new_state))
        state = new_state
        roll_number += 1

    return tuple(steps)
