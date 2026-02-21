import { t, getLang } from "./i18n.js";

const $ = (s) => document.querySelector(s);

export function renderQuestion(detail, answer) {
  if (!detail) return;
  const lang = getLang();
  const card = $("#question-card");

  const badgeText =
    detail.type === "single" ? t("q_single") :
    detail.type === "multiple" ? t("q_multiple") :
    t("q_truefalse");
  $("#q-badge").textContent = badgeText;

  const stem = lang === "en" && detail.question_en ? detail.question_en : detail.question_zh;
  $("#q-stem").textContent = stem;

  if (detail.image_path) {
    $("#q-image-wrap").style.display = "";
    $("#q-image").src = detail.image_path;
  } else {
    $("#q-image-wrap").style.display = "none";
  }

  const optionsEl = $("#q-options");
  optionsEl.innerHTML = "";

  detail.options.forEach((opt) => {
    const div = document.createElement("div");
    div.className = "option-item";
    div.dataset.label = opt.label;

    if (answer?.submitted) {
      div.classList.add("disabled", "revealed");
      if (opt.is_correct) div.classList.add("correct");
      else if (answer.selected.includes(opt.label)) div.classList.add("incorrect");
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

    if (answer?.submitted) {
      const expText = lang === "en" && opt.explanation_en ? opt.explanation_en : opt.explanation_zh;
      if (expText) {
        const expEl = document.createElement("div");
        expEl.className = "option-explanation";
        expEl.textContent = expText;
        bodyEl.appendChild(expEl);
      }

      const iconEl = document.createElement("span");
      iconEl.className = "option-icon";
      iconEl.textContent = opt.is_correct ? "✓" : (answer.selected.includes(opt.label) ? "✗" : "");
      div.appendChild(iconEl);
    }

    div.appendChild(labelEl);
    div.appendChild(bodyEl);

    if (!answer?.submitted) {
      div.addEventListener("click", () => {
        div.dispatchEvent(new CustomEvent("option-select", { bubbles: true, detail: opt.label }));
      });
    }

    optionsEl.appendChild(div);
  });

  const submitBtn = $("#submit-btn");
  if (answer?.submitted) {
    submitBtn.style.display = "none";
    const expArea = $("#explanation-area");
    const expText = lang === "en" && detail.explanation_en ? detail.explanation_en : detail.explanation_zh;
    if (expText) {
      expArea.style.display = "";
      $("#explanation-text").textContent = expText;
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
  $("#q-number").textContent = state.total > 0 ? `${state.currentIndex + 1} / ${state.total}` : "";
  $("#prev-btn").disabled = !state.hasPrev;
  $("#next-btn").disabled = !state.hasNext;
  const pct = state.total > 0 ? ((state.currentIndex + 1) / state.total) * 100 : 0;
  $("#progress-bar").style.width = `${pct}%`;
}

export function showQuiz(show) {
  $("#welcome-screen").style.display = show ? "none" : "";
  $("#quiz-area").style.display = show ? "" : "none";
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
}

export function renderBankList(banks) {
  const list = $("#bank-list");
  list.innerHTML = "";
  if (banks.length === 0) {
    list.innerHTML = `<p class="empty-hint" data-i18n="no_banks">${t("no_banks")}</p>`;
    return;
  }
  banks.forEach((bank) => {
    const div = document.createElement("div");
    div.className = "bank-item";
    div.textContent = bank.title || bank.path;
    div.dataset.path = bank.path;
    list.appendChild(div);
  });
}
