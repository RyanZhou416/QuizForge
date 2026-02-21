const translations = {
  zh: {
    banks: "题库列表", no_banks: "尚未加载题库", open_bank: "打开题库文件",
    filters: "筛选", topic_label: "主题", type_label: "题型", diff_label: "难度",
    all: "全部", single: "单选", multiple: "多选", truefalse: "判断",
    easy: "简单", medium: "中等", hard: "困难",
    shuffle: "随机顺序", stats: "统计",
    answered: "已答", correct_rate: "正确率",
    drop_hint: "拖入 .db 题库文件，或点击下方按钮打开",
    submit: "提交", prev: "上一题", next: "下一题",
    explanation: "解析",
    q_single: "单选", q_multiple: "多选（可多选）", q_truefalse: "判断",
    true_opt: "正确", false_opt: "错误",
  },
  en: {
    banks: "Question Banks", no_banks: "No bank loaded", open_bank: "Open .db File",
    filters: "Filters", topic_label: "Topic", type_label: "Type", diff_label: "Difficulty",
    all: "All", single: "Single", multiple: "Multiple", truefalse: "True/False",
    easy: "Easy", medium: "Medium", hard: "Hard",
    shuffle: "Shuffle", stats: "Statistics",
    answered: "Answered", correct_rate: "Accuracy",
    drop_hint: "Drag & drop a .db quiz bank file, or click below",
    submit: "Submit", prev: "Previous", next: "Next",
    explanation: "Explanation",
    q_single: "Single Choice", q_multiple: "Multiple Choice", q_truefalse: "True / False",
    true_opt: "True", false_opt: "False",
  },
};

let currentLang = localStorage.getItem("qf_lang") || "zh";

export function getLang() { return currentLang; }

export function setLang(lang) {
  currentLang = lang;
  localStorage.setItem("qf_lang", lang);
  applyI18n();
}

export function toggleLang() {
  setLang(currentLang === "zh" ? "en" : "zh");
  return currentLang;
}

export function t(key) {
  return translations[currentLang]?.[key] ?? translations.zh[key] ?? key;
}

export function applyI18n() {
  document.querySelectorAll("[data-i18n]").forEach((el) => {
    const key = el.getAttribute("data-i18n");
    if (el.tagName === "OPTION") el.textContent = t(key);
    else if (el.tagName === "INPUT") el.placeholder = t(key);
    else el.textContent = t(key);
  });
}

export function localizedText(obj) {
  if (!obj) return "";
  if (typeof obj === "string") return obj;
  return obj[currentLang] || obj.zh || obj.en || "";
}
