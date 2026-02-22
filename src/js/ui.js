import { t, getLang } from "./i18n.js";

const $ = (s) => document.querySelector(s);

export function renderQuestion(detail, answer, examActive = false) {
  if (!detail) return;
  const lang = getLang();

  const badgeText =
    detail.type === "single" ? t("q_single") :
    detail.type === "multiple" ? t("q_multiple") :
    t("q_truefalse");
  $("#q-badge").textContent = badgeText;

  const stem = lang === "en" && detail.question_en ? detail.question_en : detail.question_zh;
  $("#q-stem").textContent = stem;

  if (detail.image_path) {
    $("#q-image-wrap").style.display = "";
    const imgEl = $("#q-image");
    imgEl.src = detail.image_path;
    imgEl.onclick = () => {
      const lb = $("#image-lightbox");
      $("#lightbox-img").src = detail.image_path;
      lb.classList.add("active");
    };
  } else {
    $("#q-image-wrap").style.display = "none";
  }

  const optionsEl = $("#q-options");
  optionsEl.innerHTML = "";

  const showExplanation = answer?.submitted && !examActive;

  if (detail.type === "truefalse") {
    renderTrueFalse(optionsEl, detail, answer, showExplanation, examActive);
  } else {
    renderChoiceOptions(optionsEl, detail, answer, showExplanation, examActive, lang);
  }

  const submitBtn = $("#submit-btn");
  if (answer?.submitted) {
    submitBtn.style.display = "none";
    const expArea = $("#explanation-area");
    if (!examActive) {
      const expText = lang === "en" && detail.explanation_en ? detail.explanation_en : detail.explanation_zh;
      if (expText) {
        expArea.style.display = "";
        $("#explanation-text").textContent = expText;
      } else {
        expArea.style.display = "none";
      }
    } else {
      expArea.style.display = "none";
    }
  } else {
    submitBtn.style.display = "";
    submitBtn.disabled = !answer || answer.selected.length === 0;
    $("#explanation-area").style.display = "none";
  }
}

export function updateStats(state) {
  $("#stat-answered").textContent = `${state.answeredCount}/${state.total}`;
  $("#stat-rate").textContent = state.rate !== null ? `${state.rate}%` : "--%";
  $("#stat-history-rate").textContent = state.historyRate !== null ? `${state.historyRate}%` : "--%";
  $("#q-number").textContent = state.total > 0 ? `${state.currentIndex + 1} / ${state.total}` : "";
  $("#prev-btn").disabled = !state.hasPrev || state.examActive;
  $("#next-btn").disabled = !state.hasNext;
  const progressBase = state.maxAnsweredIndex >= 0 ? state.maxAnsweredIndex + 1 : 0;
  const pct = state.total > 0 ? (progressBase / state.total) * 100 : 0;
  $("#progress-bar").style.width = `${pct}%`;

  const summaryBtn = $("#summary-btn");
  if (state.answeredCount > 0 && !state.examActive) {
    summaryBtn.style.display = "";
  } else {
    summaryBtn.style.display = "none";
  }

  const resetBtn = $("#reset-progress-btn");
  if (state.total > 0) resetBtn.style.display = "";
}

export function showQuiz(show) {
  $("#welcome-screen").style.display = show ? "none" : "";
  $("#quiz-area").style.display = show ? "" : "none";
  $("#summary-screen").style.display = "none";
}

export function showSummary(show) {
  $("#quiz-area").style.display = show ? "none" : "";
  $("#summary-screen").style.display = show ? "" : "none";
}

export function renderTopics(topics) {
  const sel = $("#filter-topic");
  while (sel.options.length > 1) sel.remove(1);
  topics.forEach((topic) => {
    const opt = document.createElement("option");
    opt.value = topic;
    opt.textContent = topic;
    sel.appendChild(opt);
  });

  const examSel = $("#exam-topic");
  if (examSel) {
    while (examSel.options.length > 1) examSel.remove(1);
    topics.forEach((topic) => {
      const opt = document.createElement("option");
      opt.value = topic;
      opt.textContent = topic;
      examSel.appendChild(opt);
    });
  }
}

export function renderBankList(banks, activePath) {
  const list = $("#bank-list");
  list.innerHTML = "";
  if (banks.length === 0) {
    list.innerHTML = `<p class="empty-hint" data-i18n="no_banks">${t("no_banks")}</p>`;
    return;
  }
  banks.forEach((bank) => {
    const div = document.createElement("div");
    div.className = "bank-item";
    if (bank.path === activePath) div.classList.add("active");
    div.textContent = bank.title || bank.path;
    div.dataset.path = bank.path;
    div.addEventListener("click", () => {
      div.dispatchEvent(new CustomEvent("bank-select", { bubbles: true, detail: bank.path }));
    });
    list.appendChild(div);
  });
}

export function renderBankMeta(meta) {
  const el = $("#bank-meta");
  if (!meta || (!meta.title && !meta.description)) {
    el.style.display = "none";
    return;
  }
  el.style.display = "";
  $("#bank-meta-title").textContent = meta.title || "";
  $("#bank-meta-desc").textContent = meta.description || "";
}

export function renderQuestionGrid(questions, answers, currentIndex, progressCache) {
  const grid = $("#question-grid");
  const section = $("#grid-section");
  if (!questions || questions.length === 0) {
    section.style.display = "none";
    return;
  }
  section.style.display = "";
  grid.innerHTML = "";

  questions.forEach((q, idx) => {
    const btn = document.createElement("div");
    btn.className = "qg-item";
    btn.textContent = idx + 1;

    if (idx === currentIndex) {
      btn.classList.add("qg-current");
    }

    const ans = answers[q.id];
    if (ans?.submitted) {
      btn.classList.add(ans.correct ? "qg-correct" : "qg-incorrect");
    } else if (progressCache && progressCache[q.id]) {
      btn.classList.add("qg-history");
    }

    btn.addEventListener("click", () => {
      btn.dispatchEvent(new CustomEvent("grid-jump", { bubbles: true, detail: idx }));
    });
    grid.appendChild(btn);
  });
}

export function renderSummary(state, allDetails) {
  const { answers, questions } = state;
  const total = questions.length;
  const answeredCount = Object.values(answers).filter((a) => a.submitted).length;
  const correctCount = Object.values(answers).filter((a) => a.correct).length;
  const rate = answeredCount > 0 ? Math.round((correctCount / answeredCount) * 100) : 0;

  // Score section
  const scoreEl = $("#summary-score");
  scoreEl.innerHTML = `
    <div class="summary-stat"><div class="stat-value">${total}</div><div class="stat-label">${t("total_questions")}</div></div>
    <div class="summary-stat"><div class="stat-value">${answeredCount}</div><div class="stat-label">${t("answered_count")}</div></div>
    <div class="summary-stat"><div class="stat-value">${correctCount}</div><div class="stat-label">${t("correct_count")}</div></div>
    <div class="summary-stat"><div class="stat-value">${rate}%</div><div class="stat-label">${t("accuracy")}</div></div>
  `;

  // Breakdown by type
  const types = {};
  questions.forEach((q) => {
    const tKey = q.type || "unknown";
    if (!types[tKey]) types[tKey] = { total: 0, correct: 0 };
    types[tKey].total++;
    const ans = answers[q.id];
    if (ans?.correct) types[tKey].correct++;
  });

  const breakdownEl = $("#summary-breakdown");
  let breakdownHTML = `<h3>${t("by_type")}</h3>`;
  for (const [type, data] of Object.entries(types)) {
    const label = t(type === "single" ? "q_single" : type === "multiple" ? "q_multiple" : "q_truefalse");
    const pct = data.total > 0 ? Math.round((data.correct / data.total) * 100) : 0;
    breakdownHTML += `<div class="breakdown-row"><span>${label}</span><span>${data.correct}/${data.total} (${pct}%)</span></div>`;
  }
  breakdownEl.innerHTML = breakdownHTML;

  // Wrong answers list
  const wrongEl = $("#wrong-list");
  const wrongQuestions = questions
    .map((q, idx) => ({ q, idx, ans: answers[q.id] }))
    .filter((item) => item.ans?.submitted && !item.ans.correct);

  if (wrongQuestions.length === 0) {
    wrongEl.innerHTML = `<h3>${t("wrong_questions")}</h3><p class="empty-hint">${t("no_wrong")}</p>`;
  } else {
    const lang = getLang();
    let wrongHTML = `<h3>${t("wrong_questions")}</h3>`;
    wrongQuestions.forEach((item) => {
      const stem = lang === "en" && item.q.question_en ? item.q.question_en : item.q.question_zh;
      const preview = stem.length > 50 ? stem.slice(0, 50) + "..." : stem;
      wrongHTML += `<div class="wrong-item" data-idx="${item.idx}"><span class="wrong-num">#${item.idx + 1}</span><span>${preview}</span></div>`;
    });
    wrongEl.innerHTML = wrongHTML;
  }
}

export function renderExamSummary(examResult) {
  const scoreEl = $("#summary-score");
  const mins = Math.floor(examResult.elapsed / 60);
  const secs = examResult.elapsed % 60;
  const timeStr = `${mins}${t("minutes")}${secs}${t("seconds")}`;

  scoreEl.innerHTML = `
    <div class="summary-stat"><div class="stat-value">${examResult.score}</div><div class="stat-label">${t("exam_score")}</div></div>
    <div class="summary-stat"><div class="stat-value">${examResult.correctCount}/${examResult.total}</div><div class="stat-label">${t("correct_count")}</div></div>
    <div class="summary-stat"><div class="stat-value">${timeStr}</div><div class="stat-label">${t("exam_time_used")}</div></div>
    <div class="summary-stat"><div class="stat-value">${examResult.passed ? t("exam_passed") : t("exam_failed")}</div><div class="stat-label">${examResult.score}%</div></div>
  `;
}

function renderTrueFalse(container, detail, answer, showExplanation, examActive) {
  const group = document.createElement("div");
  group.className = "tf-group";

  const trueOpt = detail.options.find((o) => o.label === "True");
  const falseOpt = detail.options.find((o) => o.label === "False");
  if (!trueOpt || !falseOpt) return;

  [trueOpt, falseOpt].forEach((opt) => {
    const btn = document.createElement("div");
    btn.className = "tf-btn";
    btn.dataset.label = opt.label;

    if (answer?.submitted) {
      btn.classList.add("disabled");
      if (!examActive) {
        if (opt.is_correct) btn.classList.add("tf-correct");
        else if (answer.selected.includes(opt.label)) btn.classList.add("tf-incorrect");
        else btn.classList.add("tf-dim");
      } else {
        if (answer.selected.includes(opt.label)) btn.classList.add("selected");
      }
    } else if (answer?.selected?.includes(opt.label)) {
      btn.classList.add("selected");
    }

    const icon = document.createElement("div");
    icon.className = "tf-icon";
    icon.textContent = opt.label === "True" ? "\u2714" : "\u2718";

    const label = document.createElement("div");
    label.className = "tf-label";
    label.textContent = opt.label === "True" ? t("true_opt") : t("false_opt");

    btn.appendChild(icon);
    btn.appendChild(label);

    if (!answer?.submitted) {
      btn.addEventListener("click", () => {
        btn.dispatchEvent(new CustomEvent("option-select", { bubbles: true, detail: opt.label }));
      });
    }

    group.appendChild(btn);
  });

  container.appendChild(group);

  if (showExplanation) {
    [trueOpt, falseOpt].forEach((opt) => {
      const expText = getLang() === "en" && opt.explanation_en ? opt.explanation_en : opt.explanation_zh;
      if (expText) {
        const expEl = document.createElement("div");
        expEl.className = "option-explanation";
        expEl.style.display = "block";
        expEl.style.marginBottom = "8px";
        expEl.textContent = `${opt.label === "True" ? t("true_opt") : t("false_opt")}: ${expText}`;
        container.appendChild(expEl);
      }
    });
  }
}

function renderChoiceOptions(container, detail, answer, showExplanation, examActive, lang) {
  detail.options.forEach((opt) => {
    const div = document.createElement("div");
    div.className = "option-item";
    div.dataset.label = opt.label;

    if (answer?.submitted) {
      div.classList.add("disabled");
      if (!examActive) {
        div.classList.add("revealed");
        if (opt.is_correct) div.classList.add("correct");
        else if (answer.selected.includes(opt.label)) div.classList.add("incorrect");
      } else {
        if (answer.selected.includes(opt.label)) div.classList.add("selected");
      }
    } else if (answer?.selected?.includes(opt.label)) {
      div.classList.add("selected");
    }

    const labelEl = document.createElement("div");
    labelEl.className = "option-label";
    labelEl.textContent = opt.label;

    const bodyEl = document.createElement("div");
    bodyEl.className = "option-body";

    const textEl = document.createElement("div");
    textEl.className = "option-text";
    textEl.textContent = lang === "en" && opt.text_en ? opt.text_en : opt.text_zh;

    bodyEl.appendChild(textEl);

    if (showExplanation) {
      const expText = lang === "en" && opt.explanation_en ? opt.explanation_en : opt.explanation_zh;
      if (expText) {
        const expEl = document.createElement("div");
        expEl.className = "option-explanation";
        expEl.textContent = expText;
        bodyEl.appendChild(expEl);
      }

      const iconEl = document.createElement("span");
      iconEl.className = "option-icon";
      iconEl.textContent = opt.is_correct ? "\u2713" : (answer.selected.includes(opt.label) ? "\u2717" : "");
      div.appendChild(iconEl);
    }

    div.appendChild(labelEl);
    div.appendChild(bodyEl);

    if (!answer?.submitted) {
      div.addEventListener("click", () => {
        div.dispatchEvent(new CustomEvent("option-select", { bubbles: true, detail: opt.label }));
      });
    }

    container.appendChild(div);
  });
}

export function updateExamTimer(remaining, total) {
  const timer = $("#exam-timer");
  const display = $("#exam-timer-display");
  const mins = Math.floor(remaining / 60);
  const secs = remaining % 60;
  display.textContent = `${String(mins).padStart(2, "0")}:${String(secs).padStart(2, "0")}`;

  if (remaining <= 60) {
    timer.classList.add("warning");
  } else {
    timer.classList.remove("warning");
  }
}
