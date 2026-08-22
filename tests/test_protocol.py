from cd2_matrix_studio.protocol import (
    LED_COUNT,
    build_packets,
)


def test_static_packet_shape():
    frames = [[(0, 0, 0)] * LED_COUNT]
    packets = build_packets(frames)
    assert len(packets) == 11
    assert all(len(packet) == 64 for packet in packets)
    assert packets[0][:10] == bytes.fromhex("5a a5 61 07 0a 00 00 00 0a 7c")
    assert packets[1][:15] == bytes.fromhex(
        "5a a5 62 39 00 0a 00 00 32 01 01 64 03 00 00"
    )


def test_animation_21_frames_matches_observed_chunk_count():
    frames = [[(3, 3, 3)] * LED_COUNT for _ in range(21)]
    packets = build_packets(frames, speed_code=4)
    assert len(packets) == 206
    assert packets[0][:10] == bytes.fromhex("5a a5 61 07 0a 00 00 00 cd 3f")
