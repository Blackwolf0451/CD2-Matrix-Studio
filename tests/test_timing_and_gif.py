from __future__ import annotations

import json

import pytest
from PIL import Image

from cd2_matrix_studio.gif_import import Crop, POSITIONS, gif_timeline, load_gif, sample_leds
from cd2_matrix_studio.project import Project, blank_frame
from cd2_matrix_studio.protocol import LED_COUNT, MAX_FRAMES, build_animation_payload
from cd2_matrix_studio.timing import expand_frames, ticks_for_duration


def test_frame_duration_rounds_to_base_tick():
    assert ticks_for_duration(800, 40) == 20
    assert ticks_for_duration(120, 40) == 3
    assert ticks_for_duration(50, 40) == 1
    assert ticks_for_duration(60, 40) == 2
    assert ticks_for_duration(70, 10) == 7


def test_hold_expansion_and_static_frame():
    a = [(255, 0, 0)] * LED_COUNT
    b = [(0, 0, 255)] * LED_COUNT
    p = Project(frames=[a, b], frame_durations_ms=[80, 120])
    expanded = p.to_device_frames()
    assert len(expanded) == 5
    assert expanded[:2] == [a] * 2
    assert expanded[2:] == [b] * 3
    assert build_animation_payload(expanded, p.device_speed_code)[:2] == bytes([5, 4])
    static = Project(frames=[a], frame_durations_ms=[8000])
    assert len(static.to_device_frames()) == 1
    assert build_animation_payload(static.to_device_frames(), 4)[:2] == bytes([1, 1])


def test_device_budget_is_enforced():
    f = blank_frame()
    p = Project(frames=[f, f], frame_durations_ms=[8000, 8000])
    with pytest.raises(ValueError, match="maximum 200"):
        p.to_device_frames()
    assert p.device_frame_count() == 400


def test_project_v2_is_backward_compatible(tmp_path):
    frame = blank_frame()
    old = {
        "format": "cd2-matrix-studio", "version": 2,
        "animation": {"frame_interval_ms": 10}, "frames": [frame, frame],
    }
    project = Project.from_dict(old)
    assert project.frame_durations_ms == [10, 10]
    project.frame_durations_ms[1] = 800
    target = tmp_path / "roundtrip.cd2proj"
    project.save(target)
    loaded = Project.load(target)
    assert loaded.to_dict()["version"] == 3
    assert loaded.frame_durations_ms == [10, 800]
    assert loaded.frame_interval_ms == 10
    assert len(Project.from_dict({"colors": frame}).frames) == 1
    assert len(Project.from_dict({"frames": [frame], "speed_code": 1}).frames) == 1


def test_162_led_positions_exact():
    assert len(POSITIONS) == LED_COUNT == 162
    assert POSITIONS[0][1] == 0.5
    assert POSITIONS[-1][1] == 15.5
    assert len(set(POSITIONS)) == LED_COUNT


def test_image_sampling_cropping():
    left_red = Image.new("RGB", (40, 20), (255, 0, 0))
    normal = sample_leds(left_red, Crop())
    assert len(normal) == LED_COUNT
    assert all(v == (255, 0, 0) for v in normal)
    assert any(v == (255, 0, 0) for v in sample_leds(left_red, Crop("fit")))


def test_gif_file_decode_and_timeline(tmp_path):
    a = Image.new("RGB", (32, 32), "red")
    b = Image.new("RGB", (32, 32), "blue")
    file = tmp_path / "two.gif"
    a.save(file, save_all=True, append_images=[b], duration=[80, 120], loop=0)
    images, delays = load_gif(file)
    assert delays == [80, 120]
    frames, durations = gif_timeline(images, delays, Crop(), 40, 200)
    assert durations == [80, 120]
    assert len(frames) == 2
    assert all(color == (255, 0, 0) for color in frames[0])
    assert all(color == (0, 0, 255) for color in frames[1])


def test_identical_gif_frames_are_coalesced():
    frame = Image.new("RGBA", (10, 10), (30, 50, 70, 255))
    frames, holds = gif_timeline([frame, frame], [120, 80], Crop(), 40, 200)
    assert len(frames) == 1
    assert holds == [200]


def test_gif_is_trimmed_to_frame_budget():
    frame = Image.new("RGB", (20, 20), "white")
    frames, holds = gif_timeline([frame], [10000], Crop(), 40, 10000)
    assert len(frames) == 1
    assert holds == [8000]
    assert len(expand_frames([blank_frame(), blank_frame()], [4000, 4000], 40)) == 200
