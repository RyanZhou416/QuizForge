# QuizForge

Cross-platform quiz application with SQLite question banks.

- **Desktop**: Tauri (Rust) backend + Vite frontend
- **Web**: Same frontend with sql.js (SQLite WASM) — drag & drop `.db` files

## Features

- Single choice / Multiple choice / True-False question types
- Per-option and per-question explanations shown after submission
- Chinese / English bilingual support (switchable)
- Filter by topic, difficulty, question type
- Shuffle questions
- Progress tracking
- Dark / Light theme
- Folder watching for `.db` quiz bank files (desktop)

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | HTML + CSS + vanilla JS, Vite |
| Desktop backend | Rust, Tauri v2, rusqlite, notify |
| Web fallback | sql.js (SQLite compiled to WASM) |
| Database | SQLite `.db` files (one per quiz bank) |

## Getting Started

### Prerequisites

- Node.js >= 18
- Rust toolchain
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
npm run tauri build
```

## Creating Quiz Banks

Quiz banks are standard SQLite `.db` files. Use the included `create_sample_db.py` as a reference:

```bash
python create_sample_db.py
```

See the [plan document](docs/plan.md) for the full SQLite schema.

## License

MIT
