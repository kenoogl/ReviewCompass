"""T-011 のテスト：要件追跡の双方向整合（作業単位の厳密検査）。

対応タスク：runtime tasks.md T-011
対応設計節：design.md §要件と設計の対応
対応要件：各 Requirement の機械判定可能な完了条件の網羅（要件追跡の双方向整合）

tasks.md の要件追跡表（要件→タスク）と各タスク本文の対応要件欄（タスク→要件）を、
作業単位で完全な逆対応として突き合わせる（緩い番号ベースだけでなく、表の各マス ⇔
各タスク本文を照合する）。foundation T-010 同型の集合ベース検査も併せて行う。
"""
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
TASKS_MD = REPO_ROOT / ".reviewcompass/specs/runtime/tasks.md"

# 集合ベース検査は本ファイル内で自前実装し、foundation ツールへの直接 import 依存を避ける
# （P-008 対処、2026-06-02）。作業単位の厳密検査は test_per_task_traceability_consistent が担う。


def _norm_task(num):
  return f"T-{int(num):03d}"


def parse_table(text):
  """§要件追跡表を解析して 要件番号 → タスク集合 を返す。"""
  marker = "## 要件追跡"
  table = text.split(marker, 1)[1]
  result = {}
  for line in table.splitlines():
    m = re.match(r"\|\s*Requirement\s*(\d+)[：:]", line)
    if not m:
      continue
    req = int(m.group(1))
    tasks = {_norm_task(n) for n in re.findall(r"T-(\d+)", line)}
    result[req] = tasks
  return result


def parse_bodies(text):
  """各タスク本文の対応要件欄を解析して タスク → 要件番号集合 を返す。"""
  body = text.split("## 要件追跡", 1)[0]
  result = {}
  current = None
  for line in body.splitlines():
    h = re.match(r"###\s*(T-\d+)", line)
    if h:
      current = h.group(1)
      continue
    # 太字フィールド「**対応要件**」の行だけを拾う（責務行などの散文中の
    # 「対応要件欄」という語句に誤反応しないようフィールド見出しで限定する）。
    if current and "**対応要件**" in line:
      reqs = {int(n) for n in re.findall(r"Requirement\s*(\d+)", line)}
      result[current] = reqs
  return result


def _invert_bodies(bodies):
  """タスク→要件集合 を 要件→タスク集合 に反転する。"""
  inv = {}
  for task, reqs in bodies.items():
    for r in reqs:
      inv.setdefault(r, set()).add(task)
  return inv


def test_tasks_md_exists():
  assert TASKS_MD.is_file()


def test_set_based_traceability_consistent():
  """集合ベース（要件番号の有無）の双方向整合。foundation ツール非依存の自前実装（P-008）。"""
  text = TASKS_MD.read_text(encoding="utf-8")
  table_reqs = set(parse_table(text))
  body_reqs = set(_invert_bodies(parse_bodies(text)))
  missing_in_body = table_reqs - body_reqs
  missing_in_table = body_reqs - table_reqs
  assert not missing_in_body and not missing_in_table, (
    f"集合ベースの双方向整合違反：表のみ={sorted(missing_in_body)} 本文のみ={sorted(missing_in_table)}"
  )


def test_per_task_traceability_consistent():
  """作業単位（表の各マス ⇔ 各タスク本文）の厳密な双方向整合。"""
  text = TASKS_MD.read_text(encoding="utf-8")
  table = parse_table(text)
  inv_bodies = _invert_bodies(parse_bodies(text))

  reqs = set(table) | set(inv_bodies)
  errors = []
  for r in sorted(reqs):
    in_table = table.get(r, set())
    in_body = inv_bodies.get(r, set())
    body_only = in_body - in_table
    table_only = in_table - in_body
    if body_only:
      errors.append(f"要件{r}：本文は担うが表に無い {sorted(body_only)}")
    if table_only:
      errors.append(f"要件{r}：表は担うとするが本文に無い {sorted(table_only)}")
  assert errors == [], "作業単位の双方向整合違反：\n" + "\n".join(errors)


def test_all_10_requirements_covered():
  """要件 1〜10 すべてが追跡表とタスク本文の双方に現れる。"""
  text = TASKS_MD.read_text(encoding="utf-8")
  table = parse_table(text)
  body_reqs = set()
  for reqs in parse_bodies(text).values():
    body_reqs |= reqs
  assert set(table.keys()) == set(range(1, 11)), f"追跡表の要件が 1〜10 でない：{sorted(table)}"
  assert set(range(1, 11)) <= body_reqs, f"本文に現れない要件：{sorted(set(range(1, 11)) - body_reqs)}"
