# Review raw and triage traceability plan

作成日：2026-06-03

## 背景

evaluation implementation drafting 中に、複数モデルへ post-write verification と
YAML audit を依頼した。結果の一部は `findings:` YAML として自動 parse できたが、
一部はコードフェンス、XML 風タグ、または `findings` 欠落により parse できなかった。

このとき、runner は provider 応答を parse 前に永続保存していなかったため、
parse 失敗時の raw 応答を後から完全には復元できない状態になった。

## 未対応だった点

- 全モデルの raw 応答を成果物として保存していなかった。
- parse 失敗を「自動成形不能」として扱わず、実質的に集約から落としていた。
- どのラウンドで、どの対象 hash に対し、どのモデルが何を返したかの台帳がなかった。
- 各 finding を foundation 正本語彙の `final_label` と、人間判断要否で分類した項目単位の表がなかった。
- モデル同士が議論して合意形成したのか、独立レビュー結果をオーケストレーターが集約したのかが記録上曖昧だった。
- 最終 manifest は要約としては有効だが、レビュー過程の監査ログとしては粒度が不足していた。
- 検証者表記に会社名ベースの表現が混じり、モデル ID と版で追跡する規律が徹底されていなかった。

## 確定方針

今後、API 経由でモデルへレビュー・監査を依頼する場合は、全モデルについて raw 応答を必ず保存する。
parse 成功・失敗にかかわらず raw を保存し、parse 失敗は「レビュー不能」ではなく
「自動成形不能」として扱う。

モデル同士の対話がない限り、記録上は「合意形成」ではなく
「独立レビュー群をオーケストレーターが集約」と表現する。

検証者は会社名ではなくモデル ID と版で記録する。provider 名は実行経路のメタデータとして残してよいが、
判断主体の表記には使わない。

## runner 側の対応

`tools/api_providers/run_role.py` に次のオプションを追加した。

- `--raw-out <path>`：provider 生応答を保存する。parse 成否に関係なく保存する。
- `--parsed-out <path>`：成形済み YAML を保存する。parse 成功時のみ保存する。
- `--review-run-dir <path>`：review run 成果物ディレクトリを指定し、`raw/`、`parsed/`、
  `target-manifest.yaml`、`rounds.yaml`、`model-result-summary.yaml` を生成・更新する。
- `--round-id <id>`：review run に記録する round ID。未指定時は `round-1`。

これにより、`findings:` YAML として読めない応答も raw として残し、後から人間または別処理で成形できる。
`--review-run-dir` 指定時は parse 失敗時でも raw と `rounds.yaml` / `model-result-summary.yaml`
を更新し、該当モデルを `parse_status: parse_failed`、`triage_status: triage_pending` として残す。

CLI オプション自体は任意指定だが、レビュー・監査運用では `--review-run-dir` 指定を必須として扱う。
post-write-verification manifest に `review_run:` を記録した場合は、`tools/check-workflow-action.py next`
が raw、rounds、summary、triage の整合を完了条件として機械判定する。
この確認を経ていないレビュー結果は、監査ログとして不完全と扱う。

複数モデルを 1 つの review run に集約する入口として `tools/api_providers/run_review.py` を追加した。
同 script は `primary`、`adversarial`、`judgment` の 3 role を同じ `--review-run-dir` に順に実行し、
`run_role.py` と同じ raw / parsed / rounds / summary 成果物を更新する。
さらに、ユーザ提示用の `review_summary.md` と、finding 単位の `triage.yaml` 下書きを生成する。
API 応答の parse に失敗した role があっても、raw と `parse_status: parse_failed` を残し、
他 role の実行と summary 生成は継続する。

## 推奨ディレクトリ構造

レビューまたは監査 1 件ごとに、次のような成果物を残す。

```text
docs/notes/review-runs/<run_id>/
  target-manifest.yaml
  rounds.yaml
  triage.yaml
  model-result-summary.yaml
  raw/
    <model_id>.round-1.txt
  parsed/
    <model_id>.round-1.yaml
```

`<model_id>` は設定ファイルまたは実行ログに記録された実際のモデル ID をそのまま使う。
上のファイル名は形式例であり、特定モデルの実在性を保証する一覧ではない。
raw 応答ファイルは provider から返ったテキストをそのまま保存するため、拡張子は `.txt` に統一する。
UTF-8 テキストとして受領した内容を、改行や本文を正規化せず保存する。
受領直後の原本 raw は非改変で保存し、秘匿化が必要な場合は共有用の派生成果物だけを別途作る。
原本 raw の保存先、共有範囲、保持期間は保護対象として扱う。

## rounds.yaml の最小項目

階層を曖昧にしないため、round 単位の情報とモデル応答単位の情報を分ける。
`prompt_id` は `prompt_set_version` 内の識別子であり、`prompt_sha256` は実際に送った
プロンプト本文の checksum である。

```yaml
round_id: review-2026-06-03-r1
purpose: post_write_verification
invocation_timestamp: "2026-06-03T13:24:00+09:00"
target_files:
  - path: docs/operations/EVALUATION.md
    sha256: "<sha256>"
prompt_set_version: "<prompt-set-version>"
prompt_id: "<prompt-id-within-set>"
prompt_sha256: "<sha256>"
model_results:
  - model_id: claude-sonnet-4-6
    provider: anthropic-api
    role: primary
    treatment: primary
    invocation_path: api
    raw_path: raw/claude-sonnet-4-6.round-1.txt
    parsed_path: parsed/claude-sonnet-4-6.round-1.yaml
    parse_status: parsed
    formatted_by: parser
    formatted_by_actor_type: orchestrator
    formatted_by_actor: codex
    formatted_at: "2026-06-03T13:30:00+09:00"
    follow_up_action: triage
```

`parse_status` は `parsed` / `parse_failed` のいずれかで、初回自動 parse の結果を表す。
手動または支援付き成形を行った場合でも、初回結果は上書きしない。
`invocation_path` は runner 台帳内の局所フィールドであり、foundation 正本語彙の
`review_mode=api_mediated` とは別物である。
`role` は API runner の役割、`treatment` は evaluation が使う実行条件の比較軸であり、
初期運用では `primary` / `adversarial` / `judgment` を同じ値で対応付ける。
`formatted_by` は `parser` / `human` / `assisted` のいずれかとし、`assisted` の場合は
支援したモデル ID と版、および最終確定した人間またはオーケストレーターを別フィールドで記録する。
`parse_status`、`follow_up_action`、`invocation_path`、`formatted_by`、
`formatted_by_actor_type`、`decision_status`、`decision_actor_type` は本メモ内の暫定局所語彙であり、
foundation に正本語彙を追加するかどうかは後続判断とする。

## triage.yaml の最小項目

- `finding_id`
- `run_id`
- `source_model`
- `source_round`
- `source_raw_path`
- `source_parsed_path`
- `severity_original`
- `severity_normalized`: `CRITICAL` / `ERROR` / `WARN` / `INFO`
- `target_location`
- `plain_language_summary`
- `final_label`: `must-fix` / `should-fix` / `leave-as-is`
- `decision_status`: `decided` / `human_required`
- `decision_actor`
- `decision_actor_type`: `model` / `human` / `orchestrator`
- `decision_at`
- `decision_reason`
- `applied_files`
- `superseded_by`

`source_model` とモデル由来の `decision_actor` は、会社名ではなくモデル ID と版で記録する。
`decision_actor_type=model` の場合は、対応するモデル ID と版を `decision_actor` に入れる。
`decision_actor_type=orchestrator` の場合は、使用した実行主体名を入れ、参照したモデル出力は
`source_model` と `source_raw_path` で追跡する。

## 必要性判定の三段階

`severity_original` はモデルが返した重大度をそのまま保存する。`severity_normalized` は
foundation 正本語彙である `runtime/schemas/finding.schema.json` の
`CRITICAL` / `ERROR` / `WARN` / `INFO` へ正規化する。
修正必要性の最終判断は、foundation 正本語彙である
`runtime/schemas/necessity_judgment.schema.json` の `final_label` に保存する。

- `must-fix`：仕様・契約・安全側既定・比較可能性に影響するもの。原則として反映または人判断。
- `should-fix`：読みやすさ、将来の保守性、後続設計の追跡性を改善するもの。可能なら反映、設計判断を伴う場合は後続論点へ。
- `leave-as-is`：表現、リンクテキスト、重複削減など。記録に残し、同じ箇所を触るときにまとめて処理するか、修正不要と判断する。

`decision_actor` は、最終判断を下した主体を記録する。モデル出力をそのまま採用した場合でも、
採用判断をした主体は別に記録する。
`decision_status=human_required` は未解決の中間状態であり、最終的には
`decision_status=decided` と foundation 正本の `final_label` へ遷移させる。

raw から手動成形した parsed YAML には、手動であっても一意な `finding_id` を付与する。
採番は `<run_id>-<source_model>-<source_round>-<連番>` を暫定形式とし、`source_model` には
モデル ID と版を含める。ファイル名や ID に使えない文字は機械採番時に安全な表記へ正規化する。
後続で機械採番へ置き換える。

`parse_status=parse_failed` の raw 応答は、成形完了まで `rounds.yaml` の `model_results` に残し、
`follow_up_action: format_pending` として追跡する。成形できた時点で `parsed_path` を追加し、
finding 単位の判断を `triage.yaml` へ移す。成形不能または判断保留の場合は
`decision_status=human_required` として残し、放置された raw 応答が台帳から消えないようにする。

## 機械判定化

規律だけで「全モデルの結果をまとめてからトリアージへ進む」ことを守るのは不十分である。
今後、post-write-verification manifest に `review_run:` を記録する場合は、
`tools/check-workflow-action.py next` が review run 成果物の整合を機械判定する。

`review_run:` 付き manifest は、次の条件を満たさない限り完了扱いにしない。

- `target-manifest.yaml`、`rounds.yaml`、`triage.yaml`、`model-result-summary.yaml` が存在する。
- `rounds.yaml` の全 `model_results` に `model_id`、`raw_path`、`raw_sha256`、`parse_status` がある。
- 各 `raw_path` が存在し、実ファイルの sha256 が `raw_sha256` と一致する。
- `required_verifiers` の全モデルが `rounds.yaml` の `model_results` に存在する。
- `model-result-summary.yaml` の `models` に、`rounds.yaml` の全モデルが存在する。
- `triage.yaml` の `items` は全件 `decision_status: decided` で、`final_label` が
  `must-fix` / `should-fix` / `leave-as-is` のいずれかである。
- `rounds.yaml` に存在する各モデルは、`triage.yaml` の `source_model` に現れるか、
  `model-result-summary.yaml` で `triage_status: no_findings` と明示される。
- `model-result-summary.yaml` に `triage_status: triage_pending` が残る review run は完了扱いにしない。
- `decision_status: human_required` が残る review run は完了扱いにしない。

この機械判定は「チャット上で表を提示したか」を直接検査するものではない。
代替として、モデル別まとめを永続成果物 `model-result-summary.yaml` として必須化し、
完了 manifest から参照可能にする。ユーザ向け報告では、この summary artifact の内容を
平易な説明つきで示してから、三段階トリアージと修正方針へ進む。

`model-result-summary.yaml` の最小項目は次のとおり。

```yaml
run_id: "<run-id>"
models:
  - model_id: claude-sonnet-4-6
    raw_path: raw/claude-sonnet-4-6.round-1.txt
    parse_status: parse_failed
    triage_status: triaged
    findings_count: 3
    must_fix_count: 0
    should_fix_count: 2
    leave_as_is_count: 1
    human_required_count: 0
```

`triage_status` は `triage_pending` / `triaged` / `no_findings` のいずれかとする。
`triage_pending` は runner が raw と summary を初期生成しただけで、finding 単位の判断が
まだ `triage.yaml` に移っていない状態を表す。
`triaged` は finding 単位の判断が `triage.yaml` に移された状態、
`no_findings` は raw を読んだうえで指摘なしと判断した状態を表す。
完了 manifest の機械判定では、`triage_pending` が残っていれば未完了として扱う。

## 実運用フロー

複数モデル API レビューでは、次の順序を守る。

1. `tools/api_providers/run_review.py` を `--review-run-dir docs/notes/review-runs/<run_id>` 付きで実行する。
2. `model-result-summary.yaml` と `review_summary.md` を読み、モデル別に raw 保存、parse 状態、所見件数をユーザへ示す。
3. `triage.yaml` 下書きの各 finding を、`must-fix` / `should-fix` / `leave-as-is` の三段階へ分類する。
4. `decision_status: human_required` の項目は、平易な説明と推薦案を添えて人間判断へ上げる。
5. 修正が必要な項目だけを反映し、反映後に post-write-verification manifest の `review_run:` から
   raw / rounds / summary / triage の整合を機械判定する。

`run_review.py` が生成する `triage.yaml` は下書きであり、`final_label` は自動確定しない。
初期状態では `decision_status: human_required` として残し、オーケストレーターまたは人間が
根拠を確認した後にだけ `decision_status: decided` へ進める。

## 今回分への扱い

今回の `docs/operations/EVALUATION.md` と `config/api-settings.yaml` のレビューでは、
最終 manifest と一部ログに要約は残っているが、全ラウンドの raw / parsed / finding 単位 triage は残っていない。
そのため、今回分は完全な監査再構成はできない。

次回以降は `--review-run-dir` を必須運用にし、必要に応じて個別の `--raw-out` と
`--parsed-out` も併用する。runner が生成した raw / parsed / rounds / summary を起点に、
raw から成形した結果を `triage.yaml` へ落としてから修正・人判断へ進む。

必須化の施行方法（CLI で必須にするか、workflow check / CI で検出するか）は後続実装で確定する。
それまでの暫定運用では、`--review-run-dir` の指定を含まないレビュー結果は監査ログとして不完全と扱う。

`config/api-settings.yaml` など設定ファイルを対象にする場合、raw 応答には対象ファイル本文が
含まれうる。現行の同ファイルはシークレット本体を持たない前提だが、将来シークレット値を
含む設定を対象にする場合は raw 保存先と共有範囲を別途制限する。

raw 応答の既定運用は非公開・最小共有とする。保存先はリポジトリ内に置く場合でも
公開・配布対象へ含めず、必要な担当者だけが読む。保持期間、暗号化、削除方針は後続で
正式化するが、シークレットを含む可能性がある対象では raw 保存先を通常の共有ログから分離する。

モデル同士の対話がある議論モードを採用する場合は、本メモの独立レビュー台帳とは別に
`discussion.yaml` を置く。少なくとも参加モデル、各発話の raw path、発話順、参照した前発話、
合意ではなく人判断へ上げた論点を記録する。議論モードの詳細スキーマは後続論点とする。
議論モードで生成した raw も、同じ run の raw 一覧から漏れないよう `rounds.yaml` の
`model_results` から参照するか、`discussion.yaml` を参照する橋渡し項目を置く。
`discussion.yaml` は発話順の台帳案、`aggregation_mode` は evaluation 取り込み後の
メタデータ案であり、どちらを正本フィールドにするかは後続の変換規則で確定する。

`tools/api_providers` 由来の review run 証拠を、`EVALUATION.md` が定める
`api_mediated` 証拠として取り込む変換規則は未確定である。`docs/notes/review-runs/<run_id>/`
を `experiments/analysis/imports/` 配下の可搬証拠束へ変換する規則を後続論点として扱う。
`parse_status=parse_failed` の round、または `decision_status=human_required` が残る triage は、
変換規則が確定するまで標準比較候補へ入れない。

今回分で部分的に残っている記録は、post-write manifest
`.reviewcompass/post-write-verification/post-write-2026-06-03-015.yaml` と、端末ログ上の
一部の構造化出力である。全 raw と全ラウンドの triage 台帳は存在しない。
台帳不存在の review run 証拠は、変換規則が確定するまで `parse_status=parse_failed`
または `decision_status=human_required` を含む証拠と同じく、標準比較候補へ入れない。

## 2026-06-03 追加 raw 取得と暫定トリアージ

本メモの post-write verification 対象について、次の 3 モデルの raw 応答を追加取得した。
モデル ID は `config/api-settings.yaml` の当該 variant で使った実行時値である。
当初 `/private/tmp/` に保存した raw は一時保存に過ぎないため、同内容を
`docs/notes/review-runs/postwrite-vocab-2026-06-03-r1/raw/` へ永続保存した。

- `claude-sonnet-4-6`: `docs/notes/review-runs/postwrite-vocab-2026-06-03-r1/raw/claude-sonnet-4-6.round-1.txt`
  - sha256: `fd7caf8059ac2463c51db31b33b7cbbc06304309d842d1a5e02a0523f4cdafc5`
- `gpt-5.4`: `docs/notes/review-runs/postwrite-vocab-2026-06-03-r1/raw/gpt-5.4.round-1.txt`
  - sha256: `bad3f0d8e1282cd2ff29f127e7882e44b6647f01709fe1abec6316cef3c7cd81`
- `gemini-3.1-pro-preview`: `docs/notes/review-runs/postwrite-vocab-2026-06-03-r1/raw/gemini-3.1-pro-preview.round-1.txt`
  - sha256: `78fe7cb98f881fb915e2d621c0a706155a32292cd0c790d2847eb09d59a91c29`

暫定トリアージでは、foundation 正本語彙へ正規化した `final_label` として
`must-fix` 2 件、`should-fix` 11 件、`leave-as-is` 6 件を確認した。
`should-fix` / `leave-as-is` のうち、台帳階層、raw 保存境界、主体記録、pending lifecycle、議論モード raw 参照に関するものは
本メモへ反映した。

`must-fix` 所見はどちらも評価上の扱いに関わるため、最終判断は人間に留保する。

- 独立レビュー群のオーケストレーター集約と、モデル間対話を伴う議論モードを、
  `api_mediated` 証拠の評価集計で同じ母集団に混ぜるかどうか。
  推薦案は、現行では混ぜず、後続の変換規則で `aggregation_mode: independent_orchestrated`
  と `aggregation_mode: discussion` を分けて記録すること。
- `parse_failed`、`decision_status=human_required`、raw/triage 台帳不存在の review run 証拠を、
  完全破棄相当の `rejected` にするか、探索分析に限って `admitted_exploratory` を許すか。
  推薦案は、現行では安全側に `rejected` とし、探索利用を許す場合は人間の明示 opt-in と
  caveat 記録を必須にすること。
