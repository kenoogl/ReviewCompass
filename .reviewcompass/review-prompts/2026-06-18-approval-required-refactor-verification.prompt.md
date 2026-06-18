# 設計文書レビュー：approval_required 別軸化の修正検証

## 修正の背景

以前のレビューで、次の問題が判明した。

1. `effect_kind`（副作用の種別）が「操作が何をするか」と「承認ゲートが必要か」の2役を担っており、設計として成立しない
2. `effect_kind: irreversible_action` という値は「何をするか」ではなく「どのくらい危険か」を表しており、他の4値（`read / write / state_mutation / external_call`）と異質

## 修正内容

2つの文書を修正した。

### 機械化設計メモ（`docs/notes/working/2026-06-18-mechanized-workflow-execution-design.md`）

operation contract（操作の契約）の属性に `approval_required` を追加した。

```
変更前：
| effect_kind | 副作用の種別。read / write / state_mutation / external_call / irreversible_action の5値 |

変更後：
| effect_kind        | 副作用の種別。read / write / state_mutation / external_call の4値 |
| approval_required  | 実行前に人間の承認が必要か。true / false |
```

承認ゲートの説明文を変更した。

```
変更前：effect_kind: irreversible_action を持つ操作は承認ゲートを通過してからでないと実行できない
変更後：approval_required: true を持つ操作は承認ゲートを通過してからでないと実行できない
       approval_required は effect_kind とは独立した属性であり、state_mutation であっても
       approval_required: true になる操作がある
```

Phase 5 の計画を変更した。

```
変更前：effect_kind: irreversible_action に承認ゲートを強制する
変更後：approval_required: true の操作に承認ゲートを強制する
```

### 統合設計メモ（`docs/notes/2026-06-18-integrated-design-selection-execution-layers.md`）

§3 の対応表の変更：
- 「不可逆か」列を「approval_required」列に変更
- `commit_stop_point` の effect_kind を `irreversible_action` → `state_mutation` に変更
- `record_human_decision` の approval_required を「いいえ（承認ゲートの部品）」に明示

§3.1 の変更：
- タイトルを「`effect_kind: irreversible_action` が必要な操作」→「`approval_required: true` の操作」に変更
- 「`approval_required` は `effect_kind` とは独立した属性」という説明を追加
- `run_maintenance` の記述を「maintenance YAML の `approval_required` が true のものは承認ゲートを通す」に変更

§3.2 の変更：
- `approval` gate の effect_kind を `irreversible_action` → `state_mutation` に変更
- `approval` gate の approval_required を「いいえ（承認要求の設定自体は可逆。承認が必要なのはその後の対象操作）」に明示

§5.1 の変更：
- 「`effect_kind: irreversible_action` を持つ操作の前に必須」→「`approval_required: true` を持つ操作の前に必須」に変更

## レビューで確認してほしい点

1. `approval_required` を `effect_kind` から独立した属性として分離したことで、
   承認ゲートの判定基準は正しく定義されているか。
   `effect_kind: state_mutation` かつ `approval_required: true` という組み合わせは
   operation contract として整合しているか。

2. §3.2 で `approval` gate の `approval_required` を「いいえ」としたことは適切か。
   （承認要求を設定する操作自体には承認ゲートは不要であり、承認が必要なのはその後の対象操作という考え方）
   この分類に問題があれば指摘すること。

3. 修正後の §3 の表・§3.1・§3.2・§5.1 の間に矛盾はないか。
   修正によって新たな整合性の問題が生じていれば指摘すること。

## 出力形式

```yaml
findings:
  - severity: ERROR / WARN / INFO
    target_location: 対象箇所
    description: |
      （指摘内容）
    rationale: |
      （根拠）
```

問題が見つからない場合は `findings: []` と返すこと。
