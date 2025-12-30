# Папка для шрифтов JetBrains Mono

## Куда поместить файлы шрифта

Поместите файлы шрифта JetBrains Mono в эту папку (`static/fonts/`).

### Необходимые файлы:

Для полной поддержки шрифта нужны следующие файлы:

- `JetBrainsMono-Regular.woff2` (или .woff, .ttf)
- `JetBrainsMono-Bold.woff2` (или .woff, .ttf)
- `JetBrainsMono-Italic.woff2` (или .woff, .ttf)
- `JetBrainsMono-BoldItalic.woff2` (или .woff, .ttf)

### Где скачать JetBrains Mono:

1. **Официальный сайт**: https://www.jetbrains.com/lp/mono/
2. **GitHub**: https://github.com/JetBrains/JetBrainsMono
3. **Google Fonts**: https://fonts.google.com/specimen/JetBrains+Mono

### Формат файлов:

Рекомендуется использовать `.woff2` (самый современный и компактный формат), но также поддерживаются `.woff` и `.ttf`.

### Структура папки после добавления файлов:

```
static/
  └── fonts/
      ├── JetBrainsMono-Regular.woff2
      ├── JetBrainsMono-Bold.woff2
      ├── JetBrainsMono-Italic.woff2
      └── JetBrainsMono-BoldItalic.woff2
```

### Если файлы находятся в корне проекта:

Если вы добавили файлы в корень проекта (`C:\Hugo\12-microstartups\`), переместите их в эту папку (`static/fonts/`).

### После добавления файлов:

1. Сохраните файлы в `static/fonts/`
2. Опубликуйте изменения:
   ```powershell
   git add static/fonts/
   git commit -m "Добавлены файлы шрифта JetBrains Mono"
   git push
   ```
3. Шрифт автоматически применится ко всему сайту!


