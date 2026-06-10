# 次セッション継続用メモ

最終更新：2026-06-10。正本は `tools/check-workflow-action.py next --json` と各 feature の `spec.json`。この TODO は入口メモであり、作業順序の正本ではない。

作業ディレクトリ：`/Users/Daily/Development/ReviewCompass/`
リポジトリ：`git@github.com:kenoogl/ReviewCompass.git`（main ブランチ）

## 0. 全体像

ReviewCompass は、複数 LLM のレビュー結果を raw で保存し、三段階トリアージと人間／proxy_model の判断を経て、仕様・実装・規律を改善するための自己適用型レビュー基盤である。

開発は feature ごとの `workflow_state` に従い、intent → feature-partitioning → requirements → design → tasks → implementation の各 phase を、drafting／triad-review／review-wave／alignment／approval の段で進める。

LLM の記憶に頼らず、`tools/check-workflow-action.py next --json`、spec.json、post-write manifest、commit guard、carry-forward register などの機械判定を、作業順序と規律遵守の正本にする。

重要件は、raw・要約・三段階トリアージ・判断理由を残し、通常モードでは修正前に利用者承認を得る。自律／proxy_model モードでは、判断代行の raw・候補案・採用案・理由を記録する。

旧 ReviewCompass 固有の状態台帳は carry-forward register に抽象化し、配布先プロジェクトでは別の状態入力に差し替えられるようにする。

## 1. 起動時に必ず行うこと

1. `tools/check-workflow-action.py next --json` を実行し、`next_action` を作業順序の正本として扱う。
2. `git status --short` と `git log --oneline -5` で到達点を確認する。
3. `next_action.required_disciplines` に出た規律だけを、操作直前に読む。
4. `post_write_verification`、`reopen_in_progress`、`resume_in_progress`、`unknown` が返った場合は通常作業へ進まない。

Python 実行は、必要に応じて venv を使う：

```bash
.venv/bin/python3 tools/check-workflow-action.py next --json
```

## 2. 不可逆操作の規律

- spec.json の workflow_state 変更、commit、push、規律ファイル変更、大方針転換は利用者の明示承認が必要。
- commit は利用者から「コミット」と明示された場合だけ実行する。
- commit は原則 `tools/guarded-git-commit.py -m "<message>" --rationale "<理由>"` 経由。
- commit 前に `.reviewcompass/approvals/commit-approval.json` を staged 内容と SHA に合わせる。
- post-write-verification 対象文書を staged する場合、completed manifest と SHA 一致が必要。
- API review-run の結果を使う場合は、raw、モデル別要約、三段階トリアージをまとめて提示する。重要件は通常モードでは修正前に案を示して承認を得る。

## 3. 現在位置

`next --json` の直近確認では、次は以下：

- kind: `completed`
- reason: `すべての workflow_state が完了しています`

全 feature の workflow_state は完了済み：

- `foundation`
- `runtime`
- `evaluation`
- `analysis`
- `workflow-management`
- `self-improvement`
- `conformance-evaluation`

上記 7 feature は、intent、feature-partitioning、requirements、design、tasks、implementation の全段が完了している。

直近 commit：

- `be9aa4f Ignore generated deploy package output`
- `06c86c2 Track deploy package and update session TODO`
- `b6fdf9f Document venv dependency for deployment smoke`
- `fde83df Fix hook test fixtures for stage-2 imports`
- `305614e Align Claude adapter with Codex setup`

直近 push：

- 2026-06-10 に、初期デプロイ関連一式から本 TODO 更新までを push し、`main` と `origin/main` を同期。push 前の `origin/main` は `45df25e` だった（本 TODO の旧記載 `64de32c` は不正確だったため訂正）。

作業ツリー：

- `build/`（生成済み配布物）は生成物として追跡解除し、`.gitignore` に登録済み（`be9aa4f`）。実体は `build/deploy/ReviewCompass/` に残してあり、配布物として使える。

## 4. 次作業

通常ワークフロー上の未完了タスクはない。

次セッションでは、まず `next --json` で `kind: completed` が維持されていることと、`git status --short` が clean であることを確認する。

候補タスク：

1. `docs/operations/INITIAL_DEPLOYMENT_USER_GUIDE.md` 第 9 節以降に従い、配布物の配置と実アプリ pilot を開始する。
2. completed 到達後の全体サマリを作る。
3. `post_hoc_intent_diff` の実データ試行結果を、将来の fixture または回帰確認に使うか判断する。
4. review-wave 改善メモに残した follow-up candidates を、次の改善候補として扱う。

## 5. 直近の完了事項

- 2026-06-10：初期デプロイ関連の未 push コミット群を `origin/main` へ push。`build/` はいったん追跡したのち、生成物のため追跡解除して `.gitignore` へ登録（`06c86c2`→`be9aa4f`）。本 TODO の状態記述（push 状態、`build/` の扱い、`origin/main` の位置）を修正。この TODO 修正は利用者明示指示により独立検証なしとし、人間検証者代替を manifest に記録。
- 2026-06-10：配布前 smoke を実施し合格。`tools/build-deploy-package.py --clean --verify --smoke-external-app-root <一時root>` で配布物 262 ファイルの生成・検査と、一時 root への review-run 記録書き込みを確認。システムの python3 では `httpx` 不足で失敗するため、`.venv/bin/python3` での実行が必要と判明。
- 2026-06-10：`docs/operations/INITIAL_DEPLOYMENT_USER_GUIDE.md` 第 8 節へ smoke の `.venv` 依存を追記（本文の依存説明＋依頼例の 1 行）。post-write 検証は Gemini 1 体で 2 巡（round-1 の should-fix を利用者承認で適用 → r2 所見ゼロ）、manifest `post-write-2026-06-10-011.yaml` を生成し、`b6fdf9f` として commit（guarded-git-commit 経由、利用者指示）。
- 2026-06-09〜06-10：初期デプロイ一式を整備（deploy manifest、配布物生成ツール、配布物検査、外部アプリ root smoke、初期導入利用者ガイド、初期設定 LLM ガイド、Claude adapter の Codex 整合、hook テスト fixture 修正）。`df5bf66`〜`fde83df`（2026-06-10 push 済み）。
- 既存システムへの後追い intent 追加に対し、仕様駆動開発の reopen 手続きを実施し、requirements／design／tasks／implementation の再確認連鎖を完了。
- `conformance-evaluation` に `post_hoc_intent_diff` を追加し、既存仕様・実装コードから後追い intent の差分候補を抽出できるようにした。
- `post_hoc_intent_diff` を ReviewCompass の実データで追加試行し、記録 `.reviewcompass/specs/conformance-evaluation/conformance/2026-06-09-real-data-r2-post-hoc-intent-diff.md` を保存。
- workflow-management に、後追い intent／上流正本変更時の reopen 分類、feature impact 判定、downstream impact 判定、drafting-before-review 防止、commit 代行判定の機械ガードを反映。
- `64de32c` までの一連の変更を `main` に push 済み。
- 全 7 feature の implementation review-wave、alignment、approval を完了。
- `implementation.approval=true` を全 feature に設定し、`next --json` が `kind: completed` を返す状態にした。
- workflow-management の draft triage 残りを未解決扱いするように `review_triage.py` を修正し、回帰テストを追加。
- review-wave 中に見つかった 3 件のブロッカーを解消：
  - workflow-management の draft triage 残り
  - evaluation の証跡配置
  - foundation recheck pending
- carry-forward register を正本化し、旧 `.reviewcompass/pending-cross-feature-findings.md` を `learning/workflow/carry-forward-register/sources/` へ移動。
- `learning/workflow/carry-forward-register/reviewcompass-import.yaml` を `required_inputs.unresolved_cross_scope_items` の実体にした。
- 再利用される入力や review-target bundle に旧台帳参照が残らない監査を追加。
- `legacy_references` のような弱い参照羅列を正本 YAML から削除し、再生成しても入らないようにした。

## 6. 参照

- workflow navigation: `docs/operations/WORKFLOW_NAVIGATION.md`
- session guide: `docs/operations/SESSION_WORKFLOW_GUIDE.md`
- carry-forward register: `learning/workflow/carry-forward-register/reviewcompass-import.yaml`
- historical source: `learning/workflow/carry-forward-register/sources/reviewcompass-pending-cross-feature-findings.md`
