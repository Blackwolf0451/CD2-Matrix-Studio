# CD2 Matrix Studio

**Unofficial LED matrix editor for the Flydigi Charging Dock 2 Pro.**

CD2 Matrix Studio is a Windows desktop application for drawing directly on the dock's 162-LED RGB matrix, creating animations frame by frame, previewing them, and sending them directly to the dock.

> **Unofficial community project.** CD2 Matrix Studio is not affiliated with, sponsored by, or endorsed by Flydigi.

## Features

- Direct editing of all **162 RGB LEDs**
- Static images and multi-frame animations
- **10 ms / 40 ms** animation timing supported by the dock
- Draw, erase, fill and clear
- Horizontal mirror mode
- Undo / redo
- Recent colors remembered between launches
- Frame thumbnails
- Add, duplicate, delete, copy/paste and drag-and-drop frame reordering
- Animation preview
- English and Russian interface
- Built-in user guide
- Automatic dock detection
- Save/load projects as `.cd2proj`
- Import legacy JSON projects from earlier editor versions
- Portable Windows EXE and installer builds
- No telemetry

## Supported device

Currently tested with:

- **Flydigi Charging Dock 2 Pro**
- USB VID: `37D7`
- USB PID: `6001`

Other Flydigi docks have not been tested and should not be assumed compatible.

## Quick start

1. Connect the Charging Dock 2 Pro to the PC by USB.
2. Fully close **Flydigi Space Station**, including its tray icon.
3. Start **CD2 Matrix Studio**.
4. Draw directly on the LED matrix or create animation frames.
5. For animations, choose **10 ms** or **40 ms**.
6. Click **Send to Dock**.

The release EXE does **not** require Python to be installed.

## Download

Use the **Releases** section of this repository for the latest Windows build.

Release assets:

- `CD2-Matrix-Studio.exe` — portable version
- `CD2-Matrix-Studio-Setup.exe` — installer

## Project files

The recommended project extension is:

```text
.cd2proj
```

The format is JSON-based and intentionally kept readable. Older JSON drawings created by the prototype editor can also be opened.

## Building from source

Requirements:

- Windows 10/11
- Python 3.10+
- PySide6
- hidapi

Quick development launch:

```bat
run_dev.bat
```

Build the portable EXE:

```bat
build_windows.bat
```

The result is written to:

```text
dist\CD2-Matrix-Studio.exe
```

The installer source is in:

```text
installer\cd2_matrix_studio.iss
```

GitHub Actions workflows are included for CI, Windows builds and tagged releases.

## Documentation

- [English user guide](docs/USER_GUIDE_EN.md)
- [Русская инструкция](docs/USER_GUIDE_RU.md)
- [Protocol notes](docs/PROTOCOL.md)

## Troubleshooting

### Dock is not detected

Reconnect the dock, try another USB port and restart the application.

### Sending fails

Fully close Flydigi Space Station. Only one application should access the dock's HID interface at a time.

### Animation speed

The dock exposes two confirmed timing presets through the official software:

- `10 ms`
- `40 ms`

CD2 Matrix Studio sends the corresponding timing values directly to the dock.

## Scope and safety

CD2 Matrix Studio implements LED frame transfer only. It is **not** a firmware flashing tool and does not intentionally write or replace dock firmware.

## Contributing

Bug reports, compatibility reports, protocol captures and pull requests are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

CD2 Matrix Studio source code is released under the [MIT License](LICENSE).

Third-party dependencies retain their own licenses. See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
