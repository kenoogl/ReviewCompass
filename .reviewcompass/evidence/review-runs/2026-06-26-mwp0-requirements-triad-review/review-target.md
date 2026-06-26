# Requirements Triad-Review: MWP-0（next --json kind 再設計）

## 背景

ReviewCompass というワークフロー管理ツールがある。このツールは `next --json` というコマンドを提供しており、コマンドを実行すると「作業の現在地（kind）」と「次に実行すべき操作（required_action）」を JSON で返す。

今回の変更（MWP-0）の動機：
- 現状の `kind` 値は 41 種類あり、「作業の現在地カテゴリ」「手続きの内部サブステップ」「コミット操作の前確認」が同一フィールドに混在している
- この混在によって機械的な次アクション決定が困難になっている
- `kind` を「作業の現在地カテゴリ」のみを示す7種類に整理し、コミット操作の前確認（`commit_candidate` / `commit_mixing_risk` / `commit_unit_stale`）は `commit-preflight` という別サブコマンドの出力に移動する

今回の reopen 手続き（仕様変更のやり直し手続き）の第3過程として、要件書（requirements.md）の変更内容をレビューする。

## 変更した要件の内容

requirements.md の Requirement 2（検査スクリプトの提供）に、受入基準 12 を新設した。

**新設した受入基準（Requirement 2 受入 12）の全文：**
```
12. 本機能は `commit_candidate`、`commit_mixing_risk`、`commit_unit_stale` の3種類の判定を
`next --json` の `kind` から除外し、`commit-preflight` サブコマンドの出力にのみ含める。
これらの判定は「作業の現在地カテゴリ」ではなく「コミット操作の前確認」であり、
`next --json` の `kind` は作業の現在地のみを示す7種類
（`completed` / `in_progress` / `blocking_in_progress` / `verification_pending` /
`reopen_in_progress` / `feature_definition_required` / `unknown`）に限定する。
設計の詳細は `docs/notes/2026-06-26-next-json-kind-redesign.md` を正本とする。
（2026-06-26 reopen R-0 next-json-kind-redesign、根拠：`docs/reviews/reopen-classification-2026-06-26-wm-next-json-kind-redesign.md`）
```

**Requirement 2 の目的：**
保守担当者が、所定手続きの段完了を機械検査できるようにする。検査は主張ではなく証拠に基づき、結論不能なら遮断する。

**既存の受入基準 11（今回の変更に隣接する部分の抜粋）：**
```
11. 本機能は `next --json` の目標応答スキーマを `.reviewcompass/schema/next_action_response.schema.json`
として JSON Schema 形式で定義する。…（中略）…
（2）`next_action` の最低限の必須フィールドは `kind`（文字列・`required_action` の分類子、
値域は design で確定）・`required_action`…
```
受入 11 は `kind` フィールドの値域を「design（設計書）で確定」と書いている。

## 審査してほしい判断ポイント

以下の claim（判断対象）を独立して分析してほしい。

### claim-A：受入 12 の要件としての完結性

受入 12 は、実装者が何を作ればよいかを一意に決定できる記述になっているか。
- 「次 --json の kind から3種類を除外する」という記述だけで、除外の基準と対象が明確か
- 「commit-preflight サブコマンドの出力にのみ含める」という記述は、commit-preflight の仕様を前提としているが、requirements.md に commit-preflight 自体の受入基準は存在しない。これは問題か（design で補完できる範囲か）
- 「設計の詳細は design note を正本とする」という委任が適切か

### claim-B：受入 11 と受入 12 の整合性

受入 11 は `kind` フィールドの値域を「design で確定」と書いている。
受入 12 は7種類の kind 値を直接列挙している。

この2つの記述は矛盾しているか、それとも整合しているか。
- 「design で確定」という記述が「受入 12 で確定した」という事実と矛盾するか
- 受入 11 を修正して「値域は受入 12 で確定」と書き直す必要があるか
- またはこのままで問題ないか、その理由は何か

### claim-C：Requirement 2 への配置の妥当性

受入 12 を Requirement 2（検査スクリプト）の下に配置した。

Requirement 2 の目的は「段完了の機械検査」であり、`next --json` の出力インターフェイス定義を含む（受入 6〜11 が next --json の各側面を定義している）。

この配置は適切か。あるいは `next --json` の出力インターフェイスを定義する別の Requirement があるべきか。

## 参考：設計文書の概要（抜粋）

変更後の kind 7種類の設計意図：

| kind | 意味 |
|------|------|
| `completed` | 全作業完了 |
| `in_progress` | 通常の作業中 |
| `blocking_in_progress` | 本線とは別の作業中（完了後に親へ戻る） |
| `verification_pending` | 書き込み後の検証待ち |
| `reopen_in_progress` | 再開手続き中 |
| `feature_definition_required` | 初期設定未完了（正常な未完了状態） |
| `unknown` | 想定外のエラー状態 |

除外する3種類とその理由：
- `commit_candidate`：コミット可能な状態であることを示す → 「現在地」ではなく「操作の前確認」
- `commit_mixing_risk`：混在リスクありのコミット待ち → 同上
- `commit_unit_stale`：コミット対象が古い → 同上
