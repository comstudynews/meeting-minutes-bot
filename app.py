from __future__ import annotations
import json
from pathlib import Path
from dotenv import load_dotenv

from src.media import ensure_dirs, to_wav_16k_mono, split_wav
from src.stt import transcribe_files
from src.summarize import summarize_minutes

def main() -> None:
    load_dotenv()

    base = Path(__file__).parent
    uploads = base / "data" / "uploads"
    chunks_dir = base / "data" / "chunks"
    outputs = base / "data" / "outputs"
    ensure_dirs(uploads, chunks_dir, outputs)

    file_path_str = input("업로드 파일 경로(음성/동영상)를 입력하세요: ").strip()
    src = Path(file_path_str)

    if not src.exists():
        raise FileNotFoundError(f"파일이 없습니다: {src}")

    wav_path = uploads / f"{src.stem}.wav"
    to_wav_16k_mono(src, wav_path)

    chunk_seconds = 60
    chunks = split_wav(wav_path, chunk_seconds=chunk_seconds, out_dir=chunks_dir)

    transcript = transcribe_files(chunks, language="ko")
    minutes = summarize_minutes(transcript)

    out_file = outputs / f"{src.stem}_minutes.json"
    out_file.write_text(json.dumps(minutes, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"완료: {out_file}")

if __name__ == "__main__":
    main()
