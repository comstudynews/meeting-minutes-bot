from __future__ import annotations
from pathlib import Path
from typing import List

from openai import OpenAI

def transcribe_files(files: List[Path], language: str = "ko") -> str:
    client = OpenAI()
    texts: List[str] = []

    for f in files:
        with open(f, "rb") as audio_fp:
            # 모델/파라미터는 조직 정책과 가용 모델에 따라 조정합니다.
            # 오디오 관련 사용법은 OpenAI Audio 가이드를 기준으로 합니다.
            # https://platform.openai.com/docs/guides/audio
            result = client.audio.transcriptions.create(
                model="gpt-4o-mini-transcribe",
                file=audio_fp,
                language=language,
            )
        texts.append(result.text)

    return "\n".join(texts)
