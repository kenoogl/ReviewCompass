# proxy_model 判断依頼：implementation triad-review round-1 の三段階トリアージ

あなたは ReviewCompass の proxy_model（人間判断の代行役）である。操縦 LLM（Claude）とは独立に、
以下の 8 所見（6 同根クラスタ）について、候補案から採用案を選び、最終ラベル
（must-fix／should-fix／leave-as-is）を決定せよ。コミット・プッシュ・spec.json 更新・フェーズ移行の
判断は本依頼の範囲外である。

## レビュー対象の文脈

- 対象：conformance-evaluation の配置規約 P1 reopen（R-0）、implementation フェーズの TDD 実装差分
- 上流契約（承認済み tasks 確定本文）の要点：
  - 書き込みは常に新配置 `evidence/features/<feature>/conformance/`。旧配置 `specs/<feature>/conformance/` への新規書き込み禁止（凍結契約）
  - 読み取りは新→旧フォールバック、同名は新を正とし警告
  - 採番 CF-NNN／JD-NNN は凍結期に新旧合算スコープで統合算出
  - MV-1〜3 の凍結違反検出は git 追跡履歴が正本（P1 実装反映コミット時点の在籍ファイル＝凍結集合、以降の追加・変更＝違反）
  - 推定ログは新配置 `evidence/estimation/<run_id>/` へ書き込み、旧 `logs/estimation/` への新規追加は違反検出。凍結済み旧推定ログは MV-6 の読み取り対象に含める
  - `_cross_feature` は横断名前空間で `specs/_cross_feature/conformance/` のまま（tasks T-015、凍結対象外）
- TDD 経過：赤 12 件 → 緑（全 894 件 pass）

## 操縦 LLM による事実確認（判断材料）

- 【C1 関連・実証済み】`git ls-files --others --exclude-standard` は .gitignore 対象の未追跡ファイルを一覧から除外する。最小例で、ignore された新規ファイルが凍結違反検出から漏れることを機械的に確認した。ただし現リポジトリでは旧配置のファイルはすべて git 追跡済みで、`logs/estimation/` を ignore する規則は存在しない。
- 【C5 関連・反証済み】主役所見 primary-004 の「実装の `_legacy_violations` も削除を violations に含めていない」という主張は誤り。`git diff --name-only <freeze_commit>` は削除ファイルも列挙するため、凍結ファイルの削除は `frozen_file_changed` として検出されることを最小例で確認した。未カバーなのはテストのみ。

## 同根クラスタと候補案

### C1：凍結違反検出が ignore されたファイルを見逃す
- 対象所見：gpt-5.5-adversarial-001（ERROR）、claude-sonnet-4-6-primary-001（INFO、同根＝未追跡ファイルの扱いの境界）
- 候補案：
  - A：`--exclude-standard` を外し、ignore 対象も検出する。ignored ファイルの検出テストを追加（操縦 LLM の推薦案）
  - B：git 外のファイルシステム走査を併用する
  - C：現状維持し、運用文書に注記する
- 利点と弱点：A は 1 行変更で契約（旧配置への新規出現はすべて違反）に一致。旧配置は書き込み禁止区画なのでノイズも異常シグナルであり実害なし。B は「git 追跡履歴が正本」の設計と二重基準になる。C は対象アプリが logs/ を ignore する構成で検出漏れが残る。

### C2：差分基準が作業ツリー比較である
- 対象所見：claude-sonnet-4-6-primary-002（WARN）
- 候補案：
  - A：挙動は維持（作業ツリー比較はコミット前の違反も捕まえる安全側）し、「freeze 後にコミット済みの変更も検出する」テストを追加して挙動を固定（操縦 LLM の推薦案）
  - B：`git diff <freeze_commit> HEAD` の履歴のみ比較へ変更
  - C：現状維持（テスト追加なし）
- 利点と弱点：B は未コミットの違反を見逃すようになり安全性が下がる。凍結集合の判定自体は ls-tree（freeze コミット基準）のままで揺れない。

### C3：`_cross_feature` 例外の報告と判定の堅牢性
- 対象所見：gpt-5.5-adversarial-003（WARN）、claude-sonnet-4-6-primary-003（INFO、同根＝同例外の扱い）
- 候補案：
  - A：read_record の `source` を `_cross_feature` 専用値（例 `cross_feature_namespace`）で報告し、凍結検査の除外判定を部分文字列一致からパス成分一致へ強化、テスト追加（操縦 LLM の推薦案）
  - B：運用文書への注記のみ
  - C：現状維持
- 利点と弱点：A は誤認（evidence 移行済みとの誤解）と理論的誤除外の両方を塞ぐ。変更は局所的。

### C4：凍結済み旧推定ログを MV-6 の「読み取り対象」に含める実装がない
- 対象所見：gpt-5.5-adversarial-002（ERROR）
- 候補案：
  - A：既存 `prompt.log` を新旧両配置から走査して MV-6 の 2 条件（禁止パス不在・自律探索禁止条項の存在）を検査するメソッドを追加し、テストを付ける（操縦 LLM の推薦案）
  - B：第 1 期は手動 grep 運用（design §18.4）のため、運用文書の手順記載に留める
  - C：現状維持
- 利点と弱点：A は tasks T-012 責務文「凍結済み旧推定ログも MV-6 の読み取り対象に含める」を機械検証可能にする。小規模実装。B は tasks の確定テスト要件（推定ログの凍結期テストは 2 件のみ）とは整合するが、契約が文書上の約束に留まる。

### C5：凍結ファイル削除の検出が未テスト
- 対象所見：claude-sonnet-4-6-primary-004（INFO）
- 候補案：
  - A：削除が `frozen_file_changed` として検出されることを固定するテストを追加（操縦 LLM の推薦案。所見中の「実装が削除を含めない」は事実誤認と注記して棄却）
  - B：現状維持
- 利点と弱点：A はテスト 1 件で凍結契約の「変更」に削除が含まれることを固定できる。

### C6：運用文書に P3 未実施時の扱いがない
- 対象所見：claude-sonnet-4-6-primary-005（INFO）
- 候補案：
  - A：現状維持＝leave-as-is（互換終了は配置規約 PLC-DEC-011〔P3 専用 reopen〕が正本で、文書は「暗黙の終了はない」を明記済み。期限管理は配置規約計画側の責務）（操縦 LLM の推薦案）
  - B：運用文書へ P3 未実施時の扱いを追記
- 利点と弱点：B は本実装の責務範囲を超えて配置規約計画の内容を二重記載することになり、正本の分散を招く。

## 元レビュー raw（全文）

### raw/claude-sonnet-4-6.round-1.txt（主役、5 所見）

（run ディレクトリ `raw/claude-sonnet-4-6.round-1.txt` の全文を以下に転記）

findings:
  - severity: INFO
    target_location: "tools/conformance_evaluation/machine_verification.py: _legacy_violations メソッド"
    description: "untracked ファイル（ls-files --others）を凍結違反の「追加」候補に含めているが、git 追跡されていないファイルは freeze_commit 時点の ls-tree にも ls-files にも現れないため、凍結集合外への新規追加と同様に扱われる。これ自体は design §18 の「効力発生は実装切替と同時」という契約と整合するが、git add 前の一時ファイルや IDE 生成ファイルが誤検出を引き起こすリスクがある。テスト (test_t012_record_freeze_violations_detected_from_git_history) では untracked ファイルのシナリオを直接検証していないため、契約の境界条件として文書化または専用テストで明示すべき。"
    rationale: "凍結違反検出の誤検出抑制は運用上の信頼性に直結する。design §18 は「git 追跡履歴が正本」と規定しているが、untracked ファイルの扱いが明示されていないため、実装の意図が契約から読み取れない。WARN 未満の情報所見として記録する。"

  - severity: WARN
    target_location: "tools/conformance_evaluation/machine_verification.py: _legacy_violations メソッド、changed の取得"
    description: "`changed` は `git diff --name-only <freeze_commit>` で取得しているが、このコマンドはワーキングツリーと freeze_commit の差分（ステージ済み＋未ステージ）を返す。HEAD と freeze_commit が一致しない状況（freeze_commit が過去のコミットで、その後に別の変更コミットが存在する場合）では、凍結後のコミット済み変更も `changed` に含まれるため `modified` として正しく検出されるが、ステージ済みの一時的な変更も含まれてしまう。設計 §18 の「git 追跡履歴が正本」という規定に照らすと `git diff --name-only <freeze_commit> HEAD` の方が追跡履歴の比較として意図に近い可能性がある。テストは `_git_commit_all` で変更後のファイルをコミットせずにワーキングツリーのまま検査しているため、現テストではこの差異が顕在化しない。"
    rationale: "凍結違反の誤検出または検出漏れは、遮断推奨の MV-3 チェックの信頼性を損ない、運用者の判断を誤らせる。テスト設計と実装コマンドの乖離は契約の弱体化に相当する（レビュー観点4）。"

  - severity: INFO
    target_location: "tools/conformance_evaluation/machine_verification.py: check_record_freeze、_cross_feature 除外"
    description: "_cross_feature 除外を `'/_cross_feature/' not in reason` という文字列マッチで実装しているが、reason 文字列は `'added_after_freeze: .reviewcompass/specs/_cross_feature/conformance/...'` 形式であり、パス区切りが `/` なのでスラッシュ囲みの `/_cross_feature/` では `.reviewcompass/specs/_cross_feature/conformance/` の `specs/` と `conformance/` の間の部分を捉える。パスが `specs/_cross_feature` で始まる場合、`/_cross_feature/` は `s/_cross_feature/` の後ろにあるため実際に含まれる。一方 `conformance_dir` の `_cross_feature` 分岐（evaluation_record.py）では `feature == '_cross_feature'` で正確に比較しており、文字列含有チェックは feature 名に `_cross_feature` を部分文字列として含む別の feature（例: `billing__cross_feature`）があった場合に誤除外する理論的リスクがある。現実的影響は低いが、`LEGACY_RECORD_PATTERN` で既に `.reviewcompass/specs/<feature>/conformance/` を捕捉しているため、パス要素として `== '_cross_feature'` で比較する方が堅牢。"
    rationale: "tasks T-015 の _cross_feature 例外は凍結対象外という明示的な契約であり、誤除外・誤検出の両方を避ける正確な実装が求められる（レビュー観点5）。"

  - severity: INFO
    target_location: "tests/conformance-evaluation/test_conformance_evaluation.py: test_t012_record_freeze_violations_detected_from_git_history"
    description: "テストは freeze_commit 後に unlink してファイルを削除するシナリオ（凍結済みファイルの削除）を検証していない。design §18 の凍結契約は「追加・変更」を違反として明示しているが、削除の扱い（違反か否か）がテストでカバーされておらず、実装の `_legacy_violations` も削除を violations に含めていない。仕様が削除を凍結違反としない意図であれば、その根拠をコメントまたは設計文書に記載すべき。"
    rationale: "凍結集合の完全性検証としてテスト網羅が不十分な可能性がある（レビュー観点4・5）。仕様の明示的な記述がない場合、将来の実装者が削除を許容してよいか判断できない。"

  - severity: INFO
    target_location: "docs/operations/CONFORMANCE_EVALUATION.md: §6.0 凍結期の扱い"
    description: "「互換の終了は P3 の専用 reopen における仕様改訂として扱う（暗黙の終了はない）」という記述は実装の設計意図と整合しているが、P3 reopen が実施されなかった場合の取り扱い（永続的フォールバック継続の可否）については言及がない。運用リスクは低いが、P3 期限の明示または未実施時の継続可否を簡記すると運用文書の完全性が向上する。"
    rationale: "運用文書と実装の整合確認（レビュー観点6）として、将来の運用者への情報提供の観点から記録する。"

### raw/gpt-5.5.round-1.txt（敵対役、3 所見）

（run ディレクトリ `raw/gpt-5.5.round-1.txt` の全文を以下に転記）

findings:
  - severity: ERROR
    target_location: "tools/conformance_evaluation/machine_verification.py::_legacy_violations"
    description: "旧配置への未追跡追加を `git ls-files --others --exclude-standard` で検出しているため、ignore 対象の旧配置ファイルが凍結違反から漏れる"
    rationale: "凍結契約は旧 `specs/<feature>/conformance/` および旧 `logs/estimation/` への P1 以降の追加を違反として検出することを要求している。特に `logs/` は ignore 対象になりやすく、`--exclude-standard` を付けると ignored な未追跡ログが検査対象から除外され、旧ルートへの新規書き込みを見逃す。未追跡・ignored を含むファイルシステム走査、または ignore を無視した git 走査が必要。"
  - severity: ERROR
    target_location: "tools/conformance_evaluation/machine_verification.py::check_prompt_isolation / check_estimation_log_freeze"
    description: "凍結済み旧 `logs/estimation/` を MV-6 のプロンプト内容検査対象に含める実装がない"
    rationale: "上流契約では、推定ログの書き込み先は新配置へ切り替えつつ、凍結済み旧推定ログは MV-6 の読み取り対象に含める必要がある。現在の `check_prompt_isolation` は渡された prompt を新配置へ書き込んでその prompt だけを検査し、`check_estimation_log_freeze` は旧ログの追加・変更検出だけを行うため、既存の旧ログに forbidden path や自律探索禁止条項欠落があっても MV-6 として検出されない。"
  - severity: WARN
    target_location: "tools/conformance_evaluation/evaluation_record.py::EvaluationRecordModel.read_record"
    description: "`_cross_feature` の読み取り結果が specs 配下の例外配置でも `source: evidence` と報告される"
    rationale: "`_cross_feature` は実 feature ではないため配置を `specs/_cross_feature/conformance/` のまま維持する契約になっている。`conformance_dir()` が `_cross_feature` では旧配置と同一パスを返すため読み取り自体は可能だが、`read_record()` は新配置扱いの分岐に入り `source: evidence` を返す。運用・診断・警告表示で cross-feature 例外を evidence 移行済みと誤認させるおそれがある。"

### raw/gemini-3.1-pro-preview.round-1.txt（判定役、所見ゼロ）

findings: []

## 回答形式（厳守）

次の YAML だけを返すこと。8 所見すべてに 1 エントリずつ。finding_id は完全な ID
（例 `2026-06-12-implementation-placement-p1-reopen-triad-review-run-gpt-5.5-adversarial-001`）を使う。
`selected_option` はクラスタの候補案記号（A／B／C）、`final_label` は must-fix／should-fix／leave-as-is、
`rejected_options` は選ばなかった各案の棄却理由を 1 文ずつ書く。

```yaml
decisions:
  - finding_id: <完全な finding_id>
    cluster_id: <C1〜C6>
    selected_option: <A|B|C>
    final_label: <must-fix|should-fix|leave-as-is>
    rationale: <採用理由（日本語、2〜4 文）>
    rejected_options:
      <記号>: <棄却理由>
```
