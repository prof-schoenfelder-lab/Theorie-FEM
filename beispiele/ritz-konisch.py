import marimo

__generated_with = "0.25.1"
app = marimo.App(width="medium", app_title="Konischer Stab: Ritzsches Verfahren")


@app.cell
def _():
    import marimo as mo
    import numpy as np
    import matplotlib.pyplot as plt

    ROT, BLAU, GRUEN, GRAU = "#d40000", "#0050b4", "#006414", "#9a9a9a"
    RITZ = "#b2182b"
    plt.rcParams.update({"font.family": "serif", "mathtext.fontset": "stix", "font.size": 14})

    from matplotlib.ticker import FuncFormatter
    # Achsenbeschriftung mit deutschem Komma
    KOMMA = FuncFormatter(lambda v, _: f"{v:g}".replace(".", ","))
    return BLAU, GRAU, GRUEN, KOMMA, RITZ, ROT, mo, np, plt


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
    # Konischer Stab: Ritzsches Verfahren

    Beispiel aus Vorlesung 2: Stab mit $A(x) = A_0 - (A_0 - A_1)\,x/L$, links fest, rechts Zugkraft $F$.
    $E = 70\,000\,\text{MPa}$, $L = 1000\,\text{mm}$, $F = 5000\,\text{N}$, $A_0 = 100\,\text{mm}^2$.

    Ritz-Ansatz mit Polynomen bis zum Grad $n$, die alle $u(0) = 0$ erfüllen:

    $$\tilde u(x) = \sum_{i=1}^{n} a_i\,\varphi_i(x), \qquad \varphi_i = \left(\frac{x}{L}\right)^i$$

    (Gleicher Ansatz wie mit $x^i$, nur haben alle Koeffizienten die Einheit mm.)

    > Ab welchem Grad ist die **Spannung am Stabende** auf 5 % genau, ab welchem die **Verschiebung**?
    > Was passiert ohne Verjüngung ($A_1/A_0 = 1$)? Und bei sehr starker Verjüngung?
    """)
    return


@app.cell
def _(mo):
    n = mo.ui.slider(1, 8, step=1, value=1, label="Ansatzgrad $n$", show_value=True)
    verh = mo.ui.slider(0.1, 1.0, step=0.05, value=0.2, label="Verjüngung $A_1/A_0$", show_value=True)
    mo.hstack([n, verh], justify="start", gap=3)
    return n, verh


@app.cell
def _(np, verh):
    E, L, F, A0 = 70000.0, 1000.0, 5000.0, 100.0
    A1 = verh.value * A0

    def A(x):
        return A0 - (A0 - A1) / L * x

    def u_exakt(x):
        if abs(A0 - A1) < 1e-12:
            return F * x / (E * A0)
        return F * L / (E * (A0 - A1)) * np.log(A0 / A(x))

    def ritz(n):
        """K a = q mit K_ij = ∫ EA φi' φj' dx und q_i = F φi(L); ∫ exakt über Polynom-Integrale."""
        def I(m):                                # ∫0^L A(x) (x/L)^m dx
            return L * (A0 / (m + 1) - (A0 - A1) / (m + 2))
        i = np.arange(1, n + 1)
        K = E / L**2 * np.outer(i, i) * np.array([[I(a + b - 2) for b in i] for a in i])
        q = F * np.ones(n)
        a = np.linalg.solve(K, q)

        def u(x):
            return sum(ai * (x / L) ** k for ai, k in zip(a, i))

        def sig(x):
            return E * sum(ai * k * (x / L) ** (k - 1) / L for ai, k in zip(a, i))

        Pi = -0.5 * q @ a                        # im Minimum: Π = −½ qᵀa = −½ F ũ(L)
        return K, q, a, u, sig, Pi

    return A, A0, A1, E, F, L, ritz, u_exakt


@app.cell
def _(A0, A1, GRAU, L, ROT, np, plt):
    # Skizze des Systems: veränderlich mit der Verjüngung, Lager und Kraft immer dabei
    figs, axs = plt.subplots(figsize=(10, 2.2))
    s = 0.006                                    # Halbhöhe je mm² Querschnitt (nur für die Skizze)
    h0, h1 = s * A0 * 2.2, s * A1 * 2.2
    axs.fill([0, 1, 1, 0], [h0, h1, -h1, -h0], color="#e6e6e6", ec="k", lw=1.2)
    axs.plot([0, 1], [0, 0], color=GRAU, lw=0.8, ls=(0, (8, 3, 2, 3)))
    axs.plot([0, 0], [-h0 - 0.35, h0 + 0.35], color="k", lw=2)
    for _y in np.linspace(-h0 - 0.35, h0 + 0.35, 12):
        axs.plot([-0.025, 0], [_y - 0.08, _y], color="k", lw=0.8)
    axs.annotate("", xy=(1.13, 0), xytext=(1.0, 0), arrowprops=dict(arrowstyle="-|>", color=ROT, lw=2))
    axs.text(1.14, 0.12, "$F$", color=ROT, fontsize=18)
    axs.text(0.02, h0 + 0.12, "$A_0$", fontsize=15)
    axs.text(0.98, h1 + 0.12, "$A_1$", fontsize=15, ha="right")
    axs.text(0.5, -h0 - 0.35, f"$L = {L:.0f}$ mm", ha="center", fontsize=14)
    axs.set_xlim(-0.06, 1.22); axs.set_ylim(-h0 - 0.5, h0 + 0.5)
    axs.set_aspect("auto"); axs.axis("off")
    figs.tight_layout()
    figs
    return


@app.cell
def _(A, BLAU, F, KOMMA, L, RITZ, n, np, plt, ritz, u_exakt):
    K, q, a, u, sig, Pi = ritz(n.value)
    x = np.linspace(0, L, 400)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
    ax1.plot(x, u_exakt(x), color=BLAU, lw=2, label="exakt")
    ax1.plot(x, u(x), color=RITZ, lw=1.8, ls="--", label=f"Ritz, Grad {n.value}")
    ax1.set_xlabel("$x$ in mm"); ax1.set_ylabel("$u$ in mm"); ax1.grid(alpha=0.3); ax1.legend(loc="upper left")

    ax2.plot(x, F / A(x), color=BLAU, lw=2, label="exakt")
    ax2.plot(x, sig(x), color=RITZ, lw=1.8, ls="--", label="Ritz")
    ax2.set_xlabel("$x$ in mm"); ax2.set_ylabel(r"$\sigma$ in MPa"); ax2.set_ylim(0, None)
    ax2.grid(alpha=0.3); ax2.legend(loc="upper left")
    for _ax in (ax1, ax2):
        _ax.xaxis.set_major_formatter(KOMMA); _ax.yaxis.set_major_formatter(KOMMA)
    fig.tight_layout()
    fig
    return K, Pi, a, sig, u


@app.cell
def _(A, F, L, Pi, mo, sig, u, u_exakt):
    def _k(v, fmt):
        """Zahl mit deutschem Komma (Tabelle außerhalb von Formeln)."""
        return format(v, fmt).replace(".", ",").replace("-", "−")

    def _fehler(r, e):
        _v = (r - e) / abs(e) * 100
        return "0,00 %" if abs(_v) < 0.005 else _k(_v, "+.2f") + " %"

    _uL, _sL = u_exakt(L), F / A(L)
    _Pex = -0.5 * F * _uL
    mo.md(
        f"| | Ritz | exakt | Fehler |\n|:--|:-:|:-:|:-:|\n"
        f"| Verschiebung am Stabende $u(L)$ in mm | {_k(u(L), '.4f')} | {_k(_uL, '.4f')} | {_fehler(u(L), _uL)} |\n"
        f"| Spannung am Stabende $\\sigma(L)$ in MPa | {_k(sig(L), '.1f')} | {_k(_sL, '.1f')} | {_fehler(sig(L), _sL)} |\n"
        f"| Spannung am Lager $\\sigma(0)$ in MPa | {_k(sig(0.0), '.1f')} | {_k(F / A(0.0), '.1f')} | {_fehler(sig(0.0), F / A(0.0))} |\n"
        f"| potentielle Energie $\\Pi$ in Nmm | {_k(Pi, '.1f')} | {_k(_Pex, '.1f')} | {_fehler(Pi, _Pex)} |\n\n"
        "$\\Pi$ liegt immer **über** dem exakten Minimum: Jeder Ansatz ist eine Einschränkung."
    )
    return


@app.cell
def _(A, BLAU, F, GRAU, GRUEN, L, RITZ, n, np, plt, ritz, u_exakt):
    _gs = np.arange(1, 9)
    _ergeb = [ritz(g) for g in _gs]
    _uL, _sL = u_exakt(L), F / A(L)
    _Pex = -0.5 * F * _uL
    # Fehler unter 1e-10 % als Rundungsrauschen auf 1e-10 begrenzen (z. B. ohne Verjüngung schon bei Grad 1 exakt)
    _eu = np.maximum([abs(r[3](L) - _uL) / _uL * 100 for r in _ergeb], 1e-10)
    _es = np.maximum([abs(r[4](L) - _sL) / _sL * 100 for r in _ergeb], 1e-10)
    _ep = np.maximum([abs(r[5] - _Pex) / abs(_Pex) * 100 for r in _ergeb], 1e-10)

    _figk, _axk = plt.subplots(figsize=(8, 4))
    _axk.semilogy(_gs, _eu, "-o", color=BLAU, lw=1.8, ms=4, label="Verschiebung $u(L)$")
    _axk.semilogy(_gs, _es, "-o", color=RITZ, lw=1.8, ms=4, label=r"Spannung $\sigma(L)$")
    _axk.semilogy(_gs, _ep, "-o", color=GRUEN, lw=1.4, ms=3, label=r"Energie $\Pi$")
    _axk.axhline(5, color=GRAU, ls="--", lw=1)
    _axk.text(7.6, 6, "5 %", color="#666666")
    _axk.axvline(n.value, color="k", lw=0.8, ls=":")
    if max(_eu.max(), _es.max(), _ep.max()) < 1e-6:
        _axk.text(4.5, 1e-1, "Schon Grad 1 ist exakt:\nDie Lösung ist linear und liegt im Ansatz.",
                  ha="center", va="center", fontsize=14, color="#444444")
    _axk.set_xlabel("Ansatzgrad $n$"); _axk.set_ylabel("Fehler (logarithmische Skala)")
    _axk.set_title("Konvergenz: Fehler über dem Ansatzgrad", fontsize=14)
    _axk.set_ylim(1e-5, 200)
    # Achse in Prozent statt Zehnerpotenzen: 100 %, 10 %, 1 %, 0,1 % …
    _axk.set_yticks([10.0 ** _k for _k in range(-5, 3)])
    _axk.yaxis.set_major_formatter(plt.FuncFormatter(
        lambda v, _: (f"{v:.5f}".rstrip("0").rstrip(".") + " %").replace(".", ",")))
    _axk.yaxis.set_minor_formatter(plt.NullFormatter())
    _axk.grid(alpha=0.3, which="both"); _axk.legend(loc="lower left")
    _figk.tight_layout()
    _figk
    return


@app.cell
def _(K, a, mo, n):
    def zahl(v, fmt):
        return format(v, fmt).replace(".", "{,}")

    if n.value <= 4:
        zeilen = r" \\ ".join(" & ".join(zahl(v, ".0f") for v in z) for z in K)
        koeff = r" \\ ".join(zahl(v, ".4f") for v in a)
        _aus = mo.md(
            "**Gleichungssystem** $\\mathbf{K}\\,\\mathbf{a} = \\mathbf{q}$ mit "
            "$K_{ij} = \\int_0^L EA\\,\\varphi_i'\\,\\varphi_j'\\,\\mathrm{d}x$ in N/mm und $q_i = F$:\n\n"
            f"$$\\begin{{pmatrix}} {zeilen} \\end{{pmatrix}}\\,\\mathbf{{a}} = \\mathbf{{q}}"
            f"\\quad\\Rightarrow\\quad \\mathbf{{a}} = \\begin{{pmatrix}} {koeff} \\end{{pmatrix}}\\ \\text{{mm}}$$\n\n"
            "Anders als bei der FEM ist die Matrix **voll besetzt**: Jede Ansatzfunktion wirkt auf dem ganzen Stab."
        )
    else:
        _aus = mo.md(
            f"**Gleichungssystem:** {n.value} × {n.value}, voll besetzt. (Für $n \\le 4$ wird es angezeigt.)"
        )
    _aus
    return


if __name__ == "__main__":
    app.run()
