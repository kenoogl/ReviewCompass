# 仕様・実装乖離監査プロセス記録

作成日：2026-06-08

## 0. 位置づけ

本メモは、ReviewCompass の通常 workflow completed 後に、開発途中でアドホックに追加された機能が既存仕様へ正しく戻されているかを確認するための監査プロセスを記録する。

この作業は、`conformance-evaluation` の本格実装前に行う手作業または半自動のテストケースとして扱う。目的は、実装コードから requirements / design 相当の情報を起こし、既存上流文書と照合する逆方向チェックの有効性と必要な出力形式を確認することである。

本メモは作業順序の正本ではない。通常 workflow の正本は、引き続き `tools/check-workflow-action.py next --json` と各 feature の `spec.json` である。

## 1. 背景

現在の開発コードは仕様に基づいて作成されたが、実装途中でアドホックに機能追加した箇所がある。その場合、次のような乖離が起こり得る。

- 実装には存在するが requirements / design に戻されていない機能がある。
- requirements / design に書かれた契約と実装の実際の入出力や失敗条件が異なる。
- 実装で得た知見が仕様文書、運用文書、または将来の conformance-evaluation schema に反映されていない。
- 仕様化不要な内部実装詳細と、仕様へ戻すべき外部契約が混ざっている。

この問題は、既存仕様からコードを読む順方向の実装適合レビューだけでは検出しにくい。仕様に存在しない実装は、仕様項目を起点にした確認では見落とされやすいためである。

そのため、本作業では、実装コードから requirements / design 相当を推定して既存仕様と比較する逆方向の conformance-evaluation を、まず小さく手作業で実施する。

## 2. 方針

初回は conformance-evaluation の完全自動実装を先に作らず、既存 criteria に基づく read-only 監査として進める。

理由：

- 現行の `tools/conformance_evaluation/` 実装には基礎構造があるが、自動推定はまだ placeholder 寄りであり、いきなり全面自動化すると監査観点が固まらない。
- 実際の ReviewCompass コードを対象にすると、どの情報をコードから抽出すべきか、どの差分分類が必要か、どの出力が後続判断に役立つかを確認できる。
- この手作業監査の成果物を、後続の conformance-evaluation 本格実装のテストケース、期待出力、schema 設計材料として再利用できる。

## 3. 対象範囲と初回対象

本監査プロセスの最終対象は、ReviewCompass の全 7 feature とする。

- `foundation`
- `runtime`
- `evaluation`
- `analysis`
- `workflow-management`
- `self-improvement`
- `conformance-evaluation`

ただし、初回対象は `workflow-management` とする。

理由：

- `tools/check-workflow-action.py`、commit / push guard、post-write verification、reopen / resume / autonomous-plan など、実装上の契約が多い。
- アドホックな運用改善が入りやすい領域であり、仕様と実装の乖離検査の価値が高い。
- 既存の `requirements.md` / `design.md` / `tasks.md` と実装コードの対応を確認しやすい。

初回監査で手順、差分分類、成果物形式を固めた後、同じ形式で残り 6 feature に展開する。

## 4. 手順

### Step 1. 監査範囲の固定

対象 feature、対象仕様文書、対象実装ファイル、対象テストを列挙する。

初回候補：

- 仕様文書：`.reviewcompass/specs/workflow-management/requirements.md`
- 仕様文書：`.reviewcompass/specs/workflow-management/design.md`
- 参考文書：`.reviewcompass/specs/workflow-management/tasks.md`
- 実装：`tools/check-workflow-action.py`
- 実装：`tools/guarded-git-commit.py`
- 関連テスト：`tests/` または各 tool 配下の該当テスト
- 関連運用文書：`docs/operations/WORKFLOW_PRECHECK.md`
- 関連運用文書：`docs/operations/WORKFLOW_NAVIGATION.md`

### Step 2. コード由来の設計スケッチ作成

実装コードとテストから、次を抽出する。

- 公開 CLI / subcommand
- 入力引数
- 出力形式
- exit code
- 読み書きするファイル
- guard / fail-closed 条件
- workflow state 判定
- post-write verification 判定
- commit / push 時の遮断条件
- manifest / approval record の期待構造
- テストで固定されている境界条件

この段階では既存 requirements / design を正解として扱わず、コードから観測できる契約だけを記録する。

### Step 3. 既存仕様との照合

コード由来スケッチを、conformance-evaluation の 6 criteria に合わせて既存仕様と比較する。

requirements conformance：

- 受け入れ基準と実装の対応
- API / データ契約と実装の対応
- 例外系・境界条件と実装の対応

design conformance：

- モジュール構成・データモデルと実装の対応
- 接合面（API シグネチャ・エラーモデル）と実装の対応
- アルゴリズム・性能達成手段と実装の対応

### Step 4. 差分分類

差分は次の分類で記録する。

- `spec-missing`：実装にはあるが仕様にない。
- `code-missing`：仕様にはあるが実装にない。
- `mismatch`：仕様と実装が異なる。
- `implementation-detail`：仕様化不要な内部詳細である。
- `obsolete-spec`：仕様側が古い可能性が高い。
- `needs-user-decision`：仕様と実装のどちらを正とするか利用者判断が必要である。

分類時点では、仕様や実装を修正しない。修正候補は別途、利用者確認後に扱う。

### Step 5. 反映候補の整理

差分ごとに次のいずれかを候補として記録する。この段階では、仕様変更、実装修正、テスト追加、削除、carry-forward 登録のいずれも承認済みとは扱わない。

- requirements / design に戻す候補。
- operations / notes に戻す候補。
- 実装から削る候補。
- テストを追加して契約化する候補。
- 内部詳細として残し、仕様化しない候補。
- 判断保留として carry-forward する候補。

反映候補を実際に採用する場合は、別途利用者判断を受けてから扱う。仕様変更、規律変更、commit、push は不可逆操作または正本文書変更に該当し得るため、必要な承認と post-write verification を行う。

## 5. 初回成果物

初回監査では、少なくとも次を作る。

- コード由来設計スケッチ
- 仕様照合表
- 差分分類表
- conformance-evaluation 本格実装へのフィードバック

保存先候補：

- `docs/notes/2026-06-08-workflow-management-conformance-drift-audit.md`

## 6. 本格実装へのフィードバック観点

このテストケースから、conformance-evaluation 本格実装に必要な次の要素を確認する。

- コードから抽出すべき contract field
- requirements / design との照合単位
- finding ID の採番規則
- 差分分類の列挙値
- evidence refs の表現
- 自動推定できる項目と人間判断が必要な項目の境界
- check mode の期待出力
- 後続の TDD cycle evidence や finding-to-fix traceability との接続

## 7. 現時点の合意事項

- まず提案済みの手順で進める。
- この作業を conformance-evaluation 本格実装のテストケースとして扱う。
- 全 7 feature を対象にする。
- 初回は `workflow-management` を小さく対象にし、手順と成果物形式を固めてから残り feature に展開する。
- 仕様や実装の修正は、差分分類と利用者確認の後に行う。
- プロセスと成果物を記録し、後続の自動化に使える形にする。
