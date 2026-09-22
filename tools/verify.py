#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""net-course-portfolio 结构与发布态验证引擎。

设计约束（见 docs/development.md · 质量流程）：
  - 结构四件套：div 开闭相等、pre 开闭相等、课时页数、侧边栏状态标记数
  - 新访客零态：落地页 / 状态标记 / 进度文本 / 进度条宽度
  - 版本号多处同值
  - 新旧措辞双向 grep（声明式规则表，按版本）

兼容 Python 3.9（macOS 自带 /usr/bin/python3），仅用标准库。
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "index.html"
README = ROOT / "README.md"
CHANGELOG = ROOT / "CHANGELOG.md"
DEVELOPMENT = ROOT / "docs" / "development.md"

# ---- 断言常量：结构不变量（改动课程本体后若这些数变了，先确认是否预期）----
EXPECT_DIV = 3259
EXPECT_PRE = 71
EXPECT_LESSONS = 31
EXPECT_NAV_STATUS = 30
EXPECT_SECTIONS = 216
EXPECT_SECTION_DIST = {"0": 6, "1": 8, "2": 8, "30": 5}  # 其余课时为 DEFAULT_SECTIONS
DEFAULT_SECTIONS = 7
EXPECT_FLEX_SUM = 32

PASS, FAIL, WARN, SKIP = "PASS", "FAIL", "WARN", "SKIP"

results = []


def record(cid, name, status, detail):
    results.append({"id": cid, "name": name, "status": status, "detail": detail})
    return status


def read_or_skip(path):
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8")


def strip_scripts_styles_comments(html):
    """剥掉 script/style/注释，供标签栈配对使用（这些区域含裸 < > 会污染配对）。"""
    out = re.sub(r"<script\b[\s\S]*?</script>", "", html, flags=re.I)
    out = re.sub(r"<style\b[\s\S]*?</style>", "", out, flags=re.I)
    out = re.sub(r"<!--[\s\S]*?-->", "", out)
    return out


def iter_tags(text):
    """按引号感知方式扫描标签，产出 (is_close, tag_name)。"""
    i, n = 0, len(text)
    while i < n:
        lt = text.find("<", i)
        if lt < 0:
            return
        j = lt + 1
        in_single = in_double = False
        while j < n:
            ch = text[j]
            if in_single:
                if ch == "'":
                    in_single = False
            elif in_double:
                if ch == '"':
                    in_double = False
            elif ch == "'":
                in_single = True
            elif ch == '"':
                in_double = True
            elif ch == ">":
                break
            j += 1
        if j >= n:
            return
        raw = text[lt + 1:j]
        i = j + 1
        if not raw or raw[0] in "!?/ " and not raw.startswith("/"):
            continue
        is_close = raw.startswith("/")
        name = raw[1:] if is_close else raw
        name = name.strip().split()[0].split("/")[0].lower() if name.strip() else ""
        if name:
            yield is_close, name


# ---------------- 结构检查 ----------------

def check_struct():
    html = INDEX.read_text(encoding="utf-8")

    n_open = len(re.findall(r"<div[\s>]", html))
    n_close = len(re.findall(r"</div>", html))
    ok = n_open == n_close == EXPECT_DIV
    record("S1", "div 开闭平衡", PASS if ok else FAIL,
           "%d / %d（期望 %d / %d）" % (n_open, n_close, EXPECT_DIV, EXPECT_DIV))

    p_open = len(re.findall(r"<pre[\s>]", html))
    p_close = len(re.findall(r"</pre>", html))
    ok = p_open == p_close == EXPECT_PRE
    record("S2", "pre 开闭平衡", PASS if ok else FAIL,
           "%d / %d（期望 %d / %d）" % (p_open, p_close, EXPECT_PRE, EXPECT_PRE))

    track = ["div", "pre", "span", "h2", "table", "ul", "li", "a", "p", "aside", "code"]
    depth = {t: 0 for t in track}
    bad = None
    for is_close, name in iter_tags(strip_scripts_styles_comments(html)):
        if name not in depth:
            continue
        if is_close:
            depth[name] -= 1
            if depth[name] < 0 and bad is None:
                bad = "出现多余的 </%s>" % name
        else:
            depth[name] += 1
    if bad is None:
        leftover = {k: v for k, v in depth.items() if v != 0}
        if leftover:
            bad = "未闭合：%s" % ", ".join("%s×%d" % (k, v) for k, v in sorted(leftover.items()))
    record("S3", "标签栈配对", PASS if bad is None else FAIL, bad or "全部标签深度归零")

    ids = sorted(int(m) for m in re.findall(r'id="lesson-(\d+)"', html))
    ok = len(ids) == EXPECT_LESSONS and ids == list(range(EXPECT_LESSONS))
    record("S4", "课时页数", PASS if ok else FAIL,
           "%d 个（%s）" % (len(ids), "0..%d 连续" % (EXPECT_LESSONS - 1) if ok else "编号不连续"))

    nav = len(re.findall(r'class="nav-status', html))
    record("S5", "侧边栏状态标记", PASS if nav == EXPECT_NAV_STATUS else FAIL,
           "%d 个（期望 %d）" % (nav, EXPECT_NAV_STATUS))

    total = len(re.findall(r'<div class="section"', html))
    record("S7", "section 总数 == h2 总数",
           PASS if total == EXPECT_SECTIONS and len(re.findall(r"<h2[\s>]", html)) == EXPECT_SECTIONS else FAIL,
           "section %d / h2 %d（期望各 %d）" % (total, len(re.findall(r"<h2[\s>]", html)), EXPECT_SECTIONS))

    # 逐课时 section 分布
    anchors = [(int(m.group(1)), m.start()) for m in re.finditer(r'<div class="lesson-page[^"]*" id="lesson-(\d+)"', html)]
    anchors.sort(key=lambda x: x[1])
    end = html.find("<!-- end main -->")
    if end < 0:
        end = len(html)
    dist = {}
    for idx, (num, pos) in enumerate(anchors):
        stop = anchors[idx + 1][1] if idx + 1 < len(anchors) else end
        dist[num] = len(re.findall(r'<div class="section"', html[pos:stop]))
    wrong = []
    for num, cnt in dist.items():
        exp = EXPECT_SECTION_DIST.get(str(num), DEFAULT_SECTIONS)
        if cnt != exp:
            wrong.append("lesson-%d=%d(期望%d)" % (num, cnt, exp))
    record("S6", "逐课时 section 分布", PASS if not wrong else FAIL,
           " ".join(wrong) if wrong else "%d 个课时全部符合分布" % len(dist))


# ---------------- 零态检查 ----------------

def check_zero_state():
    html = INDEX.read_text(encoding="utf-8")

    done = len(re.findall(r'data-status="done"', html))
    record("Z1", '无 data-status="done"', PASS if done == 0 else FAIL, "%d 处（期望 0）" % done)

    m = re.search(r'<div class="progress-text">(.*?)</div>', html, re.S)
    got = m.group(1).strip() if m else "(未找到 .progress-text)"
    want = "进度: 0 / 30 课时 · 点击状态图标可手动标记"
    record("Z2", "进度文本为零态", PASS if got == want else FAIL,
           "实际=%r 期望=%r" % (got, want))

    m = re.search(r'<div class="progress-fill"\s+style="([^"]*)"', html)
    got = m.group(1).strip().rstrip(";") if m else "(未找到 .progress-fill)"
    record("Z3", "进度条宽度为零态", PASS if got == "width:0%" else FAIL,
           "实际=%r 期望='width:0%%'" % got)

    leftovers = []
    for kw in ("3 / 11", "27.3%"):
        c = html.count(kw)
        if c:
            leftovers.append("%s ×%d" % (kw, c))
    record("Z4", "无开发态遗留串", PASS if not leftovers else FAIL,
           " ".join(leftovers) if leftovers else "『3 / 11』『27.3%』均零命中")

    act = re.findall(r'<div class="lesson-page active" id="lesson-(\d+)"', html)
    nav = re.findall(r'<a class="nav-item active"[^>]*data-lesson="(\d+)"', html)
    ok = act == ["0"] and nav == ["0"]
    record("Z5", "落地页为课时 01", PASS if ok else FAIL,
           "lesson-page active=%s, nav-item active=%s（期望均为 ['0']）" % (act or "无", nav or "无"))


# ---------------- 版本号一致性 ----------------

def _grab(pattern, text, flags=0):
    m = re.search(pattern, text, flags)
    return m.group(1) if m else None


def collect_versions():
    """返回 [(位置, 版本号或 None)]，None 表示该处未找到（属结构性缺失）。"""
    out = []
    html = read_or_skip(INDEX) or ""
    rd = read_or_skip(README) or ""
    ch = read_or_skip(CHANGELOG) or ""
    dv = read_or_skip(DEVELOPMENT) or ""

    out.append(("index.html 头部注释", _grab(r"<!--\s*课程版本\s*(v\d+\.\d+)", html)))
    out.append(("index.html 侧边栏页脚", _grab(r">\s*课程版本\s*(v\d+\.\d+)\s*<br>", html)))
    out.append(("README 仓库结构", _grab(r"课程本体（当前版本\s*(v\d+\.\d+)）", rd)))
    out.append(("README 版本区间", _grab(r"每个版本（v\d+\.\d+\s*→\s*(v\d+\.\d+)）", rd)))
    out.append(("CHANGELOG 当前版本", _grab(r"当前版本：\*\*(v\d+\.\d+)\*\*", ch)))

    m = re.findall(r"^\|\s*(v\d+\.\d+)\s*\|", ch, re.M)
    out.append(("CHANGELOG 总览末行", m[-1] if m else None))

    m = re.findall(r"^\|\s*(v\d+\.\d+)\s*\|", dv, re.M)
    out.append(("development.md 版本表末行", m[-1] if m else None))
    return out


def check_versions():
    pairs = collect_versions()
    missing = [p for p, v in pairs if not v]
    values = sorted(set(v for _, v in pairs if v))
    if missing:
        record("V1", "版本号多处同值", FAIL, "未找到：%s" % ", ".join(missing))
        return
    if len(values) == 1:
        record("V1", "版本号多处同值", PASS, "%s ×%d 处" % (values[0], len(pairs)))
    else:
        detail = "；".join("%s=%s" % (p, v) for p, v in pairs)
        record("V1", "版本号多处同值", FAIL, "不一致 → " + detail)


# ---------------- 残留双向检查 ----------------

RESIDUE = {
    "v1.5": {
        "require": [
            ("index.html", "课程版本 v1.5"),
            ("index.html", "<div class=\"nav-section-title\">阶段 1 · 学习诊断与环境准备"),
            ("index.html", "阶段 9 · 综合项目与考核"),
        ],
        "forbid": [
            ("index.html", "阶段 0"),
            ("index.html", "课程版本 v1.4"),
            ("README.md", "阶段 0"),
            ("docs/sources.md", "阶段 4–7"),
            ("docs/course-plan.md", "阶段 0"),
        ],
    },
    "v1.6": {
        "require": [
            ("index.html", '保留<br><small>4</small>'),
            ("index.html", "CWR / ECE"),
            ("index.html", "关于 NS 位"),
            ("index.html", "进度: 0 / 30 课时"),
            ("index.html", 'style="width:0%"'),
            ("README.md", "课时 11 Socket 聊天室"),
        ],
        "forbid": [
            ("index.html", '保留<br><small>3</small>'),
            ("index.html", ">N</div>"),
            ("index.html", "NS / CWR / ECE"),
            ("index.html", "进度: 3 / 11"),
            ("index.html", "27.3%"),
            ("README.md", "含 9 个标志位"),
            ("README.md", "故障考试"),
        ],
    },
    "all": None,  # 运行时展开为全部键
}


def check_residue(ver):
    if ver == "all":
        keys = [k for k in RESIDUE if k != "all"]
    else:
        keys = [ver]
    for k in keys:
        spec = RESIDUE.get(k)
        if spec is None:
            record("R:" + k, "残留检查 %s" % k, FAIL, "未知版本规则（可用：%s）" %
                   ", ".join(sorted(x for x in RESIDUE if x != "all")))
            continue
        bad, good = [], []
        for rel, kw in spec["require"]:
            p = ROOT / rel
            if not p.exists() or kw not in p.read_text(encoding="utf-8"):
                bad.append("缺『%s』@%s" % (kw, rel))
            else:
                good.append(kw)
        for rel, kw in spec["forbid"]:
            p = ROOT / rel
            if p.exists() and kw in p.read_text(encoding="utf-8"):
                bad.append("残留『%s』@%s" % (kw, rel))
        record("R:" + k, "残留检查 %s" % k, PASS if not bad else FAIL,
               "；".join(bad) if bad else "新措辞 %d 项齐备、旧措辞零残留" % len(good))


# ---------------- TCP 头部 flex 求和 ----------------

def check_flex_sum():
    html = INDEX.read_text(encoding="utf-8")
    a = html.find("偏移 12")
    b = html.find("偏移 16")
    if a < 0 or b < 0 or b <= a:
        record("F1", "偏移 12 行 flex 求和", FAIL, "未定位到『偏移 12』/『偏移 16』")
        return
    seg = html[a:b]
    vals = [int(x) for x in re.findall(r"flex:(\d+)", seg)]
    total = sum(vals)
    record("F1", "偏移 12 行 flex 求和",
           PASS if total == EXPECT_FLEX_SUM else FAIL,
           "%s = %d（期望 %d）" % (" + ".join(str(v) for v in vals), total, EXPECT_FLEX_SUM))


# ---------------- 主流程 ----------------

def main():
    ap = argparse.ArgumentParser(
        prog="verify.sh",
        description="net-course-portfolio 结构与发布态验证",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="示例：\n  tools/verify.sh\n  tools/verify.sh --residue all\n  tools/verify.sh --flex-sum\n")
    ap.add_argument("--json", action="store_true", help="输出机读 JSON")
    ap.add_argument("--quiet", action="store_true", help="只输出 FAIL / WARN")
    ap.add_argument("--residue", metavar="VER", help="按版本做新旧措辞双向检查（v1.5 / v1.6 / all）")
    ap.add_argument("--flex-sum", action="store_true", help="仅检查 TCP 头部『偏移 12』行的 flex 求和")
    ap.add_argument("--only", choices=["struct", "zero", "version"], help="只跑某一类检查")
    args = ap.parse_args()

    if not INDEX.exists():
        sys.stderr.write("错误：找不到 %s\n" % INDEX)
        return 2

    if args.flex_sum:
        check_flex_sum()
    else:
        run_all = args.only is None
        if run_all or args.only == "struct":
            check_struct()
        if run_all or args.only == "zero":
            check_zero_state()
        if run_all or args.only == "version":
            check_versions()
        if args.residue:
            check_residue(args.residue)

    fails = [r for r in results if r["status"] == FAIL]
    warns = [r for r in results if r["status"] == WARN]
    passes = [r for r in results if r["status"] == PASS]

    if args.json:
        print(json.dumps({"results": results, "summary":
                          {"passed": len(passes), "failed": len(fails), "warnings": len(warns)}},
                         ensure_ascii=False, indent=2))
    else:
        for r in results:
            if args.quiet and r["status"] == PASS:
                continue
            print("[%s] %-4s %s" % (r["status"], r["id"], r["name"]))
            if r["detail"]:
                print("       %s" % r["detail"])
        print("\nSummary: %d passed, %d failed, %d warnings" % (len(passes), len(fails), len(warns)))
        if fails:
            print("未通过：" + ", ".join(r["id"] for r in fails))

    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
