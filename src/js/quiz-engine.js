import * as db from "./db-bridge.js";

let questions = [];
let currentIndex = 0;
let answers = {};
let progressCache = {};
let onChangeCallback = null;

export function onStateChange(cb) { onChangeCallback = cb; }
function notify() { if (onChangeCallback) onChangeCallback(getState()); }

export async function loadQuestions(filters = {}, shuffle = false) {
  questions = await db.getQuestions(filters);
  if (shuffle) {
    for (let i = questions.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [questions[i], questions[j]] = [questions[j], questions[i]];
    }
  }
  progressCache = await db.getProgress();
  currentIndex = 0;
  answers = {};
  notify();
}

export function getState() {
  const total = questions.length;
  const answeredCount = Object.keys(answers).length;
  const correctCount = Object.values(answers).filter((a) => a.correct).length;
  return {
    total,
    currentIndex,
    answeredCount,
    correctCount,
    rate: answeredCount > 0 ? Math.round((correctCount / answeredCount) * 100) : null,
    hasNext: currentIndex < total - 1,
    hasPrev: currentIndex > 0,
    currentQuestion: questions[currentIndex] || null,
    currentAnswer: questions[currentIndex] ? answers[questions[currentIndex].id] : null,
  };
}

export async function getCurrentDetail() {
  const q = questions[currentIndex];
  if (!q) return null;
  return db.getQuestionDetail(q.id);
}

export function goNext() {
  if (currentIndex < questions.length - 1) { currentIndex++; notify(); }
}

export function goPrev() {
  if (currentIndex > 0) { currentIndex--; notify(); }
}

export function goTo(index) {
  if (index >= 0 && index < questions.length) { currentIndex = index; notify(); }
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
  notify();
  return ans;
}
