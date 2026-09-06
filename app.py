"""
Dynamische Programmierung am Cutting-Stock-Problem – interaktive Konzept-Demo
Sebastian Hanisch - Operations Research und Machine Learning

Zweites Stück der Cutting-Stock-Linie: Kontrast zu cutting-stock-branch-bound-demo,
dieselbe Rolle wie dynamic-programming-demo in der ersten Linie - aber mit einer
grundlegend anderen eigenen Schwäche: hier bläht sich der Zustandsraum mit der
ANZAHL AUFTRAGSTYPEN auf, nicht mit der Kapazität.

Lauffähig mit: streamlit run app.py
"""

import streamlit as st

import csdp_constants as C
from csdp_bruteforce import solve_bruteforce
from csdp_evaluation import compute_stats, stats_up_to_step
from csdp_presets import (
    apply_preset,
    bounds,
    init_session_state_defaults,
    load_permalink_settings,
    randomize_seed,
    sync_query_params,
)
from csdp_scenario import generate_instance
from csdp_solver import solve
from csdp_trace import build_trace
from csdp_visualization import build_states_chart

st.set_page_config(page_title="Cutting Stock Dynamische Programmierung – Sebastian Hanisch", layout="wide")


@st.cache_data(show_spinner=False)
def _compute_solve(n_types, roll_width, max_demand, seed):
    instance = generate_instance(n_types, roll_width, max_demand, seed)
    result = solve(instance)
    return instance, result


st.title("🧮📏 Dynamische Programmierung am Cutting-Stock-Problem")
st.markdown(
    """
Zweites Stück der Cutting-Stock-Linie - ein **Kontrast** zu
[cutting-stock-branch-bound-demo](https://github.com/sebastian-hanisch/cutting-stock-branch-bound-demo),
dieselbe Rolle wie [dynamic-programming-demo](https://github.com/sebastian-hanisch/dynamic-programming-demo)
in der ersten Linie - aber mit einer grundlegend ANDEREN eigenen Schwäche: dort blähte
sich die Tabelle mit der **Kapazität** auf, hier bläht sich der **Zustandsraum mit
der Anzahl Auftragstypen** auf - komplett unabhängig von der Rollenbreite. Genau
**wie** das funktioniert, erklärt der aufgeklappte Abschnitt direkt darunter.
"""
)
st.caption(
    "Anders als die Fall-Demos im Portfolio, die an einem Anwendungsfall mehrere Verfahren "
    "vergleichen, zeigt diese Demo - wie cutting-stock-branch-bound-demo aus dieser Linie - "
    "ein Verfahren an einem wachsenden Beispiel."
)

with st.expander("So funktioniert die Rekursion", expanded=True):
    st.markdown(
        r"""
Der **Zustand** ist ein Vektor: wie viele Einheiten von jedem Auftragstyp noch zu
schneiden sind. Von einem Zustand aus wird jedes zulässige **Muster** durchprobiert
(eine Kombination von Stücken, die zusammen auf eine Rolle passt) - für jedes Muster
wird rekursiv der Rest gelöst, das Minimum plus die eine gerade benutzte Rolle ist
das Ergebnis für diesen Zustand. Bereits berechnete Zustände werden gespeichert
(memoisiert), nie zweimal gelöst.

Die Suche nach einem guten Muster IST selbst ein kleines rucksackartiges
Teilproblem - hier an jedem Zustand vollständig durchprobiert. Genau diese
Aufzählung wird **Column Generation** (ein späteres Stück dieser Linie) nicht
erschöpfend, sondern gezielt lösen - der direkte Vorgeschmack.

Weiter unten sehen Sie das Ergebnis als **Rollenplan**: eine Sequenz "Rolle 1: dieses
Muster, Rolle 2: jenes Muster, ...", bis kein Bedarf mehr übrig ist.
        """
    )

st.caption("🎯 Schnellstart – ein Beispielszenario laden:")
PRESET_HELP = {
    "Winzige Instanz (Zustandsraum komplett sichtbar)": "3 Auftragstypen - der komplette Zustandsraum ist winzig, der ganze Rollenplan leicht nachvollziehbar.",
    "Wachsender Zustandsraum (noch schnell)": "6 Auftragstypen - der Zustandsraum ist bereits über 1.000 Zustände groß, aber noch in Sekundenbruchteilen lösbar.",
    "Grenze erreicht (Column Generation wird nötig)": "8 Auftragstypen, hoher Bedarf - der Zustandsraum wird zu groß für vollständige Aufzählung. Genau das motiviert Column Generation.",
}
preset_cols = st.columns(len(C.PRESETS))
for i, name in enumerate(C.PRESETS.keys()):
    with preset_cols[i]:
        st.button(name, use_container_width=True, on_click=apply_preset, args=(name,), help=PRESET_HELP[name])

st.caption(
    "🔗 Die Adresszeile oben spiegelt Ihre aktuelle Konfiguration wider – einfach kopieren, "
    "um ein Szenario zu teilen."
)

load_permalink_settings()
init_session_state_defaults()

with st.sidebar:
    st.header("⚙️ Einstellungen")
    n_types = st.slider(
        "Anzahl Auftragstypen", *bounds("n_types_slider"), key="n_types_slider",
        help="Die für dieses Stück entscheidende Wachstumsachse - der Zustandsraum wächst multiplikativ mit dieser Zahl.",
    )
    roll_width = st.slider("Rollenbreite", *bounds("roll_width_slider"), key="roll_width_slider")
    max_demand = st.slider("Maximaler Bedarf je Auftragstyp", *bounds("max_demand_slider"), key="max_demand_slider")
    seed = st.number_input("Zufalls-Seed", *bounds("seed_input"), key="seed_input", step=1)

    st.button(
        "🎲 Neue Instanz generieren",
        use_container_width=True,
        on_click=randomize_seed,
        help="Würfelt neue Auftragsbreiten und -mengen.",
    )

sync_query_params(n_types, roll_width, max_demand, seed)

scenario_key = (int(n_types), int(roll_width), int(max_demand), int(seed))

with st.spinner("Fülle den Zustandsraum..."):
    instance, result = _compute_solve(*scenario_key)

st.caption(
    f"🔗 {instance.n_types} Auftragstypen, Breiten {instance.item_widths} mit Bedarf "
    f"{instance.item_demands}, Rollenbreite {instance.roll_width}."
)

st.markdown("## 🎯 Der Rollenplan")

if not result.reached:
    st.error(
        f"⛔ Diese Instanz hätte einen Zustandsraum von bis zu **{result.theoretical_max_states:,}** "
        f"möglichen Bedarfsvektoren - die Suche wurde nach {result.states_explored:,} tatsächlich "
        f"berechneten Zuständen abgebrochen (Grenze: {C.MAX_STATES_EXPLORED:,}). Anders als bei einem "
        f"Suchbaum kann diese Rekursion kein Zwischenergebnis liefern, solange nicht alle nötigen "
        f"Zustände berechnet sind - deshalb hier bewusst gar kein (unvollständiges) Ergebnis. "
        f"Reglereinstellungen (weniger Auftragstypen, geringerer Bedarf) verkleinern den "
        f"Zustandsraum. Genau dieser Punkt motiviert Column Generation: statt vorab ALLE Muster "
        f"für ALLE Zustände zu berechnen, sucht es gezielt nur die Muster, die tatsächlich helfen."
    )
else:
    trace = build_trace(result)
    max_step = len(trace)

    if "csdp_step" not in st.session_state or st.session_state.get("csdp_step_owner") != scenario_key:
        st.session_state["csdp_step"] = max_step
        st.session_state["csdp_step_owner"] = scenario_key

    if max_step == 0:
        step = 0
        st.caption("Kein Bedarf vorhanden - kein Regler nötig.")
    else:
        step = st.slider(
            "Schritt (Rolle)", 0, max_step, key="csdp_step",
            help="Ein Schritt = eine im Rollenplan festgelegte Rolle.",
        )

    live = stats_up_to_step(instance, trace, step)
    lm1, lm2, lm3 = st.columns(3)
    lm1.metric("Rollen bisher festgelegt", f"{live['rolls_so_far']} / {max_step}")
    lm2.metric("Restbedarf (Einzelstücke)", f"{live['remaining_total']:,}")
    lm3.metric("Zustände im Memo", f"{result.states_explored:,}")

    if step > 0:
        st.markdown("**Rollenplan bisher:**")
        for s in trace[:step]:
            pattern_txt = ", ".join(
                f"{p}× Typ {i + 1} (Breite {instance.item_widths[i]})"
                for i, p in enumerate(s.pattern) if p > 0
            )
            st.markdown(f"- **Rolle {s.roll_number}**: {pattern_txt} → Restbedarf {s.to_state}")

    if step == max_step:
        true_optimum = solve_bruteforce(instance) if instance.n_types <= 4 else None
        if true_optimum is not None:
            st.caption(
                f"Bewiesenes Optimum: **{result.best_value}** Rollen - stimmt mit der unabhängigen "
                f"Bruteforce-Referenz überein."
                if result.best_value == true_optimum
                else f"⚠️ Optimum {result.best_value} weicht von der Bruteforce-Referenz {true_optimum} ab - bitte melden."
            )
        else:
            st.caption(f"Bewiesenes Optimum: **{result.best_value}** Rollen.")

st.markdown("---")

st.subheader("📐 Wie stark bläht sich der Zustandsraum wirklich auf?")
st.markdown(
    """
Live für Ihre aktuelle Instanz: wie viele der theoretisch möglichen Bedarfs-
Kombinationen wurden tatsächlich besucht?
"""
)

stats = compute_stats(result)
gc1, gc2 = st.columns(2)
gc1.metric(
    "Theoretisches Maximum", f"{stats['theoretical_max_states']:,}",
    help="Produkt aus (Bedarf je Typ + 1) über alle Auftragstypen - wächst multiplikativ mit "
    "jedem zusätzlichen Typ, unabhängig von der Rollenbreite.",
)
gc2.metric(
    "Tatsächlich besuchte Zustände", f"{stats['states_explored']:,}" + ("" if stats["reached"] else " (Grenze erreicht)"),
)
st.plotly_chart(build_states_chart(result), use_container_width=True, key="states_chart")

if not stats["reached"]:
    st.warning(
        "⚠️ Die Sicherheitsgrenze wurde erreicht, bevor die Rekursion abschließen konnte - "
        "genau der Punkt, an dem vollständige Aufzählung praktisch aufgibt."
    )
elif stats["states_explored"] >= 500:
    st.info(
        f"ℹ️ Bereits bei {instance.n_types} Auftragstypen braucht die Rekursion "
        f"{stats['states_explored']:,} Zustände - unabhängig davon, wie breit die Rolle ist. "
        f"Mehr Auftragstypen (siehe Presets) lassen diese Zahl noch viel schneller wachsen."
    )
else:
    st.info(
        "Bei dieser (kleinen) Instanz bleibt der Zustandsraum noch überschaubar - probieren Sie "
        "mehr Auftragstypen (Presets oben oder Regler), um die Explosion live zu sehen."
    )

st.markdown("---")

with st.expander("📐 Mathematische Formulierung"):
    st.markdown(
        r"""
**Zustand**: Vektor $\vec{r} = (r_1, \dots, r_n)$ - Restbedarf je Auftragstyp.
**Muster**: Vektor $p$ mit $p_i \le r_i$ und $\sum_i w_i p_i \le W$ - eine
Kombination von Stücken, die zusammen auf eine Rolle passt.

$$
f(\vec{r}) = \begin{cases} 0 & \vec{r} = \vec{0} \\ 1 + \min\limits_{p \subseteq \vec{r},\ p \ne \vec{0}} f(\vec{r} - p) & \text{sonst} \end{cases}
$$

Das Optimum steht in $f(\vec{q})$, ausgehend vom vollen Bedarfsvektor $\vec{q}$.
Rückverfolgung: an jedem Zustand wurde das gewählte Muster gespeichert, ihm
rückwärts zu folgen ergibt den Rollenplan.

**Komplexität**: der Zustandsraum hat höchstens $\prod_i (q_i + 1)$ Elemente -
**multiplikativ** in der Anzahl Auftragstypen $n$, komplett unabhängig von der
Rollenbreite $W$. Das ist der genaue Gegensatz zu
[dynamic-programming-demo](https://github.com/sebastian-hanisch/dynamic-programming-demo)
aus der ersten Linie, dessen Tabelle mit der Kapazität wächst, aber nicht mit der
Anzahl Paket-Typen. Beide Verfahren sind exakt und pseudopolynomial - nur an
unterschiedlichen Stellen "pseudo".

Implementiert in `csdp_solver.py` (memoisierte Rekursion), `csdp_patterns.py`
(Muster-Aufzählung je Zustand) und `csdp_trace.py` (Rückverfolgung zum Rollenplan).
        """
    )

st.markdown("---")

st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning. Interesse an einer maßgeschneiderten Lösung für "
    "Ihr Unternehmen? [Kontakt aufnehmen](https://sebastianhanisch.net/kontakt.html)"
)
