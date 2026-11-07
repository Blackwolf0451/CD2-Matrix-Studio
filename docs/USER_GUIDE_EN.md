# CD2 Matrix Studio — User Guide

## 1. Connect the dock

Connect the Flydigi Charging Dock 2 Pro directly to the PC by USB.

The top-right status should change to **Dock connected**.

If the dock is not detected:

- reconnect the USB cable;
- try another USB port;
- close and reopen CD2 Matrix Studio.

## 2. Close Flydigi Space Station

Before sending a project to the dock, fully close Flydigi Space Station, including its tray icon if present. Both applications may otherwise try to access the same HID device.

## 3. Draw

Use the tool panel on the left:

- **Draw** — paint LEDs with the selected color;
- **Erase** — turn LEDs off;
- **Fill** — fill the whole frame with the selected color;
- **Clear frame** — turn every LED in the current frame off;
- **Mirror** — paint the matching LED on the opposite side of the same row.

Recent colors appear below the color picker and are remembered between launches.

Left-drag paints. Right-drag always erases.

## 4. Choose a color

Click **Color** and select any RGB color in the system color picker.

## 5. Create an animation

The right panel contains the frame list.

- **Add** — create a blank frame after the current frame;
- **Duplicate** — copy the current frame;
- **Delete** — remove the selected frame;
- **Move up / Move down** — change the frame order;
- drag frames with the mouse to reorder them;
- **Ctrl+C / Ctrl+V** copies and pastes a frame.

Each frame also shows a small LED-matrix thumbnail.

Animations can contain up to 200 frames.

## 6. Preview and animation speed

Click **Preview animation** to play the frames inside the editor.

Use **Animation speed** to select:

- **10 ms** — faster;
- **40 ms** — slower.

The selected value is now used both by the editor preview and by the dock itself. These are the two timing modes observed in Flydigi Space Station.

## 7. Send to the dock

Click **Send to Dock**.

If sending fails, first make sure Flydigi Space Station is fully closed and try again.

## 8. Save a project

Use **File → Save**.

The recommended extension is:

`*.cd2proj`

The format is JSON-based and intended to stay easy to inspect and convert.

## 9. Language

Use **Language → English / Русский**.

The selected language is remembered automatically.

## 10. Safety

The application sends the same style of HID data used for LED frame uploads. It does not intentionally flash or replace dock firmware.


## GIF import and frame duration (v1.1)

Set **Frame duration** for the selected frame. The preview respects that duration. The dock supports only 10/40 ms base intervals, so the application repeats frames automatically during transfer (max. 200 device frames).

Select **Import GIF…**, adjust Fill/Fit, zoom, X/Y offset and clip length. The crop preview uses the dock's real 162 LED layout. The GIF replaces the current project after confirmation.
