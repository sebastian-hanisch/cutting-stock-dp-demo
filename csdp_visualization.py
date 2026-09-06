"""Balkendiagramm: tatsächlich besuchte vs. theoretisch mögliche Zustände - der
Kern-Beleg für "der Zustandsraum bläht sich mit der Auftragstypenzahl auf"."""


def build_states_chart(result):
    import plotly.graph_objects as go

    labels = ["Tatsächlich besucht", "Theoretisches Maximum"]
    values = [result.states_explored, result.theoretical_max_states]

    fig = go.Figure(
        data=go.Bar(
            x=labels, y=values, marker_color=["#1f77b4", "#c4cbd8"],
            text=[f"{v:,}" for v in values], textposition="outside",
        )
    )
    fig.update_layout(
        template="plotly_white", height=280,
        yaxis=dict(title="Anzahl Zustände", fixedrange=True),
        xaxis=dict(fixedrange=True),
        margin=dict(t=20, l=10, r=10, b=10),
    )
    return fig
