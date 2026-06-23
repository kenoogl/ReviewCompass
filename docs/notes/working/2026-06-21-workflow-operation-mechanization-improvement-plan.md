---
date: 2026-06-21
record_type: working-note
status: draft
topic: workflow-operation-mechanization-improvement
related:
  - .reviewcompass/backlog/plans/plan-2026-06-23-effective-prompt-freshness-audit.yaml
  - docs/notes/working/2026-06-18-mechanized-workflow-execution-design.md
  - docs/operations/WORKFLOW_NAVIGATION.md
  - docs/operations/WORKFLOW_DISCIPLINE_MAP.yaml
  - .reviewcompass/specs/workflow-management/requirements.md
  - .reviewcompass/specs/workflow-management/design.md
  - .reviewcompass/specs/workflow-management/tasks.md
---

# Workflow Operation 機械化改善計画

## 1. 背景

今回の開発で、workflow の入口はかなり機械化された。

- `next --json` で workflow 上の唯一地点を得る
- その地点で読むべき effective prompt を得る
- `spec.json` 更新、commit、push などの不可逆操作は guard / precheck / 承認を通す

一方で、effective prompt を読んだ後の処理にはまだ手作業の組み立てが残っている。また、effective prompt 自体も完全に「事前生成済みのものを読むだけ」にはなっておらず、その場で元文書や規律を解釈して追加構成する場面がある。

このため、現在の到達点は「入口の機械化」であり、地点内 operation の機械化は未完成である。

## 2. 課題整理

### 2.1 Effective Prompt が読むだけになっていない

effective prompt は地点別の実行指示として固定されるべきだが、現状は次が混在している。

- 生成済み effective prompt を読む
- `next --json` の返却値からその場で規律を再解釈する
- 足りない情報を LLM が検索して、実質的に追加 prompt を組み立てる
- API review prompt や proxy decision prompt を別途その場で作文する

結果として、effective prompt が「唯一の地点入力」として十分に閉じていない。

### 2.2 Effective Prompt 後の Operation が緩い

effective prompt を読んだ後に何をするかは、まだ LLM の手作業判断に依存している。

緩い例:

- API レビュー用 prompt の構成
- 上流資料本文をどこまで含めるか
- main preanalysis の作成
- triad-review 結果の同根クラスタ化
- proxy_model に渡す判断単位の分割
- `must-fix` / `should-fix` / `leave-as-is` のトリアージ
- 実装修正後の確認順序

これらは規律やメモで方針が整ってきたが、まだ「operation contract から次に実行すべき処理、入力、停止条件が一意に出る」状態ではない。

### 2.3 API Review Prompt の品質が不安定

過去の試行で次の問題が出た。

- 複数の判断を1つの prompt に詰め込み、注意が発散した
- 要件や設計の該当部分を本文ではなくパスだけで渡した
- 上流との接続を考慮すべき場面で、一般的な API review 観点だけに寄った
- review prompt 自体の品質監査が不足した
- proxy_model に任せる前提なのに、利用者の関与を前提にした運用へ戻りかけた

これらは LLM の能力不足というより、operation の入力と出力が機械的に確定していなかったことが原因である。

## 3. 改善方針

### 3.1 監査を先に置く

この計画は、`.reviewcompass/backlog/plans/plan-2026-06-23-effective-prompt-freshness-audit.yaml` の実装を前提にする。

理由:

- stale な effective prompt を読んだ状態で operation を機械化しても、古い規律に従うだけになる
- 元文書と effective prompt の同期が保証されていなければ、operation contract の信頼性も下がる
- 監査があれば、元文書変更後の prompt 更新漏れを先に止められる

したがって順序は次とする。

1. effective prompt freshness audit
2. effective prompt 再生成導線
3. operation contract / prompt generation 機械化

### 3.2 Effective Prompt の役割を縮小する

effective prompt は、巨大な手順書ではなく「その地点での言語タスク仕様」とする。

含めるもの:

- decision point
- 現在地点の要約ではなく機械判定結果
- この地点で有効な規律
- LLM が担当する language task
- output contract
- 禁止事項
- 次 operation への入口

含めないもの:

- commit / push / spec-set などの機械操作を LLM に直接実行させる手順
- API review prompt の自由作文
- source bundle をその場で探す作業
- 複数判断をまとめた曖昧な依頼

### 3.3 Operation Contract へ寄せる

effective prompt の後に必要な処理は、operation contract として分解する。

候補 operation:

- `prepare_review_source_bundle`
- `prepare_main_preanalysis`
- `prepare_api_review_prompt`
- `audit_api_review_prompt`
- `run_triad_review`
- `cluster_review_findings`
- `prepare_proxy_decision_prompt`
- `run_proxy_decision`
- `record_proxy_decision`
- `apply_triage_fix`
- `record_alignment_evidence`
- `prepare_lightweight_self_check`
- `prepare_commit`

各 operation は次を持つ。

```yaml
operation_id: prepare_api_review_prompt
decision_point_kinds: []
required_inputs: []
source_bundle_policy: non_summary_excerpt_required
output_paths: []
output_schema: null
approval_required: false
effect_kind: write
preconditions: []
postconditions: []
stop_condition: null
next_operation: null
```

### 3.4 Source Bundle を機械化する

レビューや proxy 判断に渡す資料は、LLM がその場で探して組み立てるのではなく、operation が source bundle として作る。

原則:

- パスだけを渡さない
- 必要本文または非要約の該当範囲を含める
- 要約を使う場合は `summary` と明示する
- 要約禁止の場面では、該当本文の原文を含める
- source bundle に含めたファイル、範囲、SHA を記録する

### 3.5 判断を小さく分割する

proxy_model や API review に渡す判断は、項目ごとに分割する。

理由:

- 複数判断を1 prompt に詰め込むと注意が発散する
- 判断理由が曖昧になる
- 後から triage や再実行が難しくなる

原則:

- 1 prompt = 1 主判断
- 必要なら shared source bundle を参照する
- 出力は構造化 YAML
- 判断不能なら `insufficient_information` を許可する

### 3.6 Review Prompt 自体を監査対象にする

API review prompt はレビュー品質を左右するため、実行前に prompt audit を行う。

監査観点:

- 一般的な API review 観点が含まれているか
- 場面固有の縦方向接続が含まれているか
- source bundle が本文を含んでいるか
- パスだけになっていないか
- 複数判断を詰め込みすぎていないか
- main preanalysis の不足観点を検出できるか
- output contract が明確か
- reviewer に求める役割が明確か

## 4. 実装順序

### Phase 0: 監査計画の実装待ち

effective prompt freshness audit が最低限動くまで、この計画の本実装は始めない。

### Phase 1: 現状 operation 棚卸し

`next_action.kind` ごとに、effective prompt 後に LLM が手作業で組み立てている処理を列挙する。

成果物:

- operation 候補一覧
- 手作業依存箇所一覧
- 機械化優先度

### Phase 2: 低リスク地点から contract 化

まず低リスク地点を対象にする。

- `completed`
- `lightweight_self_check`
- `commit_candidate`

ここで、operation contract の形式、precondition、postcondition、stop condition を固定する。

### Phase 3: Review 系 Operation へ拡張

次に review 系へ進む。

- `triad-review`
- `review-wave`
- `alignment`
- `approval`

特に `triad-review` は、source bundle、main preanalysis、API review prompt、prompt audit、review-run 実行、結果整理を分けて扱う。

### Phase 4: Prompt Generation の機械化

API review prompt / proxy decision prompt を operation contract と source bundle から生成する。

受入条件:

- 手作業で prompt を作文しない
- 生成 prompt に source bundle の本文が含まれる
- output contract が毎回同じ形式で入る
- prompt audit を通らないと API review を起動しない

### Phase 5: Proxy Decision の分割実行

proxy_model に渡す判断単位を小さくし、各 prompt / raw response / decision / rationale を保存する。

受入条件:

- 1 prompt = 1 主判断
- proxy decision の raw response が保存される
- 採用案と判断理由が保存される
- main LLM が後処理する場合も、判断根拠が追跡できる

### Phase 6: next / operation-prompt 連携

`next --json` から次 operation が機械可読に分かるようにする。

候補:

```yaml
next_action:
  kind: stage
  phase: design
  stage: triad-review
  next_operation:
    id: prepare_review_source_bundle
    contract_path: .reviewcompass/operation-contracts/prepare_review_source_bundle.yaml
```

## 5. テスト方針

TDD で進める。

初期テスト:

1. `lightweight_self_check` が operation contract から必要 manifest 形式を返す
2. `completed` が追加作業なしの言語出力だけを許す
3. `commit_candidate` が commit preflight と approval 導線だけを許す
4. review source bundle がパスだけの資料を拒否する
5. 要約禁止場面で summary-only source を拒否する
6. API review prompt が複数主判断を含む場合に audit が WARN/DEVIATION を返す
7. proxy decision prompt が 1 主判断に分割されていることを検査する
8. prompt audit 未完了の review-run 起動を拒否する

## 6. 受入条件

この改善が一区切りになる条件:

- `next --json` の地点から次 operation が機械可読に分かる
- effective prompt はその地点の言語タスク仕様に限定される
- source bundle は機械的に生成され、本文または非要約範囲を含む
- API review prompt / proxy decision prompt は自由作文ではなく生成物になる
- prompt audit を通った prompt だけが API review に使われる
- proxy 判断は小さい単位で保存され、後処理の根拠が追跡できる
- 手作業の組み立てが残る場合は、明示的に `manual_decision_required` として記録される

## 7. 未決事項

- operation contract の保存場所
- `next --json` が直接 `next_operation` を返すか、別コマンドで取得するか
- operation-prompt と effective prompt の境界
- review prompt の「一般観点」と「場面固有観点」の標準スキーマ
- main preanalysis をどの operation の成果物にするか
- prompt audit の reviewer を main / adversarial / judgment のどれにするか
- proxy_model の variant default をどの registry に固定するか

## 8. 結論

現状の workflow は、入口の一意化と effective prompt 読み込みまでは進んだが、地点内処理にはまだ LLM の手作業組み立てが残っている。

次の改善は、いきなり review prompt 生成を増やすことではなく、まず effective prompt freshness audit を整えること。そのうえで、effective prompt 後の処理を operation contract、source bundle、prompt audit、proxy decision 分割へ順に落としていく。
