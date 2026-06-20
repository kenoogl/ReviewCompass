---
date: 2026-06-20
record_type: experiment-report
status: active
topic: APIレビュー用プロンプト方式の比較
related:
  - docs/disciplines/discipline_llm_as_judge_prompting.md
  - docs/operations/SESSION_WORKFLOW_GUIDE.md#vertical-intent-transfer-review
  - docs/operations/API_REVIEW_PROMPT_QUALITY.md
  - templates/review/api_review_criteria_template.md
  - templates/review/api_review_prompt_quality_criteria_template.md
  - docs/notes/working/2026-06-20-api-review-prompt-quality-side-track.md
  - .reviewcompass/specs/workflow-management/reviews/2026-06-20-workflow-management-design-vertical-redo-review-run/
  - .reviewcompass/specs/workflow-management/reviews/2026-06-20-workflow-management-design-vertical-redo-prompt-quality-run/
  - .reviewcompass/specs/workflow-management/reviews/2026-06-20-workflow-management-design-vertical-redo-review-run-v2/
---

# APIレビュー用プロンプト方式の比較レポート

## 目的

本レポートは、`workflow-management` design triad-review で実施した旧方式の API review-run と、新しいプロンプト品質レビュー付き方式の差分を記録する。

比較した問いは次である。

> API review-run の前に、レビュー用プロンプト自体を adversarial / judgment で品質確認すると、レビュー結果にどのような違いが出るか。

今回の対象は `workflow-management` の Requirement 13〜16 を design へ縦方向に再伝達する reopen R-0 の design triad-review である。

## 比較対象

### 旧方式

Review-run：

- `.reviewcompass/specs/workflow-management/reviews/2026-06-20-workflow-management-design-vertical-redo-review-run/`

実行内容：

- `--criteria-file`: `review-target.md`
- `--target`: `review-target.md`
- 実際の target manifest: `review-target.md`
- 3 役: `gpt-5.4` / `claude-sonnet-4-6` / `gemini-3.1-pro-preview`

結果：

| model | findings |
|---|---:|
| gpt-5.4 | 0 |
| claude-sonnet-4-6 | 0 |
| gemini-3.1-pro-preview | 0 |

旧方式の問題は `prompt-audit-summary.md` に記録済みである。主な問題は、プロンプトが `design.md` をレビュー対象として語っている一方、実際の `# Target document` と `target-manifest.yaml` は `review-target.md` だったことである。

### 新方式

Prompt quality run：

- `.reviewcompass/specs/workflow-management/reviews/2026-06-20-workflow-management-design-vertical-redo-prompt-quality-run/`

Corrected design review run：

- `.reviewcompass/specs/workflow-management/reviews/2026-06-20-workflow-management-design-vertical-redo-review-run-v2/`

実行内容：

1. main が `design-review-criteria-draft.md` を作成した。
2. `claude-sonnet-4-6` が adversarial としてプロンプト素案をレビューした。
3. adversarial は 5 件のプロンプト品質所見を返した。
4. main が 5 件を反映した。
5. `gemini-3.1-pro-preview` が judgment として、修正版プロンプトの使用可否を判定した。
6. judgment は `findings: []` を返した。
7. 修正版 criteria を使い、`design.md` を実 target として design triad-review を再実行した。

Corrected run の target:

- `--criteria-file`: `design-review-criteria-draft.md`
- `--target`: `.reviewcompass/specs/workflow-management/design.md`
- 実際の target manifest: `.reviewcompass/specs/workflow-management/design.md`

結果：

| model | findings | severity |
|---|---:|---|
| gpt-5.4 | 6 | ERROR:5, WARN:1 |
| claude-sonnet-4-6 | 9 | ERROR:5, WARN:3, INFO:1 |
| gemini-3.1-pro-preview | 0 | - |
| 合計 | 15 | ERROR:10, WARN:4, INFO:1 |

## 入力構造の違い

| 観点 | 旧方式 | 新方式 |
|---|---|---|
| 実 review target | `review-target.md` | `design.md` |
| criteria と target の分離 | なし。同じファイルを使用 | あり。criteria はレビュー観点、target は design 本文 |
| target manifest | `review-target.md` のみ | `design.md` |
| 上流資料 | requirements / design の要約中心。source_documents は path 列挙 | Requirement 12 context と Requirement 13〜16 の目的・転送要件・禁止事項を criteria に明示 |
| プロンプト品質確認 | 実行後に人手で問題発見 | 実行前に adversarial / judgment で確認 |
| 旧失敗の再発防止 | 明示なし | `design.md` を唯一の review target と明記 |

最大の違いは、旧方式ではモデルが「レビュー用の要約」を見ていたのに対し、新方式ではモデルが実際の `design.md` を target として読んだことである。

## プロンプト品質レビューで見つかった問題

adversarial は、修正版プロンプト素案に対して次の 5 件を指摘した。

| 指摘 | severity | 反映 |
|---|---|---|
| front matter の source_materials が path-only に見える | WARN | front matter は provenance のみと明示し、本文に埋め込んだ材料キーを記録 |
| 旧失敗の説明はあるが、同じ target-selection error を禁止していない | WARN | `design.md` を唯一の review target と明記 |
| Required Check 9 が Requirement 12 を参照するが、Requirement 12 の内容がない | WARN | Requirement 12 registry / preflight context を追加 |
| unsupported addition の severity が不明 | INFO | downstream を拘束する未根拠追加は ERROR と明記 |
| out of scope が commit/push 境界の finding まで抑制し得る | INFO | モデル自身の承認を禁じるだけで、境界に関する finding は許す文面に変更 |

judgment は反映後のプロンプトについて `findings: []` を返した。これにより、新方式では「プロンプトが最低限使えるか」を実レビュー前に検査できた。

## レビュー結果の違い

旧方式では全モデルが `findings: []` を返した。

新方式では 15 件の所見が出た。これらは 7 クラスタに整理された。

| cluster | triage案 | 内容 |
|---|---|---|
| C1 | must-fix | operation contract / registry / preflight authority boundary が未整理 |
| C2 | must-fix | 19 required_action mapping と compound operation detail が不足 |
| C3 | must-fix | approval record binding と proxy / human boundary が不足または矛盾 |
| C4 | must-fix | active reopen scope の正本 state structure が未定義 |
| C5 | must-fix | Phase 0 completion criteria / D-003 traceability が design level で不十分 |
| C6 | should-fix | structured prompt length-bound check の source of truth が未定義 |
| C7 | should-fix | design drafting status と implementation status の表現が混ざる |

旧方式の `findings: []` は、設計が完全だったことを示したのではなく、実際にはプロンプトが design 本文を十分に審査させていなかった可能性が高い。

## 何が検出可能になったか

新方式では、特に次の種類の問題が見えるようになった。

### 1. 要約では隠れる本文内矛盾

旧方式の `review-target.md` は、design が registry / contract 境界を整理しているという要約を持っていた。

新方式では `design.md` 本体を target にしたため、次のような本文内の矛盾が検出された。

- `stages/operation-registry.yaml` と `stages/operation-contracts.yaml` のどちらが contract authority か
- operations docs / script implementation が precheck vocabulary の authority に見える箇所
- proxy_model が approval stage を代行できる旧モデルと、phase approval は human-only という新モデルの矛盾

### 2. 「設計で決めるべきこと」と「tasks が後で決めること」の分離

新方式では、Requirement 13〜16 の上流意図を criteria に明示したため、次の不足が設計問題として検出された。

- 19 `required_action` の個別 mapping
- `run_maintenance` / `run_workflow_stage` の branch / internal step / max effect / approval aggregation
- `decision_scope` を operation / required_action ごとにどう決めるか
- active reopen scope の正本 state structure

これらは tasks.md で補えばよい詳細ではなく、design が権限を持って決めるべき事項として露出した。

### 3. 上流接続レビュー固有の問題

Requirement 16 は active reopen scope と historical `spec.json.reopened` を区別することを要求する。旧方式ではこの問いが要約内で「区別している」と見えた。

新方式では、区別を宣言しているだけで、active scope がどこに保存され、`next --json` が何を読むのかが設計されていない、という不足が検出された。

これは `SESSION_WORKFLOW_GUIDE.md#vertical-intent-transfer-review` の「上流目的・責務境界・受入条件が対象成果物へ欠落なく引き継がれているか」という観点が効いた例である。

## モデルごとの差

| model | 旧方式 | 新方式 | 観察 |
|---|---:|---:|---|
| gpt-5.4 | 0 | 6 | 本文内矛盾、authority boundary、human/proxy contradiction を多く検出 |
| claude-sonnet-4-6 | 0 | 9 | 19語彙 mapping、compound operation、active scope など design authority 不足を広く検出 |
| gemini-3.1-pro-preview | 0 | 0 | 今回は最終判定役として保守的に no findings。prompt quality judgment では使用可判定に有効だった |

`claude-sonnet-4-6` は、利用者方針どおり adversarial として有効に働いた。`Opus-4-8` は使用していない。

## 解釈

今回の差分は、モデル性能差だけでは説明できない。最も大きな要因は、プロンプトの構造である。

旧方式は、criteria と target が同一の author-written summary だったため、モデルは「要約の自己整合性」を審査しやすかった。

新方式は、criteria と target を分離し、target manifest に `design.md` を置き、criteria 側に上流意図と禁止事項を明示した。これにより、モデルは「上流要件と design 本文の照合」を行えるようになった。

つまり、新方式の効果は次の 3 点である。

1. 審査対象の取り違えを防いだ。
2. 上流接続レビューに必要な材料を prompt 内に入れた。
3. 実レビュー前に prompt 自体を adversarial / judgment で検査し、レビュー不能な prompt を弾いた。

## 今後の運用ルール案

API review-run を開始する前に、少なくとも次を確認する。

1. `--target` は実際の審査対象本文であること。
2. `--criteria-file` は審査観点・上流材料・範囲外・finding policy を持つこと。
3. criteria と target を同じ author-written summary にしないこと。
4. `target-manifest.yaml` に実審査対象が入ること。
5. source materials は path-only にせず、必要な本文または構造化要約を prompt 内に入れること。
6. 縦方向意図監査では、上流の目的、責務境界、受入条件、禁止事項、未確定事項、対象 phase へ引き継ぐべき判断を含めること。
7. 実レビュー前に、main が素案作成、adversarial がプロンプト品質レビュー、judgment が使用可否判定を行うこと。

## 汎用テンプレート化

上記の運用ルールは、今回の `workflow-management` design review だけに閉じず、API review-run 前の共通手順として抽象化した。

汎用手順とテンプレートは次に配置した。

- `docs/operations/API_REVIEW_PROMPT_QUALITY.md`
- `templates/review/api_review_criteria_template.md`
- `templates/review/api_review_prompt_quality_criteria_template.md`

これらは「APIレビュー用プロンプトを作成し、そのプロンプト自体を品質確認する仕組み」を定めるものであり、今回の v2 design review 所見を本線 gate 完了根拠として自動採用するものではない。v2 design review の C1〜C7 は、後続の本線 triage gate で利用者へ提示し、別途判断する。

## 残課題：手作業運用時の runner / 停止条件ミス

2026-06-20 の proxy_model 判断準備では、プロンプト品質レビューの考え方自体は有効だった一方、手作業運用で次の問題が発生した。

- proxy_model 本判断には `tools/api_providers/run_proxy_decision.py` を使うべきところ、一度 `tools/api_providers/run_role.py` を使い、C1〜C7 の判断ではなくプロンプト出力契約への追加レビューを得た。
- prompt quality judgment の `WARN` / `INFO` をどこまで修正して打ち切るかの運用基準が曖昧で、細部修正ループが長くなった。
- proxy_model 本判断の成功条件（`decisions` list と `proxy_model_id` を持つこと）と、誤経路検出条件（`findings` が返ったら本判断ではないこと）が機械的に事前確認されていなかった。
- C1〜C7 という複数の独立判断を 1 つの proxy_model 判断 prompt に押し込んだため、注意が発散し、出力契約や全件 traceability の調整に意識が寄りやすくなった。本来は判断項目ごとに prompt を分け、それぞれ prompt quality review を通すべきだった。

これは、API レビュー用プロンプト作成の思想そのものの否定ではなく、手作業で runner 選択・停止条件・出力契約を管理している間に起こる運用ミスである。将来、次が機械処理化されれば収束する見込みがある。

1. review purpose から runner を一意に選ぶ preflight（prompt quality は `run_role.py`、proxy decision は `run_proxy_decision.py`）。
2. prompt quality review の severity 別停止基準（`CRITICAL` / `ERROR` は修正必須、`WARN` は修正または明示採用、`INFO` は原則記録のみ等）。
3. proxy decision 実行前の出力契約 preflight（`decisions`、`proxy_model_id`、cluster / finding traceability、authority limit confirmation）。
4. 誤経路検出（proxy decision で `findings` 形式が返った場合は本判断として扱わず停止）。
5. 反復上限（adversarial 1 回、judgment 最大 N 回を超えたら利用者判断へ戻す）。
6. 判断粒度 preflight（複数の独立 cluster / finding / design-policy 判断を 1 prompt にまとめず、判断項目ごとに prompt・prompt quality review・proxy decision を分ける）。
7. 外部 API 送信基準（ReviewCompass リポジトリ内の仕様・設計・レビュー要約・証跡パスは、秘密情報・個人情報・第三者送信禁止情報を含まない限り、利用者が API review / proxy_model 判断を明示承認した場合の通常レビュー材料として扱う）。

この残課題は、今回の本線 design triad-review 所見 C1〜C7 の採否判断とは別に扱う。現時点では追加実装へ広げず、機械処理化対象の運用課題として記録する。

## 結論

今回の新方式により、旧方式では `findings: []` になっていた design triad-review から、実際には C1〜C7 の設計課題が検出された。

これは、プロンプト品質が API review-run の結果に直接影響すること、特に縦方向意図監査では target materialization と upstream materialization が不可欠であることを示している。

したがって、今回のような上流接続を含む API review-run では、レビュー対象本文と criteria を分離し、実レビュー前にプロンプト自体を 2 者レビューする運用を標準化するべきである。
