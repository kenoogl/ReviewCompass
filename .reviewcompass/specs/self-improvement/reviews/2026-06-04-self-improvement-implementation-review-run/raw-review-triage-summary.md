# self-improvement implementation review-run raw summary and triage draft

run_id: 2026-06-04-self-improvement-implementation-review-run

## 入力と方針

本 review-run は、workflow-management の先例を成果物構造の参考に留め、self-improvement の intent/feature-partitioning 由来の機能責務と requirements/design/tasks からレビュー観点を生成した。

対象の中心は、規律と実体の双方向同期、提案権と実体変更権の分離、入力モデル、signal 抽出、提案、検証、承認、rollback、効果測定、機械検査、他機能接合、T-001〜T-011 の traceability である。

## モデル別 raw 結果

| モデル | raw | 構造化状態 | 所見 |
| --- | --- | --- | --- |
| claude-sonnet-4-6 | raw/claude-sonnet-4-6.round-1.txt | parsed | ERROR 4、WARN 6、INFO 2 |
| gpt-5.4 | raw/gpt-5.4.round-1.txt | parse_failed | raw 上は ERROR 4、WARN 4 |
| gemini-3.1-pro-preview | raw/gemini-3.1-pro-preview.round-1.txt | parsed | findings: [] |

gpt-5.4 は raw response は取得済みだが、review-run の parser が期待する構造に合わず parsed YAML は生成されなかった。raw は人間またはメインセッション LLM が読めるため、三段階トリアージの材料には含める。

## 三段階トリアージ案

### must-fix

1. 提案モデルの `motivating_evidence` 検証が集合比較の向きで壊れている。
   - 出典: claude-sonnet-4-6 WARN 005
   - 平易な説明: 必須3項目がちょうど揃った正しい証拠を、誤って不正扱いする可能性がある。提案 YAML の中核検証なので重要。

2. `proposed_change` の型が仕様と実装で食い違っている。
   - 出典: gpt-5.4 ERROR 1、claude-sonnet-4-6 WARN 007 と関連
   - 平易な説明: 仕様側は提案本文を文字列として扱う例を持つ一方、実装と schema は object 固定になっている。正しい提案を通せない、または下流との契約が崩れる。

3. 効果測定の平均採用日数が廃止済みの `approved_at` に依存している。
   - 出典: claude-sonnet-4-6 WARN 008、gpt-5.4 ERROR 4
   - 平易な説明: 現在の正本では `approved_at` を使わないため、平均採用日数が常に 0 に近い無意味な値になる。論文用・dogfooding 用の記録指標にも影響する。

4. T-011 traceability の完了判定が実際の文書形式と合っていない可能性がある。
   - 出典: claude-sonnet-4-6 ERROR 001、ERROR 002、WARN 006
   - 平易な説明: テスト戦略や要件追跡を確認する最後のゲートが、英語 token や表の行形式に依存しており、正しい実装でも失敗する、または無効な検査になる恐れがある。

5. `status_change` の aspirational → enforced 昇格承認が通常承認と同じ強さになっている可能性がある。
   - 出典: claude-sonnet-4-6 ERROR 003
   - 平易な説明: 正式規律化は普通の承認より重い操作として扱う設計だが、実装上は同じ「承認します」で通るなら、特別ゲートになっていない。

6. `new_discipline` の「関係明示」が機械検証可能な形に定義されていない。
   - 出典: claude-sonnet-4-6 ERROR 004
   - 平易な説明: 「既存規律との関係を書く」という条件が、空でない文字列なら通る状態だと、実質的に中身を検査していない。

7. RB 採番が全4ディレクトリ走査ルールを満たしていない可能性がある。
   - 出典: gpt-5.4 ERROR 3
   - 平易な説明: rollback ID の衝突を避けるために複数ディレクトリを見る設計なのに、rollback 配下だけを見るなら履歴連結が壊れる可能性がある。

8. self-improvement の運用文書が規律ファイル直接更新権を持つように読める。
   - 出典: gpt-5.4 WARN 4
   - 平易な説明: 実装は提案権のみのはずだが、文書が `docs/disciplines/` 更新を出力に含めると、権限分離を誤解させる。

### should-fix

1. proposal schema に提案種別ごとの条件分岐が弱い。
   - 出典: claude-sonnet-4-6 WARN 007、gpt-5.4 ERROR 2 と関連
   - 平易な説明: Python 実装だけで検査している条件があり、schema だけ読む下流には伝わりにくい。

2. consolidation の `source_discipline_paths` が archive パスを扱えるか確認が必要。
   - 出典: gpt-5.4 ERROR 2
   - 平易な説明: 統廃合では archive 済み規律も参照しうるため、パス制約が狭すぎると正しい提案を表現できない。

3. input_model が `records` 配列 YAML 前提に寄りすぎている。
   - 出典: gpt-5.4 WARN 2
   - 平易な説明: 上流出力を直接消費する設計なのに、中間形式への整形を前提にすると契約が弱くなる。

4. signal schema の独自キー `required_for_obsolete_or_conflict` は JSON Schema として強制されない。
   - 出典: gpt-5.4 WARN 3
   - 平易な説明: 人間には意味が分かっても、標準 schema validator は見ない可能性がある。

5. commit 独立性をハッシュ値の不一致として判定している点は再確認が必要。
   - 出典: gpt-5.4 WARN 1
   - 平易な説明: 所有者と意味が違うことが重要で、同じ commit hash なら必ず不正とは限らない。

6. conversation 参照のみの承認証跡は事後監査に弱い。
   - 出典: claude-sonnet-4-6 WARN 010
   - 平易な説明: 会話ログが deploy 後に同梱されないと、承認の中身を機械的に追えない。

### leave-as-is

1. signal 抽出の分類優先順位の曖昧さ。
   - 出典: claude-sonnet-4-6 INFO 011
   - 平易な説明: 第1期は半自動運用なので即時の遮断条件ではない。ただし後で自動化するなら優先順位を定義する価値がある。

2. proposal schema が `RB-NNN` を許容する点。
   - 出典: claude-sonnet-4-6 INFO 012
   - 平易な説明: 名前空間の緩さではあるが、ただちに壊れるとは限らない。rollback schema 側との役割分担を見て判断する。

3. rejection 語彙の追加候補。
   - 出典: claude-sonnet-4-6 WARN 009
   - 平易な説明: 運用語彙の改善候補ではあるが、正本語彙の拡張判断が必要で、実装修正だけで進めるべきではない。

## 次の判断

must-fix は実装修正候補だが、重要件であるため、この記録だけで実装修正へは進まない。次段階では must-fix を同根問題ごとにまとめ、1件ずつ平易な説明、候補案、推薦案、影響範囲、必要テストを提示し、承認または proxy decision を記録してから実装する。
