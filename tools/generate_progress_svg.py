from __future__ import annotations

import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "readme"
PROJECT = "FastIPTV Player"
SCOPE = "Product roadmap"
STATUS = "N/A — NO CANONICAL ROADMAP"
REASON = "No authoritative product roadmap or verified completion denominator exists."


def card() -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="180" viewBox="0 0 1200 180" role="img" aria-labelledby="title desc">\n  <title id="title">{PROJECT} progress</title><desc id="desc">{PROJECT}: {SCOPE} progress is N/A because no canonical roadmap exists.</desc>\n  <defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#02050A"/><stop offset="1" stop-color="#07111C"/></linearGradient><pattern id="grid" width="26" height="26" patternUnits="userSpaceOnUse"><path d="M26 0H0V26" stroke="#62E5FF" stroke-opacity="0.06"/></pattern></defs>\n  <rect x="1" y="1" width="1198" height="178" rx="24" fill="url(#bg)" stroke="#62E5FF" stroke-opacity="0.22"/><rect x="1" y="1" width="1198" height="178" rx="24" fill="url(#grid)"/>\n  <text x="50" y="45" fill="#62E5FF" font-family="Segoe UI,Arial,sans-serif" font-size="18" font-weight="700" letter-spacing="4">SWIR PROGRESS</text>\n  <text x="50" y="82" fill="#F4FAFF" font-family="Segoe UI,Arial,sans-serif" font-size="30" font-weight="800">{PROJECT}</text>\n  <text x="50" y="108" fill="#8DA8B8" font-family="Segoe UI,Arial,sans-serif" font-size="16">{SCOPE}: no verified denominator</text>\n  <text x="1085" y="82" text-anchor="end" fill="#F4FAFF" font-family="Segoe UI,Arial,sans-serif" font-size="34" font-weight="800">N/A</text>\n  <text x="1085" y="108" text-anchor="end" fill="#62E5FF" font-family="Segoe UI,Arial,sans-serif" font-size="14" font-weight="700">{STATUS}</text>\n  <rect x="50" y="126" width="1100" height="24" rx="12" fill="#08131F" stroke="#62E5FF" stroke-opacity="0.14"/>\n  <text x="50" y="168" fill="#8DA8B8" font-family="Segoe UI,Arial,sans-serif" font-size="13">{REASON}</text>\n</svg>\n'''


def mini() -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="900" height="72" viewBox="0 0 900 72" role="img" aria-labelledby="title desc">\n  <title id="title">{PROJECT} compact progress</title><desc id="desc">Product roadmap progress is N/A because no canonical roadmap exists.</desc>\n  <rect x="1" y="1" width="898" height="70" rx="18" fill="#02050A" stroke="#62E5FF" stroke-opacity="0.22"/>\n  <text x="24" y="27" fill="#62E5FF" font-family="Segoe UI,Arial,sans-serif" font-size="13" font-weight="700" letter-spacing="2">SWIR ROADMAP</text>\n  <text x="24" y="52" fill="#F4FAFF" font-family="Segoe UI,Arial,sans-serif" font-size="20" font-weight="800">N/A</text>\n  <rect x="170" y="24" width="700" height="20" rx="10" fill="#08131F"/>\n  <text x="870" y="58" text-anchor="end" fill="#8DA8B8" font-family="Segoe UI,Arial,sans-serif" font-size="12">NO CANONICAL ROADMAP</text>\n</svg>\n'''


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    expected = {OUT / "progress-card.svg": card(), OUT / "progress-mini.svg": mini()}
    stale = []
    for path, content in expected.items():
        if args.check:
            if not path.exists() or path.read_text(encoding="utf-8") != content:
                stale.append(str(path.relative_to(ROOT)))
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
    if stale:
        raise SystemExit("stale progress SVG: " + ", ".join(stale))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
