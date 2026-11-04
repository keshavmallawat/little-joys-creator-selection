"""Check the numbers in a written file against outputs/final/claims.csv.

Usage (from the repo root):
    python src/check_numbers.py report/report.md
    python src/check_numbers.py outputs/final/directions_draft.md --show-untagged
    python src/check_numbers.py report/report.md --strict     (warnings also fail)

Convention in the text: a claim_id from claims.csv, then the numbers it backs, up to the
next ';' or ')' or line break or the next claim_id, e.g.
    (cr_CR-13_bootstrap_top5: 83.5%, n=200)
For every tagged segment this script checks that
  - the claim_id exists (unknown ids that look like claim ids are errors);
  - every number in the segment appears in that claim's statement/value/n (a share like
    0.835 also counts as 83.5%; rounding to the number of decimals written is allowed);
  - a tier word in the segment (supported / suggestive / fragile) matches the claim's tier.
Numbers outside any tagged segment are listed as warnings (--show-untagged prints them);
some are legitimate (product facts quoted from ads.csv, time marks), so read them, do not
ignore them. Exit code 1 on errors (and on warnings with --strict).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
NUM = re.compile(r"-?\d+(?:\.\d+)?")
TIERS = ("supported", "suggestive", "fragile")
ID_LIKE = re.compile(r"(?<![\w-])((?:ads|cr|floor|struct|limit|label|proxy|post|comparisons)_[A-Za-z0-9_\-]*[A-Za-z0-9])(?![\w])")


def claim_numbers(row: pd.Series) -> list[float]:
    text = " ".join(str(row[c]) for c in ("statement", "value", "n") if pd.notna(row[c]))
    nums = [float(x) for x in NUM.findall(text)]
    out = list(nums)
    out += [round(x * 100, 6) for x in nums if 0 < abs(x) <= 1]  # fractions also as percent
    return out


def matches(token: str, pool: list[float]) -> bool:
    v = float(token)
    dec = len(token.split(".")[1]) if "." in token else 0
    tol = 0.5 * 10 ** (-dec) + 1e-9
    return any(abs(v - c) <= tol for c in pool)


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print(__doc__)
        return 2
    strict, show = "--strict" in sys.argv, "--show-untagged" in sys.argv
    path = Path(args[0])
    text = path.read_text(encoding="utf-8")
    claims = pd.read_csv(ROOT / "outputs" / "final" / "claims.csv").set_index("claim_id")
    ids = sorted(claims.index, key=len, reverse=True)
    idre = re.compile(r"(?<![\w-])(" + "|".join(re.escape(i) for i in ids) + r")(?![\w])")

    errors: list[str] = []
    ok = 0
    covered = [False] * len(text)
    matches_ = list(idre.finditer(text))
    for k, m in enumerate(matches_):
        start = m.end()
        stops = [len(text)]
        nxt = matches_[k + 1].start() if k + 1 < len(matches_) else None
        if nxt is not None:
            stops.append(nxt)
        for sep in (";", ")", "\n"):
            j = text.find(sep, start)
            if j != -1:
                stops.append(j)
        end = min(stops)
        seg = text[start:end]
        for i in range(m.start(), end):
            covered[i] = True
        row = claims.loc[m.group(1)]
        pool = claim_numbers(row)
        bad = [t for t in NUM.findall(seg) if not matches(t, pool)]
        line = text.count("\n", 0, m.start()) + 1
        if bad:
            errors.append(f"line {line}: {m.group(1)}: number(s) {bad} not in the claim "
                          f"[{str(row['value'])[:80]} | {row['n']}]")
            continue
        words = [w for w in TIERS if re.search(rf"\b{w}\b", seg[:50])]
        if words and str(row["tier"]) in TIERS and words[0] != row["tier"]:
            errors.append(f"line {line}: {m.group(1)}: text says '{words[0]}' but the claim tier is '{row['tier']}'")
            continue
        ok += 1

    known = set(claims.index)
    for m in ID_LIKE.finditer(text):
        if m.group(1) not in known and not any(m.group(1) == i for i in known):
            line = text.count("\n", 0, m.start()) + 1
            errors.append(f"line {line}: '{m.group(1)}' looks like a claim_id but is not in claims.csv")

    # numbers outside tagged segments
    masked = "".join(" " if covered[i] else ch for i, ch in enumerate(text))
    masked = re.sub(r"`[^`]*`", " ", masked)                     # code spans
    masked = re.sub(r"\b(?:CR|LJ)-\d+\b", " ", masked)            # creator / ad ids
    masked = re.sub(r"\d{4}-\d{2}-\d{2}", " ", masked)            # dates
    masked = re.sub(r"\(\d+[–-]\d+s\)|\d+[–-]\d+s", " ", masked)  # time marks
    masked = re.sub(r"(?m)^[ \t]*(?:#+ |\*\*)?\d+\.(?:\*\*)?", " ", masked)  # list numbers
    loose = []
    for m in NUM.finditer(masked):
        line = masked.count("\n", 0, m.start()) + 1
        ctx = text.splitlines()[line - 1].strip()
        loose.append((line, m.group(0), ctx[:110]))

    print(f"{path}: {len(matches_)} claim tags, {ok} verified, {len(errors)} errors, "
          f"{len(loose)} untagged numbers")
    for e in errors:
        print("  ERROR", e)
    if show:
        for line, tok, ctx in loose:
            print(f"  untagged line {line}: {tok}   | {ctx}")
    elif loose:
        print("  (run with --show-untagged to list the untagged numbers)")
    return 1 if errors or (strict and loose) else 0


if __name__ == "__main__":
    sys.exit(main())
