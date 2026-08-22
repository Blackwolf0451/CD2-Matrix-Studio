from cd2_matrix_studio.project import (
    Project,
    device_speed_code_to_interval_ms,
    interval_ms_to_device_speed_code,
)
from cd2_matrix_studio.protocol import LED_COUNT


def test_load_legacy_v2():
    data = {
        "version": 2,
        "rows": [],
        "colors": [[0, 0, 0] for _ in range(LED_COUNT)],
    }
    project = Project.from_dict(data)
    assert len(project.frames) == 1
    assert len(project.frames[0]) == LED_COUNT


def test_round_trip():
    project = Project(frame_interval_ms=10)
    loaded = Project.from_dict(project.to_dict())
    assert loaded.frames == project.frames
    assert loaded.frame_interval_ms == 10


def test_timing_mapping():
    assert interval_ms_to_device_speed_code(10) == 1
    assert interval_ms_to_device_speed_code(40) == 4
    assert device_speed_code_to_interval_ms(1) == 10
    assert device_speed_code_to_interval_ms(4) == 40
