import * as db from "./db-bridge.js";

let questions = [];
let currentIndex = 0;
let answers = {};
let progressCache = {};
let onChangeCallback = null;

let examState = {
  active: false,
  timeLimit: 0,
  startTime: null,
  timerId: null,
  questionCount: 0,
  onTick: null,
  onTimeUp: null,
};

export function onStateChange(cb) { onChangeCallback = cb; }
function notify() { if (onChangeCallback) onChangeCallback(getState()); }

function cacheKey() {
  const bp = db.getCurrentBankPath();
  return bp ? `qf_session_${bp}` : null;
}

function saveSessionCache() {
  const key = cacheKey();
  if (!key || examState.active) return;
  try {
    localStorage.setItem(key, JSON.stringify({ answers, currentIndex }));
  } catch (_) { /* quota exceeded */ }
}

function loadSessionCache() {
  const key = cacheKey();
  if (!key) return null;
  try {
    const raw = localStorage.getItem(key);
    return raw ? JSON.parse(raw) : null;
  } catch (_) { return null; }
}

function clearSessionCache() {
  const key = cacheKey();
  if (key) localStorage.removeItem(key);
}

export async function loadQuestions(filters = {}, shuffle = false) {
  questions = await db.getQuestions(filters);
  if (shuffle) {
    for (let i = questions.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [questions[i], questions[j]] = [questions[j], questions[i]];
    }
  }
  progressCache = await db.getProgress();

  const cached = loadSessionCache();
  if (cached && !shuffle && Object.keys(filters).every((k) => !filters[k])) {
    answers = cached.answers || {};
    currentIndex = Math.min(cached.currentIndex || 0, questions.length - 1);
  } else {
    currentIndex = 0;
    answers = {};
  }

  notify();
}

export function getState() {
  const total = questions.length;
  const answeredCount = Object.values(answers).filter((a) => a.submitted).length;
  const correctCount = Object.values(answers).filter((a) => a.correct).length;

  let historyAnswered = 0;
  let historyCorrect = 0;
  for (const p of Object.values(progressCache)) {
    historyAnswered += (p.answered || 0);
    historyCorrect += (p.correct || 0);
  }

  let maxAnsweredIndex = -1;
  for (let i = questions.length - 1; i >= 0; i--) {
    if (answers[questions[i].id]?.submitted) { maxAnsweredIndex = i; break; }
  }

  return {
    total,
    currentIndex,
    answeredCount,
    correctCount,
    maxAnsweredIndex,
    rate: answeredCount > 0 ? Math.round((correctCount / answeredCount) * 100) : null,
    historyRate: historyAnswered > 0 ? Math.round((historyCorrect / historyAnswered) * 100) : null,
    hasNext: currentIndex < total - 1,
    hasPrev: currentIndex > 0,
    currentQuestion: questions[currentIndex] || null,
    currentAnswer: questions[currentIndex] ? answers[questions[currentIndex].id] : null,
    questions,
    answers,
    progressCache,
    examActive: examState.active,
  };
}

export async function getCurrentDetail() {
  const q = questions[currentIndex];
  if (!q) return null;
  return db.getQuestionDetail(q.id);
}

export function goNext() {
  if (currentIndex < questions.length - 1) { currentIndex++; saveSessionCache(); notify(); }
}

export function goPrev() {
  if (examState.active) return;
  if (currentIndex > 0) { currentIndex--; saveSessionCache(); notify(); }
}

export function goTo(index) {
  if (index >= 0 && index < questions.length) { currentIndex = index; saveSessionCache(); notify(); }
}

export function selectOption(questionId, optionLabel) {
  if (answers[questionId]?.submitted) return;
  if (!answers[questionId]) answers[questionId] = { selected: [], submitted: false, correct: false };
  const ans = answers[questionId];
  const q = questions.find((q) => q.id === questionId);
  if (!q) return;

  if (q.type === "single" || q.type === "truefalse") {
    ans.selected = [optionLabel];
  } else {
    const idx = ans.selected.indexOf(optionLabel);
    if (idx >= 0) ans.selected.splice(idx, 1);
    else ans.selected.push(optionLabel);
  }
  notify();
}

export async function submitAnswer(questionId, options) {
  if (answers[questionId]?.submitted) return answers[questionId];
  const ans = answers[questionId];
  if (!ans || ans.selected.length === 0) return null;

  const correctLabels = options.filter((o) => o.is_correct).map((o) => o.label);
  const selectedSet = new Set(ans.selected);
  const correctSet = new Set(correctLabels);
  const isCorrect =
    selectedSet.size === correctSet.size &&
    [...selectedSet].every((l) => correctSet.has(l));

  ans.submitted = true;
  ans.correct = isCorrect;

  await db.saveProgress(questionId, ans.selected.join(","), isCorrect);
  progressCache = await db.getProgress();
  saveSessionCache();
  notify();
  return ans;
}

export async function resetProgress() {
  await db.resetProgress();
  clearSessionCache();
  progressCache = {};
  answers = {};
  currentIndex = 0;
  notify();
}

// ── Exam Mode ──

export async function startExam(filters, timeMinutes, questionCount, onTick, onTimeUp) {
  let allQuestions = await db.getQuestions(filters);
  for (let i = allQuestions.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [allQuestions[i], allQuestions[j]] = [allQuestions[j], allQuestions[i]];
  }

  const count = Math.min(questionCount, allQuestions.length);
  if (count === 0) return false;

  questions = allQuestions.slice(0, count);
  currentIndex = 0;
  answers = {};

  examState.active = true;
  examState.timeLimit = timeMinutes * 60;
  examState.startTime = Date.now();
  examState.questionCount = count;
  examState.onTick = onTick;
  examState.onTimeUp = onTimeUp;

  if (timeMinutes > 0) {
    examState.timerId = setInterval(() => {
      const elapsed = Math.floor((Date.now() - examState.startTime) / 1000);
      const remaining = Math.max(0, examState.timeLimit - elapsed);
      if (onTick) onTick(remaining, examState.timeLimit);
      if (remaining <= 0) {
        endExam();
        if (onTimeUp) onTimeUp();
      }
    }, 1000);
  }

  notify();
  return true;
}

export function endExam() {
  if (examState.timerId) {
    clearInterval(examState.timerId);
    examState.timerId = null;
  }
  examState.active = false;
  notify();
}

export function getExamResult() {
  const elapsed = examState.startTime
    ? Math.floor((Date.now() - examState.startTime) / 1000)
    : 0;
  const total = questions.length;
  const answeredCount = Object.values(answers).filter((a) => a.submitted).length;
  const correctCount = Object.values(answers).filter((a) => a.correct).length;
  const score = total > 0 ? Math.round((correctCount / total) * 100) : 0;

  return {
    total,
    answeredCount,
    correctCount,
    score,
    elapsed,
    passed: score >= 60,
  };
}

export function isExamActive() { return examState.active; }

export function reset() {
  endExam();
  questions = [];
  currentIndex = 0;
  answers = {};
  progressCache = {};
  notify();
}
