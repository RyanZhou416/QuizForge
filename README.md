# QuizForge

Cross-platform quiz application with SQLite question banks.

- **Desktop**: Tauri (Rust) backend + Vite frontend
- **Web**: Same frontend with sql.js (SQLite WASM) — drag & drop `.db` files

## Features

- Single choice / Multiple choice / True-False question types
- Dedicated True/False UI with large toggle buttons
- Per-option and per-question explanations shown after submission
- Chinese / English bilingual support (switchable)
- Filter by topic, difficulty, question type, keyword search
- Shuffle questions
- Progress tracking with localStorage caching (web) / SQLite (desktop)
- Answer state caching — resume from where you left off after page refresh
- Export / Import progress as JSON backup
- Question image support with lightbox zoom viewer
- Exam mode with timer and auto-submit
- Question navigation grid with color-coded status
- Quiz summary with per-type breakdown and wrong answer review
- Close current bank / Remove banks from list
- Dark / Light theme
- Folder watching for `.db` quiz bank files (desktop)
- Drag & drop file loading (web)

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | HTML + CSS + vanilla JS, Vite |
| Desktop backend | Rust, Tauri v2, rusqlite, notify |
| Web fallback | sql.js (SQLite compiled to WASM) |
| Database | SQLite `.db` files (one per quiz bank) |
| Deployment | Docker + Caddy, GitHub Actions CI/CD |

## Getting Started

### Prerequisites

- Node.js >= 18
- Rust toolchain (for desktop builds only)
- Tauri CLI v2: `cargo install tauri-cli --version "^2"`

### Development

```bash
npm install
npm run tauri dev
```

### Web-only dev (no Rust needed)

```bash
npm run dev
```

Open http://localhost:1420 and drag in a `.db` quiz bank file.

### Build

```bash
# Desktop
npm run tauri build

# Web only
npm run build
```

## Creating Quiz Banks

### Method 1: AI Generation

Use the magic prompt in [`docs/quiz-generation-prompt.md`](docs/quiz-generation-prompt.md) to have an AI generate quiz content as JSON, then convert to `.db`:

```bash
# Generate JSON with AI (follow the prompt instructions)
# Convert to .db
python json_to_db.py quiz.json -o quiz.db

# With images (extract from PDF first)
python extract_pdf_images.py input.pdf -o images/
python json_to_db.py quiz.json -o quiz.db -i images/
```

### Method 2: Manual

Quiz banks are standard SQLite `.db` files. Use the included `create_sample_db.py` as a reference:

```bash
python create_sample_db.py
```

See the [schema document](docs/plan.md) for the full SQLite schema.

## Deployment

See the [build and deploy guide](docs/build-and-deploy.md) for Docker, CI/CD, and platform-specific build instructions.

### Quick Docker Deploy

```bash
npm run build
docker compose up -d
```

Or with volume mount for easy updates:

```yaml
services:
  quizforge:
    image: caddy:2-alpine
    ports:
      - "8080:80"
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile:ro
      - ./dist:/srv
```

## License

MIT
