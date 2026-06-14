"""追記専用マージ：既存記録と新生成の包含関係を判定する。

session-record の取り込み（backfill / --session）は出力を毎回丸ごと書き直すが、
元ログ（jsonl）が何らかの理由で縮んだ場合に取り込み済み記録を失わないよう、
書き込み前に「消さずに足す（追記専用）」かどうかを判定する。

判定は層 1（整形済み転写）の本文（front-matter を除く）の行を順序保存で比較する：
  same   : 本文が一致 → 書き込みを起こさない
  extend : 旧本文が新本文の部分列（増えただけ）→ 更新する
  shrink : 旧本文の行が新本文に順序保存で含まれない（消える方向）→ 保全する

層 2（人が読む記録）は同一の元ログから生成されるため、層 1 が拡張なら層 2 も
情報を失わない。よって層 1 の判定に層 1・層 2 双方の書き込み／保全を従わせる
（層 2 の「（なし）→実データ」の空欄置換を縮小と誤判定しないため）。
"""
from .provenance import split_front_matter


def is_subsequence(small, big):
  """small の各要素が big に順序を保って現れるか（部分列か）を返す。"""
  it = iter(big)
  return all(item in it for item in small)


def classify_update(existing_text, new_text):
  """既存記録 existing_text に対し、新生成 new_text が same / extend / shrink の
  どれかを返す。front-matter（来歴）は毎回変わるため本文だけで比較する。
  """
  _, old_body = split_front_matter(existing_text)
  _, new_body = split_front_matter(new_text)
  if old_body == new_body:
    return "same"
  if is_subsequence(old_body.split("\n"), new_body.split("\n")):
    return "extend"
  return "shrink"
