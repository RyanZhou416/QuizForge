#!/usr/bin/env python3
"""
Convert a QuizForge JSON quiz bank to SQLite .db file.
Automatically embeds referenced images as base64 data URIs.

Usage:
    python json_to_db.py input.json                        -> generates input.db
    python json_to_db.py input.json output.db              -> generates output.db
    python json_to_db.py input.json -i images/             -> resolve images from images/
    python json_to_db.py *.json                            -> batch convert all JSON files
"""

import json
import sqlite3
import sys
import os
import glob
import base64
import mimetypes

SCHEMA = """
CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT);
CREATE TABLE IF NOT EXISTS questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT, type TEXT NOT NULL, topic TEXT,
    difficulty TEXT, question_zh TEXT NOT NULL, question_en TEXT,
    image_path TEXT, explanation_zh TEXT, explanation_en TEXT
);
CREATE TABLE IF NOT EXISTS options (
    id INTEGER PRIMARY KEY AUTOINCREMENT, question_id INTEGER NOT NULL REFERENCES questions(id),
    label TEXT NOT NULL, text_zh TEXT NOT NULL, text_en TEXT,
    is_correct INTEGER NOT NULL DEFAULT 0, explanation_zh TEXT, explanation_en TEXT,
    sort_order INTEGER NOT NULL DEFAULT 0
);
"""

MIME_MAP = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".webp": "image/webp",
    ".svg": "image/svg+xml",
    ".bmp": "image/bmp",
}


def resolve_image(image_path, search_dirs):
    """Try to find an image file and convert it to a base64 data URI."""
    if not image_path:
        return None
    if image_path.startswith("data:"):
        return image_path

    for base_dir in search_dirs:
        full_path = os.path.join(base_dir, image_path)
        if os.path.isfile(full_path):
            ext = os.path.splitext(full_path)[1].lower()
            mime = MIME_MAP.get(ext) or mimetypes.guess_type(full_path)[0] or "image/png"
            with open(full_path, "rb") as img_f:
                b64 = base64.b64encode(img_f.read()).decode("ascii")
            print(f"  Embedded image: {image_path} ({mime})")
            return f"data:{mime};base64,{b64}"

    print(f"  WARNING: Image not found: {image_path}")
    return image_path


def convert(json_path, db_path=None, image_dirs=None):
    if db_path is None:
        db_path = os.path.splitext(json_path)[0] + ".db"

    json_dir = os.path.dirname(os.path.abspath(json_path))
    search_dirs = [json_dir]
    if image_dirs:
        search_dirs = [os.path.abspath(d) for d in image_dirs] + search_dirs

    with open(json_path, "r", encoding="utf-8") as f:
        raw = f.read().strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1]
        if raw.endswith("```"):
            raw = raw.rsplit("```", 1)[0]
        data = json.loads(raw)

    if os.path.exists(db_path):
        os.remove(db_path)

    conn = sqlite3.connect(db_path)
    conn.executescript(SCHEMA)

    meta = data.get("meta", {})
    for k, v in meta.items():
        conn.execute("INSERT INTO meta (key, value) VALUES (?, ?)", (k, v))

    questions = data.get("questions", [])
    if not questions:
        print(f"WARNING: No questions found in {json_path}")
        conn.close()
        return

    img_count = 0
    for q in questions:
        qtype = q.get("type", "single")
        image_path = resolve_image(q.get("image_path"), search_dirs)
        if image_path and image_path.startswith("data:"):
            img_count += 1

        cur = conn.execute(
            "INSERT INTO questions (type, topic, difficulty, question_zh, question_en, image_path, explanation_zh, explanation_en) VALUES (?,?,?,?,?,?,?,?)",
            (
                qtype,
                q.get("topic"),
                q.get("difficulty"),
                q.get("question_zh", q.get("question_en", "")),
                q.get("question_en"),
                image_path,
                q.get("explanation_zh"),
                q.get("explanation_en"),
            ),
        )
        qid = cur.lastrowid

        for idx, opt in enumerate(q.get("options", [])):
            conn.execute(
                "INSERT INTO options (question_id, label, text_zh, text_en, is_correct, explanation_zh, explanation_en, sort_order) VALUES (?,?,?,?,?,?,?,?)",
                (
                    qid,
                    opt.get("label", chr(65 + idx)),
                    opt.get("text_zh", opt.get("text_en", "")),
                    opt.get("text_en"),
                    int(bool(opt.get("is_correct", False))),
                    opt.get("explanation_zh"),
                    opt.get("explanation_en"),
                    idx,
                ),
            )

    conn.commit()

    count = conn.execute("SELECT COUNT(*) FROM questions").fetchone()[0]
    topics = conn.execute(
        "SELECT topic, COUNT(*) FROM questions GROUP BY topic ORDER BY topic"
    ).fetchall()

    db_size = os.path.getsize(db_path)
    conn.close()

    print(f"\nCreated {db_path} ({db_size / 1024:.1f} KB) with {count} questions, {img_count} embedded images:")
    for t, c in topics:
        print(f"  {t or '(no topic)'}: {c}")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    args = sys.argv[1:]
    image_dirs = []
    json_files = []
    db_path = None
    i = 0
    while i < len(args):
        if args[i] in ("-i", "--images"):
            i += 1
            if i < len(args):
                image_dirs.append(args[i])
        elif args[i].endswith(".json"):
            json_files.append(args[i])
        elif not json_files:
            json_files.append(args[i])
        else:
            db_path = args[i]
        i += 1

    expanded = []
    for pattern in json_files:
        expanded.extend(glob.glob(pattern))
    json_files = [f for f in expanded if f.endswith(".json")]

    if not json_files:
        print(f"No JSON files found")
        sys.exit(1)

    if len(json_files) == 1 and db_path:
        convert(json_files[0], db_path, image_dirs)
    else:
        for f in json_files:
            print(f"\n--- Processing {f} ---")
            try:
                convert(f, image_dirs=image_dirs)
            except Exception as e:
                print(f"ERROR processing {f}: {e}")


if __name__ == "__main__":
    main()
