"""check_encoding_convention.py：符号化規約整合検証スクリプト（foundation T-008）。

design.md §4「mandatory／deferred の JSON Schema 符号化規約」に各スキーマが準拠するかを
機械的に検証する。読み取り専用の検証器であり、ファイル書き込みの副作用はない（topic-07 F-010）。

符号化規約（design.md §4）：
- mandatory 項目は `required` 配列に列挙する（mandatory を表現する配列が存在すること）
- deferred 拡張点は `required` に列挙せず、`description` に明記し、最上位に `x-deferred` 注記
  （先送り対象と委譲先を文章で示す）を置く
- 検証器側契約は `x-deferred` の代替として専用注記キー（例 `x-staleness-propagation`）を
  用いてよい。その場合も委譲先を文章で示す義務は変わらない

使い方：
  python3 check_encoding_convention.py <schema1.json> [<schema2.json> ...]
  exit 0：全スキーマ準拠／非ゼロ：違反あり（stderr に詳細）
"""
import json
import sys

# x-deferred の代替として許容される専用注記キー（design.md §4）
DEFERRED_ALIAS_KEYS = ["x-deferred", "x-staleness-propagation"]


def _check_nested_required(node, path, errors):
  """入れ子の object・配列 items を再帰し、properties を持つ object の各階層に required が
  あるかを検査する（design.md §4 行311：最上位の required のみで入れ子内部を代表させない）。

  properties を持たない object（保持方法を runtime に委ねる空 object 等）は mandatory 項目が
  ないため required を要求しない。
  """
  if not isinstance(node, dict):
    return
  props = node.get("properties")
  if isinstance(props, dict) and props:
    if "required" not in node:
      errors.append(f"{path}: properties を持つが required がない（入れ子階層の mandatory 未表現）")
    for key, sub in props.items():
      _check_nested_required(sub, f"{path}.{key}", errors)
  items = node.get("items")
  if isinstance(items, dict):
    _check_nested_required(items, f"{path}[items]", errors)


def check_schema_encoding(schema):
  """1 スキーマが符号化規約に準拠するか検査し、違反のエラーリストを返す（空なら準拠）。"""
  errors = []

  # ルール 1：最上位に required 配列が存在する（mandatory を表現）
  if "required" not in schema:
    errors.append("required 配列が存在しない（mandatory 項目を表現できない）")
  elif not isinstance(schema["required"], list):
    errors.append("required が配列でない")

  # ルール 2：deferred 注記（x-deferred または代替キー）がある場合の妥当性
  present_deferred_keys = [k for k in DEFERRED_ALIAS_KEYS if k in schema]
  for key in present_deferred_keys:
    value = schema.get(key)
    if not isinstance(value, str) or not value.strip():
      errors.append(f"{key} が非空の文字列でない（委譲先を文章で示す義務）")
    # deferred を宣言するスキーマは description で deferred 旨を明記する規約
    desc = schema.get("description")
    if not isinstance(desc, str) or not desc.strip():
      errors.append(f"{key} があるが description が欠落（deferred 旨の明記義務）")

  # ルール 3：入れ子 object・配列 items 内の各階層でも required を表現する（P-002 対処、§4 行311）
  props = schema.get("properties")
  if isinstance(props, dict):
    for key, sub in props.items():
      _check_nested_required(sub, f"properties.{key}", errors)
  items = schema.get("items")
  if isinstance(items, dict):
    _check_nested_required(items, "items", errors)

  return errors


def main(argv):
  """スキーマファイル群を検査する。全準拠なら 0、違反があれば非ゼロを返す。"""
  if not argv:
    print("使い方：check_encoding_convention.py <schema.json> ...", file=sys.stderr)
    return 2

  total_errors = 0
  for path in argv:
    try:
      with open(path, encoding="utf-8") as f:
        schema = json.load(f)
    except (OSError, json.JSONDecodeError) as exc:
      print(f"[ERROR] {path}：読み込み／解析に失敗：{exc}", file=sys.stderr)
      total_errors += 1
      continue

    errors = check_schema_encoding(schema)
    if errors:
      total_errors += len(errors)
      for e in errors:
        print(f"[VIOLATION] {path}：{e}", file=sys.stderr)
    else:
      print(f"[OK] {path}")

  return 0 if total_errors == 0 else 1


if __name__ == "__main__":
  sys.exit(main(sys.argv[1:]))
