import marimo

__generated_with = "0.25.1"
app = marimo.App(width="medium", app_title="Federsystem: Steifigkeitsmatrix")


@app.cell
def _():
    import marimo as mo
    import numpy as np
    import matplotlib.pyplot as plt

    ROT, BLAU, GRUEN, GRAU = "#d40000", "#0050b4", "#006414", "#9a9a9a"
    plt.rcParams.update({"font.family": "serif", "mathtext.fontset": "stix", "font.size": 14})
    return GRAU, GRUEN, ROT, mo, np, plt


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
    # Federsystem: Steifigkeitsmatrix

    System aus Vorlesung 0: Feder $c_1$ von der Wand zum mittleren Balken ($p_2$), Feder $c_2$ zwischen den Balken,
    Feder $c_3$ von der Wand zum rechten Balken ($p_1$). Steifigkeiten in Vielfachen von $k$, Kräfte in Vielfachen von $F$.

    > Was passiert, wenn $c_1$ und $c_3$ gegen null gehen? Für welche Kräfte ist $N_2 = 0$?
    """)
    return


@app.cell
def _(mo):
    mo.image(src=str(mo.notebook_location() / "public" / "federsystem-system.svg"),
             alt="Federsystem: Wand links, Federn c1, c2, c3, starre Balken mit den Kräften f1, f2 und den Verschiebungen p1, p2",
             width=720).center()
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
    det = np.linalg.det(K)
    singulaer = abs(det) < 1e-9
    if singulaer:
        p = None
        N = None
    else:
        p = np.linalg.solve(K, q)
        u = np.array([p[1], p[0] - p[1], p[0]])
        N = np.array([c1.value, c2.value, c3.value]) * u
    return K, N, det, p, q, singulaer


@app.cell
def _(K, N, det, mo, p, q, singulaer):
    def zahl(v):
        return "0" if abs(v) < 1e-12 else f"{v:.4g}".replace(".", "{,}")

    def zahl_text(v):
        """Zahl für Tabellen außerhalb von Formeln: deutsches Komma."""
        return "0" if abs(v) < 1e-12 else f"{v:.4g}".replace(".", ",")

    kmat = rf"\begin{{pmatrix}} {zahl(K[0, 0])} & {zahl(K[0, 1])} \\ {zahl(K[1, 0])} & {zahl(K[1, 1])} \end{{pmatrix}}"
    qvec = rf"\begin{{pmatrix}} {zahl(q[0])}\,F \\ {zahl(q[1])}\,F \end{{pmatrix}}"
    if singulaer:
        _aus = mo.md(
            f"$$k\\,{kmat}\\begin{{pmatrix}} p_1 \\\\ p_2 \\end{{pmatrix}} = {qvec}$$\n\n"
            f"**$\\det \\mathbf{{K}} = 0$: Die Matrix ist singulär.** Das System ist nicht ausreichend gelagert "
            f"und kann als Ganzes verschoben werden. Es gibt keine eindeutige Lösung."
        )
    else:
        _aus = mo.md(
            f"$$k\\,{kmat}\\begin{{pmatrix}} p_1 \\\\ p_2 \\end{{pmatrix}} = {qvec}"
            f"\\quad\\Rightarrow\\quad p_1 = {zahl(p[0])}\\,\\frac{{F}}{{k}},\\quad p_2 = {zahl(p[1])}\\,\\frac{{F}}{{k}}$$\n\n"
            f"| Feder | $N_1$ | $N_2$ | $N_3$ |\n|:--|:-:|:-:|:-:|\n"
            f"| Kraft in $F$ | {zahl_text(N[0])} | {zahl_text(N[1])} | {zahl_text(N[2])} |\n\n"
            f"$\\det \\mathbf{{K}} = {zahl(det)}\\,k^2$ · Kontrolle: mittlerer Balken $-N_1 + N_2 + f_2 = "
            f"{zahl(-N[0] + N[1] + q[1])}$, rechter Balken $-N_2 - N_3 + f_1 = {zahl(-N[1] - N[2] + q[0])}$"
        )
    _aus
    return


@app.cell
def _(GRAU, GRUEN, N, ROT, f1, f2, np, p, plt, singulaer):
    def feder(ax, x0, x1, y, farbe, lw):
        n, a = 8, 0.12
        xs = np.linspace(x0 + 0.25 * (x1 - x0), x1 - 0.25 * (x1 - x0), 2 * n + 1)
        ys = y + a * np.array([0] + [(-1) ** i for i in range(1, 2 * n)] + [0])
        ax.plot([x0, xs[0]], [y, y], color=farbe, lw=lw)
        ax.plot(xs, ys, color=farbe, lw=lw)
        ax.plot([xs[-1], x1], [y, y], color=farbe, lw=lw)

    def komma(v, stellen=3):
        """Zahl für Matplotlib-Formeln mit deutschem Komma."""
        return f"{v:.{stellen}g}".replace(".", "{,}")

    def platte(ax, x, y0, y1, farbe, alpha):
        ax.add_patch(plt.Rectangle((x - 0.06, y0), 0.12, y1 - y0, fc=farbe, ec="k", alpha=alpha, lw=1))

    fig, ax = plt.subplots(figsize=(8, 3.2))
    xw, xm, xr = 0.0, 2.0, 4.0
    s = 0.0 if singulaer else 0.5 / max(1e-9, np.max(np.abs(p)))
    ax.plot([xw, xw], [-0.2, 2.2], color="k", lw=2.5)                 # feste Wand links
    for yy in np.arange(-0.15, 2.2, 0.15):
        ax.plot([xw, xw - 0.12], [yy, yy - 0.12], color="k", lw=0.8)
    for zustand in ("unverformt", "verformt"):
        if zustand == "verformt" and singulaer:
            continue
        if zustand == "unverformt":
            dm = dr = 0.0
            farbe, alpha, lw = GRAU, 0.35, 1.0
        else:
            dm, dr = s * p[1], s * p[0]               # Darstellung skaliert
            farbe, alpha, lw = ROT, 0.9, 1.6
        platte(ax, xm + dm, -0.1, 1.3, farbe, alpha)
        platte(ax, xr + dr, -0.1, 2.1, farbe, alpha)
        feder(ax, xw, xm + dm - 0.06, 0.6, farbe if zustand == "verformt" else GRAU, lw)
        feder(ax, xm + dm + 0.06, xr + dr - 0.06, 0.6, farbe if zustand == "verformt" else GRAU, lw * 1.6)
        feder(ax, xw, xr + dr - 0.06, 1.7, farbe if zustand == "verformt" else GRAU, lw)
    # äußere Kräfte an den Balken (Länge ~ Betrag, Richtung nach Vorzeichen), an der verformten Lage
    dm_k, dr_k = (0.0, 0.0) if singulaer else (s * p[1], s * p[0])
    for xp, y, fw, name in ((xm + dm_k, 1.15, f2.value, "f_2"), (xr + dr_k, 1.95, f1.value, "f_1")):
        if abs(fw) > 1e-9:
            x0 = xp + np.sign(fw) * 0.06                      # Pfeil beginnt an der Balkenseite
            lang = 0.15 * abs(fw) + 0.2
            ax.annotate("", xy=(x0 + np.sign(fw) * lang, y), xytext=(x0, y),
                        arrowprops=dict(arrowstyle="-|>", color=ROT, lw=2, mutation_scale=14))
            ax.text(x0 + np.sign(fw) * lang / 2, y + 0.12, f"${name} = {komma(fw)}\\,F$", color=ROT, ha="center", fontsize=15,
                    bbox=dict(fc="white", ec="none", pad=1, alpha=0.85))
    if not singulaer:
        for x, y, nn in ((1.0, 0.95, f"$N_1 = {komma(N[0])}\\,F$"), (3.0, 0.95, f"$N_2 = {komma(N[1])}\\,F$"),
                         (2.0, 2.05, f"$N_3 = {komma(N[2])}\\,F$")):
            ax.text(x, y, nn, ha="center", color=GRUEN, fontsize=15)
    ax.set_xlim(-0.3, 5.9); ax.set_ylim(-0.4, 2.4); ax.axis("off")
    ax.set_title("grau: unverformt · rot: verformt (Verschiebungen skaliert)", fontsize=14, color="#555555")
    fig.tight_layout()
    fig
    return


if __name__ == "__main__":
    app.run()
