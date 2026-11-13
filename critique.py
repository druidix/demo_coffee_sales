#!/usr/bin/env python3
"""Reflection step: a stronger model critiques chart_v<N>.py and its PNG output.

Usage: ./critique.py 1   -> reads chart_v1.py + charts/chart_v1.png, writes critiques/critique_v1.md
"""
import base64
import sys
from pathlib import Path

import anthropic
import pandas as pd
from dotenv import load_dotenv

CRITIC_MODEL = "claude-fable-5-1"
ROOT = Path(__file__).parent

SYSTEM = """You are a senior data-visualization reviewer. You critique charts for a business
audience: correctness first, then whether the chart's main message is readable at a
glance, then legibility and polish. Be concrete: every issue names the specific fix in
matplotlib/pandas terms. Do not rewrite the whole script."""

PROMPT = """The goal of this chart: compare coffee sales between Q1 2025 and Q1 2026.

The data file (data/coffee_sales_q1.csv) has these columns and sample rows:
{sample}

Here is the code that produced the attached chart:
```python
{code}
```

Review the rendered chart image and the code. Reply in Markdown with:
1. **Verdict** - one or two sentences on whether the chart achieves its goal.
2. **Issues** - a numbered list, most important first. For each: severity (high/medium/low),
   what is wrong, and the concrete fix.
Keep it under 500 words."""


def main() -> None:
    if len(sys.argv) != 2 or not sys.argv[1].isdigit():
        sys.exit("usage: ./critique.py <version-number>")
    v = sys.argv[1]
    code_path, png_path = ROOT / f"chart_v{v}.py", ROOT / "charts" / f"chart_v{v}.png"
    for p in (code_path, png_path):
        if not p.exists():
            sys.exit(f"missing {p}")

    sample = pd.read_csv(ROOT / "data" / "coffee_sales_q1.csv", nrows=4).to_csv(index=False)
    image_b64 = base64.standard_b64encode(png_path.read_bytes()).decode()

    load_dotenv(ROOT / ".env")
    client = anthropic.Anthropic()
    response = client.beta.messages.create(
        model=CRITIC_MODEL,
        max_tokens=16000,
        output_config={"effort": "high"},
        # Fable models can decline on safety classifiers; "default" reroutes by refusal category
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
        system=SYSTEM,
        messages=[{
            "role": "user",
            "content": [
                {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": image_b64}},
                {"type": "text", "text": PROMPT.format(sample=sample, code=code_path.read_text())},
            ],
        }],
    )

    if response.stop_reason == "end_turn":
        critique = "".join(b.text for b in response.content if b.type == "text")
    elif response.stop_reason == "refusal":
        sys.exit(f"critic refused: {response.stop_details}")
    elif response.stop_reason == "max_tokens":
        sys.exit("critic hit max_tokens; raise the limit")
    else:
        sys.exit(f"unexpected stop_reason: {response.stop_reason}")

    if response.model != CRITIC_MODEL:
        print(f"note: served by fallback model {response.model}, not {CRITIC_MODEL}")

    out = ROOT / "critiques" / f"critique_v{v}.md"
    out.parent.mkdir(exist_ok=True)
    out.write_text(f"<!-- critic: {response.model} -->\n\n{critique}\n")
    print(critique)
    print(f"\nwrote {out}  (in={response.usage.input_tokens} out={response.usage.output_tokens} tokens)")


if __name__ == "__main__":
    main()
