import marimo

__generated_with = "0.25.1"
app = marimo.App(width="medium", app_title="Konischer Stab: Elementanzahl und Konvergenz")


@app.cell
def _():
    import marimo as mo
    import numpy as np
    import matplotlib.pyplot as plt

    ROT, BLAU, GRUEN, GRAU = "#d40000", "#0050b4", "#006414", "#9a9a9a"
    plt.rcParams.update({"font.family": "serif", "mathtext.fontset": "stix", "font.size": 11})
    return BLAU, GRAU, ROT, mo, np, plt


@app.cell
def _(mo):
    mo.md(r"""
    # Konischer Stab: Elementanzahl und Konvergenz

    Beispiel aus Vorlesung 3: Stab mit $A(x) = A_0 - (A_0 - A_1)\,x/L$, links gelagert, rechts Zugkraft $F$.
    $E = 70\,000$ MPa, $L = 1000$ mm, $F = 5000$ N, $A_0 = 100$ mm².
    Jedes lineare Element bekommt die Querschnittsfläche in seiner Mitte.

    > Wie viele Elemente brauchen Sie, damit die **maximale Spannung** auf 5 % genau ist?
    > Und wie viele für die **Verschiebung am Stabende**?
    """)
    return


@app.cell
def _(mo):
    n = mo.ui.slider(1, 30, step=1, value=3, label="Anzahl Elemente $n$", show_value=True)
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

    def fem(n):
        """FEM wie in der Vorlesung: Elementmatrizen, Inzidenzmatrizen, Zusammenbau, Lösung."""
        Le = L / n
        Ke = [E * A((e + 0.5) * Le) / Le * np.array([[1.0, -1.0], [-1.0, 1.0]]) for e in range(n)]
        Lam = []
        for e in range(n):                       # p^e = (p_1^e, p_2^e): rechter, linker Knoten
            La = np.zeros((2, n + 1))
            La[0, e + 1] = 1.0
            La[1, e] = 1.0
            Lam.append(La)
        Ksys = sum(La.T @ K @ La for La, K in zip(Lam, Ke))
        qsys = np.zeros(n + 1)
        qsys[-1] = F
        p = np.zeros(n + 1)                      # Randbedingung p_1 = 0: erste Zeile/Spalte streichen
        p[1:] = np.linalg.solve(Ksys[1:, 1:], qsys[1:])
        sig = np.array([E * (La @ p)[0] / Le - E * (La @ p)[1] / Le for La in Lam])
        return Le, Ksys, p, sig

    return A, A1, F, L, fem, u_exakt


@app.cell
def _(A, BLAU, F, L, ROT, fem, n, np, plt, u_exakt):
    Le, Ksys, p, sig = fem(n.value)
    x = np.linspace(0, L, 400)
    xk = np.arange(n.value + 1) * Le

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 3.8))
    ax1.plot(x, u_exakt(x), color=BLAU, lw=2, label="exakt")
    ax1.plot(xk, p, "-o", color=ROT, lw=1.6, ms=4, label=f"FEM, {n.value} Elemente")
    ax1.set_xlabel("$x$ in mm"); ax1.set_ylabel("$u$ in mm"); ax1.grid(alpha=0.3); ax1.legend(loc="upper left")

    ax2.plot(x, F / A(x), color=BLAU, lw=2, label="exakt")
    ax2.stairs(sig, np.r_[xk], color=ROT, lw=1.6, fill=False, label="FEM")
    ax2.fill_between(np.repeat(xk, 2)[1:-1], np.repeat(sig, 2), color=ROT, alpha=0.08, lw=0)
    ax2.set_xlabel("$x$ in mm"); ax2.set_ylabel(r"$\sigma$ in MPa"); ax2.set_ylim(0, None)
    ax2.grid(alpha=0.3); ax2.legend(loc="upper left")
    fig.tight_layout()
    fig
    return Ksys, p, sig


@app.cell
def _(A, F, L, mo, p, sig, u_exakt):
    fu = (p[-1] - u_exakt(L)) / u_exakt(L) * 100
    fs = (sig.max() - F / A(L)) / (F / A(L)) * 100
    mo.md(
        f"| | FEM | exakt | Fehler |\n|:--|:-:|:-:|:-:|\n"
        f"| Verschiebung am Stabende $u(L)$ in mm | {p[-1]:.4f} | {u_exakt(L):.4f} | {fu:+.2f} % |\n"
        f"| maximale Spannung in MPa | {sig.max():.1f} | {F / A(L):.1f} | {fs:+.2f} % |\n"
    )
    return


@app.cell
def _(A, BLAU, F, L, ROT, fem, n, np, plt, u_exakt):
    ns = np.arange(1, 61)
    eu = np.array([abs(fem(k)[2][-1] - u_exakt(L)) / u_exakt(L) * 100 for k in ns])
    es = np.array([abs(fem(k)[3].max() - F / A(L)) / (F / A(L)) * 100 for k in ns])
    figk, axk = plt.subplots(figsize=(7.5, 3.6))
    axk.loglog(ns, eu, color=BLAU, lw=1.8, label="Verschiebung $u(L)$")
    axk.loglog(ns, es, color=ROT, lw=1.8, label=r"max. Spannung $\sigma(L)$")
    axk.axhline(5, color="#9a9a9a", ls="--", lw=1)
    axk.text(1.05, 5.5, "5 %", color="#666666")
    axk.plot([n.value, n.value], [eu[n.value - 1], es[n.value - 1]], "o", color="k", ms=5)
    axk.set_xlabel("Anzahl Elemente $n$"); axk.set_ylabel("Fehler in %")
    axk.set_title("Konvergenz: Fehler über der Elementanzahl", fontsize=11)
    axk.grid(alpha=0.3, which="both"); axk.legend()
    figk.tight_layout()
    figk
    return


@app.cell
def _(Ksys, mo, n, np):
    if n.value <= 6:
        zeilen = r" \\ ".join(" & ".join("0" if abs(v) < 1e-9 else f"{v:.0f}" for v in z) for z in Ksys)
        _aus = mo.md(
            "**Systemsteifigkeitsmatrix** $\\mathbf{K}_{sys} = \\sum_e \\boldsymbol{\\Lambda}^{e\\mathsf{T}}"
            "\\mathbf{K}^e\\boldsymbol{\\Lambda}^e$ in N/mm (vor dem Einarbeiten der Randbedingung):\n\n"
            f"$$\\begin{{pmatrix}} {zeilen} \\end{{pmatrix}}$$\n\n"
            "Nur die Diagonale und ihre direkten Nachbarn sind besetzt (Bandstruktur)."
        )
    else:
        _belegt = np.count_nonzero(np.abs(Ksys) > 1e-9)
        _aus = mo.md(
            f"**Systemsteifigkeitsmatrix:** {Ksys.shape[0]} × {Ksys.shape[1]}, davon nur {_belegt} von "
            f"{Ksys.size} Einträgen besetzt. (Für $n \\le 6$ wird die Matrix angezeigt.)"
        )
    _aus
    return


if __name__ == "__main__":
    app.run()
