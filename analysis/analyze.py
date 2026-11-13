"""E1 (dose-response) and E2 (mitigations) analysis: tables (CSV + LaTeX) and figures (PDF).

Input : results/analysis/E1.csv, E2.csv  (from analysis/aggregate.py)
Output: results/analysis/{tables,figures}/

Unit of analysis is the episode; tasks are the clustering unit (12 tasks, 3 reps each per cell).
- Effects vs baseline: difference of cell means, 95% CI from a task-cluster bootstrap.
- Dose trend per (model, source): OLS  y ~ k + task fixed effects, task-clustered SEs,  on the k=0 baseline plus
  the k>0 cells of that source; Holm correction over the 10 (model, source) slopes.
- Source vs filler: y ~ k + k:is_source + task FE on source + filler cells (shared baseline),
  the interaction tests whether a real sub-task costs more than an equal-length neutral message.
- E2: y ~ C(condition, Treatment('none')) + task FE, Holm over the 4 mitigations.

Needs pandas, statsmodels, matplotlib (installed in the Leonardo venv).
"""
from __future__ import annotations

import re
import warnings
from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from statsmodels.stats.multitest import multipletests

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parent.parent
IN = ROOT / "results" / "analysis"
TAB, FIG = IN / "tables", IN / "figures"
RNG = np.random.default_rng(20261104)
N_BOOT = 2000

SOURCES = ["user", "env", "text", "cascade", "filler"]
SOURCE_LABEL = {"user": "User side-request", "env": "Environment (failing test)",
                "text": "Text (TODO/README)", "cascade": "Cascade (broken dependency)",
                "filler": "Filler (neutral control)"}
MODELS = ["qwen3-coder:30b", "gpt-oss:20b"]
MODEL_LABEL = {"qwen3-coder:30b": "qwen3-coder 30B", "gpt-oss:20b": "gpt-oss 20B"}
# reference categorical palette (dataviz skill), slots 1-2; text stays in ink colours
COLOR = {"qwen3-coder:30b": "#2a78d6", "gpt-oss:20b": "#eb6834"}
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e4e3df"
CONDITIONS = ["none", "anchor", "checklist", "subagent", "tasklist"]
COND_LABEL = {"none": "No mitigation", "anchor": "Goal re-anchoring hook", "checklist": "Stop-hook checklist",
              "subagent": "Sub-agent delegation", "tasklist": "Task list"}

OUTCOMES = {"hidden_pass": "Hidden-test pass rate", "full_pass": "Goal fully met",
            "oos_existing_ratio": "Out-of-scope edits (existing files)",
            "oos_new_other_lines": "Stray new files (lines)", "tool_calls": "Tool calls"}


def load(name: str) -> pd.DataFrame:
    d = pd.read_csv(IN / f"{name}.csv")
    d["full_pass"] = (d["hidden_pass"] >= 0.999).astype(float)
    d["hidden_pass"] = d["hidden_pass"].fillna(0.0)
    return d


def cluster_boot(a: pd.DataFrame, b: pd.DataFrame | None, col: str) -> tuple:
    """Mean of `a` (or mean(a) - mean(b)) with a 95% CI resampling tasks with replacement."""
    tasks = sorted(set(a["task"]) | (set(b["task"]) if b is not None else set()))
    ga = {t: g[col].to_numpy() for t, g in a.groupby("task")}
    gb = {t: g[col].to_numpy() for t, g in b.groupby("task")} if b is not None else {}

    def stat(ts):
        va = np.concatenate([ga[t] for t in ts if t in ga])
        if b is None:
            return va.mean()
        vb = np.concatenate([gb[t] for t in ts if t in gb])
        return va.mean() - vb.mean()

    est = stat(tasks)
    boots = [stat(RNG.choice(tasks, len(tasks))) for _ in range(N_BOOT)]
    lo, hi = np.percentile(boots, [2.5, 97.5])
    return est, lo, hi


def fit(formula: str, data: pd.DataFrame):
    """OLS with task fixed effects and task-clustered (CR1) standard errors.

    (A random-intercept MixedLM was the first choice but hits singular fits on the sparse count
    outcomes; with every task present in every cell, task fixed effects estimate the same contrasts.)"""
    data = data.reset_index(drop=True)
    return smf.ols(f"{formula} + C(task)", data).fit(cov_type="cluster",
                                                      cov_kwds={"groups": pd.factorize(data["task"])[0]})


def mixed(formula: str, data: pd.DataFrame, term: str) -> tuple:
    m = fit(formula, data)
    return m.params[term], m.bse[term], m.pvalues[term]


# --------------------------------------------------------------------------- E1
def e1_tables(d: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for m in MODELS:
        dm = d[d.model == m]
        base = dm[dm.source == "none"]
        for src in SOURCES:
            for k in (0, 1, 2, 4):
                cell = base if k == 0 else dm[(dm.source == src) & (dm.k == k)]
                r = {"model": m, "source": src, "k": k, "n": len(cell)}
                for col in OUTCOMES:
                    r[col], r[col + "_lo"], r[col + "_hi"] = cluster_boot(cell, None, col)
                    if k:
                        r["d_" + col], r["d_" + col + "_lo"], r["d_" + col + "_hi"] = cluster_boot(cell, base, col)
                if src == "user" and k:
                    r["side_pass"] = cell["side_pass"].mean()
                rows.append(r)
    cells = pd.DataFrame(rows)
    cells.to_csv(TAB / "e1_cells.csv", index=False)

    tests = []
    for m in MODELS:
        dm = d[d.model == m]
        base = dm[dm.source == "none"]
        filler = dm[dm.source == "filler"]
        for src in SOURCES:
            sub = pd.concat([base, dm[dm.source == src]])
            for col in ("hidden_pass", "oos_new_other_lines"):
                b, se, p = mixed(f"{col} ~ k", sub, "k")
                r = {"model": m, "source": src, "outcome": col, "slope": b, "se": se, "p": p}
                if src != "filler":
                    both = pd.concat([base, dm[dm.source == src], filler])
                    both["is_src"] = (both.source == src).astype(int)
                    # both arms start from the same k=0 baseline episodes: shared intercept, separate slopes
                    bi, sei, pi = mixed(f"{col} ~ k + k:is_src", both, "k:is_src")
                    r.update(vs_filler=bi, vs_filler_se=sei, vs_filler_p=pi)
                tests.append(r)
    tests = pd.DataFrame(tests)
    for col in ("hidden_pass", "oos_new_other_lines"):
        sel = tests.outcome == col
        tests.loc[sel, "p_holm"] = multipletests(tests.loc[sel, "p"], method="holm")[1]
        sel2 = sel & tests.vs_filler_p.notna()
        tests.loc[sel2, "vs_filler_p_holm"] = multipletests(tests.loc[sel2, "vs_filler_p"], method="holm")[1]
    tests.to_csv(TAB / "e1_tests.csv", index=False)
    return cells, tests


def write_tex(path: Path, lines: list) -> None:
    """Typeset minus signs as math minus (plain '-' prints as a hyphen in the table)."""
    path.write_text(re.sub(r"(?<![\w$])-(\d)", r"$-$\1", "\n".join(lines) + "\n"))


def stars(p: float) -> str:
    return "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""


def e1_latex(cells: pd.DataFrame, tests: pd.DataFrame) -> None:
    """Table: hidden pass at k=0/1/2/4 per source x model, plus Holm-corrected slope per k."""
    lines = [r"\begin{tabular}{llcccccc}", r"\toprule",
             r"Model & Source & $k{=}0$ & $k{=}1$ & $k{=}2$ & $k{=}4$ & Slope per sub-task & vs.\ filler \\",
             r"\midrule"]
    for m in MODELS:
        for i, src in enumerate(SOURCES):
            c = cells[(cells.model == m) & (cells.source == src)].set_index("k")
            t = tests[(tests.model == m) & (tests.source == src) & (tests.outcome == "hidden_pass")].iloc[0]
            vals = " & ".join(f"{c.loc[k, 'hidden_pass']:.2f}" for k in (0, 1, 2, 4))
            slope = f"{t.slope:+.3f}{stars(t.p_holm)}"
            vf = "--" if src == "filler" else f"{t.vs_filler:+.3f}{stars(t.vs_filler_p_holm)}"
            name = MODEL_LABEL[m] if i == 0 else ""
            lines.append(f"{name} & {SOURCE_LABEL[src]} & {vals} & {slope} & {vf} \\\\")
        lines.append(r"\midrule" if m != MODELS[-1] else r"\bottomrule")
    lines.append(r"\end{tabular}")
    write_tex(TAB / "e1_hidden.tex", lines)


def style(ax) -> None:
    ax.spines[["top", "right"]].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(INK2)
        ax.spines[s].set_linewidth(0.6)
    ax.tick_params(colors=INK2, labelsize=7, width=0.6)
    ax.grid(axis="y", color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)


def e1_figure(cells: pd.DataFrame) -> None:
    rows = [("hidden_pass", "Hidden-test pass rate", (0, 1)),
            ("oos_new_other_lines", "Stray new files (lines)", None)]
    fig, axes = plt.subplots(len(rows), len(SOURCES), figsize=(7.2, 3.6), sharex=True, sharey="row")
    for r, (col, ylabel, ylim) in enumerate(rows):
        for c, src in enumerate(SOURCES):
            ax = axes[r, c]
            style(ax)
            for m in MODELS:
                s = cells[(cells.model == m) & (cells.source == src)].sort_values("k")
                ax.fill_between(s.k, s[col + "_lo"], s[col + "_hi"], color=COLOR[m], alpha=0.12, linewidth=0)
                ax.plot(s.k, s[col], color=COLOR[m], linewidth=1.5, marker="o", markersize=3.5,
                        markeredgecolor="white", markeredgewidth=0.6, label=MODEL_LABEL[m])
            if ylim:
                ax.set_ylim(*ylim)
            ax.set_xticks([0, 1, 2, 4])
            if r == 0:
                ax.set_title(SOURCE_LABEL[src].replace(" (", "\n("), fontsize=7, color=INK)
            if c == 0:
                ax.set_ylabel(ylabel, fontsize=7, color=INK)
            if r == len(rows) - 1:
                ax.set_xlabel("sub-tasks injected ($k$)", fontsize=7, color=INK2)
    h, lab = axes[0, 0].get_legend_handles_labels()
    fig.legend(h, lab, loc="upper center", ncol=2, frameon=False, fontsize=7, bbox_to_anchor=(0.5, 1.02))
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(FIG / "e1_dose_response.pdf", bbox_inches="tight")
    plt.close(fig)


# --------------------------------------------------------------------------- E2
def e2(d: pd.DataFrame) -> pd.DataFrame:
    base = d[d.condition == "none"]
    rows = []
    for c in CONDITIONS:
        cell = d[d.condition == c]
        r = {"condition": c, "n": len(cell), "hook_fires": cell.hook_fires.mean()}
        for col in OUTCOMES:
            r[col], r[col + "_lo"], r[col + "_hi"] = cluster_boot(cell, None, col)
            if c != "none":
                r["d_" + col], r["d_" + col + "_lo"], r["d_" + col + "_hi"] = cluster_boot(cell, base, col)
        r["side_pass"] = cell.side_pass.mean()
        rows.append(r)
    out = pd.DataFrame(rows)
    pvals = {}
    for col in ("hidden_pass", "full_pass", "oos_new_other_lines"):
        m = fit(f"{col} ~ C(condition, Treatment('none'))", d)
        ps = [m.pvalues[f"C(condition, Treatment('none'))[T.{c}]"] for c in CONDITIONS[1:]]
        adj = multipletests(ps, method="holm")[1]
        for c, p, pa in zip(CONDITIONS[1:], ps, adj):
            out.loc[out.condition == c, f"p_{col}"] = p
            out.loc[out.condition == c, f"p_holm_{col}"] = pa
    out.to_csv(TAB / "e2_conditions.csv", index=False)

    lines = [r"\begin{tabular}{lcccccc}", r"\toprule",
             r"Condition & Hidden pass & $\Delta$ vs.\ none [95\% CI] & Goal fully met & Side request met"
             r" & Stray lines & Tool calls \\", r"\midrule"]
    for _, r in out.iterrows():
        delta = "--" if r.condition == "none" else (
            f"{r.d_hidden_pass:+.3f} [{r.d_hidden_pass_lo:+.2f}, {r.d_hidden_pass_hi:+.2f}]"
            f"{stars(r.p_holm_hidden_pass)}")
        lines.append(f"{COND_LABEL[r.condition]} & {r.hidden_pass:.3f} & {delta} & {r.full_pass:.2f} & "
                     f"{r.side_pass:.2f} & {r.oos_new_other_lines:.1f} & {r.tool_calls:.1f} \\\\")
    lines += [r"\bottomrule", r"\end{tabular}"]
    write_tex(TAB / "e2_conditions.tex", lines)

    fig, ax = plt.subplots(figsize=(4.2, 2.0))
    style(ax)
    ax.grid(axis="y", visible=False)
    ax.grid(axis="x", color=GRID, linewidth=0.6)
    sub = out[out.condition != "none"].iloc[::-1]
    y = np.arange(len(sub))
    ax.axvline(0, color=INK2, linewidth=0.8)
    ax.hlines(y, sub.d_hidden_pass_lo, sub.d_hidden_pass_hi, color=COLOR[MODELS[0]], linewidth=1.5)
    ax.plot(sub.d_hidden_pass, y, "o", color=COLOR[MODELS[0]], markersize=5, markeredgecolor="white",
            markeredgewidth=0.8)
    ax.set_yticks(y, [COND_LABEL[c] for c in sub.condition], fontsize=7, color=INK)
    ax.set_xlabel("$\\Delta$ hidden-test pass rate vs. no mitigation (95% CI)", fontsize=7, color=INK2)
    fig.tight_layout()
    fig.savefig(FIG / "e2_mitigations.pdf", bbox_inches="tight")
    plt.close(fig)
    return out


def main() -> None:
    TAB.mkdir(parents=True, exist_ok=True)
    FIG.mkdir(parents=True, exist_ok=True)
    d1 = load("E1")
    cells, tests = e1_tables(d1)
    e1_latex(cells, tests)
    e1_figure(cells)
    d2 = load("E2")
    out2 = e2(d2)
    pd.set_option("display.width", 200)
    print(cells[["model", "source", "k", "n", "hidden_pass", "d_hidden_pass", "d_hidden_pass_lo", "d_hidden_pass_hi",
                 "full_pass", "oos_existing_ratio", "oos_new_other_lines", "side_pass"]].round(3).to_string())
    print(tests.round(4).to_string())
    print(out2[["condition", "hidden_pass", "d_hidden_pass", "d_hidden_pass_lo", "d_hidden_pass_hi",
                "p_holm_hidden_pass", "full_pass", "p_holm_full_pass", "side_pass", "oos_new_other_lines",
                "p_holm_oos_new_other_lines", "tool_calls", "hook_fires"]].round(3).to_string())
    for name, d in (("E1", d1), ("E2", d2)):
        print(name, "eval errors:", d.eval_errors.fillna("").str.split(";").explode().str.split(":").str[:2]
              .str.join(":").value_counts().to_dict())
        print(name, "final subtype:", d.final_subtype.fillna("missing").value_counts().to_dict(),
              "compactions>0:", int((d.compactions > 0).sum()))


if __name__ == "__main__":
    main()
