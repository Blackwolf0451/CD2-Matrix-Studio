# Публикация CD2 Matrix Studio на GitHub

Ниже — самый простой путь от готовой папки проекта до первого релиза.

## 1. Создать репозиторий

На GitHub:

1. Нажать **New repository**.
2. Название: `CD2-Matrix-Studio`.
3. Description, например:

   `Unofficial LED matrix editor for the Flydigi Charging Dock 2 Pro`

4. Выбрать **Public**.
5. Не добавлять README, `.gitignore` и License через GitHub — они уже есть в проекте.
6. Нажать **Create repository**.

## 2. Загрузить проект через Git

Открыть PowerShell в папке проекта:

```powershell
git init
git add .
git commit -m "CD2 Matrix Studio v1.0.0"
git branch -M main
git remote add origin https://github.com/USERNAME/CD2-Matrix-Studio.git
git push -u origin main
```

Вместо `USERNAME` указать свой GitHub username.

## 3. Проверить Actions

После первого push открыть вкладку **Actions**.

Должны появиться проверки и Windows build.

Если Windows build завершился успешно, внутри run будут доступны два artifacts:

- portable EXE;
- installer.

Их стоит скачать и проверить локально до публичного релиза.

## 4. Что проверить перед v1.0.0

Минимальный чек-лист:

- приложение запускается без установленного Python;
- док определяется;
- статичный рисунок отправляется;
- анимация отправляется;
- 10 ms работает;
- 40 ms работает;
- RU / EN переключаются;
- старый JSON открывается;
- `.cd2proj` сохраняется и снова открывается;
- инструкция открывается внутри программы;
- uninstall установщика работает.

## 5. Сделать релиз

После проверки:

```powershell
git tag v1.0.0
git push origin v1.0.0
```

Workflow `release.yml` автоматически:

1. запускает тесты;
2. собирает portable EXE;
3. собирает installer;
4. создаёт GitHub Release;
5. прикладывает оба `.exe`.

## 6. Скриншоты

Перед публикацией желательно добавить в README 2–3 актуальных изображения:

- главное окно с рисунком;
- несколько кадров анимации;
- окно встроенной инструкции или отправки.

Лучше использовать скриншоты именно финального `v1.0.0`, а не старых beta-сборок.

## 7. Первый текст релиза

Можно использовать готовый файл:

```text
RELEASE_NOTES_v1.0.0.md
```

## 8. Если не хочется пользоваться Git через консоль

Можно установить GitHub Desktop:

1. создать новый repository из существующей папки;
2. Publish repository;
3. после публикации тег `v1.0.0` удобнее создать через Git/PowerShell или интерфейс GitHub Release.

## Важно

Flydigi Space Station должен быть полностью закрыт во время отправки LED-данных из CD2 Matrix Studio. Это стоит оставить в README и инструкции, потому что обе программы обращаются к одному HID-устройству.
