# Changelog

## 1.0.1

- Removed the redundant matrix Eyedropper tool from the drawing toolbar
- Color picking remains available through the color selection dialog

## 1.0.0

- First public release
- Direct editing of the 162-LED RGB matrix
- Static images and multi-frame animations
- Confirmed 10 ms / 40 ms animation timing
- RU / EN interface and built-in documentation
- Eyedropper, recent colors and mirror mode
- Frame thumbnails, copy/paste and drag-and-drop reordering
- Portable EXE and installer build pipeline
- Public protocol documentation

## Pre-release history

## 0.9.7

- Added proper Russian frame-count declension in send confirmations
- 1 кадр / 2–4 кадра / 5+ кадров now use natural Russian wording

## 0.9.6

- The send confirmation now hides animation speed when only one frame is being sent
- Single-frame send prompt text is cleaner and no longer mentions interval unnecessarily

## 0.9.5

- Made the confirmation dialogs more compact
- Removed duplicated large dialog titles inside the dialog body
- Reduced empty space in delete/send confirmations
- Tightened button layout in confirmation dialogs

## 0.9.4

- Replaced the delete/send yes-no prompts with custom themed confirmation dialogs
- Added runtime Qt translation loading so built-in dialog labels are translated in Russian
- Switched the color picker to an explicit non-native Qt dialog for consistent styling and translation
- Fixed more Russian UI strings so fewer English labels leak through

## 0.9.3

- Added drag-and-drop frame reordering
- Added frame thumbnails in the animation list
- Added Copy frame / Paste frame with Ctrl+C / Ctrl+V
- Added an Eyedropper tool
- Added persistent Recent colors swatches
- Refined left-side spacing and shortcuts panel
- Refined frame list hover/selection styling
- Kept the confirmed 10 ms / 40 ms real dock timing control

## 0.9.2

- Mapped the two official animation timing presets from USB captures:
  - 10 ms -> device timing byte 0x01
  - 40 ms -> device timing byte 0x04
- Animation timing now affects both editor preview and the dock
- Replaced the bottom slider with a cleaner 10 ms / 40 ms segmented control
- Removed the technical preview-speed note from the main UI
- Reworked the bottom panel into a dedicated animation bar
- Shortened Russian shortcut labels so the quick-actions block fits correctly
- Reworked shortcut rows into compact key badges + action text

## 0.9.1

- Replaced the Language menu with an EN / RU switch in the header
- User guide now opens inside the application
- Reworked shortcut hints into separate visual key/action rows
- Replaced the plain symmetry checkbox with a toggle switch
- Renamed Preview to Animation preview / Просмотр анимации

## 0.9.0

- Rebuilt UI using PySide6 / Qt
- Added English / Russian language switching
- Added automatic dock status indicator
- Added static and animation frame editor
- Added project format `.cd2proj`
- Added legacy JSON import
- Added Windows portable build workflow
- Added Inno Setup installer workflow
- Removed technical protocol controls from the main UI
- Removed bundled wolf presets and experimental content
