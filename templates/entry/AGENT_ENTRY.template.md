# ReviewCompass エージェント入口（対象アプリ用）

（本ファイルはテンプレート `templates/entry/AGENT_ENTRY.template.md` から実体化する。実体化の際、次の行を記入する）

- 実体化日：`<初期設定日を記入>`
- 実体化元の配布物：`<配布物ディレクトリ名を記入>`

## 1. 本文書の役割

対象アプリで ReviewCompass を使う LLM セッションの入口規律である。対象アプリ自身の開発方針（言語、テスト方針、コーディング規約など）は対象アプリ側の指示に従う。

本文書はデフォルト一式であり、対象アプリの方針と合わない節は利用者判断で調整してよい（調整した節と理由を本文書の末尾に記録する）。既存の入口文書（CLAUDE.md／AGENTS.md）の規律と本書の規律が衝突した場合、自動的な優先順位は定めない。衝突を検出した LLM は作業を進めず利用者へ提示し、利用者判断で本書側の該当節を調整する。

## 2. 配布物の場所と境界

- ReviewCompass 配布物の場所（**絶対パスで記入**）：`<初期設定時に記入>`
  - 環境によって場所が異なる場合は、利用者に確認して本欄を更新する。
- 配布物ディレクトリと対象アプリ root を混同しない。
- 対象アプリへ書き込んでよいのは `.reviewcompass/` 配下と、利用者が承認した箇所だけ。
- API key、token、password などの秘密値をファイルへ書き込まない。環境変数など配布物外の方法で渡す。

## 3. 毎セッションの起点

作業開始前、または次に何をするかを提案する前に、対象アプリ root で必ず次を実行する（`<配布物>` は §2 の記入値）。

```bash
<配布物>/tools/check-workflow-action.py next --json
```

`next_action` を作業順序の正本とし、`kind` の読み方は配布物の `docs/operations/WORKFLOW_NAVIGATION.md` に従う。`post_write_verification` 等が返った場合は通常作業へ進まない。

feature が未確定の段階（`.reviewcompass/feature-dependency.yaml` が無い、または `feature_order` が未定義）では、`next` は `feature_definition_required` を返し、intent と feature-partitioning の実施を案内する。案内に従って機能分割を確定し、承認された分割結果を `.reviewcompass/feature-dependency.yaml` に記録する。

## 4. 開発の進め方（TDD）

原則としてテスト駆動開発（TDD）で進める。

- 期待される入出力に基づき、まずテストを作成する。
- 実装コードは書かず、テストのみを用意し、実行して失敗を確認する。
- テストが正しいことを確認できた段階で commit の停止点とする。
- その後、テストをパスさせる実装を進める。実装中はテストを変更しない。
- すべてのテストが通過するまで繰り返す。

対象アプリに既存のテスト方針がある場合は、利用者判断で本節を調整する。

## 5. 不可逆操作の承認

- commit・push・spec.json（workflow_state）の変更・設定変更は、利用者の明示承認が必要。
- commit は利用者から「コミット」と明示された場合だけ実行する。代行時は配布物の `tools/guarded-git-commit.py` を使う（事前検査と承認レコードの確認が自動で入る）。
- push の前には `check-workflow-action.py push --rationale "<理由>"` の事前検査を通す。

## 6. review-run の規律（実行前後のゲート）

- **実行前**：使用する variant（モデルの組）と役ごとの provider／model を利用者へ提示し、曖昧なまま開始しない。
- **実行後**：raw 参照、モデル別要約、三段階トリアージ案（must-fix／should-fix／leave-as-is）をまとめて利用者へ提示して停止する。重要件は承認を得てから修正に進む。

## 7. 文書書き込み後の独立検証（post-write 検証）

検査ツールは、対象アプリの `docs/` 配下と `TODO_NEXT_SESSION.md` の未コミット変更を検証対象として検出する。`post_write_verification` が返ったら、書いた本人と異なる検証者（別系統の LLM）による検証 → トリアージ → manifest 作成を済ませてから通常作業へ戻る。manifest は対象アプリ側の `.reviewcompass/post-write-verification/` に作られる。

## 8. セッション引き継ぎ（TODO 運用）

`TODO_NEXT_SESSION.md` を配布物のテンプレート（`templates/todo/TODO_NEXT_SESSION.template.md`）から作成し、セッション終了時に到達点と次作業を更新する。TODO は入口メモであり、正本は `next --json` と spec.json とする。

## 9. 完了報告

作業を終えて利用者へ返答するときは、最低限次を示す：作業サマリ（実施した変更・判断・未変更の範囲）、検証結果（実行したテストと確認コマンド）、現在状態（git と next の要点）、次タスク。未実施・失敗・承認待ちがある場合は完了扱いにせず明記する。

## 10. LLM 別の注意

### 共通

- 規律と恒久記録の正本は repo 内のみ。LLM 固有の記憶機能や repo 外ファイルを規律の正本にしない。記録が必要なら repo 内へ、利用者承認のうえ書く。
- 本書の規律は LLM の種類に依存しない。どの LLM でも同じ手順・同じゲートで作業する。
- review-run の variant（モデルの組）は、起草者（操縦している LLM）との独立を保つため、操縦 LLM に応じた既定を使う。小規模の 1 体検証は両操縦共通で `post_write_verification_google`。
- proxy_model（人の判断を代行させる場合のモデル）も、操縦 LLM と別系列のモデルを選ぶ。

### Claude Code で作業する場合

- 入口は CLAUDE.md（本ファイルへの取り込み 1 行）。
- project memory（セッション開始時に自動読み込みされる記憶）が表示されても、規律の正本として扱わない。memory への書き込みは原則行わない。
- hook・許可設定は対象アプリの `.claude/` 配下に置く。
- 3 役 review-run の既定 variant：接尾辞なしの `*_independent_3way` 系（例：`post_write_verification_independent_3way`）。

### Codex CLI で作業する場合

- 入口は AGENTS.md（本ファイルへの参照 1 行）。
- 自動読み込みされる記憶機能はない。repo 外への記録を前提にしない。
- hook 設定は対象アプリの `.codex/hooks.json` に置く。
- 3 役 review-run の既定 variant：`*_independent_3way_codex_operator` 系（例：`post_write_verification_independent_3way_codex_operator`）。

## 11. 入口ファイルへの挿入行（初期設定用の定型文）

既存の入口ファイルの末尾へ、利用者承認のうえ次の 1 行を追記する（ファイルが無ければこの 1 行だけの新規作成、同じ行が既にあれば何もしない）。

- `CLAUDE.md` へ（取り込み行）：

  ```text
  @.reviewcompass/AGENT_ENTRY.md
  ```

- `AGENTS.md` へ（指示文）：

  ```text
  ReviewCompass を使う作業では、最初に `.reviewcompass/AGENT_ENTRY.md` を読み、その規律に従う。
  ```

## 12. 調整の記録

（対象アプリの方針に合わせて本書の節を調整した場合、ここに「節番号・調整内容・理由・日付」を記録する）
