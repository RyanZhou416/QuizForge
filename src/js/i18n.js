const translations = {
  zh: {
    banks: "题库列表", no_banks: "尚未加载题库", open_bank: "打开题库文件", open_folder: "打开题库文件夹",
    folder_loaded: "已加载 {n} 个题库",
    filters: "筛选", topic_label: "主题", type_label: "题型", diff_label: "难度",
    all: "全部", single: "单选", multiple: "多选", truefalse: "判断",
    easy: "简单", medium: "中等", hard: "困难",
    shuffle: "随机顺序", stats: "统计",
    answered: "已答", correct_rate: "正确率", history_rate: "历史正确率",
    drop_hint: "拖入 .db 题库文件，或点击下方按钮打开",
    submit: "提交", prev: "上一题", next: "下一题",
    explanation: "解析",
    q_single: "单选", q_multiple: "多选（可多选）", q_truefalse: "判断",
    true_opt: "正确", false_opt: "错误",
    search_placeholder: "搜索题目...",
    question_nav: "题目导航",
    reset_progress: "重置进度",
    reset_confirm: "确定要重置所有进度吗？此操作不可撤销。",
    reset_done: "进度已重置",
    bank_opened: "题库已加载",
    file_error: "文件格式错误，请选择 .db 文件",
    view_summary: "查看总结",
    summary_title: "答题总结",
    total_questions: "总题数",
    answered_count: "已答题数",
    correct_count: "答对题数",
    accuracy: "正确率",
    by_type: "按题型统计",
    wrong_questions: "错题列表",
    retry: "重新做题",
    back_to_quiz: "返回做题",
    no_wrong: "全部正确，太棒了！",
    exam_mode: "考试模式",
    exam_setup: "考试设置",
    exam_count: "题目数量",
    exam_time: "时间限制（分钟，0 = 不限时）",
    exam_topic: "主题筛选",
    exam_difficulty: "难度筛选",
    cancel: "取消",
    start_exam: "开始考试",
    exam_end: "考试结束",
    exam_score: "得分",
    exam_time_used: "用时",
    exam_passed: "通过",
    exam_failed: "未通过",
    exam_auto_submit: "时间到，已自动交卷",
    exam_not_enough: "符合条件的题目不足",
    exam_finish: "交卷",
    minutes: "分钟",
    seconds: "秒",
  },
  en: {
    banks: "Question Banks", no_banks: "No bank loaded", open_bank: "Open .db File", open_folder: "Open Quiz Folder",
    folder_loaded: "{n} banks loaded",
    filters: "Filters", topic_label: "Topic", type_label: "Type", diff_label: "Difficulty",
    all: "All", single: "Single", multiple: "Multiple", truefalse: "True/False",
    easy: "Easy", medium: "Medium", hard: "Hard",
    shuffle: "Shuffle", stats: "Statistics",
    answered: "Answered", correct_rate: "Accuracy", history_rate: "Historical Accuracy",
    drop_hint: "Drag & drop a .db quiz bank file, or click below",
    submit: "Submit", prev: "Previous", next: "Next",
    explanation: "Explanation",
    q_single: "Single Choice", q_multiple: "Multiple Choice", q_truefalse: "True / False",
    true_opt: "True", false_opt: "False",
    search_placeholder: "Search questions...",
    question_nav: "Question Nav",
    reset_progress: "Reset Progress",
    reset_confirm: "Reset all progress? This cannot be undone.",
    reset_done: "Progress reset",
    bank_opened: "Bank loaded",
    file_error: "Invalid file format. Please select a .db file",
    view_summary: "View Summary",
    summary_title: "Quiz Summary",
    total_questions: "Total",
    answered_count: "Answered",
    correct_count: "Correct",
    accuracy: "Accuracy",
    by_type: "By Type",
    wrong_questions: "Wrong Answers",
    retry: "Retry All",
    back_to_quiz: "Back to Quiz",
    no_wrong: "All correct, great job!",
    exam_mode: "Exam Mode",
    exam_setup: "Exam Setup",
    exam_count: "Number of Questions",
    exam_time: "Time Limit (minutes, 0 = unlimited)",
    exam_topic: "Topic Filter",
    exam_difficulty: "Difficulty Filter",
    cancel: "Cancel",
    start_exam: "Start Exam",
    exam_end: "Exam Complete",
    exam_score: "Score",
    exam_time_used: "Time Used",
    exam_passed: "Passed",
    exam_failed: "Failed",
    exam_auto_submit: "Time is up. Auto-submitted.",
    exam_not_enough: "Not enough questions matching filters",
    exam_finish: "Finish Exam",
    minutes: "min",
    seconds: "sec",
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
  document.querySelectorAll("[data-i18n-placeholder]").forEach((el) => {
    el.placeholder = t(el.getAttribute("data-i18n-placeholder"));
  });
}

export function localizedText(obj) {
  if (!obj) return "";
  if (typeof obj === "string") return obj;
  return obj[currentLang] || obj.zh || obj.en || "";
}
