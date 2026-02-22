let isTauri = false;
let tauriInvoke = null;
let sqlJs = null;
let currentDb = null;
let currentDbPath = null;

export async function initBridge() {
  if (window.__TAURI_INTERNALS__) {
    isTauri = true;
    const coreMod = "@tauri-apps/" + "api/core";
    const { invoke } = await import(/* @vite-ignore */ coreMod);
    tauriInvoke = invoke;
  }
}

async function ensureSqlJs() {
  if (sqlJs) return;
  const initSqlJs = (await import("sql.js")).default;
  sqlJs = await initSqlJs({
    locateFile: () => "/sql-wasm.wasm",
  });
}

export function getMode() { return isTauri ? "desktop" : "web"; }

export async function openBankFromPath(path) {
  if (isTauri) {
    await tauriInvoke("open_bank", { path });
    currentDbPath = path;
    return;
  }
  throw new Error("Use openBankFromFile in web mode");
}

export async function openBankFromFile(file) {
  await ensureSqlJs();
  const buf = await file.arrayBuffer();
  currentDb = new sqlJs.Database(new Uint8Array(buf));
  currentDbPath = file.name;
}

export async function getBankMeta() {
  if (isTauri) return tauriInvoke("get_bank_meta");
  if (!currentDb) return {};
  const rows = currentDb.exec("SELECT key, value FROM meta");
  if (!rows.length) return {};
  const meta = {};
  rows[0].values.forEach(([k, v]) => { meta[k] = v; });
  return meta;
}

export async function getQuestions(filters = {}) {
  if (isTauri) return tauriInvoke("get_questions", { filters });
  if (!currentDb) return [];
  let sql = "SELECT id, type, topic, difficulty, question_zh, question_en, image_path FROM questions WHERE 1=1";
  const params = [];
  if (filters.topic) { sql += " AND topic = ?"; params.push(filters.topic); }
  if (filters.type) { sql += " AND type = ?"; params.push(filters.type); }
  if (filters.difficulty) { sql += " AND difficulty = ?"; params.push(filters.difficulty); }
  if (filters.keyword) {
    sql += " AND (question_zh LIKE ? OR question_en LIKE ?)";
    const kw = `%${filters.keyword}%`;
    params.push(kw, kw);
  }
  sql += " ORDER BY id";
  const stmt = currentDb.prepare(sql);
  stmt.bind(params);
  const questions = [];
  while (stmt.step()) {
    const row = stmt.getAsObject();
    questions.push(row);
  }
  stmt.free();
  return questions;
}

export async function getQuestionDetail(id) {
  if (isTauri) return tauriInvoke("get_question_detail", { id });
  if (!currentDb) return null;
  const qStmt = currentDb.prepare(
    "SELECT * FROM questions WHERE id = ?",
  );
  qStmt.bind([id]);
  if (!qStmt.step()) { qStmt.free(); return null; }
  const q = qStmt.getAsObject();
  qStmt.free();

  const oStmt = currentDb.prepare(
    "SELECT * FROM options WHERE question_id = ? ORDER BY sort_order, id",
  );
  oStmt.bind([id]);
  const options = [];
  while (oStmt.step()) options.push(oStmt.getAsObject());
  oStmt.free();

  return { ...q, options };
}

export async function getTopics() {
  if (isTauri) return tauriInvoke("get_topics");
  if (!currentDb) return [];
  const rows = currentDb.exec("SELECT DISTINCT topic FROM questions WHERE topic IS NOT NULL ORDER BY topic");
  if (!rows.length) return [];
  return rows[0].values.map(([v]) => v);
}

export async function saveProgress(questionId, answer, correct) {
  if (isTauri) return tauriInvoke("save_progress", { questionId, answer, correct });
  let progress = JSON.parse(localStorage.getItem("qf_progress") || "{}");
  const prev = progress[questionId] || { answered: 0, correct: 0 };
  progress[questionId] = {
    answered: prev.answered + 1,
    correct: prev.correct + (correct ? 1 : 0),
    last_answer: answer,
  };
  localStorage.setItem("qf_progress", JSON.stringify(progress));
}

export async function getProgress() {
  if (isTauri) return tauriInvoke("get_progress");
  return JSON.parse(localStorage.getItem("qf_progress") || "{}");
}

export async function resetProgress() {
  if (isTauri) return tauriInvoke("reset_progress");
  localStorage.removeItem("qf_progress");
}

export async function exportProgress() {
  const progress = await getProgress();
  const bankName = currentDbPath ? currentDbPath.replace(/^.*[\\/]/, "").replace(/\.db$/i, "") : "quizforge";
  const data = {
    bank: currentDbPath || "unknown",
    exportedAt: new Date().toISOString(),
    progress,
  };
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `${bankName}_progress_${new Date().toISOString().slice(0, 10)}.json`;
  a.click();
  URL.revokeObjectURL(url);
}

export async function importProgress(file) {
  const text = await file.text();
  const data = JSON.parse(text);
  const progress = data.progress || data;
  if (typeof progress !== "object" || progress === null) {
    throw new Error("Invalid progress format");
  }
  if (isTauri) {
    for (const [qid, entry] of Object.entries(progress)) {
      const id = parseInt(qid, 10);
      if (isNaN(id)) continue;
      for (let i = 0; i < (entry.answered || 1); i++) {
        const isCorrect = i < (entry.correct || 0);
        await tauriInvoke("save_progress", {
          questionId: id,
          answer: entry.last_answer || "",
          correct: isCorrect,
        });
      }
    }
  } else {
    const existing = JSON.parse(localStorage.getItem("qf_progress") || "{}");
    Object.assign(existing, progress);
    localStorage.setItem("qf_progress", JSON.stringify(existing));
  }
}

let webBankFiles = [];

export async function getBankList() {
  if (isTauri) return tauriInvoke("get_bank_list");
  return webBankFiles.map((f) => ({
    path: f.name,
    title: f.name.replace(/\.db$/i, ""),
  }));
}

export async function addWebBankFiles(files) {
  for (const f of files) {
    if (!webBankFiles.some((b) => b.name === f.name)) {
      webBankFiles.push(f);
    }
  }
}

export async function openWebBankByName(name) {
  const file = webBankFiles.find((f) => f.name === name);
  if (!file) throw new Error("Bank not found: " + name);
  await openBankFromFile(file);
}

export async function closeBank() {
  if (isTauri) {
    await tauriInvoke("close_bank");
  } else if (currentDb) {
    currentDb.close();
    currentDb = null;
  }
  currentDbPath = null;
}

export async function removeWebBank(name) {
  if (isTauri) return;
  webBankFiles = webBankFiles.filter((f) => f.name !== name);
}

export function isLoaded() {
  return isTauri ? !!currentDbPath : !!currentDb;
}

export function getCurrentBankPath() {
  return currentDbPath;
}
