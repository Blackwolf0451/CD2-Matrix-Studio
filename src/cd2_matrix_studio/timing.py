"""Per-frame timing on top of the dock's two confirmed uniform timing modes."""
from __future__ import annotations

from collections.abc import Sequence

from .protocol import MAX_FRAMES

MIN_DURATION_MS = 10
MAX_DURATION_MS = 60000


def ticks_for_duration(duration_ms: int, base_interval_ms: int) -> int:
    """Approximate each desired duration using the nearest whole device tick."""
    duration_ms = int(duration_ms)
    base_interval_ms = int(base_interval_ms)
    if duration_ms < MIN_DURATION_MS or duration_ms > MAX_DURATION_MS:
        raise ValueError(f"Frame duration must be {MIN_DURATION_MS}–{MAX_DURATION_MS} ms")
    if base_interval_ms not in (10, 40):
        raise ValueError("The device supports 10 ms and 40 ms timing")
    return max(1, (duration_ms + base_interval_ms // 2) // base_interval_ms)


def expanded_frame_count(durations_ms: Sequence[int], base_interval_ms: int, *, single_static: bool = False) -> int:
    if not durations_ms:
        raise ValueError("An animation needs at least one frame")
    if single_static and len(durations_ms) == 1:
        return 1
    return sum(ticks_for_duration(ms, base_interval_ms) for ms in durations_ms)


def expand_frames(frames: Sequence, durations_ms: Sequence[int], base_interval_ms: int) -> list:
    """Expand frame holds into a uniform stream without altering the protocol."""
    if not frames or len(frames) != len(durations_ms):
        raise ValueError("Frame/duration count mismatch")
    if len(frames) == 1:
        return [list(frames[0])]
    count = expanded_frame_count(durations_ms, base_interval_ms)
    if count > MAX_FRAMES:
        raise ValueError(
            f"This animation requires {count} device frames (maximum {MAX_FRAMES}). "
            "Try a shorter duration, fewer frames, or the 40 ms timing preset."
        )
    output = []
    for frame, ms in zip(frames, durations_ms):
        output.extend([list(frame)] * ticks_for_duration(ms, base_interval_ms))
    return output
