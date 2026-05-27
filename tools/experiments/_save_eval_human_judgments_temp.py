"""evaluation tasks の利用者本人判定 19 件（topic-34〜52）を topic-NN-human.yaml に保存する一時スクリプト。"""
from pathlib import Path

import yaml

RESULTS_DIR = Path(__file__).resolve().parent / "results"

# (topic_num, finding_id, decision, rationale, alt_proposal, case_1, case_2, note)
JUDGMENTS = [
  (34, "F-001", "採用：案 1", "完全一致 13 件の一括採用（多数派採用、議論なし）の 1 件として、議論なしで案 1 採用。全 6 経路が案 1 で完全一致、判定役の暗示推奨と整合。", None, 8, 3,
   "完全一致 13 件の一括採用、議論なしで案 1 採用"),
  (35, "F-002", "採用：案 1", "T-006 のメトリクス計算と版被覆記録の関係が近いので、同じタスクにまとめる発想を採用。タスク数を 11 のまま維持、要件追跡表 Req 5 受入 4／5 を T-006 にも連結。3 対 3 の真っ二つだったが、責務領域の近さと既存タスク数維持を重視。", None, 8, 5,
   "分岐 6 件のうち 1 件目、3 対 3 の真っ二つから案 1 採用"),
  (36, "A-001", "採用：案 1", "完全一致 13 件の一括採用（多数派採用、議論なし）の 1 件として、議論なしで案 1 採用。Gemini-flash は 2 ターン目で案 1 到達、F-002 と一体作業で対処（同根）。", None, 8, 5,
   "完全一致 13 件の一括採用、F-002 と一体作業"),
  (37, "F-003", "別案", "別案（責務主担当制 ＋ 3 列構造）を採用。T-001 から Req 5 受入 2 を縮約 ＋ T-006 を主担当として識別子連結保持の機械検証機構を実装 ＋ T-007 ／ T-009 は依存関係欄に「T-006 機構を前提」と明記 ＋ T-011 双方向整合チェックにも追加 ＋ 要件追跡表に「主担当／利用／検証」の 3 列構造を導入。実装の橋渡しを最重視。",
   "Sonnet API ／ GPT-5.5 の別案（案 1 と案 2 のハイブリッド：T-001 縮約 ＋ T-006 主担当 ＋ T-007／T-009 依存明示 ＋ T-011 追加 ＋ 要件追跡表 3 列構造）", 7, 6,
   "分岐 6 件のうち 2 件目、案 1（4 経路）と別案（2 経路、Sonnet API ／ GPT-5.5）の対立、別案採用"),
  (38, "F-006", "採用：案 1", "完全一致 13 件の一括採用、議論なしで案 1 採用。T-010 前提に T-006 ／ T-007 ／ T-009 を追加（runtime A-004 と同型処理）。", None, 8, 3,
   "完全一致 13 件の一括採用、runtime A-004 同型"),
  (39, "F-011", "採用：案 1", "完全一致 13 件の一括採用、議論なしで案 1 採用。T-011 完了条件に「4 下流接合面の機械検証」を追加（A-003 と一体作業で対処）。", None, 8, 3,
   "完全一致 13 件の一括採用、A-003 と一体作業"),
  (40, "A-003", "採用：案 1", "完全一致 13 件の一括採用、議論なしで案 1 採用。F-011 と一体作業で T-011 成果物リストに test_downstream_interface.py を追加。", None, 8, 3,
   "完全一致 13 件の一括採用、F-011 と一体作業"),
  (41, "A-002", "採用：案 1", "完全一致 13 件の一括採用、議論なしで案 1 採用。T-007 対応要件欄に Req 9 受入 6 を追加、要件追跡表で Req 9 受入分担を明記（runtime A-002 と同型処理）。", None, 8, 3,
   "完全一致 13 件の一括採用、runtime A-002 同型"),
  (42, "F-007", "採用：案 1", "完全一致 13 件の一括採用、議論なしで案 1 採用。T-009 前提タスクに T-008 を追記（明示性向上）。", None, 8, 3,
   "完全一致 13 件の一括採用"),
  (43, "F-008", "採用：案 1", "案 1（注記そのまま）を採用。runtime F-008 ／ topic-26 の判定（別案＝案 2 ＋ 注記）と同様の枠組みで、foundation／runtime／evaluation の 3 機能で同じ運用に従う構造を維持。完了条件は「承認の記録方法は foundation tasks T-001 と同じ運用に従う」のままで、foundation の運用が将来確定時に追随。利用者発言（topic-26）「完了条件というのは機械が判断するものか？」の方針継承。", None, 7, 5,
   "分岐 6 件のうち 3 件目、案 1（4 経路）と別案（2 経路、Sonnet API ／ GPT-5.4）の対立、案 1 採用（一貫性重視）"),
  (44, "F-009", "採用：案 1", "完全一致 13 件の一括採用、議論なしで案 1 採用。T-007 完了条件に「有効母集団規則適用後の比較集計に invalid／analysis_blocked が 0 件であること」の機械判定基準を補記。", None, 8, 3,
   "完全一致 13 件の一括採用"),
  (45, "F-012", "改良版 A", "改良版 A（両方全件 ＋ 環境差で分担）を採用。T-003 テスト要件に「単体検証（モック環境）：境界 7 ケース全件を網羅」、T-011 テスト要件に「経路統合検証（実環境）：同じ 7 ケースを実環境経路でエンドツーエンド検証。T-003 と意図的二層、二重実装ではない」と明記。実装者の迷いゼロを最優先、テスト網羅性最大。",
   "改良版 A（Sonnet API 別案に近い、案 1 の枠内でケース単位の境界を環境差で明示）", 9, 3,
   "分岐 6 件のうち 4 件目、案 1（4 経路）と別案（2 経路）の対立、案 1 の改良版 A 採用（環境差で 7 ケース全件分担）"),
  (46, "F-013", "採用：案 1", "完全一致 13 件の一括採用、議論なしで案 1 採用。T-001 責務欄に「仕様文書の配置先＝ evaluation/analysis_layout/、実体生成物の配置先＝ experiments/analysis/」の境界を明示（runtime F-013 と同型処理）。", None, 8, 5,
   "完全一致 13 件の一括採用、runtime F-013 同型"),
  (47, "F-014", "採用：案 1", "完全一致 13 件の一括採用、議論なしで案 1 採用。T-011 完了条件に語彙正本ハッシュ照合または参照のみ使用の機械検証を明記（runtime F-012 と同一作業）。", None, 8, 3,
   "完全一致 13 件の一括採用、runtime F-012 同一作業"),
  (48, "F-015", "採用：案 1", "完全一致 13 件の一括採用、議論なしで案 1 採用。T-009 責務欄を findings_summary に統一し、design.md 側スキーマと一致させる（design 軽量再オープン手続きが必要）。", None, 8, 5,
   "完全一致 13 件の一括採用、design 軽量再オープン必要"),
  (49, "A-004", "採用：案 1", "完全一致 13 件の一括採用、議論なしで案 1 採用。T-002 完了条件に対称性検証の操作的判定方法（パス構造ハッシュ照合等）を補記（runtime A-005 同型処理）。", None, 8, 3,
   "完全一致 13 件の一括採用、runtime A-005 同型"),
  (50, "A-005", "採用：案 1", "完全一致 13 件の一括採用、議論なしで案 1 採用。T-009 責務記述で 2 出力器の内部関係（共通スキーマ ＋ 出力器分離）を補記、粒度は維持（runtime A-003 同型処理）。", None, 8, 5,
   "完全一致 13 件の一括採用、runtime A-003 同型"),
  (51, "A-006", "別案", "別案（前提追加 ＋ 責務欄／インライン注釈で入力源と判定境界の対応関係を明示）を採用。F-006 の対処（T-010 前提に T-006 ／ T-007 ／ T-009 追加）に加えて、T-010 責務欄に「選択ロジック判定境界の入力源は T-007 の treatment_comparisons.json、T-009 の exploratory 集計、必要に応じて T-006 の被覆率を入力として判定」と 1 文補記、または前提欄に注釈を加える。実装段への橋渡しを重視。",
   "別案（4 経路一致：Sonnet API ／ GPT-5.5 ／ Gemini-flash ／ Gemini-pro、いずれも「前提追加 ＋ 責務欄／インライン注釈で入力源と判定境界の対応関係を明示」を提案）", 5, 7,
   "分岐 6 件のうち 5 件目、案 1（2 経路）と別案（4 経路）の対立、別案採用（明示性重視）"),
  (52, "A-007", "別案 A", "別案 A（遅延管理テーブル新設）を採用。T-009 完了条件の参照文字列を「analysis 仕様（起草予定）の下流接合面条件を満たす形式」と仮称化 ＋ tasks.md 末尾に「遅延確認事項テーブル（Deferred Verification Table、DVT）」を新設、DVT-001 として管理 ＋ T-011 完了条件で「DVT テーブル内の未解除項目がない（または延期理由が明記されている）」をゲート化。将来の遅延項目増加に備える拡張性も確保。",
   "別案 A（Sonnet API の遅延管理テーブル新設 ＋ 参照文字列の仮称化）", 6, 4,
   "分岐 6 件のうち 6 件目、案 1（4 経路）と別案（2 経路）の対立、別案 A 採用（将来拡張性重視）"),
]


def main() -> int:
  RESULTS_DIR.mkdir(parents=True, exist_ok=True)
  for topic_num, fid, decision, rationale, alt_prop, c1, c2, note in JUDGMENTS:
    # response_text の中身（YAML 風文字列）
    rt_parts = [
      f'decision: "{decision}"',
      f"rationale: |",
      f"  {rationale}",
    ]
    if alt_prop:
      rt_parts.append(f"alternative_proposal: |")
      rt_parts.append(f"  {alt_prop}")
    else:
      rt_parts.append("alternative_proposal: |")
    rt_parts.append("confidence: 1.0")
    rt_parts.append("turns_used: 1")
    rt_parts.append("uncertainty_factors:")
    rt_parts.append("assumed_context:")
    rt_parts.append("case_scores:")
    rt_parts.append(f"  case_1: {c1}")
    rt_parts.append(f"  case_2: {c2}")
    rt_parts.append("comment_to_human:")
    rt_parts.append(f"  - {note}")

    response_text = "\n".join(rt_parts) + "\n"

    data = {
      "provider": "human",
      "model": "user",
      "turn_number": 1,
      "duration_seconds": 0,
      "sent_messages_count": 0,
      "note": f"利用者本人の判定（topic-{topic_num}、{fid}）。本セッション 33（2026-05-27）の対話形式判定。{note}",
      "response_text": response_text,
    }

    out_path = RESULTS_DIR / f"topic-{topic_num:02d}-human.yaml"
    out_path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")
    print(f"  保存: {out_path.name}（{fid}、{decision}）")

  print(f"\n合計 {len(JUDGMENTS)} 件の利用者本人判定を保存完了")
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
