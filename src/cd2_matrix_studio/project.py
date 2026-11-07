"""CD2 Matrix Studio project format, including v2 compatibility and frame holds."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Sequence

from .protocol import LED_COUNT, ROWS
from .timing import MAX_DURATION_MS, MIN_DURATION_MS, expand_frames, expanded_frame_count

RGB = tuple[int, int, int]
OFF: RGB = (0, 0, 0)
SUPPORTED_FRAME_INTERVALS_MS = (10, 40)
DEFAULT_FRAME_INTERVAL_MS = 40


def blank_frame() -> list[RGB]:
    return [OFF for _ in range(LED_COUNT)]


def interval_ms_to_device_speed_code(interval_ms: int) -> int:
    interval_ms = int(interval_ms)
    if interval_ms not in SUPPORTED_FRAME_INTERVALS_MS:
        raise ValueError(f"Unsupported device interval: {interval_ms} ms")
    return interval_ms // 10


def device_speed_code_to_interval_ms(speed_code: int) -> int:
    return {1: 10, 4: 40}.get(int(speed_code), DEFAULT_FRAME_INTERVAL_MS)


@dataclass
class Project:
    frames: list[list[RGB]] = field(default_factory=lambda: [blank_frame()])
    frame_interval_ms: int = DEFAULT_FRAME_INTERVAL_MS
    path: Path | None = None
    frame_durations_ms: list[int] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.frame_interval_ms = int(self.frame_interval_ms)
        if self.frame_interval_ms not in SUPPORTED_FRAME_INTERVALS_MS:
            raise ValueError("Unsupported base animation interval")
        self._validate_frames(self.frames)
        if not self.frame_durations_ms:
            self.frame_durations_ms = [self.frame_interval_ms] * len(self.frames)
        if len(self.frame_durations_ms) != len(self.frames):
            raise ValueError("Frame/duration count mismatch")
        self.frame_durations_ms = [int(n) for n in self.frame_durations_ms]
        if any(not MIN_DURATION_MS <= n <= MAX_DURATION_MS for n in self.frame_durations_ms):
            raise ValueError("Invalid frame duration")

    @property
    def device_speed_code(self) -> int:
        return interval_ms_to_device_speed_code(self.frame_interval_ms)

    def to_device_frames(self) -> list[list[RGB]]:
        return expand_frames(self.frames, self.frame_durations_ms, self.frame_interval_ms)

    def device_frame_count(self) -> int:
        return expanded_frame_count(
            self.frame_durations_ms, self.frame_interval_ms,
            single_static=len(self.frames) == 1,
        )

    @classmethod
    def from_dict(cls, data: dict) -> "Project":
        if data.get("format") == "cd2-matrix-studio" and "frames" in data:
            frames = [[tuple(map(int, rgb)) for rgb in frame] for frame in data["frames"]]
            cls._validate_frames(frames)
            anim = data.get("animation") or {}
            if "frame_interval_ms" in anim:
                interval = int(anim["frame_interval_ms"])
                if interval not in SUPPORTED_FRAME_INTERVALS_MS:
                    interval = DEFAULT_FRAME_INTERVAL_MS
            elif "device_speed_code" in anim:
                interval = device_speed_code_to_interval_ms(anim["device_speed_code"])
            else:
                interval = DEFAULT_FRAME_INTERVAL_MS
            durations = anim.get("frame_durations_ms")
            if durations is None:
                durations = [interval] * len(frames)
            return cls(frames=frames, frame_interval_ms=interval, frame_durations_ms=durations)
        if "frames" in data:  # Legacy format v3
            frames = [[tuple(map(int, rgb)) for rgb in frame] for frame in data["frames"]]
            return cls(frames=frames, frame_interval_ms=device_speed_code_to_interval_ms(data.get("speed_code", 4)))
        if "colors" in data:  # Legacy v1/v2 static drawings
            colors = [tuple(map(int, rgb)) for rgb in data["colors"]]
            return cls(frames=[colors])
        raise ValueError("Unsupported project format")

    @staticmethod
    def _validate_frames(frames: Sequence[Sequence[RGB]]) -> None:
        if not frames:
            raise ValueError("Project contains no frames")
        for frame in frames:
            if len(frame) != LED_COUNT:
                raise ValueError(f"A frame contains {len(frame)} LEDs instead of {LED_COUNT}")
            for rgb in frame:
                if len(rgb) != 3 or any(not 0 <= int(v) <= 255 for v in rgb):
                    raise ValueError("Invalid RGB value")

    def to_dict(self) -> dict:
        return {
            "format": "cd2-matrix-studio",
            "version": 3,
            "device": "flydigi-charging-dock-2-pro",
            "rows": list(ROWS),
            "animation": {
                "frame_interval_ms": self.frame_interval_ms,
                "device_speed_code": self.device_speed_code,
                "frame_durations_ms": self.frame_durations_ms.copy(),
            },
            "frames": self.frames,
        }

    @classmethod
    def load(cls, path: str | Path) -> "Project":
        p = Path(path)
        with p.open("r", encoding="utf-8") as f:
            data = json.load(f)
        project = cls.from_dict(data)
        project.path = p
        return project

    def save(self, path: str | Path | None = None) -> Path:
        p = Path(path) if path else self.path
        if p is None:
            raise ValueError("No project path specified")
        self.__post_init__()  # Validate before overwriting an existing project.
        with p.open("w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)
        self.path = p
        return p
