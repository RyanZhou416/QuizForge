import { initBridge, openBankFromFile, getTopics, isLoaded, getMode } from "./db-bridge.js";
import * as engine from "./quiz-engine.js";
import * as ui from "./ui.js";
import { applyI18n, toggleLang, getLang, setLang } from "./i18n.js";

const $ = (s) => document.querySelector(s);

let currentDetail = null;

async function refreshQuestion() {
  const state = engine.getState();
  ui.updateStats(state);
  if (!state.currentQuestion) return;
  currentDetail = await engine.getCurrentDetail();
  ui.renderQuestion(currentDetail, state.currentAnswer);
}

async function loadBank() {
  const topics = await getTopics();
  ui.renderTopics(topics);
  await engine.loadQuestions({}, $("#shuffle-toggle").checked);
  ui.showQuiz(true);
  await refreshQuestion();
}

function getFilters() {
  return {
    topic: $("#filter-topic").value || undefined,
    type: $("#filter-type").value || undefined,
    difficulty: $("#filter-difficulty").value || undefined,
  };
}

async function init() {
  applyI18n();
  initTheme();
  await initBridge();

  engine.onStateChange(async () => {
    const state = engine.getState();
    ui.updateStats(state);
  });

  // Language toggle
  $("#lang-toggle").addEventListener("click", async () => {
    toggleLang();
    if (isLoaded()) await refreshQuestion();
  });

  // Theme toggle
  $("#theme-toggle").addEventListener("click", () => {
    const html = document.documentElement;
    const isDark = html.getAttribute("data-theme") === "dark";
    html.setAttribute("data-theme", isDark ? "light" : "dark");
    localStorage.setItem("qf_theme", isDark ? "light" : "dark");
  });

  // Sidebar toggle
  $("#sidebar-toggle").addEventListener("click", () => {
    $("#sidebar").classList.toggle("collapsed");
  });

  // File input
  const fileInput = $("#file-input");
  const openHandler = () => fileInput.click();
  $("#open-bank-btn").addEventListener("click", openHandler);
  $("#open-bank-btn-main").addEventListener("click", openHandler);

  fileInput.addEventListener("change", async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    await openBankFromFile(file);
    await loadBank();
    fileInput.value = "";
  });

  // Drag & drop
  const dropZone = $("#drop-zone");
  ["dragenter", "dragover"].forEach((evt) => {
    dropZone.addEventListener(evt, (e) => { e.preventDefault(); dropZone.classList.add("dragover"); });
  });
  ["dragleave", "drop"].forEach((evt) => {
    dropZone.addEventListener(evt, () => dropZone.classList.remove("dragover"));
  });
  dropZone.addEventListener("drop", async (e) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (file && file.name.endsWith(".db")) {
      await openBankFromFile(file);
      await loadBank();
    }
  });

  // Option selection
  document.addEventListener("option-select", (e) => {
    if (!currentDetail) return;
    engine.selectOption(currentDetail.id, e.detail);
    const state = engine.getState();
    ui.renderQuestion(currentDetail, state.currentAnswer);
  });

  // Submit
  $("#submit-btn").addEventListener("click", async () => {
    if (!currentDetail) return;
    await engine.submitAnswer(currentDetail.id, currentDetail.options);
    await refreshQuestion();
  });

  // Navigation
  $("#prev-btn").addEventListener("click", async () => { engine.goPrev(); await refreshQuestion(); });
  $("#next-btn").addEventListener("click", async () => { engine.goNext(); await refreshQuestion(); });

  // Filters
  ["filter-topic", "filter-type", "filter-difficulty"].forEach((id) => {
    $(`#${id}`).addEventListener("change", async () => {
      await engine.loadQuestions(getFilters(), $("#shuffle-toggle").checked);
      await refreshQuestion();
    });
  });

  $("#shuffle-toggle").addEventListener("change", async () => {
    await engine.loadQuestions(getFilters(), $("#shuffle-toggle").checked);
    await refreshQuestion();
  });

  // Keyboard navigation
  document.addEventListener("keydown", async (e) => {
    if (!isLoaded()) return;
    if (e.key === "ArrowLeft") { engine.goPrev(); await refreshQuestion(); }
    if (e.key === "ArrowRight") { engine.goNext(); await refreshQuestion(); }
    if (e.key === "Enter") {
      const state = engine.getState();
      if (state.currentAnswer && !state.currentAnswer.submitted && state.currentAnswer.selected.length > 0) {
        await engine.submitAnswer(currentDetail.id, currentDetail.options);
        await refreshQuestion();
      }
    }
  });
}

function initTheme() {
  const saved = localStorage.getItem("qf_theme");
  if (saved) {
    document.documentElement.setAttribute("data-theme", saved);
  } else if (window.matchMedia("(prefers-color-scheme: dark)").matches) {
    document.documentElement.setAttribute("data-theme", "dark");
  }
}

init();
