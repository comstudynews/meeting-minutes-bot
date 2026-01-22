from __future__ import annotations
import json
from typing import Any

from openai import OpenAI
from src.templates import MINUTES_SYSTEM, MINUTES_USER


def normalize_minutes(m: dict[str, Any]) -> dict[str, Any]:
    # 키 흔들림 흡수
    if "participants" not in m and "attendees" in m:
        m["participants"] = m.pop("attendees")
    if "issues" not in m and "risks" in m:
        m["issues"] = m.pop("risks")
    if "notes" in m and isinstance(m["notes"], str):
        m["notes"] = [m["notes"]]

    # summary 문자열 → 리스트 변환
    if "summary" in m and isinstance(m["summary"], str):
        m["summary"] = [m["summary"]]

    # 누락 키 기본값 보정
    m.setdefault("title", "회의록")
    m.setdefault("date", None)
    m.setdefault("participants", [])
    m.setdefault("summary", [])
    m.setdefault("decisions", [])
    m.setdefault("action_items", [])
    m.setdefault("issues", [])
    m.setdefault("notes", [])

    return m


def summarize_minutes(transcript: str) -> dict[str, Any]:
    client = OpenAI()

    prompt = MINUTES_USER.format(transcript=transcript)

    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.2,
        messages=[
            {"role": "system", "content": MINUTES_SYSTEM.strip()},
            {"role": "user", "content": prompt.strip()},
        ],
    )

    text = resp.choices[0].message.content.strip()

    # ① GPT 응답을 JSON으로 파싱
    minutes = json.loads(text)

    # ② 여기서 반드시 정규화 한 번 거쳐서 반환
    return normalize_minutes(minutes)
