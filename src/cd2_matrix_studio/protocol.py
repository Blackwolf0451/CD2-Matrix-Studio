from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Iterable, Sequence

VID = 0x37D7
PID = 0x6001

ROWS = (14, 15, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3)
LED_COUNT = sum(ROWS)
MAX_FRAMES = 200

RGB = tuple[int, int, int]
Frame = Sequence[RGB]

# Observed in an official animation capture. Kept internal until the
# exact user-facing speed mapping is characterized more fully.
DEFAULT_DEVICE_SPEED_CODE = 4


class DeviceError(RuntimeError):
    pass


def checksum(packet_without_checksum: bytes | bytearray) -> int:
    return sum(packet_without_checksum[2:]) & 0xFF


def _pad64(payload: bytes) -> bytes:
    if len(payload) > 64:
        raise ValueError("HID packet exceeds 64 bytes")
    return payload + bytes(64 - len(payload))


def build_begin_packet(total_chunks: int) -> bytes:
    if not 1 <= total_chunks <= 0xFFFF:
        raise ValueError("Invalid chunk count")

    packet = bytearray(
        [
            0x5A, 0xA5, 0x61, 0x07, 0x0A,
            0x00, 0x00,
            (total_chunks >> 8) & 0xFF,
            total_chunks & 0xFF,
        ]
    )
    packet.append(checksum(packet))
    return _pad64(bytes(packet))


def build_chunk_packet(seq: int, data: bytes, total_chunks: int) -> bytes:
    if len(data) > 50:
        raise ValueError("Chunk payload exceeds 50 bytes")
    if not 0 <= seq <= 0xFFFF:
        raise ValueError("Invalid sequence index")

    packet = bytearray(
        [
            0x5A, 0xA5, 0x62,
            len(data) + 7,
            (total_chunks >> 8) & 0xFF,
            total_chunks & 0xFF,
            (seq >> 8) & 0xFF,
            seq & 0xFF,
            len(data),
        ]
    )
    packet.extend(data)
    packet.append(checksum(packet))
    return _pad64(bytes(packet))


def build_animation_payload(
    frames: Sequence[Frame],
    speed_code: int = DEFAULT_DEVICE_SPEED_CODE,
) -> bytes:
    if not 1 <= len(frames) <= MAX_FRAMES:
        raise ValueError(f"Animation must contain 1..{MAX_FRAMES} frames")

    for frame in frames:
        if len(frame) != LED_COUNT:
            raise ValueError(f"Each frame must contain {LED_COUNT} LEDs")

    second_byte = 1 if len(frames) == 1 else int(speed_code)
    if not 1 <= second_byte <= 255:
        raise ValueError("Invalid speed code")

    raw = bytearray([len(frames), second_byte, 0x64, 0x03, 0x00, 0x00])
    for frame in frames:
        for r, g, b in frame:
            raw.extend((r & 0xFF, g & 0xFF, b & 0xFF))
    return bytes(raw)


def build_packets(
    frames: Sequence[Frame],
    speed_code: int = DEFAULT_DEVICE_SPEED_CODE,
) -> list[bytes]:
    payload = build_animation_payload(frames, speed_code)
    chunks = [payload[i : i + 50] for i in range(0, len(payload), 50)]
    total = len(chunks)
    return [build_begin_packet(total)] + [
        build_chunk_packet(i, chunk, total) for i, chunk in enumerate(chunks)
    ]


def _clean_report(data: Iterable[int]) -> bytes:
    report = bytes(data)
    if len(report) >= 3 and report[0] == 0 and report[1:3] == b"\x5A\xA5":
        return report[1:]
    return report


def _wait_for_ack(
    dev,
    command: int,
    total_chunks: int | None = None,
    seq: int | None = None,
    timeout_ms: int = 1500,
) -> bytes:
    deadline = time.monotonic() + timeout_ms / 1000.0

    while time.monotonic() < deadline:
        remaining = max(1, int((deadline - time.monotonic()) * 1000))
        data = dev.read(64, remaining)
        if not data:
            continue

        report = _clean_report(data)
        if len(report) < 6 or report[:2] != b"\x5A\xA5":
            continue

        # Normal device heartbeat/status packet.
        if report[2] == 0xEF:
            continue

        if command == 0x61:
            if report[2] == 0x61 and report[3] == 0x02 and report[4] == 0x00:
                return report

        elif command == 0x62 and total_chunks is not None and seq is not None:
            if len(report) >= 10 and report[2] == 0x62 and report[3] == 0x07:
                got_total = (report[4] << 8) | report[5]
                got_seq = (report[6] << 8) | report[7]
                if got_total == total_chunks and got_seq == seq and report[8] == 0:
                    return report

    label = f"0x{command:02X}"
    if seq is not None:
        label += f", block {seq}"
    raise DeviceError(f"Device did not acknowledge {label}")


def _load_hid():
    try:
        import hid  # type: ignore
    except ImportError as exc:
        raise DeviceError(
            "The HID backend is not installed. Reinstall the application."
        ) from exc
    return hid


def enumerate_device() -> list[dict]:
    try:
        hid = _load_hid()
        return list(hid.enumerate(VID, PID))
    except Exception:
        return []


def is_device_connected() -> bool:
    return bool(enumerate_device())


def _open_device():
    hid = _load_hid()
    found = hid.enumerate(VID, PID)
    if not found:
        raise DeviceError("Charging Dock 2 Pro was not found.")

    errors: list[str] = []
    for info in found:
        try:
            dev = hid.device()
            dev.open_path(info["path"])
            dev.set_nonblocking(False)
            return dev, info
        except Exception as exc:
            errors.append(str(exc))

    detail = " | ".join(errors) if errors else "Unknown error"
    raise DeviceError(f"Could not open the dock: {detail}")


def _write_report(dev, packet64: bytes) -> None:
    # Report ID 0 for the vendor-defined HID interface.
    written = dev.write(bytes([0]) + packet64)
    if written <= 0:
        raise DeviceError("HID write failed")


def send_frames(
    frames: Sequence[Frame],
    speed_code: int = DEFAULT_DEVICE_SPEED_CODE,
) -> dict:
    packets = build_packets(frames, speed_code)
    total_chunks = len(packets) - 1

    dev, info = _open_device()
    try:
        # Drain pending status/heartbeat packets.
        dev.set_nonblocking(True)
        for _ in range(48):
            if not dev.read(64):
                break
        dev.set_nonblocking(False)

        _write_report(dev, packets[0])
        _wait_for_ack(dev, 0x61)

        for seq, packet in enumerate(packets[1:]):
            _write_report(dev, packet)
            _wait_for_ack(dev, 0x62, total_chunks=total_chunks, seq=seq)
    finally:
        dev.close()

    return info
