"""GIF decode, crop and timing conversion for the dock's non-rectangular LEDs.

This module intentionally has no Qt dependency so the geometry and sampling
can be unit-tested without a Windows desktop.
"""
from __future__ import annotations

from bisect import bisect_right
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from PIL import Image

from .protocol import LED_COUNT, MAX_FRAMES, ROWS

RGB = tuple[int, int, int]
CANVAS = 16
SCALE = 8
MAX_DECODE_MS = 8000
MAX_SOURCE_FRAMES = 500
MAX_PREVIEW_SIZE = 256
MAX_FILE_BYTES = 50 * 1024 * 1024
MAX_SOURCE_PIXELS = 4_000_000


@dataclass(frozen=True)
class Crop:
    mode: str = "fill"  # "fill" crops edges; "fit" letterboxes.
    zoom_percent: int = 100
    pan_x: int = 0  # -100..100, translated by half a logical canvas.
    pan_y: int = 0


def load_gif(path: str | Path) -> tuple[list[Image.Image], list[int]]:
    path = Path(path)
    if path.stat().st_size > MAX_FILE_BYTES:
        raise ValueError("GIF exceeds the 50 MB import limit")
    frames: list[Image.Image] = []
    delays_ms: list[int] = []
    elapsed = 0
    with Image.open(path) as source:
        if source.format != "GIF":
            raise ValueError("Only GIF files can be imported")
        if source.width * source.height > MAX_SOURCE_PIXELS:
            raise ValueError("GIF resolution is too large")
        count = min(getattr(source, "n_frames", 1), MAX_SOURCE_FRAMES)
        for i in range(count):
            source.seek(i)
            raw_delay = source.info.get("duration", 100)
            # 0 ms is an explicit ultra-fast frame, not a missing duration.
            delay = max(10, int(raw_delay if raw_delay is not None else 100))
            rgba = source.convert("RGBA")
            # A 16-column LED display never needs full-resolution GIF frames.
            # Keep imports bounded in RAM even for large animated source files.
            rgba.thumbnail((MAX_PREVIEW_SIZE, MAX_PREVIEW_SIZE), Image.Resampling.LANCZOS)
            frames.append(rgba.copy())
            remaining = MAX_DECODE_MS - elapsed
            delays_ms.append(min(delay, remaining))
            elapsed += min(delay, remaining)
            if elapsed >= MAX_DECODE_MS:
                break
    if not frames:
        raise ValueError("The GIF contains no frames")
    return frames, delays_ms


def led_positions() -> list[tuple[float, float]]:
    """Center coordinates on the 16 x 16 virtual canvas, in HID row order."""
    result: list[tuple[float, float]] = []
    for row, count in enumerate(ROWS):
        x0 = (CANVAS - count) / 2
        for col in range(count):
            result.append((x0 + col + 0.5, row + 0.5))
    assert len(result) == LED_COUNT
    return result


POSITIONS = led_positions()


def sample_leds(image: Image.Image, crop: Crop) -> list[RGB]:
    if crop.mode not in ("fill", "fit"):
        raise ValueError("Invalid crop mode")
    if not 25 <= int(crop.zoom_percent) <= 400:
        raise ValueError("Zoom must be 25–400%")
    if not -100 <= int(crop.pan_x) <= 100 or not -100 <= int(crop.pan_y) <= 100:
        raise ValueError("Invalid pan offset")

    rgba = image.convert("RGBA")
    width, height = rgba.size
    scale = (max if crop.mode == "fill" else min)(CANVAS / width, CANVAS / height)
    scale *= crop.zoom_percent / 100
    target_w = max(1, round(width * scale * SCALE))
    target_h = max(1, round(height * scale * SCALE))
    resized = rgba.resize((target_w, target_h), Image.Resampling.LANCZOS)
    output_w = output_h = CANVAS * SCALE
    # A virtual matte is used for stable transparent GIF backgrounds.
    canvas = Image.new("RGB", (output_w, output_h), (0, 0, 0))
    x = round((output_w - target_w) / 2 + crop.pan_x / 100 * output_w / 2)
    y = round((output_h - target_h) / 2 + crop.pan_y / 100 * output_h / 2)
    # Paste with RGBA alpha; colors outside are off.
    canvas.paste(resized, (x, y), resized)
    px = canvas.load()
    return [px[min(output_w - 1, max(0, round(x * SCALE))) ,
               min(output_h - 1, max(0, round(y * SCALE)))]
            for x, y in POSITIONS]


def gif_timeline(frames: Sequence[Image.Image], delays_ms: Sequence[int], crop: Crop,
                 interval_ms: int, clip_ms: int) -> tuple[list[list[RGB]], list[int]]:
    """Sample GIF in fixed 10/40-ms ticks, then coalesce identical LED frames.

    The resulting project expands to at most MAX_FRAMES real device frames.
    Trims to selected clip length; a 40-ms base allows up to 8 seconds.
    """
    if not frames or len(frames) != len(delays_ms):
        raise ValueError("Invalid GIF timeline")
    if interval_ms not in (10, 40):
        raise ValueError("Unsupported device timing")
    total_ms = sum(int(ms) for ms in delays_ms)
    if total_ms <= 0:
        raise ValueError("Invalid GIF frame durations")
    clip_ms = max(interval_ms, min(int(clip_ms), total_ms, interval_ms * MAX_FRAMES))
    tick_count = min(MAX_FRAMES, max(1, (clip_ms + interval_ms // 2) // interval_ms))
    starts = [0]
    for ms in delays_ms:
        starts.append(starts[-1] + int(ms))
    rendered: dict[int, list[RGB]] = {}
    output: list[list[RGB]] = []
    durations: list[int] = []
    for tick in range(tick_count):
        time_ms = min(total_ms - 1, tick * interval_ms + interval_ms // 2)
        index = min(len(frames) - 1, bisect_right(starts, time_ms) - 1)
        if index not in rendered:
            rendered[index] = sample_leds(frames[index], crop)
        led_frame = rendered[index]
        if output and output[-1] == led_frame:
            durations[-1] += interval_ms
        else:
            output.append(led_frame.copy())
            durations.append(interval_ms)
    return output, durations
