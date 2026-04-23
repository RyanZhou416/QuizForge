#!/usr/bin/env python3
"""
题库平衡性诊断脚本
检查：
  1. 单选题正确答案在 ABCD 上的位置分布
  2. 单选/多选题"三短一长 / 三长一短"——正确选项是不是显著比错误选项长（中文）
  3. 每题内部正确答案是否唯一的最长/最短选项（这种题用排除法可以秒杀）
  4. 正确答案选项前缀是否与错误选项明显不同（如以"以下"、"上述"打头）
  5. 多选题正确答案的数量分布
"""
import json, sys, statistics
from collections import Counter

QUIZ = sys.argv[1] if len(sys.argv) > 1 else "4月12资料1-quiz.json"

with open(QUIZ, "r", encoding="utf-8") as f:
    data = json.load(f)

questions = data["questions"]

single_qs = [q for q in questions if q["type"] == "single"]
multi_qs = [q for q in questions if q["type"] == "multiple"]
tf_qs = [q for q in questions if q["type"] == "truefalse"]

print(f"=== 题库总览 ===")
print(f"总题数: {len(questions)}  | single: {len(single_qs)}  multiple: {len(multi_qs)}  truefalse: {len(tf_qs)}")
print()

# 1. 单选题正确答案位置分布
print("=== 1. 单选题正确答案 ABCD 分布 ===")
pos_counter = Counter()
for q in single_qs:
    for o in q["options"]:
        if o["is_correct"]:
            pos_counter[o["label"]] += 1
total_single = len(single_qs)
for label in "ABCD":
    cnt = pos_counter.get(label, 0)
    pct = cnt / total_single * 100 if total_single else 0
    bar = "█" * cnt
    print(f"  {label}: {cnt:2d} ({pct:5.1f}%) {bar}")
ideal = total_single / 4
max_dev = max(abs(pos_counter.get(l, 0) - ideal) for l in "ABCD")
print(f"  理想均匀分布每格 ≈ {ideal:.1f}；最大偏离 = {max_dev:.1f}")
print()

# 2. 长度倾向 - 整库统计：正确选项 vs 错误选项的中文字符长度
print("=== 2. 中文长度倾向（正确 vs 错误）===")
correct_lens, wrong_lens = [], []
for q in single_qs + multi_qs:
    for o in q["options"]:
        L = len(o["text_zh"])
        (correct_lens if o["is_correct"] else wrong_lens).append(L)
print(f"  正确选项: n={len(correct_lens)}, 均值={statistics.mean(correct_lens):.1f}, "
      f"中位数={statistics.median(correct_lens):.1f}, std={statistics.pstdev(correct_lens):.1f}")
print(f"  错误选项: n={len(wrong_lens)}, 均值={statistics.mean(wrong_lens):.1f}, "
      f"中位数={statistics.median(wrong_lens):.1f}, std={statistics.pstdev(wrong_lens):.1f}")
diff = statistics.mean(correct_lens) - statistics.mean(wrong_lens)
print(f"  正确-错误均值差 = {diff:+.1f} 字  "
      f"({'⚠️ 正确显著更长（三短一长）' if diff > 5 else '⚠️ 正确显著更短（三长一短）' if diff < -5 else '✅ 在合理范围内'})")
print()

# 3. 单题级别：正确选项是否是该题中"唯一最长"或"唯一最短"
print("=== 3. 单题级别：正确选项是否唯一最长/最短（仅 single）===")
uniq_longest, uniq_shortest, neutral = [], [], []
for idx, q in enumerate(single_qs, 1):
    lens = [(o["label"], len(o["text_zh"]), o["is_correct"]) for o in q["options"]]
    lens_sorted = sorted(lens, key=lambda x: x[1])
    correct = [x for x in lens if x[2]][0]
    other_lens = [x[1] for x in lens if not x[2]]
    is_uniq_longest = correct[1] > max(other_lens)
    is_uniq_shortest = correct[1] < min(other_lens)
    label = f"Q{idx} ({correct[0]}) 长度{correct[1]} 其他{other_lens}"
    if is_uniq_longest:
        uniq_longest.append(label)
    elif is_uniq_shortest:
        uniq_shortest.append(label)
    else:
        neutral.append(label)
print(f"  正确选项是【唯一最长】: {len(uniq_longest)}/{len(single_qs)} 题  ({len(uniq_longest)/len(single_qs)*100:.1f}%)")
for s in uniq_longest:
    print(f"    ⚠️ {s}")
print(f"  正确选项是【唯一最短】: {len(uniq_shortest)}/{len(single_qs)} 题  ({len(uniq_shortest)/len(single_qs)*100:.1f}%)")
for s in uniq_shortest:
    print(f"    ⚠️ {s}")
print(f"  其他（不极端）: {len(neutral)}/{len(single_qs)} 题")
print()

# 4. 正确选项 vs 错误选项首字符模式（看是否常以特殊词打头）
print("=== 4. 正确选项中文首字符 vs 错误选项首字符 ===")
correct_starts = Counter(o["text_zh"][:2] for q in single_qs for o in q["options"] if o["is_correct"])
wrong_starts = Counter(o["text_zh"][:2] for q in single_qs for o in q["options"] if not o["is_correct"])
print("  正确选项首2字 top 5:")
for s, c in correct_starts.most_common(5):
    print(f"    '{s}' × {c}")
print("  错误选项首2字 top 5:")
for s, c in wrong_starts.most_common(5):
    print(f"    '{s}' × {c}")
print()

# 5. 多选题正确数量分布
print("=== 5. 多选题正确选项数量分布 ===")
mult_correct_counts = Counter()
for q in multi_qs:
    n = sum(1 for o in q["options"] if o["is_correct"])
    mult_correct_counts[n] += 1
for n, c in sorted(mult_correct_counts.items()):
    print(f"  正确数={n}: {c} 题")
print()

# 6. 极端值题目明细（按正确-平均错误长度差排序）
print("=== 6. 单选题：每题正确选项与错误选项平均长度差（>+5 或 <-5 视为风险）===")
risks = []
for idx, q in enumerate(single_qs, 1):
    correct_len = next(len(o["text_zh"]) for o in q["options"] if o["is_correct"])
    wrong_mean = statistics.mean(len(o["text_zh"]) for o in q["options"] if not o["is_correct"])
    delta = correct_len - wrong_mean
    risks.append((delta, idx, q["question_zh"][:40], correct_len, wrong_mean))
risks.sort(key=lambda x: -abs(x[0]))
for delta, idx, q_text, cl, wm in risks[:8]:
    flag = "⚠️" if abs(delta) > 5 else "  "
    print(f"  {flag} Q{idx}: Δ={delta:+.1f} (正确{cl} vs 错误均{wm:.1f}) | {q_text}...")
