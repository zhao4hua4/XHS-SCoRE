#!/usr/bin/env python3


import argparse
import json
import os
import time
from pathlib import Path
from typing import Dict, Any

import pandas as pd
from openai import OpenAI
from tqdm import tqdm

API_KEY = "removed for privacy"  # or set OPENAI_API_KEY
BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
MODEL_NAME = "qwen3-30b-a3b-instruct-2507"
TEMPERATURE = 0.1
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
        max_tokens=20,
    )
    content = completion.choices[0].message.content or ""
    try:
        parsed = json.loads(_strip_code_fences(content))
        label = str(parsed.get("label", "")).strip().upper()
    except json.JSONDecodeError:
        label = ""
    return (label if label in ALLOWED_LABELS else "", content)


def load_posts(path: Path) -> pd.DataFrame:
    df = pd.read_excel(path)
    content_col = next((c for c in CONTENT_COLS if c in df.columns), None)
    if not content_col:
        raise ValueError(f"None of {CONTENT_COLS} found in {path}")
    if "id" not in df.columns:
        df["id"] = [f"{path.stem}_{i:05d}" for i in range(len(df))]
    return df[["id", content_col]].rename(columns={content_col: "content"})


def main() -> None:
    parser = argparse.ArgumentParser(description="Run qwen3-30b-a3b CN classifier on a full Excel file.")
    parser.add_argument(
        "--input",
        default=str(Path(__file__).resolve().parent / "data" / "test.xlsx"),
        help="Path to input Excel (default: data/test.xlsx next to this script)",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    print(f"Processing file: {input_path}")
    results = []
    try:
        df = load_posts(input_path)
        client = make_client()
        for idx, row in tqdm(df.iterrows(), total=len(df), desc=f"Classifying {input_path.name}"):
            if idx > 0 and idx % 100 == 0:
                time.sleep(10)
            try:
                pred_label, raw = classify(client, str(row["content"]))
            except Exception as row_err:
                pred_label, raw = "", f"error: {row_err}"
                print(f"[warn] row {row.get('id', '?')}: {row_err}")
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
        out_name = f"{input_path.stem}_qwen30b_cn.csv"
        out_path = Path(__file__).resolve().parent / "outputs" / out_name
        output_df = pd.DataFrame(results)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        output_df.to_csv(out_path, index=False)
        print(f"Saved {len(output_df)} rows to {out_path}")


if __name__ == "__main__":
    main()
