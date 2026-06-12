---
date: 2026-06-12
classifier: claude_main_session
classification: R-0
trigger_source: 利用者決定 MLE-DEC-005（2026-06-12「私の判断がまちがっていた。コストはかかるが案ｂが根本対策と考える」）。feature-dependency.yaml がパース不能（ファイルはあるが YAML として読めない）の場合の挙動を、立ち上げ案内（OK）から遮断（DEVIATION、fail-closed）へ分離する根本対策を実施するため。
feature: workflow-management
finding: feature-dependency-parse-error-masked-by-guidance
---

## 分類根拠

reopen R-0（multi-llm-entry-spec-reflection、2026-06-12 完了、コミット 5cd16f7）の requirements
triad-review round-2 の所見 F4（gpt-5.5-adversarial-002）は、「パース不能を未定義と同じ案内（OK）に
含める例外が fail-closed 原則とずれる」と指摘した。当時の利用者決定（案 a）は「現挙動を仕様として
明文化し、改修は FUP-2026-06-12-001 として追跡」だったが、利用者が同日この判断を改め、
遮断分離の実施（案 b）を決定した（MLE-DEC-005）。

問題の実害：表のファイルを編集ミスで壊した利用者に「intent と機能分割から始めてください」という
立ち上げ案内が表示され、本当の原因（ファイル破損）が案内に覆い隠される。最悪の場合、案内に従って
表を作り直し、既存の依存関係の記録を失う。

手戻り種別は `R-0`（requirements 起点、intent へは遡らない）とする。根拠：

- 修正の最上流は requirements（Requirement 8 受入 8 の「パース不能も未定義と同様に扱う」を
  「パース不能は遮断する」へ意味変更）。
- intent・feature-partitioning は不変（fail-closed 原則の適用範囲の精密化であり、機能の意図・分割に
  影響しない）。
- 本件は前回 reopen と異なり実装変更を含む。仕様（requirements → design → tasks）を先に確定し、
  実装は仕様確定後に TDD（テスト先行）で行う正順の手続きとする。

## 事実

- 現実装：`load_feature_dependency` が YAML パースエラーを握りつぶし、`resolve_feature_order` が
  未定義と同じ立ち上げ案内（`feature_definition_required`／OK／exit 0）を返す。
- 現仕様：requirements 受入 8・design §機能依存マップモデル §7・tasks T-004 が、この挙動を
  2026-06-12 の reopen（5cd16f7）で明文化済み。いずれにも「遮断への分離は FUP-2026-06-12-001 で追跡」
  と記載があり、本 reopen はその追跡の解消である。
- 変更後の挙動（仕様化する内容）：パース不能の場合は `next_action.kind: unknown` 系の遮断とし、
  破損ファイルのパスと「ファイルを確認せよ」の理由を `reasons` に出力する（DEVIATION／exit 2）。
  ファイル不在・`feature_order` キー未定義の立ち上げ案内（OK）は従来どおり。

## feature impact 判定

| feature | decision | impact_basis | rationale |
| --- | --- | --- | --- |
| workflow-management | reopen_existing_feature | contract_ownership | Requirement 8 受入 8・design §7・T-004 の契約と検査ツール実装を所有し、直接修正するため。 |
| conformance-evaluation | no_reopen_existing_feature | no_implementation_impact | 同 feature の仕様はパース不能の挙動に言及せず（feature_order の語彙参照のみ）、影響しない。 |
| foundation | no_reopen_existing_feature | no_implementation_impact | kind 語彙は workflow-management T-004 の契約。共有語彙に変更なし。 |
| runtime | no_reopen_existing_feature | no_implementation_impact | 接合面に変更なし。 |
| evaluation | no_reopen_existing_feature | no_implementation_impact | 接合面に変更なし。 |
| analysis | no_reopen_existing_feature | consumer_or_derivative_only | 読み手であり接合面は不変。 |
| self-improvement | no_reopen_existing_feature | consumer_or_derivative_only | 読み手であり接合面は不変。 |

新 feature 判定：`no_new_feature`。

## 再実施対象

`R-0` の trigger_map（requirements alignment／approval）を基線とし、正本修正のある
requirements・design・tasks の全 review 系 gate、および**実装変更を行う implementation の
全 review 系 gate** を加える（前回 reopen と異なり implementation は確認のみではなく修正対象）。

- `stages/requirements.yaml#triad-review`〜`#approval`
- `stages/design.yaml#triad-review`〜`#approval`
- `stages/tasks.yaml#triad-review`〜`#approval`
- `stages/implementation.yaml#triad-review`〜`#approval`（TDD：失敗テスト→実装→全テスト通過）

impacted_downstream_phases：design／tasks／implementation。

## 停止点

reopen-start により in-progress ファイルを発行し、workflow-management の spec.json フラグ差し戻し
（requirements／design／tasks／implementation の alignment・approval を false、recheck 設定）を
行ったうえで、第1過程停止点として差し戻し内容の利用者承認を待つ。この時点ではコミットしない。
