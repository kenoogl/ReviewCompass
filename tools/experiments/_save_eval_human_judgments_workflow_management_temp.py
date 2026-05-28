"""workflow-management tasks の利用者本人判定 23 件（topic-76〜98）を topic-NN-human.yaml に保存する一時スクリプト。

セッション 38（2026-05-28）の対話形式判定。
- 孤立 6 件（79／81／85／87／92／98）＝起草者 Opus のみ案 1、他 6 モデルが別案/案 2 に収束 → 利用者は全件多数派を採用（起草者バイアス補正）
- 引き分け 2 件（84／89）＝案 1 と別案が 3 対 3 → 利用者判断で決定
- 多数派明確 8 件＋完全一致 6 件＋少数派多数決 1 件（86）＝多数派に沿って記録
"""
from pathlib import Path

import yaml

RESULTS_DIR = Path(__file__).resolve().parent / "results"

# (topic_num, finding_id, decision, rationale, alt_proposal, case_1, case_2, note)
JUDGMENTS = [
  # ===== 完全一致 6 件（全 7 モデル案 1）=====
  (76, "F-006", "採用：案 1", "全 7 モデル完全一致（案 1）。議論なしで案 1 採用。T-007 の前提タスクに T-005 を追加し、依存閉包を明示。", None, 8, 5,
   "完全一致 6 件の一括採用、議論なしで案 1"),
  (77, "F-008", "採用：案 1", "全 7 モデル完全一致（案 1、マルチターン後）。議論なしで案 1 採用。T-010 前提を discipline-update.yaml 新設に一意化。", None, 7, 5,
   "完全一致 6 件の一括採用、議論なしで案 1"),
  (88, "F-013", "採用：案 1", "全 7 モデル完全一致（案 1）。議論なしで案 1 採用。spec-set の --rationale 省略時ログ記録テストを T-004 テスト要件に追加。", None, 8, 4,
   "完全一致 6 件の一括採用、議論なしで案 1"),
  (93, "F-020", "採用：案 1", "全 7 モデル完全一致（案 1）。議論なしで案 1 採用。learning/ は self-improvement §13.5 に正本があるため tasks.md に出典注記で吸収。", None, 8, 4,
   "完全一致 6 件の一括採用、議論なしで案 1"),
  (95, "A-006", "採用：案 1", "全 7 モデル完全一致（案 1）。議論なしで案 1 採用。depends_on_resolves_correctly の境界テスト追加＋変更検知先送りを DVT 登録。", None, 7, 5,
   "完全一致 6 件の一括採用、議論なしで案 1。ただし topic-89（F-016）案 3 と変更検知の扱いで実装時の調停が必要"),
  (97, "A-008", "採用：案 1", "全 7 モデル完全一致（案 1）。議論なしで案 1 採用。複数 in-progress 並存を正常系として T-008 テスト要件に追記。", None, 8, 4,
   "完全一致 6 件の一括採用、議論なしで案 1"),
  # ===== 多数派 案 1（8 件）=====
  (78, "F-009", "採用：案 1", "多数派案 1（5／2）に沿って記録。完了条件 3 を DVT-W002 エントリの grep 確認に置換し、人手判断と機械検証を分離。", None, 8, 5,
   "多数派採用（案 1 5 ／ 別案 2）"),
  (80, "F-015", "採用：案 1", "多数派案 1（5／2）に沿って記録。stage_schema.json で completion_predicate を 7 値に制限する機械検証を T-003 完了条件に追加。", None, 8, 5,
   "多数派採用（案 1 5 ／ 別案 2）"),
  (82, "F-001", "採用：案 1", "多数派案 1（5／2）に沿って記録。要件追跡表 Req 1 受入 6 に DVT-W004 延期を注記。", None, 8, 4,
   "多数派採用（案 1 5 ／ 別案 2）"),
  (83, "F-003", "採用：案 1", "多数派案 1（6／1）に沿って記録。要件追跡表 Req 8 受入 4 から T-009 を外す。", None, 8, 5,
   "多数派採用（案 1 6 ／ 別案 1）"),
  (90, "F-017", "採用：案 1", "多数派案 1（6／1）に沿って記録。tools/README.md を T-001 成果物に追加し tests/ と対称化。", None, 8, 4,
   "多数派採用（案 1 6 ／ 別案 1）"),
  (91, "F-018", "採用：案 1", "多数派案 1（4／3）に沿って記録。in-progress.schema.json にハイフン統一＋design 配置ツリー追記。", None, 7, 5,
   "多数派採用（案 1 4 ／ 別案 3、僅差）"),
  (94, "A-005", "採用：案 1", "多数派案 1（5／2）に沿って記録。DVT に先送り論点 8・9 を 2 件追加（DVT-W005／W006）。", None, 8, 4,
   "多数派採用（案 1 5 ／ 別案 2）"),
  (96, "A-007", "採用：案 1", "多数派案 1（6／1）に沿って記録。T-005 完了条件 3 から判断部分を分離（F-009 と同根、同方針）。", None, 7, 5,
   "多数派採用（案 1 6 ／ 別案 1）"),
  # ===== 案 2（6 件）=====
  (84, "F-004", "採用：案 2", "引き分け（案 1 3 ／ 別案 3）を利用者判断で案 2 に決定。運用文書を T-009 に一本化し、T-010 完成後に T-009 が規律変更ゲート説明を追記する分担を明記。", None, 6, 8,
   "引き分け（案 1 3 ／ 別案 3）の利用者タイブレーク。運用文書の所有を T-009 に一本化"),
  (85, "F-007", "採用：案 2", "起草者バイアス補正：私（Opus）のみ案 1、他 6 モデルが案 2 に収束。利用者は案 2 を採用。T-008 は進行中ファイル一般管理に独立性を保ち、reopen 固有フィールドの解釈は T-007 の責務と本文に明記。", None, 4, 8,
   "起草者孤立 6 件の 1 件（私のみ案 1、他 6 案 2）。利用者は多数派案 2 を採用"),
  (86, "F-010", "採用：案 2", "多数派案 2（4 票、私 Opus は少数派案 1）に沿って記録。テンプレート変数の展開規則を stage_schema.json の構造化フィールドに格納し存在検証する形に変更。", None, 5, 8,
   "多数派採用（案 2 4 票、起草者は少数派案 1）。実質的に起草者孤立の 7 件目"),
  (87, "F-011", "採用：案 2", "起草者バイアス補正：私のみ案 1、他 6 モデルが案 2 に収束。利用者は案 2 を採用。T-009 自身の『機械検査対象外』という位置づけと矛盾する grep テスト要件を削除し、必須節の存在確認に絞る。", None, 4, 8,
   "起草者孤立 6 件の 1 件（私のみ案 1、他 6 案 2）。利用者は多数派案 2 を採用"),
  (92, "F-019", "採用：案 2", "起草者バイアス補正：私のみ案 1、他 6 モデルが案 2 に収束。利用者は案 2 を採用。WORKFLOW_MANAGEMENT.md（と WORKFLOW_PRECHECK.md）を design 配置ツリーに追記する遡及修正。", None, 4, 8,
   "起草者孤立 6 件の 1 件（私のみ案 1、他 6 案 2）。利用者は多数派案 2 を採用。design 軽量再オープンが必要"),
  (98, "A-010", "採用：案 2", "起草者バイアス補正：私のみ案 1、他 6 モデルが案 2 に収束。利用者は案 2 を採用。reopen_classification_template.md の二重列挙を解消し、T-001＝雛形配置／T-007＝内容確定を別表現に整理。", None, 4, 8,
   "起草者孤立 6 件の 1 件（私のみ案 1、他 6 案 2）。利用者は多数派案 2 を採用"),
  # ===== 別案（3 件、うち 89 は案 3）=====
  (79, "F-012", "別案を提示",
   "起草者バイアス補正：私のみ案 1、多数派が別案に収束。利用者は別案を採用。",
   "受け取り側（consumer）の統合テストは T-010 に持たせ、self-improvement の実 git mv は呼ばずテスト内で approved-updates/ に YAML を配置して状態を擬似再現する。送り手と受け手の境界（producer/consumer）の契約確認は T-011 に集約。擬似 YAML は self-improvement §8.4 正本スキーマ準拠の共有フィクスチャとし、A-019 解消後に内容を確定する。", 6, 7,
   "起草者孤立 6 件の 1 件（私のみ案 1、多数派別案）。利用者は別案採用。A-019 解消待ちの段取りを含む"),
  (81, "A-004", "別案を提示",
   "起草者バイアス補正：私のみ案 1、他 6 モデルが別案に収束。利用者は別案を採用。",
   "案 1 を拡張：tasks.md（T-003 段定義の actor 値域、T-005 値域テスト、stage_schema.json）に proxy_model を追加して design の 3 値に揃えるのに加え、(1) actor=proxy_model のとき reviewcompass.yaml#human_proxy.proxy_allowed を参照して代行可否を機械判定する処理、(2) approval 段の explicit_human_approval_recorded が proxy_model 承認をどう扱うかの判定仕様、も tasks に明示追加する。proxy 機構の実装範囲（今フェーズ実装か延期か）は要確定。", 4, 5,
   "起草者孤立 6 件の 1 件（私のみ案 1、他 6 別案）。利用者は別案採用。must-fix"),
  (89, "F-016", "別案を提示",
   "引き分け（案 1 3 ／ 別案 3）を利用者判断で別案（案 3）に決定。この仕組み自身の機能を自己適用する案。",
   "案 3：依存マップ駆動の追従強制。T-010 完了条件 4 を『self-improvement design §13.5 の変更が機能依存マップに記録されたとき、DVT-W003 を自動的に open（未解決）に差し戻し、事前検査スクリプトが再評価完了を確認するまで T-010 を完了扱いにしない』に改訂。整合検証は DVT に一本化（案 2 の利点を吸収）しつつ、追従トリガーを人の運用から機械強制へ引き上げる。【実装時の調停事項】A-006（topic-95、変更検知はフェーズ 2 の宿題）と緊張するため、§13.5 の変更検知だけ先行実装し、汎用の変更検知はフェーズ 2、という線引きで両者を調停する。", 5, 4,
   "引き分け（案 1 3 ／ 別案 3）の利用者タイブレーク。自己適用の案 3。A-006 との実装時調停が必要"),
]


def main() -> int:
  RESULTS_DIR.mkdir(parents=True, exist_ok=True)
  for topic_num, fid, decision, rationale, alt_prop, c1, c2, note in JUDGMENTS:
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
      "note": f"利用者本人の判定（topic-{topic_num}、{fid}）。セッション 38（2026-05-28）の対話形式判定。{note}",
      "response_text": response_text,
    }

    out_path = RESULTS_DIR / f"topic-{topic_num}-human.yaml"
    out_path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")
    print(f"  保存: {out_path.name}（{fid}、{decision}）")

  print(f"\n合計 {len(JUDGMENTS)} 件の利用者本人判定を保存完了")
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
