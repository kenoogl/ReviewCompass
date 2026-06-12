# proxy_model 判断依頼：implementation triad-review round-2 の三段階トリアージ

あなたは ReviewCompass の proxy_model（人間判断の代行役）である。round-1 の 8 所見は判断済み
（全クラスタで案 A 採用、適用済み・全テスト 900 件 pass）。本依頼は round-2（適用後差分の収束確認）で
出た 4 所見の判断である。コミット・プッシュ・spec.json 更新・フェーズ移行の判断は範囲外。

## 操縦 LLM による事実確認

- 【C7 関連】`tools/conformance-evaluation-check.py` は現在「CLI placeholder」で、検査を一切実行しない雛形である。
  DVT-C003 により MV 検査の本格自動化はフェーズ 4 へ延期、第 1 期は手動 grep／find 運用が tasks の確定方針。
- 【C8 関連】`conformance_dir('_cross_feature')` が specs 配下を返す限り new_path == legacy_path であり、
  仮に将来 conformance_dir の返値が変わると、既存テスト test_t009_cross_feature_read_reports_namespace_source が
  失敗して判断を強制する（安全網は既にある）。
- 【C9 関連】コミット済み削除は `git diff --name-only <freeze_commit>`（作業ツリー比較）に現れるため現実装で検出される。
  未カバーなのはテストのみ。

## クラスタと候補案

### C7：新検査が通常実行経路（CLI）に未接続（gpt-5.5-adversarial-001、WARN）
- 候補案：
  - A：CLI に凍結検査の実行を実装する。`--freeze-commit` を受け、check_record_freeze・check_estimation_log_freeze・
    check_existing_prompt_logs を実行し、DEVIATION で終了コード 1。スモークテストと運用文書の実行例を追加（操縦 LLM の推薦案）
  - B：運用文書に手動実行手順（Python ワンライナー例）を記載するに留める（DVT-C003 の段階導入方針と整合）
  - C：現状維持
- 利点と弱点：A は運用上の検出経路が立ち、placeholder の責務（T-012 成果物）にも合う。実装は薄いラッパで
  フェーズ 4 の本格自動化を先取りしすぎない。B は実行経路が人手依存のまま。C は WARN の指摘どおり見逃しリスクが残る。

### C8：_cross_feature の source 判定が暗黙の同値前提に依存（claude-sonnet-4-6-primary-001、INFO）
- 候補案：
  - A：read_record 冒頭で feature == '_cross_feature' を明示分岐し、同値前提を排除する
  - B：leave-as-is。同値は定義（_cross_feature の正本配置＝specs 名前空間）であり、変われば既存テストが失敗して
    判断を強制する（操縦 LLM の推薦案）
- 利点と弱点：A は意図が明示されるがコード追加は仮定上の将来変更への備え。B は最小変更で、安全網（テスト）が既にある。

### C9：コミット済み削除のテスト未網羅（claude-sonnet-4-6-primary-002、INFO）
- 候補案：
  - A：既存の削除テストへ「削除をコミットした後も検出される」ケースを追加する（数行。操縦 LLM の推薦案）
  - B：leave-as-is
- 利点と弱点：A はデータ消失系の重大ケースを恒久固定できる。実装変更は不要（検出は実証済み）。

### C10：検査理由メッセージの形式が未規定（claude-sonnet-4-6-primary-003、INFO）
- 候補案：
  - A：leave-as-is。理由文字列は内部表現で、テストは意図的に部分一致を使っている（操縦 LLM の推薦案）
  - B：理由フォーマットを運用文書に規定する
- 利点と弱点：B は文書の保守対象を増やし、内部表現の変更自由度を下げる。

## 元レビュー raw（全文）

### raw/claude-sonnet-4-6.round-2.txt（主役、INFO 3）

findings:
  - severity: INFO
    target_location: "tools/conformance_evaluation/evaluation_record.py: read_record() の source 判定ロジック"
    description: "_cross_feature の source が 'cross_feature_namespace' として返されるのは新配置パスが存在する場合のみ。legacy_path にしか存在しない _cross_feature 記録は 'legacy_frozen' として返される。テスト test_t009_cross_feature_read_reports_namespace_source は namespace_dir（旧配置）にのみ記録を置いているが、conformance_dir('_cross_feature') は旧配置と同一パスを返すため new_path == legacy_path となり結果的に pass する。ただし将来 _cross_feature の conformance_dir が変更された場合、この同値前提が崩れてフォールバック分岐が legacy_frozen を返す可能性がある。"
    rationale: "_cross_feature の source 値が 'cross_feature_namespace' になるか 'legacy_frozen' になるかは conformance_dir の返値と新配置ファイルの存在に依存しており、テストがその依存を明示していない。現時点では動作するが実装の意図が不明瞭で保守リスクがある。"

  - severity: INFO
    target_location: "tools/conformance_evaluation/machine_verification.py: _legacy_violations() の changed 計算"
    description: "modified の計算に使われる changed は 'diff --name-only freeze_commit' であり、作業ツリーとの差分（コミット済み変更を含む）を返す。一方 frozen は ls-tree の出力（freeze_commit 時点の追跡ファイル）。frozen に含まれるファイルが freeze 後にコミットで削除された場合、tracked にも untracked にも現れないため added にも modified にも含まれず、検出が 'diff' のみに依存する。テスト test_t012_frozen_record_deletion_is_detected は作業ツリー削除（コミット前）のケースのみを検証しており、コミット済み削除のケースは test_t012_committed_changes_after_freeze_are_violations が変更（編集）を対象としているが削除（git rm）後コミットのケースは明示的にカバーされていない。"
    rationale: "凍結集合の削除はデータ消失に相当し、凍結違反の重大ケースの一つ。コミット済み削除の検出が diff ベースで正しく機能するかテストで明示されていない点は保守上のリスクになり得る。"

  - severity: INFO
    target_location: "tools/conformance_evaluation/machine_verification.py: check_existing_prompt_logs() の log_path 表現"
    description: "check_existing_prompt_logs のエラーメッセージに含まれる log_path は Path オブジェクトの str 表現（絶対パス）であり、テスト test_t012_existing_prompt_logs_content_check では 'bad-run' という run_id の部分文字列マッチで確認している。運用文書（CONFORMANCE_EVALUATION.md）や design では理由フォーマットの規定がなく、将来パス表現が変わった場合にテストが脆弱になる。"
    rationale: "厳密な問題ではないが、reason フォーマットの明示的な規約がないと regression が起きやすい。"

### raw/gpt-5.5.round-2.txt（敵対役、WARN 1）

findings:
  - severity: WARN
    target_location: "tools/conformance_evaluation/machine_verification.py / tools/conformance-evaluation-check.py"
    description: "新規追加された凍結検査・既存 prompt.log 検査が通常の機械検査実行経路へ接続された証跡がない"
    rationale: "check_record_freeze、check_estimation_log_freeze、check_existing_prompt_logs は追加され、単体テストでは直接呼び出されているが、diff 上では tools/conformance-evaluation-check.py などの通常実行エントリポイントへの組み込みが示されていない。配置 P1 契約では旧配置への追加・変更検出、および新旧 prompt.log の MV-6 遮断検査が運用上検出される必要があるため、ヘルパー実装だけでは通常実行時に違反を見逃すリスクが残る。"

### raw/gemini-3.1-pro-preview.round-2.txt（判定役、所見ゼロ）

findings: []

## 回答形式（厳守）

次の YAML だけを返す。4 所見すべてに 1 エントリずつ。finding_id は round-2 の完全 ID
（例 2026-06-12-implementation-placement-p1-reopen-triad-review-run-gpt-5.5-adversarial-001）。
値に YAML として不正な書き出し（引用符・バッククォート始まり等）を使わないこと。

```yaml
decisions:
  - finding_id: <完全な finding_id>
    cluster_id: <C7-C10>
    selected_option: <A|B|C>
    final_label: <must-fix|should-fix|leave-as-is>
    rationale: <採用理由 2-4 文>
    rejected_options:
      <記号>: <棄却理由>
```
