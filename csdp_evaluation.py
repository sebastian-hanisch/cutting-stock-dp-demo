"""Kennzahlen aus einem DPResult und der Rollenplan-Sequenz."""


def compute_stats(result):
    return {
        "states_explored": result.states_explored,
        "theoretical_max_states": result.theoretical_max_states,
        "reached": result.reached,
        "best_value": result.best_value,
    }


def stats_up_to_step(instance, trace, step):
    """step = Anzahl bereits entschiedener Rollen (0..len(trace))."""
    full_state = instance.item_demands
    remaining_state = full_state if step == 0 else trace[step - 1].to_state
    return {
        "rolls_so_far": step,
        "remaining_state": remaining_state,
        "remaining_total": sum(remaining_state),
    }
