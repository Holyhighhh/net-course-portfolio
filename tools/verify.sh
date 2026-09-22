#!/bin/bash
# net-course-portfolio 结构与发布态验证入口。
# 引擎为 tools/verify.py（Python 3.9+，仅标准库）；本脚本只负责定位解释器并转发参数。
#
# 用法：
#   tools/verify.sh                     # 全部检查
#   tools/verify.sh --residue all       # 追加按版本的新旧措辞双向检查
#   tools/verify.sh --flex-sum          # 只校验 TCP 头部『偏移 12』行 flex 求和
#   tools/verify.sh --only struct       # 只跑结构类
#
# 退出码：0 全部通过（WARN 不算失败） / 1 存在 FAIL / 2 用法或环境错误

set -uo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

PY="${VERIFY_PY:-}"
if [ -z "$PY" ]; then
  for cand in /usr/bin/python3 python3; do
    if command -v "$cand" >/dev/null 2>&1; then PY="$cand"; break; fi
  done
fi

if [ -z "$PY" ]; then
  echo "错误：找不到可用的 python3（可用环境变量 VERIFY_PY 指定）" >&2
  exit 2
fi

exec "$PY" "$DIR/verify.py" "$@"
