import os
from pathlib import Path
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

import pytest

import src.media as m


# ---------------------------
# 더미(모킹) 클래스
# ---------------------------
class DummyAudio:
    def __init__(self):
        self.calls = []

    def write_audiofile(self, path, **kwargs):
        self.calls.append((path, kwargs))

    def close(self):
        pass


class DummyVideoClip:
    def __init__(self, audio_present=True):
        self.audio = DummyAudio() if audio_present else None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class DummyAudioClip:
    def __init__(self, src):
        self.src = src
        self.calls = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def write_audiofile(self, path, **kwargs):
        self.calls.append((path, kwargs))


class DummySegment:
    def __init__(self, length_ms: int):
        self._len = length_ms

    def __len__(self):
        return self._len

    def __getitem__(self, s):
        start = s.start or 0
        end = s.stop or self._len
        return DummySegment(end - start)

    def export(self, out_path, format=None):
        Path(out_path).write_bytes(b"fake wav")


# ---------------------------
# ensure_dirs
# ---------------------------
def test_ensure_dirs(tmp_path: Path):
    d1 = tmp_path / "a"
    d2 = tmp_path / "b" / "c"
    m.ensure_dirs(d1, d2)
    assert d1.exists() and d1.is_dir()
    assert d2.exists() and d2.is_dir()


# ---------------------------
# to_wav_16k_mono - video ok
# ---------------------------
def test_to_wav_video_ok(monkeypatch, tmp_path: Path):
    dummy_clip = DummyVideoClip(audio_present=True)

    # VideoFileClip을 더미로 대체
    monkeypatch.setattr(m, "VideoFileClip", lambda _: dummy_clip)

    # os.replace를 가짜로 대체(호출 여부 확인)
    called = {}
    def fake_replace(src, dst):
        called["src"] = src
        called["dst"] = dst
        Path(dst).write_bytes(b"ok")
    monkeypatch.setattr(os, "replace", fake_replace)

    src = tmp_path / "x.mp4"
    src.write_bytes(b"fake video")
    out = tmp_path / "out.wav"

    result = m.to_wav_16k_mono(src, out)

    assert result == out
    assert Path(out).exists()

    # audio.write_audiofile 호출 파라미터 검증
    assert len(dummy_clip.audio.calls) == 1
    path, kwargs = dummy_clip.audio.calls[0]
    assert path.endswith(".tmp.wav")
    assert kwargs["fps"] == 16000
    assert kwargs["nbytes"] == 2
    assert kwargs["codec"] == "pcm_s16le"

    # os.replace 호출 검증
    assert called["dst"] == str(out)


# ---------------------------
# to_wav_16k_mono - video no audio
# ---------------------------
def test_to_wav_video_no_audio(monkeypatch, tmp_path: Path):
    monkeypatch.setattr(m, "VideoFileClip", lambda _: DummyVideoClip(audio_present=False))

    src = tmp_path / "x.mp4"
    src.write_bytes(b"fake video")
    out = tmp_path / "out.wav"

    with pytest.raises(ValueError) as e:
        m.to_wav_16k_mono(src, out)

    assert "오디오 트랙" in str(e.value)


# ---------------------------
# to_wav_16k_mono - audio ok
# ---------------------------
def test_to_wav_audio_ok(monkeypatch, tmp_path: Path):
    dummy_audio = DummyAudioClip("x.mp3")

    monkeypatch.setattr(m, "AudioFileClip", lambda _: dummy_audio)

    # audio 경로에서는 os.replace가 호출되지 않아야 함
    monkeypatch.setattr(os, "replace", lambda *_: (_ for _ in ()).throw(AssertionError("os.replace 호출되면 안됩니다.")))

    src = tmp_path / "x.mp3"
    src.write_bytes(b"fake mp3")
    out = tmp_path / "out.wav"

    result = m.to_wav_16k_mono(src, out)

    assert result == out
    assert len(dummy_audio.calls) == 1
    path, kwargs = dummy_audio.calls[0]
    assert path == str(out)
    assert kwargs["fps"] == 16000
    assert kwargs["nbytes"] == 2
    assert kwargs["codec"] == "pcm_s16le"


# ---------------------------
# to_wav_16k_mono - unsupported
# ---------------------------
def test_to_wav_unsupported(tmp_path: Path):
    src = tmp_path / "x.txt"
    src.write_text("hi", encoding="utf-8")
    out = tmp_path / "out.wav"

    with pytest.raises(ValueError) as e:
        m.to_wav_16k_mono(src, out)

    assert "지원하지 않는 확장자" in str(e.value)


# ---------------------------
# split_wav - chunk count
# ---------------------------
def test_split_wav_chunks(monkeypatch, tmp_path: Path):
    # 길이 2500ms 오디오로 가정
    monkeypatch.setattr(m.AudioSegment, "from_wav", lambda _: DummySegment(2500))

    wav = tmp_path / "in.wav"
    wav.write_bytes(b"fake")
    out_dir = tmp_path / "chunks"

    chunks = m.split_wav(wav, chunk_seconds=1, out_dir=out_dir)

    assert len(chunks) == 3
    assert chunks[0].name.endswith("_part001.wav")
    assert chunks[1].name.endswith("_part002.wav")
    assert chunks[2].name.endswith("_part003.wav")

    for c in chunks:
        assert c.exists()


def test_split_wav_invalid_seconds(tmp_path: Path):
    wav = tmp_path / "in.wav"
    wav.write_bytes(b"fake")
    out_dir = tmp_path / "chunks"

    with pytest.raises(ValueError):
        m.split_wav(wav, chunk_seconds=0, out_dir=out_dir)
