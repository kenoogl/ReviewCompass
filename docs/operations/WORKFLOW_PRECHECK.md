# WORKFLOW_PRECHECK：ワークフロー事前検査スクリプトの正本仕様

最終更新：2026-06-04（自律・並列実行計画 `autonomous-plan` と履歴台帳ガードを追加）／2026-06-03（commit 時 post-write-verification 監査と audit-commit 追加、commit 承認レコードガード追加。Codex adapter migration：段階 3 hook 記述を実行環境 adapter 方針へ整理）／2026-05-25 セッション 24（新設、補助層 C 段階 2 の仕様確定）
位置付け：運用文書（`docs/operations/` 配下）、計画書 §5.8 補助層 C の段階 2 の正本仕様

本文書は計画書 §5.8 補助層 C 共存モデルの **段階 2（外部スクリプトによる機械的判定）** の仕様を定める。段階 2 の実装は本文書を入力として進める。仕様の変更には利用者明示承認が必要（規律 §0.2 計画書方針変更に準じる）。

## 採用承認の出典

- 「共存モデルの採用」（2026-05-25 セッション 24、補助層 C 共存モデルの採用、計画書方針変更）
- 「A から順に進める」（2026-05-25 セッション 24、文書反映の着手順序指示）
- 「次に進む」（2026-05-25 セッション 24、段階 2 仕様策定への着手）
- 「範囲案 2」（2026-05-25 セッション 24、対象範囲を spec.json ＋ commit ＋ push に確定）
- 「論点 A は、実装テスト段階でも効果測定やデバッグで必要になるのではないか？」（2026-05-25 セッション 24、実行ログ取得を MVP 必須として位置付け）
- 「論点 B は、渡す」（2026-05-25 セッション 24、`--rationale` 引数の採用）
- 「論点 C は別文書」（2026-05-25 セッション 24、本文書の独立新設）
- 「ア」（2026-05-25 セッション 24、派生論点の中間案採用と本文書起草の承認）

## 1. 概要と位置付け

### 1.1 何のための仕様か

ワークフロー事前検査スクリプト（以降「本スクリプト」）は、私（LLM、メインセッション）が ReviewCompass の開発作業を進めるとき、不可逆操作（spec.json 修正・git commit・git push）の **直前に呼び出して、当該操作が現在のワークフロー状態と整合するかを機械的に判定する** ためのコマンドラインツール。

### 1.2 共存モデル全体での位置付け

計画書 §5.8 補助層 C 共存モデルは 3 段階の役割分担で構成される：

- **段階 1（LLM 規律、恒久層）**：これから何をするかを応答内で明示、本スクリプトを呼び、出力を解釈して次の行動を決める
- **段階 2（外部スクリプト、本仕様の対象）**：spec.json／git／規律ファイル／持ち越し所見を読み、引数の処理が現状で適切かを判定して返す
- **段階 3（実行環境別 hook adapter）**：ツール呼び出し（Edit／Write／Bash 等）の前に段階 2 を自動で走らせ、逸脱なら遮断

本スクリプトは段階 2 の本体。段階 1 と段階 3 の両方から呼ばれ得る。

### 1.3 関連文書

- 計画書 §5.8 補助層 C（採用方針の正本）
- 議論メモ：[docs/notes/2026-05-25-workflow-pre-check-and-discipline-consolidation.md](../notes/2026-05-25-workflow-pre-check-and-discipline-consolidation.md)（議論経緯）
- TODO §3 セクション D（残作業の管理）
- spec.json 正本スキーマ：計画書 §5.24
- 運営ガイド：[docs/operations/SESSION_WORKFLOW_GUIDE.md](SESSION_WORKFLOW_GUIDE.md)

## 2. 共存モデルにおける段階 2 の役割

### 2.1 単一責任

段階 2 は **判定のみ** を行う。承認や合意の取得、状態の書き換え、エスカレーションは行わない。

具体的に：

- **行う**：状態を読み、判定して結果を返す、判定履歴をログに残す
- **行わない**：spec.json の書き換え（それは段階 1 が承認後に行う）、利用者への問い合わせ（それは段階 1 の役割）、強制遮断（それは段階 3 のフック設定の役割）

### 2.2 段階間のインターフェース

```
段階 1（LLM）：意図宣言
  ↓ 引数を渡してスクリプトを呼び出す
段階 2（本スクリプト）
  ↓ 終了コード ＋ 標準出力（人間可読 or JSON）
段階 1（LLM）：出力を解釈して処理続行可否を判断
```

段階 3 導入後は、段階 1 が呼び忘れた場合に各実行環境の hook adapter が同じスクリプトを自動発動する。

## 3. 適用範囲（範囲案 2）

### 3.1 対象とする処理

3 つの不可逆操作を対象とする：

1. **spec.json の `workflow_state` 修正**：機能単位 spec.json の段の真偽値を変更する操作
2. **git commit**：作業ツリーの変更を確定する操作
3. **git push**：ローカルコミットを `origin` に送る操作

### 3.2 適用範囲外（将来拡張の候補）

範囲案 2 では次は対象としない（範囲案 3 への拡張時に検討）：

- 仕様文書ファイル（`design.md`／`requirements.md`／`tasks.md`／`implementation.md` 等）の編集前検査
- 計画書（`docs/plan/`）の編集前検査
- 応答テキストのみの判断（例：「完了」「承認済」の断定）は段階 2 では機械判定不可、段階 1 規律の責務

### 3.3 拡張時の責務

将来の範囲案 3 への拡張は、本文書を改訂して仕様を追加する（規律 §0.2 計画書方針変更に該当、利用者明示承認必須）。

## 4. サブコマンド体系

3 つのサブコマンドを持つ：

```
check-workflow-action.py spec-set <feature> <phase> <stage> <new-value> [--rationale "<理由>"]
check-workflow-action.py commit --rationale "<理由>"
check-workflow-action.py push --rationale "<理由>"
check-workflow-action.py autonomous-plan <plan.yaml>
check-workflow-action.py audit-commit <commit-ish>
guarded-git-commit.py -m "<commit message>" --rationale "<理由>"
```

共通オプション：

- `--json`：機械可読の JSON 出力に切り替え（未指定時は人間可読）
- `--log-path <path>`：ログ書き出し先の上書き（既定 `docs/logs/workflow-precheck.log`）
- `--help`：使い方表示

## 5. 引数仕様

### 5.1 `spec-set` サブコマンド

```
check-workflow-action.py spec-set <feature> <phase> <stage> <new-value> [--rationale "<理由>"]
```

引数：

| 引数 | 必須 | 値の例 | 説明 |
|---|---|---|---|
| `<feature>` | 必須 | `foundation`／`runtime`／…／`conformance-evaluation` | 対象機能名、`stages/feature-dependency.yaml` の `features` キーと一致 |
| `<phase>` | 必須 | `intent`／`feature-partitioning`／`requirements`／`design`／`tasks`／`implementation` | 対象フェーズ |
| `<stage>` | 必須 | `drafting`／`triad-review`／`review-wave`／`alignment`／`approval` 等 | 対象段、フェーズにより値が異なる（計画書 §5.5） |
| `<new-value>` | 必須 | `true`／`false` | 設定したい新しい真偽値 |
| `--rationale` | 任意 | 自由文字列 | この変更を行う理由（ログ記録用、判定には影響しない） |

`--rationale` を任意とする理由：`spec-set` は機械的整合判定が中心、理由を渡しても判定そのものは変わらない。ただしログ記録のため渡すことを推奨。

### 5.2 `commit` サブコマンド

```
check-workflow-action.py commit --rationale "<理由>"
```

引数：

| 引数 | 必須 | 説明 |
|---|---|---|
| `--rationale` | **必須** | このコミットを行う理由、利用者承認の発言出典を含めることを推奨 |

`--rationale` を必須とする理由：commit は不可逆操作のため、なぜ実行するかの根拠を残すべき。

commit は利用者の職掌範囲であり、LLM は利用者の明示指示なしに実行しない。機械判定では、`--rationale` に加えて `.reviewcompass/approvals/commit-approval.json` のユーザ承認レコードを必須とする。

承認レコードの最小形：

```json
{
  "approved_action": "commit",
  "approved_by": "user",
  "approved_at": "2026-06-03T00:00:00+09:00",
  "rationale": "利用者がコミットを明示承認",
  "target_files": ["path/to/file.md"],
  "expires_after_commit": true,
  "consumed": false
}
```

`target_files` は staged ファイルの許可範囲。`"*"` を含む場合は全 staged ファイルを許可する。`consumed: true` は消費済みとして逸脱扱いにする。

実行時は直接 `git commit` ではなく、次のラッパーを使う：

```
tools/guarded-git-commit.py -m "<commit message>" --rationale "<理由>"
```

このラッパーは `check-workflow-action.py commit` を先に実行し、exit 2 なら遮断する。exit 1（WARN）は既定では停止し、利用者判断で続行する場合だけ `--allow-warn` を付ける。commit 成功後、`expires_after_commit` が false でない承認レコードは `consumed: true` に更新する。

限界：repo 内スクリプトだけでは「承認レコードを誰が作成したか」を完全には保証できない。強い保証には、段階 3 hook adapter または実行環境側で、承認レコードの発行・更新を利用者操作に限定する必要がある。

また、commit 対象の staged ファイルに post-write-verification 対象（`docs/operations/`、`TODO_NEXT_SESSION.md` 等）が含まれる場合、対象ファイル群の現在 sha256 を覆う completed manifest を必須とする。manifest がない、sha256 が一致しない、coverage matrix が不足する、未解決本質的指摘がある場合は exit 2 とする。

### 5.3 `push` サブコマンド

```
check-workflow-action.py push --rationale "<理由>"
```

引数：

| 引数 | 必須 | 説明 |
|---|---|---|
| `--rationale` | **必須** | この push を行う理由、利用者承認の発言出典を含めることを推奨 |

`--rationale` を必須とする理由：push は origin に影響する不可逆操作、なぜ実行するかの根拠を残すべき。

### 5.4 `audit-commit` サブコマンド

```
check-workflow-action.py audit-commit <commit-ish>
```

指定 commit の変更ファイルを読み、post-write-verification 対象が含まれる場合に completed manifest が存在するかを遡及監査する。`<commit-ish>` は `HEAD` や commit hash を指定できる。root commit も監査対象に含める。

commit 済みの見落とし検出用であり、通常は commit 直前の `commit` precheck が主経路。`audit-commit` は commit 内の対象ファイル内容を `git show <commit-ish>:<path>` で読み、その sha256 と現在リポジトリ内に存在する manifest の `target_sha256` を照合する。

この監査は「対象 commit 時点に manifest が存在したか」を証明する時点監査ではなく、「現在のリポジトリ状態で、その commit 内容に対応する検証記録が存在するか」を確認する是正監査である。したがって、見落とし後に追加した manifest による是正完了を認める。

`<commit-ish>` が解決できない場合は逸脱（exit 2）とする。

### 5.5 `autonomous-plan` サブコマンド

```
check-workflow-action.py autonomous-plan <plan.yaml>
```

自律・並列モードで実装作業を始める前に、実行計画 YAML を検査する。目的は、並列化できる作業だけを切り出し、重要判断の停止条件と統合時の確認点を明示し、後から判断履歴を追える台帳を残すこと。

計画 YAML は最低限、次を持つ。

- `mode: autonomous_parallel`
- `run_id`
- `authorization`：`approved_by`、`approval_record_path`、`summary_presented_to_user`、`triage_presented_to_user`
- `tasks[]`：`task_id`、`source_finding_ids`、`assignee`、`allowed_paths`、`depends_on`、`expected_tests`、`stop_conditions`
- `integration_gate`：メインセッション確認、差分範囲確認、テスト確認、判断根拠確認
- `outputs_policy`：実装差分、検証結果、判断根拠、作業ノイズの扱い
- `history`：`ledger_path`、`record_task_assignments`、`record_decision_basis`、`record_integration_result`、`retention`

`history.ledger_path` は `docs/logs/autonomous-parallel/` 配下とする。`autonomous-plan` は検査結果をこの台帳へ YAML として書き出し、後から `run_id`、task ID、承認根拠、統合ゲート、出力分類、判定結果を確認できるようにする。

## 6. 判定ロジック

### 6.1 `spec-set` の判定

対象機能の spec.json（`.reviewcompass/specs/<feature>/spec.json`）を読み、次を機械判定：

#### `<new-value>` が `true` の場合（段を通過済みにする）

- **段の依存チェック**：同フェーズ内で当該段より前の段がすべて `true` か
  - 例：`requirements approval true` → `requirements alignment` が `true` か
  - 例：`design drafting true` → `requirements approval` が `true` か
- **フェーズの依存チェック**：上流フェーズの最終段（`approval`）が `true` か
  - 例：`design drafting true` → `requirements approval` が `true`、`feature-partitioning approval` が `true`、`intent approval` が `true`
- **機能横断段の整合**：`intent`／`feature-partitioning` は全機能で同じ値を持つべき（計画書 §5.24.4）。当該機能の値だけを変えると不整合
- **承認発言の有無は判定しない**：それは段階 1 規律の責務

#### `<new-value>` が `false` の場合（reopen に相当）

- 一般に許容（reopen 手続きの一部）
- ただし当該段が `true` だった場合は警告：「reopen を実施しています、reopen 手続き（計画書 §5.6）に従っていますか」

### 6.2 `commit` の判定

`git status` と `git diff --cached` を読み、次を機械判定：

- **ユーザ承認レコードの確認**：`.reviewcompass/approvals/commit-approval.json` を読み、`approved_action=commit`、`approved_by=user`、未消費、かつ staged ファイルが `target_files` の範囲内であることを確認
  - レコードなし、形式不正、消費済み、承認対象外ファイルがある場合：逸脱（exit 2）、commit を遮断推奨
- **post-write-verification 対象の完了確認**：staged ファイルに post-write-verification 対象が含まれる場合、対象ファイル群と現在 sha256 を覆う completed manifest があることを確認
  - manifest なし、sha256 不一致、coverage matrix 不足、未解決本質的指摘ありの場合：逸脱（exit 2）、commit を遮断推奨
- **持ち越し所見の確認**：`.reviewcompass/pending-cross-feature-findings.md` を読み、未消化所見の件数を出力
  - 未消化所見が 1 件以上ある場合：警告（exit 1）、commit は可能だが要注意
  - 0 件の場合：OK（exit 0）
- **対象ファイルの分類**：staged されたファイルを次の 3 群に分類して出力
  - 通常変更：仕様文書（`*.md`）、ソースコード（`*.py` 等）
  - 要注意変更：`spec.json`、`docs/plan/` 配下、計画書、規律ファイル
  - 危険変更：`.git/` 内、`secrets`／`credentials` を含むファイル名
- **要注意変更がある場合**：警告（exit 1）、根拠の確認を促す
- **危険変更がある場合**：逸脱（exit 2）、commit を遮断推奨

### 6.3 `push` の判定

`git status` と `git log` を読み、次を機械判定：

- **作業ツリーの clean 性**：未コミット変更がある場合は逸脱（exit 2）
- **ローカル先行コミット数**：`origin/main` から進んでいるコミット数を出力
- **直近 5 コミットの題名要約**：利用者が push 前に確認しやすい形で出力
- **push 先**：`origin/main` 以外への push が要求されていれば警告（exit 1）

### 6.4 `audit-commit` の判定

`git diff-tree --root --no-commit-id --name-only -r <commit-ish>` で指定 commit の変更ファイルを取得し、post-write-verification 対象だけを抽出する。

- 対象なし：OK（exit 0）
- 対象あり、かつ commit 内ファイル内容 sha256 を覆う completed manifest がある：OK（exit 0）
- 対象あり、manifest がない／sha256 不一致／coverage matrix 不足／未解決本質的指摘あり：逸脱（exit 2）
- `<commit-ish>` が解決できない：逸脱（exit 2）

### 6.5 `autonomous-plan` の判定

実行計画 YAML を読み、次を fail-closed で判定する。

- `mode` が `autonomous_parallel` である
- `run_id` がある
- `authorization.approved_by` が `user` または `proxy_model` である
- レビュー結果サマリと三段階トリアージが提示済みである
- 各 task に `source_finding_ids`、`allowed_paths`、`expected_tests`、`important_decision_requires_approval` 停止条件がある
- 別スレッドまたはサブ担当の task は `assignee.worktree_policy: separate_worktree` である
- 依存関係のない並列 task 同士で `allowed_paths` が衝突しない
- `integration_gate` の 4 条件がすべて `true` である
- `outputs_policy.work_noise` が `exclude` であり、作業ノイズを本線 repo に取り込まない
- `history` が台帳パス、タスク割当記録、判断根拠記録、統合結果記録、保存方針を持つ

検査に通った場合も、通らなかった場合も、`history.ledger_path` が妥当なら台帳を生成する。これにより、自律実行の開始可否、止まった理由、並列 task の境界、統合時の確認点を後から追跡できる。

## 7. 出力形式

### 7.1 終了コード体系

- `0`：問題なし、処理続行可
- `1`：警告あり、呼び出し側の判断で続行可
- `2`：逸脱検出、呼び出し側が遮断推奨

### 7.2 人間可読出力（既定）

標準出力に次の構造：

```
[VERDICT] OK / WARN / DEVIATION（exit <code>）
[ACTION] <サブコマンド名 ＋ 引数の要約>
[REASON]
  - <理由 1>
  - <理由 2>
[CURRENT STATE]
  <現状の要約、複数行可>
```

例（spec-set 逸脱の場合）：

```
[VERDICT] DEVIATION（exit 2）
[ACTION] spec-set foundation requirements approval true
[REASON]
  - workflow_state.requirements.alignment が false です（approval の前提が満たされていません）
[CURRENT STATE]
  foundation.requirements:
    drafting: true
    triad-review: true
    review-wave: true
    alignment: false  ← 問題箇所
    approval: false
```

### 7.3 JSON 出力（`--json` 指定時）

機械処理向けの構造化出力。段階 3 フック導入時に使う想定：

```json
{
  "verdict": "DEVIATION",
  "exit_code": 2,
  "action": {
    "subcommand": "spec-set",
    "args": {
      "feature": "foundation",
      "phase": "requirements",
      "stage": "approval",
      "new_value": true,
      "rationale": "..."
    }
  },
  "reasons": [
    "workflow_state.requirements.alignment が false です（approval の前提が満たされていません）"
  ],
  "current_state": {
    "foundation": {
      "requirements": {
        "drafting": true,
        "triad-review": true,
        "review-wave": true,
        "alignment": false,
        "approval": false
      }
    }
  }
}
```

## 8. ログ取得（MVP 必須）

### 8.1 書式

JSON Lines 形式（1 行 ＝ 1 判定）。`--json` 出力と同じ構造に `timestamp` を追加：

```json
{"timestamp":"2026-05-25T15:30:00+09:00","action":{"subcommand":"spec-set","args":{...,"rationale":"..."}},"verdict":"OK","exit_code":0,"reasons":[],"current_state":{...}}
```

### 8.2 配置

- 既定パス：`docs/logs/workflow-precheck.log`
- `--log-path` で上書き可（テスト時の隔離用）

### 8.3 取得方針（MVP）

- 毎回の判定を 1 行追記
- ローテーションは MVP では実装しない（将来検討、計画書 §5.8 第 5 層「処理表面積の抑制」と整合）
- 削除は手動操作のみ

### 8.4 ログの活用先

- テスト失敗時のデバッグ
- 規律遵守率の事後計測（議論メモ §「派生論点」、self-improvement の効果測定指標と接続）
- 誤判定の事後追跡

## 9. テスト方針

### 9.1 テストの種類

- **ユニットテスト**：Python 標準の `unittest` で実装
- **対象**：各サブコマンドの正常系・異常系
- **配置**：`tests/tools/test_check_workflow_action.py`

### 9.2 fixture 構造

```
tests/fixtures/spec-json-cases/
├── all-true/                  # すべての段が true の状態
│   └── spec.json
├── requirements-alignment-false/  # alignment が false の状態
│   └── spec.json
├── design-drafting-blocked/   # requirements.approval が false の状態
│   └── spec.json
└── …
```

### 9.3 必須テストケース

- **正常系**：
  - `spec-set foundation requirements approval true` ＋ alignment=true → exit 0
  - `commit` ＋ pending 所見 0 件 ＋ 通常変更のみ ＋ 有効なユーザ承認レコード → exit 0
  - `commit` ＋ post-write 対象文書 ＋ 有効なユーザ承認レコード ＋ completed manifest → exit 0
  - `audit-commit HEAD` ＋ post-write 対象文書 ＋ matching completed manifest → exit 0
  - `guarded-git-commit` ＋ 有効なユーザ承認レコード → commit 実行、承認レコード消費済み
  - `push` ＋ 作業ツリー clean ＋ 先行 1 コミット → exit 0
- **警告系**：
  - `commit` ＋ pending 所見 1 件以上 → exit 1
  - `commit` ＋ spec.json 変更含む → exit 1
  - `spec-set <stage> false` ＋ 現状 true → exit 1（reopen 警告）
- **逸脱系**：
  - `spec-set foundation requirements approval true` ＋ alignment=false → exit 2
  - `spec-set foundation design drafting true` ＋ requirements.approval=false → exit 2
  - `push` ＋ 作業ツリー dirty → exit 2
  - `commit` ＋ ユーザ承認レコードなし／消費済み／承認対象外 staged ファイルあり → exit 2
  - `commit` ＋ post-write 対象文書 ＋ completed manifest なし → exit 2
  - `audit-commit HEAD` ＋ post-write 対象文書 ＋ completed manifest なし → exit 2
  - `guarded-git-commit` ＋ ユーザ承認レコードなし → commit しない
  - `commit` ＋ `.git/` 内ファイル含む → exit 2

### 9.4 TDD の遵守（入口規律）

実装は次の順序で進める：

1. 期待される入出力に基づきテストを作成（実装コードは書かない）
2. テストを実行し、失敗を確認
3. テストが正しいことを確認できた段階でコミット
4. テストをパスさせる実装を進める
5. 実装中はテストを変更せず、コードを修正し続ける
6. すべてのテストが通過するまで繰り返す

## 10. 配置場所とディレクトリ構造

```
tools/
├── check-workflow-action.py        # スクリプト本体（実行ファイル、shebang あり）
├── guarded-git-commit.py           # commit 承認レコード検査つき git commit ラッパー
└── workflow_precheck/              # 補助モジュール（必要に応じて分割）
    ├── __init__.py
    ├── spec_loader.py              # spec.json 読み込み
    ├── git_reader.py               # git status／diff 読み込み（subprocess 経由）
    ├── pending_findings.py         # pending-cross-feature-findings.md 読み込み
    ├── judges.py                   # 判定ロジック（spec_set／commit／push）
    ├── output.py                   # 人間可読／JSON 出力の整形
    └── logger.py                   # ログ書き出し

tests/
├── tools/
│   └── test_check_workflow_action.py
└── fixtures/
    └── spec-json-cases/

docs/
├── logs/
│   └── workflow-precheck.log       # 実行ログ（自動生成、gitignore 候補）
└── operations/
    └── WORKFLOW_PRECHECK.md        # 本文書
```

ログファイル `docs/logs/workflow-precheck.log` は実行時に増え続けるため、`.gitignore` への追加を検討（個別判断、利用者と相談）。

## 11. 段階 1 規律との接続

### 11.1 段階 1 が本スクリプトをいつ呼ぶか

段階 1（LLM）の規律として、不可逆操作の **直前に必ず** 本スクリプトを呼ぶ：

- spec.json の `workflow_state` を変更する Edit／Write の直前 → `spec-set` 呼び出し
- `git commit` の直前 → `commit` 呼び出し。実行は原則 `guarded-git-commit.py` 経由
- `git push` の直前 → `push` 呼び出し

### 11.2 出力の解釈と次の行動

- exit 0：処理続行
- exit 1：警告内容を応答に明示、利用者に判断を求めるか自律続行かを規律で決める
- exit 2：処理を止めて利用者に報告

### 11.3 段階 1 規律の文書化（残作業）

段階 1 規律の具体的な文言（`AGENTS.md`、`CLAUDE.md`、または規律ファイルに追加する文）は、本仕様確定後の **項目 3：段階 1 の規律化** で起草する（TODO §3 D 残作業項目 3、利用者明示承認必須）。Codex では `AGENTS.md`、Claude Code では `CLAUDE.md` が入口規律になる。

## 12. 段階 3 フック導入時の拡張余地

### 12.1 発動条件

各実行環境の hook adapter（ツール呼び出し前のフック）で、次のとき本スクリプトを自動発動：

- **Edit／Write** で対象パスが `spec.json` を含む → `spec-set` 自動呼び出し
- **Bash** で commit 系コマンドを含む → `commit` 自動呼び出し
- **Bash** で push 系コマンドを含む → `push` 自動呼び出し

### 12.2 引数の取得方法

hook adapter は、ツール呼び出しの引数を受け取る。Edit の `file_path`、Bash の `command` 文字列から、本スクリプトの引数を自動構築：

- 例：Edit `file_path` が `.reviewcompass/specs/foundation/spec.json` → `spec-set` の `<feature>` を `foundation` に
- 例：Bash `command` が `git commit ...` → `commit` を呼ぶ

引数の自動抽出ロジックは各 adapter の hook 側スクリプトに実装する。Claude Code では `.claude/hooks/pre-tool-use.sh` 等、Codex では `.codex/hooks/` と `.codex/hooks.json` 等の配置に従う。

### 12.3 fail-closed の実現

- フック側で本スクリプトの exit code を見て、`exit code ≥ 2` ならツール呼び出しを遮断
- exit 1 は警告だけ表示してツール呼び出しを通す
- exit 0 はそのまま通す

### 12.4 段階 3 導入の前提

- 段階 2 のスクリプトが安定動作している（小規模運用の実測完了）
- 段階 1 規律が確立されている
- 段階 3 導入は利用者明示承認必須（規律 §0.2、フェーズ 4 以降）

## 13. 実測結果（段階 2 小規模運用、2026-05-25 セッション 24）

本節は仕様確定後の段階 2 スクリプト実装と動作確認の実測結果を記録する。仕様 §14 残作業項目 2「段階 2 の小規模運用による実測」の成果。

### 13.1 実測の範囲

- 実 `.reviewcompass/specs/<feature>/spec.json` に対する spec-set サブコマンド
- 一時 git リポジトリでの commit／push サブコマンド（実 repo は汚さない）
- 引数妥当性検査の挙動

### 13.2 実測シナリオと結果

14 シナリオを実行、すべて想定どおりの判定（OK／WARN／DEVIATION）：

| 番号 | 種別 | 入力概要 | 想定 | 実測 |
|---|---|---|---|---|
| 1 | spec-set | foundation design drafting true | OK | OK |
| 2 | spec-set | foundation tasks drafting true（design 未承認） | DEVIATION | DEVIATION |
| 3 | spec-set | foundation requirements alignment false（reopen） | WARN | WARN |
| 4 | spec-set --json | foundation design drafting true | OK の JSON 出力 | OK の JSON |
| 5 | commit | 実 repo、staged 0、未消化 0 | OK | OK |
| 6 | push | 実 repo、tree clean、ahead 0 | OK | OK |
| 7 | spec-set | conformance-evaluation design drafting true | OK | OK |
| 8 | spec-set | foundation intent approval true（機能横断段） | OK | OK |
| 9 | spec-set | foundation requirements drafting false（reopen） | WARN | WARN |
| 10 | spec-set 引数 | foundation nonexistent-phase | 非 0 ＋ エラー | 非 0、有効値列挙 |
| 11 | commit | 未消化所見 1 件 | WARN | WARN |
| 12 | commit | spec.json 変更含む | WARN | WARN |
| 13 | commit | credentials.json 含む（危険変更） | DEVIATION | DEVIATION |
| 14 | push | dirty tree | DEVIATION | DEVIATION |

### 13.3 確認できた仕様準拠

- spec-set の判定（仕様 §6.1）：同フェーズ前段依存・上流フェーズ approval 依存・reopen 警告がすべて期待どおり動作
- commit の分類（仕様 §6.2）：通常／要注意（spec.json／docs/plan/）／危険（credentials／secret）の 3 分類が機能
- push の clean 性検査（仕様 §6.3）：未追跡ファイル 1 件でも dirty 検知、origin 未設定時も処理続行
- 終了コード体系（仕様 §7.1）：0／1／2 が想定どおり
- ログ取得（仕様 §8）：JSON Lines 形式で全シナリオの判定が追記される
- 引数妥当性検査（仕様 §5.1）：無効な値で適切なエラーメッセージと有効値の列挙

### 13.4 実測中に発見・是正した小さな問題

- 人間可読出力の真偽値表記が Python 慣習の "True/False" だったため、仕様 §7.2 サンプル準拠の小文字 "true/false" に統一（コミット `662bffb` で対処）
- `docs/logs/workflow-precheck.log` を `.gitignore` に追加（仕様 §10 の利用者と相談事項を確定、コミット `662bffb`）

### 13.5 観察事項（修正不要）

- `origin/main` 未設定時の push：「(リモート origin/main が未設定または取得失敗)」と表記して処理続行、実用上問題なし
- commit で staged ファイル 0 件の場合：OK 判定だが、実際の git commit はファイルなしで失敗するため、スクリプトとしては問題なし
- 直近 5 コミットの表示：commit メッセージが長くても折り返さずに 1 行表示（情報密度を優先）

### 13.6 結論

段階 2 スクリプトは仕様 §1〜§9 のとおり動作することを実測で確認。次の残作業項目（§14、旧 §13）に進める前提条件は揃った。

## 14. 仕様確定後の作業順序

本文書の正本化後、TODO §3 D の残作業を次の順で進める：

1. **段階 2 のスクリプト実装**（TDD で実装、tests／tools 配下に成果物）
2. **段階 2 の小規模運用による実測**（コスト・効果の数値検証）
3. **段階 1 の規律化**（`AGENTS.md`、`CLAUDE.md`、または規律ファイルに薄く追加、利用者明示承認）
4. **規律統廃合の本格議論**（実測データを踏まえて、active 規律 18 件 → 12 件程度、利用者明示承認）
5. **段階 3 のフック導入**（仕様調査、対象ツールの絞り込み、フェーズ 4 以降、利用者明示承認）

## 15. 本仕様の改訂規律

- 本仕様の変更は規律 §0.2 計画書方針変更に準じる（利用者明示承認必須）
- 改訂時は最終更新日付を更新、改訂履歴を末尾に追記
- 範囲拡張（範囲案 3 への移行など）は §3.3 に従う

## 16. 改訂履歴

- 2026-05-25 セッション 24：新設（採用承認の出典は冒頭「採用承認の出典」節を参照）
- 2026-05-25 セッション 24：§13 実測結果を追加、既存 §13〜§15 を §14〜§16 に繰り下げ（14 シナリオの実測完了に伴う追記）
