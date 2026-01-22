from __future__ import annotations
from pathlib import Path
from typing import List

from moviepy import VideoFileClip, AudioFileClip
from pydub import AudioSegment


def ensure_dirs(*dirs: Path) -> None:
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)


def to_wav_16k_mono(src: Path, wav_path: Path) -> None:
    src_str = str(src)

    if src.suffix.lower() in {".mp4", ".mov", ".mkv", ".avi", ".webm"}:
        clip = VideoFileClip(src_str)
        audio = clip.audio
    else:
        clip = None
        audio = AudioFileClip(src_str)

    wav_path.parent.mkdir(parents=True, exist_ok=True)

    audio.write_audiofile(
        str(wav_path),
        fps=16000,
        codec="pcm_s16le",
        ffmpeg_params=["-ac", "1"],
        logger=None,
    )

    audio.close()
    if clip is not None:
        clip.close()


def split_wav(wav_path: Path, chunk_seconds: int, out_dir: Path) -> List[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)

    audio = AudioSegment.from_wav(str(wav_path))
    chunk_ms = chunk_seconds * 1000

    chunks: List[Path] = []
    total_ms = len(audio)

    idx = 0
    for start in range(0, total_ms, chunk_ms):
        end = min(start + chunk_ms, total_ms)
        piece = audio[start:end]

        out_path = out_dir / f"{wav_path.stem}_{idx:04d}.wav"
        piece.export(str(out_path), format="wav")
        chunks.append(out_path)
        idx += 1

    return chunks
