from __future__ import annotations

MINUTES_SYSTEM = """
당신은 회의록 작성 도우미입니다.
출력은 반드시 JSON 객체 한 개만 반환합니다.
아래 스키마의 키 이름을 절대 변경하지 않습니다.
코드블록을 사용하지 않습니다.
"""

MINUTES_USER = """
다음 전사문을 바탕으로 회의록을 JSON으로 정리하세요.

반드시 아래 키만 사용하세요(추가/변경 금지).
{{ 
  "title": "회의 제목(추정 가능)",
  "date": null,
  "participants": [],
  "summary": [],
  "decisions": [],
  "action_items": [
    {{ "owner": null, "task": "", "due": null }}
  ],
  "issues": [],
  "notes": []
}}

작성 규칙:
1. date는 알 수 없으면 null입니다.
2. summary, decisions, issues, notes는 문장 배열입니다.
3. participants는 이름/역할을 알 수 없으면 빈 배열입니다.
4. action_items는 없으면 빈 배열입니다.

전사문:
{transcript}
"""
