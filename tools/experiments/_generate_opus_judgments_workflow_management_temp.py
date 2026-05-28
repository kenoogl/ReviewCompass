"""tools/experiments/_generate_opus_judgments_workflow_management_temp.py

workflow-management tasks の Opus 4.7（メインセッション本人）判定 23 件を一括生成する一時スクリプト。
セッション 38（2026-05-28）の workflow-management tasks 7 モデル比較実験で使用、後で削除予定。

本判定はメインセッション（claude-opus-4-7、私自身）の「最終判断者」としての判定。
workflow-management tasks の triad-review では私（メインセッション）は 3 役のいずれにも入っていない
（主役 Sonnet 4.6、敵対役 Opus 4.7 サブエージェント、判定役 Opus 4.7 サブエージェント）が、
私は本実験のプロンプト起草者であるため、純粋な独立判定ではない。note 欄にこの立場を明記。

出力：tools/experiments/results/topic-NN-opus-4-7.yaml（23 ファイル）
"""
from pathlib import Path

RESULTS_DIR = Path(__file__).resolve().parent / "results"

NOTE = """本判定はメインセッション（claude-opus-4-7、私自身）の最終判断者としての判定。
workflow-management tasks の triad-review では私は 3 役のいずれにも入っていない（主役 Sonnet 4.6、
敵対役 Opus 4.7 サブエージェント、判定役 Opus 4.7 サブエージェント）が、
私は本実験のプロンプト（事実／候補案／深掘り）の起草者であるため、純粋な独立判定ではない。
所要時間 0 は「新規 API 呼び出しではなく、判定役の統合判定と対処方向性を踏まえた起草者判断」
を意味する。本データは 7 モデル比較表の中で「起草者の意見」基準点として扱う。"""

# 23 件の Opus 4.7（メインセッション）判定
# 判定役の統合判定（§4 must-fix 対処方向性）と主役・敵対役の所見根拠を踏まえた起草者判断
JUDGMENTS = [
  # ===== 機能内 must-fix 6 件 =====
  {
    "num": 76, "finding_id": "F-006", "decision": "採用：案 1",
    "rationale": "依存閉包を前提表に明示するのが筋。T-005→T-007 の実装順を機械的に保証でき、F-007（T-008 前提の T-007 欠落）と合わせた依存チェーンの整合も取れる。案 2 の実行時 DEVIATION は安全網にはなるが、静的な実装順保証が弱い。依存は design 由来なので機能内で吸収可。",
    "case_1": 8, "case_2": 5, "confidence": 0.85,
  },
  {
    "num": 77, "finding_id": "F-008", "decision": "採用：案 1",
    "rationale": "規律変更と機能横断整合は責務が異なるため、専用ファイル（discipline-update.yaml）に分離するのが責務分離の観点で筋。cross-spec-alignment.yaml への相乗りは責務混在を招く。ファイル数は 1 つ増えるが、self-improvement との接合面（規律変更経路）を独立に管理できる利点が上回る。",
    "case_1": 7, "case_2": 5, "confidence": 0.7,
  },
  {
    "num": 78, "finding_id": "F-009", "decision": "採用：案 1",
    "rationale": "DVT-W002 エントリの存在を grep で機械検証する形に置換すれば、tasks ポリシー違反を解消しつつ論点を記録に残せる。案 2（完全削除）はクリーンだが追跡先が別表に移り grandfathering の論点が見えにくくなる。A-007（同根）と整合した処理が望ましい。",
    "case_1": 8, "case_2": 5, "confidence": 0.8,
  },
  {
    "num": 79, "finding_id": "F-012", "decision": "採用：案 1",
    "rationale": "git mv 外部依存のモックは T-010 の統合フロー（完了条件 2）に直結するため、T-010 のテスト要件に明記して所有を明確にするのが筋。案 2（T-011 集約）も機能境界をまたぐテストの一元管理として妥当だが、T-010 の完了条件 2 を T-010 自身のテストで担保できないのは責務の穴になる。A-019（スキーマ整合）確定後にモック内容を詰める。",
    "case_1": 7, "case_2": 6, "confidence": 0.72,
  },
  {
    "num": 80, "finding_id": "F-015", "decision": "採用：案 1",
    "rationale": "スキーマ層（stage_schema.json）で enum として値域を縛るのが宣言的で実装漏れに強い。T-004 実装の見落としを schema で予防できる。案 2（実装層集約）は二層重複を避けるが schema 単独では値域を保証しない。A-004（actor 値域）と同型なので整合した方針（schema 層で縛る）が望ましい。",
    "case_1": 8, "case_2": 5, "confidence": 0.82,
  },
  {
    "num": 81, "finding_id": "A-004", "decision": "採用：案 1",
    "rationale": "design が actor 値域（3 値）の正本なので、tasks.md を design に揃えるのが筋。値域の宣言的整合を確保でき、F-015（値域検査）とも整合する。案 2（延期）は design との不一致を残し値域検査の方針と矛盾しうる。proxy_allowed 解決ロジックの実装タスクは別途必要になる点は補足が要る。",
    "case_1": 8, "case_2": 4, "confidence": 0.8,
  },
  # ===== should-fix 17 件 =====
  {
    "num": 82, "finding_id": "F-001", "decision": "採用：案 1",
    "rationale": "cross-spec-alignment.yaml の段集合が DVT-W004 で未確定なので、追跡表に「段集合本体は DVT-W004 で延期」と注記して追跡の整合を保つのが現実的。案 2（責務前倒し）は DVT-W004 未解決のため記述が宙に浮く。",
    "case_1": 8, "case_2": 4, "confidence": 0.82,
  },
  {
    "num": 83, "finding_id": "F-003", "decision": "採用：案 1",
    "rationale": "T-009（多層防御運用文書）は機能依存マップの 1 箇所修正完結に直接寄与しない。誤追跡なら外すのが追跡精度を高める。案 2（寄与根拠の明記）は寄与が実在すれば妥当だが、責務記述に該当言及がなく、無理に残すと冗長。",
    "case_1": 8, "case_2": 5, "confidence": 0.75,
  },
  {
    "num": 84, "finding_id": "F-004", "decision": "採用：案 1",
    "rationale": "規律変更ゲートを実装する T-010 が自身のゲート説明も書くのが内容の正確性で勝る。WORKFLOW_PRECHECK.md を T-010 成果物に加え追記責務を明示する。案 2（T-009 集約）は運用文書の所有を一元化できるが、T-009 が T-010 の実装内容へ依存する知識依存が生じる。判断は割れやすく確信度は中程度。",
    "case_1": 6, "case_2": 6, "confidence": 0.6,
  },
  {
    "num": 85, "finding_id": "F-007", "decision": "採用：案 1",
    "rationale": "T-008 が current_blocker（reopen 固有フィールド）を読んで自己更新の許容を区別するなら T-007 への依存は実在する。F-006 と合わせ依存チェーン（T-005→T-007→T-008）を前提表で繋ぐのが整合的。案 2（責務を一般管理に絞る）も設計判断として成立するが、現状の T-008 完了条件 4 が reopen 連動を含む以上、前提追加が筋。",
    "case_1": 7, "case_2": 5, "confidence": 0.7,
  },
  {
    "num": 86, "finding_id": "F-010", "decision": "採用：案 1",
    "rationale": "should-fix の軽微な機械判定性の問題なので、grep キーワードを明示する最小修正が妥当。案 2（構造化フィールド化）は堅牢だが schema 設計の追加が必要で、should-fix の規模に対し過剰。F-011 と同型なので同じ方針で揃える。",
    "case_1": 7, "case_2": 5, "confidence": 0.7,
  },
  {
    "num": 87, "finding_id": "F-011", "decision": "採用：案 1",
    "rationale": "grep 対象キーワードの具体語を明示すれば機械検証可能になり、T-009 の最低限の品質ゲートを保てる。案 2（grep テスト削除）は T-009 の「機械検査対象外」という自己位置づけと整合するが検証を完全に失う。F-010 と同型で同じ方針が望ましい。",
    "case_1": 7, "case_2": 5, "confidence": 0.65,
  },
  {
    "num": 88, "finding_id": "F-013", "decision": "採用：案 1",
    "rationale": "design が spec-set の --rationale を「任意」と定めている設計意図（commit/push より軽い操作）を尊重し、省略時のログ記録テストを追加するのが筋。案 2（必須化）は design 遡及を伴い、省略の利便性も失う。",
    "case_1": 8, "case_2": 4, "confidence": 0.82,
  },
  {
    "num": 89, "finding_id": "F-016", "decision": "採用：案 1",
    "rationale": "§13.5 変更時の追従手段（変更検知で DVT 再登録、または整合検査の再実行）を完了条件 4 に明記すれば、機能横断の接合面（A-019 関連）の追従責務が明確になる。案 2（DVT-W003 一本化）は完了条件をシンプルにするが追従保証が DVT 運用次第になる。",
    "case_1": 7, "case_2": 6, "confidence": 0.68,
  },
  {
    "num": 90, "finding_id": "F-017", "decision": "採用：案 1",
    "rationale": "T-001 責務が「各ディレクトリに配置目的を記す README を置く」と明記しているので、tools/README.md を成果物に加えて完了条件で確認するのが責務文と整合する。tests/ との対称性も取れる。案 2（両方削除）は T-004 着手前に tools/ が Git 追跡されない期間を生む。",
    "case_1": 8, "case_2": 4, "confidence": 0.82,
  },
  {
    "num": 91, "finding_id": "F-018", "decision": "採用：案 1",
    "rationale": "ディレクトリ名が in-progress/（ハイフン）なので、スキーマファイルもハイフンに統一すると一貫性が増す。design 配置ツリーへの追記も併せて行う。案 2（アンダースコア維持）は最小修正だが命名混在が残る。ただし stage_schema.json 等の既存アンダースコア命名との全体統一は別論点。",
    "case_1": 7, "case_2": 5, "confidence": 0.68,
  },
  {
    "num": 92, "finding_id": "F-019", "decision": "採用：案 1",
    "rationale": "design 遡及（軽量再オープン）を避け、tasks.md 側に「設計ツリー外の運用文書追加」と注記して機能内で吸収するのが軽量。案 2（design 追記）は設計の正確性を高めるが遡及コストが要る。F-020 と同型で同じ方針が望ましい。",
    "case_1": 7, "case_2": 5, "confidence": 0.7,
  },
  {
    "num": 93, "finding_id": "F-020", "decision": "採用：案 1",
    "rationale": "learning/ の配置は self-improvement §13.5 に正本記述があり機能横断では整合済みなので、tasks.md に出典注記すれば足りる。案 2（本機能 design 追記）は接合面の所有が self-improvement 側にあるため二重記述になる。F-019 と同型。",
    "case_1": 8, "case_2": 4, "confidence": 0.75,
  },
  {
    "num": 94, "finding_id": "A-005", "decision": "採用：案 1",
    "rationale": "tasks.md L303 が「先送り論点を DVT で集約管理」を変更意図に掲げているので、論点 8・9 を DVT に追加して漏れを解消するのが整合的。T-011 の「DVT 未解除なし」ゲートの穴も塞がる。案 2（対象外明示）は論点 8 が T-010 の前提という指摘と整合確認が要る。",
    "case_1": 8, "case_2": 4, "confidence": 0.78,
  },
  {
    "num": 95, "finding_id": "A-006", "decision": "採用：案 1",
    "rationale": "述語の限定責務（値域チェックのみ、変更検知はフェーズ 2 宿題）を境界テストで機械検証し、先送りを DVT に登録すればフェーズ 2 への引き継ぎが明確になる。案 2（注記のみ）は軽量だが境界が機械検証されず実装漏れリスクが残る。F-015 と関連する値域・責務の機械検証テーマ。",
    "case_1": 7, "case_2": 5, "confidence": 0.72,
  },
  {
    "num": 96, "finding_id": "A-007", "decision": "採用：案 1",
    "rationale": "F-009（同根）で完了条件の機械判定化を選んだのと整合し、A-007 でも「検査の実装」と「grandfathering 判断」を分離して順序問題（自己ロック）を回避するのが筋。判断は利用者承認事項として DVT に残す。案 2（移行スクリプトで救済）は自己ロックを構造的に解くが grandfathering の是非を先取りする。",
    "case_1": 7, "case_2": 5, "confidence": 0.72,
  },
  {
    "num": 97, "finding_id": "A-008", "decision": "採用：案 1",
    "rationale": "reopen やり直しで複数 reopen-procedure-*.yaml が並ぶのは design L505（証跡保全）の正常系なので、T-008 テスト要件に複数並存ケース（優先順位・解決順）を追記して継承表との矛盾を解消するのが設計意図と整合。案 2（一律遮断）は安全側だが reopen やり直しの正常運用を妨げうる。",
    "case_1": 8, "case_2": 4, "confidence": 0.78,
  },
  {
    "num": 98, "finding_id": "A-010", "decision": "採用：案 1",
    "rationale": "既に L158 に「T-001 で配置した雛形、本タスクで内容確定」の趣旨があるので、これを注記として強化し完了主体を明示する最小修正が妥当。配置（T-001）と内容確定（T-007）の分離意図は妥当なので二重列挙は許容できる。案 2（重複解消の再構成）は機械判定の一意性を高めるが記述コストが要る。",
    "case_1": 8, "case_2": 5, "confidence": 0.78,
  },
]


def generate() -> int:
  RESULTS_DIR.mkdir(parents=True, exist_ok=True)
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
    - 3 役 triad-review の所見（主役 20／敵対役 10）と判定役の §4 対処方向性を踏まえた判定
    - 過去 foundation／runtime／evaluation／analysis tasks の判断パターンとの整合性を考慮
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
