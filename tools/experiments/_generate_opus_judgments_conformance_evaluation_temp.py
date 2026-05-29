"""tools/experiments/_generate_opus_judgments_conformance_evaluation_temp.py

conformance-evaluation tasks の Opus 4.7（メインセッション本人）判定 10 件を一括生成する一時スクリプト。
セッション 39（2026-05-29）の conformance-evaluation tasks 7 モデル比較実験で使用、後で削除予定。

出力：tools/experiments/results/topic-NN-opus-4-7.yaml（10 ファイル、topic-111〜120）
"""
from pathlib import Path

RESULTS_DIR = Path(__file__).resolve().parent / "results"

NOTE = """本判定はメインセッション（claude-opus-4-7、私自身）の最終判断者としての判定。
conformance-evaluation tasks の triad-review では私は 3 役のいずれにも入っていない（主役 Sonnet 4.6、
敵対役 Opus 4.7 サブエージェント、判定役 Opus 4.7 サブエージェント）が、
私は本実験のプロンプト（事実／候補案／後段影響）の起草者であるため、純粋な独立判定ではない。
所要時間 0 は「新規 API 呼び出しではなく、判定役の統合判定と対処方向性を踏まえた起草者判断」を意味する。
本データは 7 モデル比較表の中で「起草者の意見」基準点として扱う。"""

JUDGMENTS = [
  # ===== must-fix 2 件 =====
  {
    "num": 111, "finding_id": "G-003", "decision": "採用：案 1",
    "rationale": "axis を照合対象の 2 値（requirements/design）に固定し、intent は別フィールドに分離する案 1 を採る。Decision 4「2 軸 6 criteria」の設計思想を保て、intent の参考情報性（must-fix 対象外）を構造で表現できる。案 2（axis を 3 値拡張）は、criteria の軸が requirements/design の 2 軸のまま（§8.1）なので、axis 値域（3 値）と criteria 軸（2 軸）が別概念として併存し、axis という語に二義を持たせる。設計（承認済み）の遡及修正のため再オープン手続きの要否を確認。",
    "case_1": 8, "case_2": 4, "confidence": 0.75,
  },
  {
    "num": 112, "finding_id": "F-015", "decision": "採用：案 1",
    "rationale": "正本（pending 166/190 行）で A-011/A-012 は対処済みであり、design §20.1 の「消化予定」記述が陳腐化している。正本に合わせて更新するのみで代替案は考えにくい。self-improvement topic-103 と完全に同型。§14.3/§14.5 の A-011 参照も対処済み前提に整え、§20.1 以外に同種の陳腐化がないか全体点検する。設計の遡及修正のため再オープン手続きの要否を確認。",
    "case_1": 9, "case_2": 0, "confidence": 0.83,
  },
  # ===== should-fix 8 論点群 =====
  {
    "num": 113, "finding_id": "F-001", "decision": "採用：案 2",
    "rationale": "T-008（3 役レビュー機構）は §11.3 で §5.9 規律のメタ流用を担うのみで、axis/criterion_id を生成・参照するのは T-006/T-007。T-008 は T-005 を直接必要としない。よって前提を T-001 のまま維持し、axis/criterion_id の生成責務が T-006/T-007 にあることを tasks に明記する案 2 が、過剰な直列化を避けつつ整合を保てる。self-improvement topic-107 の「過剰直列化を避ける」教訓と整合。案 1（T-005 を前提に追加）は T-008 着手を不要に遅らせる。",
    "case_1": 5, "case_2": 7, "confidence": 0.68,
  },
  {
    "num": 114, "finding_id": "F-002", "decision": "採用：案 1",
    "rationale": "T-009/T-012 の前提に、緩い依存（完了検証前提）として T-006/T-007 を明記する。self-improvement topic-107 で確立した硬い依存／緩い依存の区別を流用すれば、推移依存で実害がない一方で前提表の追跡精度が上がり、記法も他機能と揃う。案 2（現状維持）は前提表を最小に保てるが、完了条件が参照する依存が前提表に現れない不整合が残る。",
    "case_1": 7, "case_2": 5, "confidence": 0.72,
  },
  {
    "num": 115, "finding_id": "F-006", "decision": "採用：案 1",
    "rationale": "要件追跡表に T-005（照合除外）と T-007（judgment_id）を追記し、「全タスク（スコープ前提）」の曖昧記述を具体化する。T-013 の双方向整合チェックが機能するために必要。追跡表の精度問題で実装は阻害しないが、self-improvement topic で確立した双方向整合の方針に沿う。代替案は考えにくい。",
    "case_1": 9, "case_2": 0, "confidence": 0.8,
  },
  {
    "num": 116, "finding_id": "F-007", "decision": "採用：案 1",
    "rationale": "MV-6 は唯一の「遮断必須（即時停止）」検査でバイアス防止の中核。第 1 期が手動レビューでも、推定役プロンプトログの保管形式・配置・grep 対象を明記しておけば検査手順が機械的に再現可能になり、自動化（フェーズ 4）への移行も滑らか。案 2（自動化時に委ねる）は安全性最高位の検査を第 1 期は手動依存のまま残す。DVT-C004 が技術手段を延期管理しているが、ログ形式の明記は第 1 期でも軽量に可能。",
    "case_1": 7, "case_2": 6, "confidence": 0.65,
  },
  {
    "num": 117, "finding_id": "F-008", "decision": "採用：案 1",
    "rationale": "T-004 に feature-partitioning の肯定確認テスト、T-003 に候補提示の出力形式テストを追加する。遮断（他文書）と尊重（feature-partitioning）の両境界が確認でき、TDD で実装前に明示する形になる。テスト網羅の補強で実装は阻害しない。代替案は考えにくい。",
    "case_1": 9, "case_2": 0, "confidence": 0.78,
  },
  {
    "num": 118, "finding_id": "F-011/F-012/F-014/F-016/F-018", "decision": "採用：案 1",
    "rationale": "5 件の軽微な文言整備をまとめて実施する（発番境界テスト追加／--check-partitioning 参照／完了条件 4 を「フェーズ 2 配置後に整合確認」に／DVT-C002 括弧書き整理／CONFORMANCE_EVALUATION.md 既存明記）。文言の精度が上がり機械検証・実装の解釈ブレが減る。いずれも実装段進行は阻害しない軽微修正。",
    "case_1": 9, "case_2": 0, "confidence": 0.8,
  },
  {
    "num": 119, "finding_id": "F-017", "decision": "採用：案 1",
    "rationale": "design §12.2 または §18.2 に tools/conformance_evaluation/schemas/ の配置を 1 行追記し、設計と tasks の追跡を完結させる。self-improvement で schemas/ サブフォルダ方針を design に追記済み（topic-106）であり、一貫性のため本機能でも design に明示する。承認済み design の軽微な遡及修正。案 2（tasks 注記のみ）は設計に明示がないまま残る。",
    "case_1": 7, "case_2": 6, "confidence": 0.68,
  },
  {
    "num": 120, "finding_id": "G-005", "decision": "採用：案 1",
    "rationale": "T-002 完了条件を「振り分け先パイプラインへのディスパッチ機構の確立（実体完成でなくインタフェース確立）」に整え、T-002↔T-003/T-004 の記述上の循環を解消する。最小修正で済む。案 2（段階分割を本文に明記）も有効だが記述量が増える。完了条件の表現変更で十分と判断。",
    "case_1": 7, "case_2": 6, "confidence": 0.7,
  },
]


def generate() -> int:
  for j in JUDGMENTS:
    has_alt = "alternative" in j
    alt_block = f'  alternative_proposal: |\n    {j["alternative"]}\n' if has_alt else "  alternative_proposal: |\n"
    yaml_content = f"""provider: claude-code-main-session
model: claude-opus-4-7
turn_number: 1
duration_seconds: 0
sent_messages_count: 0
note: |
  {NOTE.replace(chr(10), chr(10) + '  ')}
response_text: |
  decision: "{j['decision']}"
  rationale: |
    {j['rationale']}
{alt_block}  confidence: {j['confidence']}
  turns_used: 1
  uncertainty_factors:
    - 起草者としてのバイアス（実験プロンプトを自分が書き、その判定も自分が出すため、設計上の盲点を見落とす可能性）
    - 判定役の対処方向性を踏まえているが、議論前の暫定判断のため利用者議論で覆る可能性
  assumed_context:
    - 3 役 triad-review の所見（主役 20／敵対役独自 5）と判定役の §4.1 対処方向性を踏まえた判定
    - self-improvement tasks で確立した枠組み伝染バイアス回避・hard/soft 依存区別の方針との整合を考慮
  case_scores:
    case_1: {j['case_1']}
    case_2: {j['case_2']}
  comment_to_human:
    - 本判定は 7 モデル比較の基準点として、起草者の意見を記録するもの。最終的な対処方針は利用者議論を経て確定する
"""
    output_file = RESULTS_DIR / f"topic-{j['num']}-opus-4-7.yaml"
    output_file.write_text(yaml_content, encoding="utf-8")
    print(f"  wrote topic-{j['num']} ({j['finding_id']}, {j['decision']})")
  print(f"\n生成完了：{len(JUDGMENTS)} 件")
  return 0


if __name__ == "__main__":
  raise SystemExit(generate())
