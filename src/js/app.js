import { initBridge, openBankFromFile, openBankFromPath, openWebBankByName, addWebBankFiles, getTopics, getBankMeta, getBankList, getCurrentBankPath, isLoaded, getMode, closeBank, removeWebBank } from "./db-bridge.js";
import * as engine from "./quiz-engine.js";
import * as ui from "./ui.js";
import { applyI18n, toggleLang, t } from "./i18n.js";
import { showToast } from "./toast.js";

const $ = (s) => document.querySelector(s);

let currentDetail = null;
let searchDebounceTimer = null;

async function refreshBankList() {
  const banks = await getBankList();
  ui.renderBankList(banks, getCurrentBankPath());
}

async function refreshQuestion() {
  const state = engine.getState();
  ui.updateStats(state);
  ui.renderQuestionGrid(state.questions, state.answers, state.currentIndex, state.progressCache);
  if (!state.currentQuestion) return;
  currentDetail = await engine.getCurrentDetail();
  ui.renderQuestion(currentDetail, state.currentAnswer, state.examActive);
}

async function loadBank() {
  try {
    const topics = await getTopics();
    ui.renderTopics(topics);
    const meta = await getBankMeta();
    ui.renderBankMeta(meta);
    await engine.loadQuestions(getFilters(), $("#shuffle-toggle").checked);
    ui.showQuiz(true);
    $("#exam-mode-btn").style.display = "";
    $("#close-bank-btn").style.display = "";
    await refreshQuestion();
    showToast(t("bank_opened"), "success");
  } catch (e) {
    showToast(e.message || String(e), "error");
  }
}

function getFilters() {
  const keyword = $("#search-input").value.trim();
  return {
    topic: $("#filter-topic").value || undefined,
    type: $("#filter-type").value || undefined,
    difficulty: $("#filter-difficulty").value || undefined,
    keyword: keyword || undefined,
  };
}

async function init() {
  applyI18n();
  initTheme();

  try {
    await initBridge();
  } catch (e) {
    console.warn("initBridge:", e);
  }

  engine.onStateChange(async () => {
    const state = engine.getState();
    ui.updateStats(state);
    ui.renderQuestionGrid(state.questions, state.answers, state.currentIndex, state.progressCache);
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

  // ── Open bank ──
  const fileInput = $("#file-input");
  const openHandler = async () => {
    if (getMode() === "desktop") {
      try {
        const dialogMod = "@tauri-apps/" + "plugin-dialog";
        const { open } = await import(/* @vite-ignore */ dialogMod);
        const selected = await open({ filters: [{ name: "Quiz Bank", extensions: ["db"] }] });
        if (selected) {
          await openBankFromPath(selected);
          await loadBank();
        }
      } catch (e) {
        showToast(e.message || String(e), "error");
      }
    } else {
      fileInput.click();
    }
  };
  $("#open-bank-btn").addEventListener("click", openHandler);
  $("#open-bank-btn-main").addEventListener("click", openHandler);

  fileInput.addEventListener("change", async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    if (!file.name.endsWith(".db")) {
      showToast(t("file_error"), "error");
      return;
    }
    try {
      await addWebBankFiles([file]);
      await openBankFromFile(file);
      await loadBank();
      await refreshBankList();
    } catch (err) {
      showToast(err.message || String(err), "error");
    }
    fileInput.value = "";
  });

  // ── Open folder ──
  const folderInput = $("#folder-input");
  const folderHandler = async () => {
    if (getMode() === "desktop") {
      try {
        const dialogMod = "@tauri-apps/" + "plugin-dialog";
        const { open } = await import(/* @vite-ignore */ dialogMod);
        const selected = await open({ directory: true });
        if (selected) {
          const coreMod = "@tauri-apps/" + "api/core";
          const { invoke } = await import(/* @vite-ignore */ coreMod);
          await invoke("add_watch_folder", { path: selected });
          const banks = await getBankList();
          ui.renderBankList(banks, getCurrentBankPath());
          if (banks.length > 0) {
            await openBankFromPath(banks[0].path);
            await loadBank();
          }
          showToast(t("folder_loaded").replace("{n}", banks.length), "success");
        }
      } catch (e) {
        showToast(e.message || String(e), "error");
      }
    } else {
      folderInput.click();
    }
  };
  $("#open-folder-btn").addEventListener("click", folderHandler);
  $("#open-folder-btn-main").addEventListener("click", folderHandler);

  folderInput.addEventListener("change", async (e) => {
    const files = Array.from(e.target.files).filter((f) => f.name.endsWith(".db"));
    if (files.length === 0) {
      showToast(t("file_error"), "error");
      folderInput.value = "";
      return;
    }
    try {
      await addWebBankFiles(files);
      await openBankFromFile(files[0]);
      await loadBank();
      await refreshBankList();
      showToast(t("folder_loaded").replace("{n}", files.length), "success");
    } catch (err) {
      showToast(err.message || String(err), "error");
    }
    folderInput.value = "";
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
      try {
        await addWebBankFiles([file]);
        await openBankFromFile(file);
        await loadBank();
        await refreshBankList();
      } catch (err) {
        showToast(err.message || String(err), "error");
      }
    } else {
      showToast(t("file_error"), "error");
    }
  });

  // ── Bank list (desktop) ──
  if (getMode() === "desktop") {
    try {
      const eventMod = "@tauri-apps/" + "api/event";
      const { listen } = await import(/* @vite-ignore */ eventMod);
      await listen("banks-changed", async () => {
        const banks = await getBankList();
        ui.renderBankList(banks);
      });
      const banks = await getBankList();
      ui.renderBankList(banks);
    } catch (_) { /* not in Tauri context */ }
  }

  document.addEventListener("bank-select", async (e) => {
    try {
      if (getMode() === "desktop") {
        await openBankFromPath(e.detail);
      } else {
        await openWebBankByName(e.detail);
      }
      await loadBank();
      await refreshBankList();
    } catch (err) {
      showToast(err.message || String(err), "error");
    }
  });

  // ── Close bank ──
  $("#close-bank-btn").addEventListener("click", async () => {
    if (!isLoaded()) return;
    await closeBank();
    engine.reset();
    currentDetail = null;
    ui.resetQuizUI();
    $("#close-bank-btn").style.display = "none";
    await refreshBankList();
    showToast(t("bank_closed"), "success");
  });

  // ── Delete bank from list ──
  document.addEventListener("bank-delete", async (e) => {
    if (!confirm(t("delete_bank_confirm"))) return;
    const bankPath = e.detail;
    const isCurrent = bankPath === getCurrentBankPath();

    if (getMode() === "desktop") {
      try {
        const coreMod = "@tauri-apps/" + "api/core";
        const { invoke } = await import(/* @vite-ignore */ coreMod);
        await invoke("remove_bank_by_path", { bankPath });
      } catch (err) {
        showToast(err.message || String(err), "error");
        return;
      }
    } else {
      await removeWebBank(bankPath);
    }

    if (isCurrent) {
      await closeBank();
      engine.reset();
      currentDetail = null;
      ui.resetQuizUI();
      $("#close-bank-btn").style.display = "none";
    }

    await refreshBankList();
    showToast(t("bank_deleted"), "success");
  });

  // ── Option selection ──
  document.addEventListener("option-select", (e) => {
    if (!currentDetail) return;
    engine.selectOption(currentDetail.id, e.detail);
    const state = engine.getState();
    ui.renderQuestion(currentDetail, state.currentAnswer, state.examActive);
  });

  // ── Submit ──
  $("#submit-btn").addEventListener("click", async () => {
    if (!currentDetail) return;
    await engine.submitAnswer(currentDetail.id, currentDetail.options);
    await refreshQuestion();

    const state = engine.getState();
    if (state.examActive && state.answeredCount === state.total) {
      finishExam();
    }
  });

  // ── Navigation ──
  $("#prev-btn").addEventListener("click", async () => { engine.goPrev(); await refreshQuestion(); });
  $("#next-btn").addEventListener("click", async () => { engine.goNext(); await refreshQuestion(); });

  // ── Question grid jump ──
  document.addEventListener("grid-jump", async (e) => {
    engine.goTo(e.detail);
    await refreshQuestion();
  });

  // ── Filters ──
  ["filter-topic", "filter-type", "filter-difficulty"].forEach((id) => {
    $(`#${id}`).addEventListener("change", async () => {
      if (!isLoaded()) return;
      await engine.loadQuestions(getFilters(), $("#shuffle-toggle").checked);
      await refreshQuestion();
    });
  });

  $("#shuffle-toggle").addEventListener("change", async () => {
    if (!isLoaded()) return;
    await engine.loadQuestions(getFilters(), $("#shuffle-toggle").checked);
    await refreshQuestion();
  });

  // ── Search (debounced) ──
  $("#search-input").addEventListener("input", () => {
    if (!isLoaded()) return;
    clearTimeout(searchDebounceTimer);
    searchDebounceTimer = setTimeout(async () => {
      await engine.loadQuestions(getFilters(), $("#shuffle-toggle").checked);
      await refreshQuestion();
    }, 300);
  });

  // ── Reset progress ──
  $("#reset-progress-btn").addEventListener("click", async () => {
    if (!confirm(t("reset_confirm"))) return;
    await engine.resetProgress();
    await engine.loadQuestions(getFilters(), $("#shuffle-toggle").checked);
    await refreshQuestion();
    showToast(t("reset_done"), "success");
  });

  // ── Summary ──
  $("#summary-btn").addEventListener("click", () => {
    const state = engine.getState();
    ui.renderSummary(state, null);
    ui.showSummary(true);
  });

  $("#summary-back-btn").addEventListener("click", () => {
    ui.showSummary(false);
  });

  $("#summary-retry-btn").addEventListener("click", async () => {
    await engine.loadQuestions(getFilters(), $("#shuffle-toggle").checked);
    ui.showSummary(false);
    await refreshQuestion();
  });

  document.addEventListener("click", async (e) => {
    const wrongItem = e.target.closest(".wrong-item");
    if (wrongItem) {
      const idx = parseInt(wrongItem.dataset.idx, 10);
      engine.goTo(idx);
      ui.showSummary(false);
      await refreshQuestion();
    }
  });

  // ── Exam mode ──
  $("#exam-mode-btn").addEventListener("click", () => {
    $("#exam-dialog").classList.add("active");
  });

  $("#exam-cancel").addEventListener("click", () => {
    $("#exam-dialog").classList.remove("active");
  });

  $("#exam-start").addEventListener("click", async () => {
    const count = parseInt($("#exam-count").value, 10) || 10;
    const time = parseInt($("#exam-time").value, 10) || 0;
    const topic = $("#exam-topic").value || undefined;
    const difficulty = $("#exam-difficulty").value || undefined;

    const filters = { topic, difficulty };
    const started = await engine.startExam(
      filters, time, count,
      (remaining, total) => ui.updateExamTimer(remaining, total),
      () => {
        showToast(t("exam_auto_submit"), "info", 5000);
        finishExam();
      },
    );

    if (!started) {
      showToast(t("exam_not_enough"), "error");
      return;
    }

    $("#exam-dialog").classList.remove("active");
    $("#exam-timer").classList.add("active");
    ui.showQuiz(true);

    if (time > 0) {
      ui.updateExamTimer(time * 60, time * 60);
    }

    await refreshQuestion();
  });

  // ── Image lightbox ──
  const lightbox = $("#image-lightbox");
  lightbox.addEventListener("click", () => lightbox.classList.remove("active"));
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && lightbox.classList.contains("active")) {
      lightbox.classList.remove("active");
    }
  });

  // ── Keyboard navigation ──
  document.addEventListener("keydown", async (e) => {
    if (!isLoaded()) return;
    if (e.target.tagName === "INPUT" || e.target.tagName === "SELECT" || e.target.tagName === "TEXTAREA") return;
    if (e.key === "ArrowLeft") { engine.goPrev(); await refreshQuestion(); }
    if (e.key === "ArrowRight") { engine.goNext(); await refreshQuestion(); }
    if (e.key === "Enter") {
      const state = engine.getState();
      if (state.currentAnswer && !state.currentAnswer.submitted && state.currentAnswer.selected.length > 0) {
        await engine.submitAnswer(currentDetail.id, currentDetail.options);
        await refreshQuestion();
        if (state.examActive && state.answeredCount + 1 === state.total) {
          finishExam();
        }
      }
    }
  });
}

function finishExam() {
  engine.endExam();
  const result = engine.getExamResult();
  const state = engine.getState();

  $("#exam-timer").classList.remove("active", "warning");

  ui.renderSummary(state, null);
  ui.renderExamSummary(result);
  ui.showSummary(true);
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
