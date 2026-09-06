# Dynamische Programmierung am Cutting-Stock-Problem – Streamlit-Demo

**[→ Demo live ausprobieren](https://sebastianhanisch-cutting-stock-dp-demo.streamlit.app/)**

Zweites Stück der Cutting-Stock-Linie (nach
[cutting-stock-branch-bound-demo](https://github.com/sebastian-hanisch/cutting-stock-branch-bound-demo)):
ein **Kontrast**, kein Fix - dieselbe Rolle wie
[dynamic-programming-demo](https://github.com/sebastian-hanisch/dynamic-programming-demo)
in der ersten (Rucksack-)Linie, aber mit einer grundlegend anderen eigenen
Schwäche: dort blähte sich die Tabelle mit der **Kapazität** auf, hier bläht sich
der **Zustandsraum mit der Anzahl Auftragstypen** auf - komplett unabhängig von der
Rollenbreite.

## Der Algorithmus

**Zustand**: ein Vektor - wie viele Einheiten von jedem Auftragstyp noch zu
schneiden sind. An jedem Zustand werden alle zulässigen **Muster** (Kombinationen
von Stücken, die auf eine Rolle passen - selbst ein kleines rucksackartiges
Teilproblem) durchprobiert, memoisiert über bereits berechnete Zustände. Genau
diese erschöpfende Muster-Aufzählung wird **Column Generation** (ein späteres
Stück dieser Linie) nicht mehr erschöpfend, sondern gezielt über ein
Pricing-Teilproblem lösen.

## Empirisch UND rechnerisch bestätigte Explosion

Bei festem Bedarf pro Typ wächst die tatsächlich besuchte Zustandszahl mit der
Auftragstypenzahl $n$ etwa wie $5^n$: 4 Typen → 90 Zustände, 6 Typen → 1.440, 8
Typen → 24.000 (2,2 s) - eine Verdopplung von $n$ macht den Zustandsraum ~267×
größer, unabhängig von der Rollenbreite. Ein Extremfall (8 Typen, Bedarf bis 5)
erreicht ~65.000 Zustände in 6,9 s - bewusst als eigenes Preset genutzt, das die
Sicherheitsgrenze auslöst, statt vermieden zu werden.

## Sicherheitsgrenze wie dynamic-programming-demo, nicht wie ein Suchbaum-Verfahren

Diese Rekursion liefert kein Zwischenergebnis, solange nicht alle nötigen Zustände
berechnet sind. Bei Überschreiten von `MAX_STATES_EXPLORED` wird deshalb gar nicht
erst gerechnet, nur ehrlich erklärt, wie groß der Zustandsraum gewesen wäre - die
live erlebte Begründung, warum Column Generation später in dieser Linie nötig wird.

## Visualisierung: Rollenplan statt Baum oder 2D-Tabelle

Der Zustand ist hier ein Vektor, keine einzelne Zahl - eine 2D-Heatmap wie in
dynamic-programming-demo ergibt für mehr als zwei Auftragstypen keinen Sinn mehr.
Stattdessen: Rückverfolgung vom vollen Bedarfsvektor zum Nullvektor ergibt eine
lineare Sequenz ("Rolle 1: dieses Muster, Rolle 2: jenes Muster, ..."), unabhängig
von der Auftragstypenzahl darstellbar, mit demselben Schritt-Regler wie überall
sonst im Portfolio - plus ein Balkendiagramm "besuchte vs. theoretisch mögliche
Zustände" als Kernbeleg.

## Verifikation

- **Bruteforce-Cross-Check** über viele Zufallsinstanzen und alle kleinen Presets.
- **Zustandszahl-Wachstums-Test**: Verdopplung der Auftragstypenzahl muss den
  Zustandsraum um mehr als das Vierfache wachsen lassen (multiplikativ, nicht
  linear) - ein Regressionstest für den zentralen Fund dieser Demo.
- **Rückverfolgungs-Invariante**: die Summe aller Muster entlang des Rollenplans
  ergibt exakt den ursprünglichen Bedarfsvektor, jedes Muster respektiert die
  Rollenbreite.
- **Sicherheitsgrenzen-Test**: das "Grenze erreicht"-Preset löst zuverlässig die
  Sicherheitsgrenze aus, statt (fälschlich) ein Ergebnis zu liefern.

## Dateistruktur

| Datei | Inhalt |
|---|---|
| `app.py` | Streamlit-Hauptablauf: Presets, Einstellungen, Rollenplan, Zustandsraum-Vergleich, Formulierungs-Expander |
| `csdp_constants.py` | Defaults, Regler-Grenzen, Sicherheitsgrenzen, `PRESETS` |
| `csdp_presets.py` | `SettingSpec`/`SETTING_SPECS`, Permalink-Logik, Presets, Zufalls-Seed-Button |
| `csdp_scenario.py` | Zufällige Cutting-Stock-Instanzen (ein Rollentyp) |
| `csdp_patterns.py` | Zulässige Muster für einen Bedarfs-Zustand aufzählen |
| `csdp_solver.py` | Memoisierte Rekursion über Bedarfsvektoren |
| `csdp_trace.py` | Rückverfolgung zum Rollenplan |
| `csdp_bruteforce.py` | Unabhängige Referenzlösung (vollständige Enumeration) |
| `csdp_evaluation.py` | Kennzahlen aus einem Suchlauf |
| `csdp_visualization.py` | Zustände-Balkendiagramm (Plotly) |
| `tests/` | Bruteforce-Cross-Check, Zustandszahl-Wachstum, Rückverfolgungs-Invariante, Sicherheitsgrenzen |

## Lokal ausführen

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```

## Tests ausführen

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

---

Teil des [Operations-Research-Demo-Portfolios](https://sebastianhanisch.net/demos.html) von
[Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning.
Interesse an einer maßgeschneiderten Lösung? [Kontakt aufnehmen](https://sebastianhanisch.net/kontakt.html).
