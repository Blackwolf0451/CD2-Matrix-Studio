from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Sequence

from .protocol import LED_COUNT, ROWS

RGB = tuple[int, int, int]
OFF: RGB = (0, 0, 0)

SUPPORTED_FRAME_INTERVALS_MS = (10, 40)
DEFAULT_FRAME_INTERVAL_MS = 40


def blank_frame() -> list[RGB]:
    return [OFF for _ in range(LED_COUNT)]


def interval_ms_to_device_speed_code(interval_ms: int) -> int:
    """
    Official Flydigi captures:
      10 ms -> timing byte 0x01
      40 ms -> timing byte 0x04
    """
    interval_ms = int(interval_ms)
    if interval_ms not in SUPPORTED_FRAME_INTERVALS_MS:
        raise ValueError(
            f"Unsupported frame interval: {interval_ms} ms. "
            f"Supported values: {SUPPORTED_FRAME_INTERVALS_MS}"
        )
    return interval_ms // 10


def device_speed_code_to_interval_ms(speed_code: int) -> int:
    speed_code = int(speed_code)
    if speed_code == 1:
        return 10
    if speed_code == 4:
        return 40
    return DEFAULT_FRAME_INTERVAL_MS


@dataclass
class Project:
    frames: list[list[RGB]] = field(default_factory=lambda: [blank_frame()])
    frame_interval_ms: int = DEFAULT_FRAME_INTERVAL_MS
    path: Path | None = None

    @property
    def device_speed_code(self) -> int:
        return interval_ms_to_device_speed_code(self.frame_interval_ms)

    @classmethod
    def from_dict(cls, data: dict) -> "Project":
        # Current project format.
        if data.get("format") == "cd2-matrix-studio" and "frames" in data:
            frames = [
                [tuple(map(int, rgb)) for rgb in frame]
                for frame in data["frames"]
            ]
            cls._validate_frames(frames)

            animation = data.get("animation", {})

            # v0.9.2+
            if "frame_interval_ms" in animation:
                interval = int(animation["frame_interval_ms"])
                if interval not in SUPPORTED_FRAME_INTERVALS_MS:
                    interval = DEFAULT_FRAME_INTERVAL_MS
            # v0.9.0/v0.9.1 compatibility
            elif "device_speed_code" in animation:
                interval = device_speed_code_to_interval_ms(
                    animation.get("device_speed_code", 4)
                )
            else:
                interval = DEFAULT_FRAME_INTERVAL_MS

            return cls(frames=frames, frame_interval_ms=interval)

        # Legacy v3 project.
        if "frames" in data:
            frames = [
                [tuple(map(int, rgb)) for rgb in frame]
                for frame in data["frames"]
            ]
            cls._validate_frames(frames)
            interval = device_speed_code_to_interval_ms(data.get("speed_code", 4))
            return cls(frames=frames, frame_interval_ms=interval)

        # Legacy v1/v2 one-frame JSON.
        if "colors" in data:
            colors = [tuple(map(int, rgb)) for rgb in data["colors"]]
            cls._validate_frames([colors])
            return cls(frames=[colors])

        raise ValueError("Unsupported project format")

    @staticmethod
    def _validate_frames(frames: Sequence[Sequence[RGB]]) -> None:
        if not frames:
            raise ValueError("Project contains no frames")
        for frame in frames:
            if len(frame) != LED_COUNT:
                raise ValueError(
                    f"A frame contains {len(frame)} LEDs instead of {LED_COUNT}"
                )
            for rgb in frame:
                if len(rgb) != 3 or any(not 0 <= int(v) <= 255 for v in rgb):
                    raise ValueError("Invalid RGB value")

    def to_dict(self) -> dict:
        return {
            "format": "cd2-matrix-studio",
            "version": 2,
            "device": "flydigi-charging-dock-2-pro",
            "rows": list(ROWS),
            "animation": {
                "frame_interval_ms": int(self.frame_interval_ms),
                "device_speed_code": int(self.device_speed_code),
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
        with p.open("w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)
        self.path = p
        return p
