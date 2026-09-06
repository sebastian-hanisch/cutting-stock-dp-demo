"""Zulässige Muster für einen Bedarfs-Zustand aufzählen - selbst ein kleines,
Rucksack-artiges Teilproblem (wie viele Stücke jedes Typs passen zusammen auf eine
Rolle?), hier an jedem Zustand erschöpfend durchprobiert. Genau diese Aufzählung
löst Column Generation (späteres Stück dieser Linie) NICHT erschöpfend, sondern
gezielt über ein Pricing-Teilproblem - der direkte Vorgeschmack."""


def feasible_patterns(instance, state):
    """Alle nicht-leeren Muster p mit p_i <= state_i und sum(w_i * p_i) <= W."""
    n = instance.n_types
    widths = instance.item_widths
    roll_width = instance.roll_width
    patterns = []

    def recurse(i, remaining_width, counts):
        if i == n:
            if any(counts):
                patterns.append(tuple(counts))
            return
        max_by_width = remaining_width // widths[i] if widths[i] > 0 else 0
        max_count = min(state[i], max_by_width)
        for count in range(max_count, -1, -1):
            recurse(i + 1, remaining_width - count * widths[i], counts + [count])

    recurse(0, roll_width, [])
    return patterns
