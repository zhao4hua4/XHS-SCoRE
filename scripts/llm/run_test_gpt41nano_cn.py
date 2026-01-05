#!/usr/bin/env python3
"""
Classify posts in data/test.xlsx using OpenRouter (openai/gpt-4.1-nano) with the Chinese prompt.
Includes tqdm progress; keeps per-row error handling and saves partial results.
"""
import json
import os
from pathlib import Path
from typing import Dict, Any

import pandas as pd
from openai import OpenAI
from tqdm import tqdm

API_KEY = "removed for privacy"  # or set OPENAI_API_KEY
BASE_URL = "https://openrouter.ai/api/v1"
MODEL_NAME = "openai/gpt-4.1-nano"
TEMPERATURE = 0.1
REQUEST_TIMEOUT = 300
MAX_TOKENS = 64
MAX_ROWS = None  # set to an int to limit rows; None processes all

EXCEL_PATH = Path(__file__).resolve().parent / "data" / "test.xlsx"
OUTPUT_PATH = Path(__file__).resolve().parent / "outputs" / "test_gpt41nano_cn.csv"
CONTENT_COLS = ["content", "内容"]

SYSTEM_PROMPT = """作为一名 18-24 岁的典型活跃社交媒体用户的视角，仅根据提供的帖子文本将其分类为且仅为一个标签。
不要输出思维过程或中间推理，仅返回标签的 JSON。
- UPWARD：帖主比我更好
- DOWNWARD：帖主比我更糟
- NEUTRAL：与我差不多，或没有/不清晰的比较
"""

USER_PROMPT_TEMPLATE = """帖子：
{post_text}

仅输出 JSON：
{{"label":"UPWARD|DOWNWARD|NEUTRAL"}}
"""

ALLOWED_LABELS = {"UPWARD", "DOWNWARD", "NEUTRAL"}
LABEL_TO_CODE = {"UPWARD": 0, "NEUTRAL": 1, "DOWNWARD": 2}


def _strip_code_fences(text: str) -> str:
    t = text.strip()
    if t.startswith("```"):
        t = t[3:]
        if t.startswith("json"):
            t = t[len("json") :]
        t = t.strip()
        if t.endswith("```"):
            t = t[:-3]
    return t.strip()


def make_client() -> OpenAI:
    key = API_KEY or os.getenv("OPENAI_API_KEY", "")
    base = BASE_URL or os.getenv("OPENAI_BASE_URL", "")
    if not key:
        raise RuntimeError("Set API_KEY or OPENAI_API_KEY before running.")
    kwargs: Dict[str, Any] = {"api_key": key}
    if base:
        kwargs["base_url"] = base
    kwargs["default_headers"] = {
        "X-Title": "test_gpt41nano_cn_run",
        "HTTP-Referer": "https://openrouter.ai",
    }
    return OpenAI(**kwargs)


def classify(client: OpenAI, text: str) -> tuple[str, str]:
    completion = client.chat.completions.create(
        model=MODEL_NAME,
        temperature=TEMPERATURE,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": USER_PROMPT_TEMPLATE.format(post_text=text.strip())},
        ],
        max_tokens=MAX_TOKENS,
        timeout=REQUEST_TIMEOUT,
    )
    content = completion.choices[0].message.content or ""
    try:
        parsed = json.loads(_strip_code_fences(content))
        label = str(parsed.get("label", "")).strip().upper()
    except json.JSONDecodeError:
        label = ""
    return (label if label in ALLOWED_LABELS else "", content)


def load_posts() -> pd.DataFrame:
    df = pd.read_excel(EXCEL_PATH)
    content_col = next((c for c in CONTENT_COLS if c in df.columns), None)
    if not content_col:
        raise ValueError(f"None of {CONTENT_COLS} found in {EXCEL_PATH}")
    if "id" not in df.columns:
        df["id"] = [f"test_{i:05d}" for i in range(len(df))]
    df = df[["id", content_col]].rename(columns={content_col: "content"})
    if MAX_ROWS:
        df = df.head(MAX_ROWS)
    return df


def main() -> None:
    results = []
    try:
        df = load_posts()
        client = make_client()
        for _, row in tqdm(df.iterrows(), total=len(df), desc="Classifying test.xlsx (gpt-4.1-nano)"):
            try:
                pred_label, raw = classify(client, str(row["content"]))
            except Exception as row_err:
                pred_label, raw = "", f"error: {row_err}"
                print(f"[warn] row {row.get('id', '?')}: {row_err}")
            # Only print raw when dataset is tiny to avoid flooding output
            if len(df) <= 5:
                print(f"[debug] id={row.get('id','?')} raw_response={raw}")
            results.append(
                {
                    "id": row.get("id", ""),
                    "predicted": LABEL_TO_CODE.get(pred_label, ""),
                    "gt": "",
                    "raw": raw,
                }
            )
    except Exception as outer_err:
        print(f"[error] Fatal error encountered: {outer_err}")
    finally:
        output_df = pd.DataFrame(results)
        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        output_df.to_csv(OUTPUT_PATH, index=False)
        print(f"Saved {len(output_df)} rows to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
