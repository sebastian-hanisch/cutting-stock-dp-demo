import pytest

from csdp_bruteforce import solve_bruteforce
from csdp_constants import PRESETS
from csdp_scenario import generate_instance
from csdp_solver import solve
from csdp_trace import build_trace


@pytest.mark.parametrize("seed", range(15))
def test_matches_bruteforce_across_random_small_instances(seed):
    instance = generate_instance(n_types=4, roll_width=100, max_demand=2, seed=seed)
    result = solve(instance)
    assert result.reached
    true_min = solve_bruteforce(instance)
    assert result.best_value == true_min, f"seed={seed}"


def test_states_explored_never_exceeds_theoretical_max():
    for seed in range(10):
        instance = generate_instance(n_types=5, roll_width=100, max_demand=3, seed=seed)
        result = solve(instance)
        assert result.states_explored <= result.theoretical_max_states


def test_state_space_grows_multiplicatively_with_n_types_not_linearly():
    # Kern-Behauptung dieser Demo: Verdopplung der Auftragstypenzahl bei festem
    # Bedarf lässt den Zustandsraum um mehr als das Doppelte wachsen (tatsächlich
    # multiplikativ) - ein Regressionstest für den zentralen Fund.
    counts = {}
    for n in (2, 4, 6, 8):
        instance = generate_instance(n_types=n, roll_width=100, max_demand=4, seed=2)
        result = solve(instance, max_states=200_000)
        assert result.reached
        counts[n] = result.states_explored
    assert counts[8] > counts[4] * 4  # weit mehr als lineares (2x) Wachstum
    assert counts[4] > counts[2] * 4


def test_safety_limit_is_honored_and_flagged_as_not_reached():
    instance = generate_instance(n_types=8, roll_width=100, max_demand=5, seed=2)
    result = solve(instance, max_states=5000)
    assert not result.reached
    assert result.best_value is None
    assert result.states_explored <= 5000


def test_trace_reconstructs_the_full_demand_exactly():
    for seed in range(10):
        instance = generate_instance(n_types=4, roll_width=100, max_demand=3, seed=seed)
        result = solve(instance)
        trace = build_trace(result)
        assert len(trace) == result.best_value
        totals = [0] * instance.n_types
        for step in trace:
            for i, p in enumerate(step.pattern):
                totals[i] += p
        assert tuple(totals) == instance.item_demands, f"seed={seed}"
        # jedes Muster respektiert die Rollenbreite
        for step in trace:
            used = sum(w * p for w, p in zip(instance.item_widths, step.pattern))
            assert used <= instance.roll_width


@pytest.mark.parametrize("name", list(PRESETS.keys()))
def test_presets_behave_as_documented(name):
    instance = generate_instance(**PRESETS[name])
    result = solve(instance)
    if name == "Grenze erreicht (Column Generation wird nötig)":
        assert not result.reached
    else:
        assert result.reached
        true_min = solve_bruteforce(instance) if instance.n_types <= 4 else None
        if true_min is not None:
            assert result.best_value == true_min
