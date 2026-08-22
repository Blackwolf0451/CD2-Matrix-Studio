# Flydigi Charging Dock 2 Pro — LED protocol notes

These notes document the protocol currently implemented by CD2 Matrix Studio.

The information was derived from USB captures of Flydigi Space Station communicating with a Charging Dock 2 Pro.

## USB identity

- Vendor ID: `0x37D7`
- Product ID: `0x6001`
- Product string observed: `Flydigi CD2`
- Vendor-defined HID interface
- 64-byte HID reports

## Matrix geometry

162 RGB LEDs.

Rows from top to bottom:

```text
14, 15, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3
```

LED ordering is row-major:

- top to bottom;
- left to right inside each row.

Each LED uses three bytes:

```text
R G B
```

## Static / animation payload

Payload starts with six bytes:

```text
[frame_count] [timing] 64 03 00 00
```

Then each frame contributes:

```text
162 × RGB = 486 bytes
```

A one-frame static upload observed:

```text
01 01 64 03 00 00
```

A captured 21-frame official animation used:

```text
15 04 64 03 00 00
```

Two official timing presets have now been captured and mapped:

```text
10 ms -> timing byte 0x01
40 ms -> timing byte 0x04
```

The official UI currently exposes only these two timing presets, so CD2 Matrix Studio exposes the same two values.

## USB transfer packetization

Data is split into 50-byte chunks and wrapped in 64-byte HID reports.

Transfer start command:

```text
5A A5 61 07 0A 00 00 [chunk_count_hi] [chunk_count_lo] [checksum]
```

Data command:

```text
5A A5 62 [data_len+7]
[chunk_count_hi] [chunk_count_lo]
[sequence_hi] [sequence_lo]
[data_len]
[data...]
[checksum]
```

Checksum:

```text
sum(bytes from command byte onward) mod 256
```

The dock acknowledges the start command and each data chunk.

## Known limitations

- Vertical image shifting is not geometrically lossless because adjacent rows have different LED counts.
- Only LED frame upload behavior is documented here. Firmware update behavior is intentionally out of scope.

## Contributions

If you capture additional timing modes or another dock revision, please open an issue and attach:

- application version;
- dock revision if known;
- a minimal USB capture;
- a description of what was applied in the official software.
