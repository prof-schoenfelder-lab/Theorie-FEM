import marimo

__generated_with = "0.25.1"
app = marimo.App(width="medium", app_title="Federsystem: Minimum der potentiellen Energie")


@app.cell
def _():
    import marimo as mo
    import numpy as np
    import matplotlib.pyplot as plt

    ROT, BLAU, GRUEN = "#d40000", "#0050b4", "#006414"
    plt.rcParams.update({"font.family": "serif", "mathtext.fontset": "stix", "font.size": 14})
    return GRUEN, ROT, mo, np, plt


@app.cell
def _(mo):
    # Größere Schrift für Hörsaal und Beamer (Text, Tabellen, Regler)
    mo.Html("""<style>
      .markdown.prose { font-size: 1.25rem; }
      .markdown.prose table { font-size: 1.15rem; }
      marimo-slider { zoom: 1.3; }
      .marimo-cell img { max-width: 100%; height: auto; }
    </style>""")
    return


@app.cell
def _(mo):
    mo.md(r"""
    # Federsystem: Minimum der potentiellen Energie

    Das Federsystem aus Vorlesung 0 und 1. Die gesamte potentielle Energie hängt von beiden Verschiebungen ab:

    $$\Pi_{ges}(p_1, p_2) = \tfrac12\,\mathbf{p}^\mathsf{T}\mathbf{K}\,\mathbf{p} - \mathbf{p}^\mathsf{T}\mathbf{q}$$

    Das Bild zeigt sie als **Höhenlinien**. Der rote Punkt ist das Minimum, also die Lösung von
    $\mathbf{K}\,\mathbf{p} = \mathbf{q}$. Steifigkeiten in Vielfachen von $k$, Kräfte in Vielfachen von $F$.

    > Wohin wandert das Minimum, wenn Sie $f_2$ verändern? Wie verändert sich das Tal, wenn die Federn steifer
    > werden? Was passiert, wenn $c_1$ und $c_3$ gegen null gehen?
    """)
    return


@app.cell
def _(mo):
    mo.image(src=str(mo.notebook_location() / "public" / "federsystem-system.svg"),
             alt="Federsystem: Wand links, Federn c1, c2, c3, starre Balken mit den Kräften f1, f2 und den Verschiebungen p1, p2",
             width=600).center()
    return


@app.cell
def _(mo):
    c1 = mo.ui.slider(0, 6, step=0.5, value=2, label=r"$c_1 / k$", show_value=True)
    c2 = mo.ui.slider(0, 6, step=0.5, value=4, label=r"$c_2 / k$", show_value=True)
    c3 = mo.ui.slider(0, 6, step=0.5, value=1, label=r"$c_3 / k$", show_value=True)
    f1 = mo.ui.slider(-5, 5, step=0.5, value=3, label=r"$f_1 / F$", show_value=True)
    f2 = mo.ui.slider(-5, 5, step=0.5, value=-1, label=r"$f_2 / F$", show_value=True)
    mo.hstack([mo.vstack([c1, c2, c3]), mo.vstack([f1, f2])], justify="start", gap=3)
    return c1, c2, c3, f1, f2


@app.cell
def _(c1, c2, c3, f1, f2, np):
    K = np.array([[c2.value + c3.value, -c2.value],
                  [-c2.value, c1.value + c2.value]])
    q = np.array([f1.value, f2.value])
    singulaer = abs(np.linalg.det(K)) < 1e-9
    p = None if singulaer else np.linalg.solve(K, q)

    def Pi(p1, p2):
        """Π_ges = ½ pᵀKp − pᵀq in F²/k (auch für Gitter)."""
        return (0.5 * (K[0, 0] * p1**2 + 2 * K[0, 1] * p1 * p2 + K[1, 1] * p2**2)
                - q[0] * p1 - q[1] * p2)
    return K, Pi, p, q, singulaer


@app.cell
def _(GRUEN, Pi, ROT, np, p, plt, singulaer):
    def komma(v, stellen=3):
        """Zahl für Matplotlib-Formeln mit deutschem Komma."""
        return f"{v:.{stellen}g}".replace(".", "{,}")

    # Bildausschnitt: fest, damit man das Minimum wandern sieht; bei Bedarf so erweitert, dass es sichtbar bleibt
    lo, hi = -2.0, 3.5
    if not singulaer:
        lo = min(lo, p[0] - 1, p[1] - 1)
        hi = max(hi, p[0] + 1, p[1] + 1)
    g = np.linspace(lo, hi, 300)
    P1, P2 = np.meshgrid(g, g)
    Z = Pi(P1, P2)

    fig, ax = plt.subplots(figsize=(7, 6.2))
    if singulaer:
        stufen = np.linspace(Z.min(), Z.max(), 25)
    else:
        zmin = Pi(*p)
        stufen = zmin + (np.linspace(0, 1, 18) ** 2) * (Z.max() - zmin)    # dichter nahe dem Minimum
    if Z.max() - Z.min() > 1e-9:                         # alles null: keine Höhenlinien
        ax.contourf(P1, P2, Z, levels=stufen, cmap="Blues_r", alpha=0.85)
        ax.contour(P1, P2, Z, levels=stufen, colors="#08306b", linewidths=0.7)
    ax.axhline(0, color="k", lw=0.8); ax.axvline(0, color="k", lw=0.8)
    if not singulaer:
        ax.plot([p[0], p[0]], [lo, p[1]], ls="--", color=GRUEN, lw=1.2)
        ax.plot([lo, p[0]], [p[1], p[1]], ls="--", color=GRUEN, lw=1.2)
        ax.plot(*p, "o", color=ROT, ms=10, mec="white", mew=1.5, zorder=5)
        ax.annotate(f"$p_1 = {komma(p[0])}$,  $p_2 = {komma(p[1])}$", xy=p, xytext=(12, 12),
                    textcoords="offset points", color=ROT, fontsize=15,
                    bbox=dict(fc="white", ec="none", alpha=0.85, pad=2))
    ax.set_xlim(lo, hi); ax.set_ylim(lo, hi); ax.set_aspect("equal")
    ax.set_xlabel(r"$p_1$ in $F/k$"); ax.set_ylabel(r"$p_2$ in $F/k$")
    ax.set_title(r"Höhenlinien von $\Pi_{ges}$ (dunkel = niedrig)", fontsize=14, color="#555555")
    for _a in (ax.xaxis, ax.yaxis):
        _a.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:g}".replace(".", ",")))
    fig.tight_layout()
    fig
    return


@app.cell
def _(K, Pi, mo, np, p, q, singulaer):
    def zahl(v):
        return "0" if abs(v) < 1e-12 else f"{v:.4g}".replace(".", "{,}")

    kmat = rf"\begin{{pmatrix}} {zahl(K[0, 0])} & {zahl(K[0, 1])} \\ {zahl(K[1, 0])} & {zahl(K[1, 1])} \end{{pmatrix}}"
    if singulaer:
        _aus = mo.md(
            f"$$\\mathbf{{K}} = k\\,{kmat}, \\qquad \\det \\mathbf{{K}} = 0$$\n\n"
            "**Die Matrix ist singulär.** Das Tal hat keinen tiefsten Punkt mehr, sondern eine Rinne (oder fällt "
            "in eine Richtung immer weiter ab): Das System ist nicht ausreichend gelagert und kann als Ganzes "
            "verschoben werden. Es gibt keine eindeutige Lösung."
        )
    else:
        pii = 0.5 * p @ K @ p
        pia = -p @ q
        _aus = mo.md(
            f"$$\\mathbf{{K}} = k\\,{kmat} \\quad\\Rightarrow\\quad p_1 = {zahl(p[0])}\\,\\frac{{F}}{{k}},"
            f"\\quad p_2 = {zahl(p[1])}\\,\\frac{{F}}{{k}}$$\n\n"
            f"| im Minimum | $\\Pi_i$ | $\\Pi_a$ | $\\Pi_{{ges}}$ |\n|:--|:-:|:-:|:-:|\n"
            f"| in $F^2/k$ | ${zahl(pii)}$ | ${zahl(pia)}$ | ${zahl(Pi(*p))}$ |\n\n"
            "Im Minimum gilt immer $\\Pi_i = -\\tfrac12\\,\\Pi_a$."
        )
    _aus
    return


if __name__ == "__main__":
    app.run()
