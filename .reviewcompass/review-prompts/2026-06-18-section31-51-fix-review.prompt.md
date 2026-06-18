# 設計文書レビュー：§3.1 と §5.1 の修正確認

## レビューの目的

`docs/notes/2026-06-18-integrated-design-selection-execution-layers.md` の
§3.1 と §5.1 を修正した。この2箇所が正しく修正されているかを確認する。

## 修正前の問題

**問題A（§3.1）：循環依存**

§3.1 は「実行前に承認ゲートを通す必要がある操作」のリストだった。
そのリストに `record_human_decision` が含まれていた。

しかし §5.1 によれば、承認ゲートは次の手順で構成される。

```
wait_for_human_decision → record_human_decision → 対象操作の実行
```

`record_human_decision` 自体が承認ゲートを通す必要があるとすると、
`record_human_decision` を実行するために別の `record_human_decision` が必要になる。
これは終わらない繰り返し（循環依存）である。

**問題B（§5.1）：拒否・保留経路の未定義**

§5.1 の承認ゲートは承認した場合の経路しか定義していなかった。
人間が拒否または保留した場合に何が起きるかが書かれていなかった。

## 修正後の §3.1（該当部分のみ）

```markdown
`effect_kind: irreversible_action` となる操作は、実行前に必ず承認ゲートを通す。
該当する `required_action` は次のとおり。

- `commit_stop_point`（guarded commit）
- `apply_approved_reopen_plan`（spec.json workflow_state の rollback）
- `run_reopen_start`（reopen plan の生成と in-progress YAML 作成）
- `advance_reopen_after_commit_stop_point`（commit stop point の消費）
- `advance_reopen_after_approval_stop_point`（step advance）
- `finalize_reopen`（completed YAML への移動）
- `repair_workflow_state`（状態修復コマンドの実行）

`record_human_decision` は「判断を記録する操作」（`effect_kind: state_mutation`）であり、
承認ゲートの対象操作ではなく、承認ゲートを構成する部品である。
承認ゲートを通す対象はあくまで上記リストの操作であり、
`record_human_decision` 自体を承認ゲートに通す必要はない。
```

## 修正後の §5.1（全文）

```markdown
**選択層からの視点（D-003）：** `required_action` として `wait_for_human_decision` /
`record_human_decision` のペアで表現される。

**実行層からの視点（機械化設計）：** `effect_kind: irreversible_action` を持つ操作の前に
必須の、明示的チャンネルによる人間判断記録。

**統一定義：** 取り消し不能な操作を実行する前に、人間の判断を構造化コマンドで記録し、
その記録内容に応じて選択層（`next --json`）が次の操作を決めるチャンネル。

wait_for_human_decision
  → (人間が判断を下す)
    → record_human_decision（判断内容を記録するだけ）
      → next --json を再実行
          ↓ 承認     → 対象の不可逆操作を実行
          ↓ 拒否     → 対象操作の中止。次の required_action は各 operation contract で定義
          ↓ 保留     → 再び wait_for_human_decision へ
          ↓ 修正要求 → 再起草へ戻す（draft 系の required_action）

- `wait_for_human_decision` と `record_human_decision` は必ずペアで完結する。
- `record_human_decision` は「判断を記録する操作」であり、対象操作の実行を直接引き起こさない。
- 記録された判断の内容（承認 / 拒否 / 保留 / 修正要求）を読んで次の `required_action` を決めるのは、
  選択層（`next --json`）の責務である。
- 拒否時・保留時に `next --json` が何を返すかは各 `required_action` の operation contract で定義する。
- 「記録が完了した」ことと「承認された」ことは別の事実である。記録の完了は対象操作の許可を意味しない。
- `approval gate` という語は「このペアの構造と、その後の選択層による分岐を含む全体」を指す。

reopen の `approval` gate（`run_reopen_pending_gate` の一種）は、
この承認ゲートを `reopen-set-blocker` → `wait_for_human_decision` → `record_human_decision` の順で踏む。
拒否された場合の動作（reopen の中止・再起草・blocker 維持）は reopen の operation contract で定義する。
```

## レビューで確認してほしい点

1. **§3.1 の修正は問題Aの循環依存を解消しているか。**
   リストから `record_human_decision` を外し、「部品である」という説明を加えた。
   この修正によって循環依存は実際に断ち切れているか。
   残存する矛盾や不明点があれば指摘すること。

2. **§5.1 の4経路（承認・拒否・保留・修正要求）の定義は適切か。**
   過不足や曖昧さがあれば指摘すること。
   特に「拒否」と「修正要求」の区別が明確かを確認すること。

3. **修正後の §3.1 と §5.1 の間に矛盾はないか。**
   修正によって新たな整合性の問題が生じていないかを確認すること。

## 出力形式

```yaml
findings:
  - severity: ERROR / WARN / INFO
    target_location: "§3.1" または "§5.1" または "§3.1 と §5.1 の整合"
    description: |
      （指摘内容）
    rationale: |
      （根拠）
```

問題が見つからない場合は `findings: []` と返すこと。
