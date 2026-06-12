# レビュー対象：reopen R-0（parse-error-failclosed）requirements 変更

## 0. variant 選定理由（実行前ゲートの記録）

- 使用 variant：`implementation_review_independent_3way`（context: triad_review、API 3 社独立）
- 役割：primary=anthropic-api/claude-sonnet-4-6、adversarial=openai-api/gpt-5.5、judgment=gemini-api/gemini-3.1-pro-preview
- 選定理由：本日の multi-llm-entry reopen の triad-review と同一構成（利用者承認済みの
  「Claude Code 操縦時の API 既定」。正本は SESSION_WORKFLOW_GUIDE §3.3 (a-3)）。

## 1. レビューの位置付け

reopen R-0（分類記録 `docs/reviews/reopen-classification-2026-06-12-parse-error-failclosed.md`）の
第3過程、requirements フェーズの triad-review。対象 feature は workflow-management のみ。

背景：feature-dependency.yaml（機能一覧表）が「存在するが YAML として読めない」場合、現実装は
ファイル不在・キー未定義と同じ立ち上げ案内（OK）を返す。この挙動は本日の先行 reopen の
triad-review 所見 F4 でいったん「現挙動の明文化＋改善候補追跡」（案 a）と決まったが、利用者が
同日この判断を改め、「破損が案内に覆い隠される」問題の根本対策として遮断分離（案 b、MLE-DEC-005）を
決定した。本変更は**実装より先に仕様を確定する正順**であり、実装は仕様確定後に implementation 段で
TDD（失敗テスト→実装→全テスト通過）により行う。**現時点で実装は旧挙動のまま**である（意図的）。

## 2. 変更内容（workflow-management requirements.md Requirement 8）

### 2.1 受入 8 の限定（案内の対象を不在・未定義のみに）

> 8. feature 一覧が解決できない場合のうち、`feature-dependency.yaml` がどの探索先にも存在しない、
> または `feature_order` キーが未定義の場合、検査ツールはエラーではなく
> `next_action.kind: feature_definition_required`（verdict OK、exit code 0）を返し、
> intent／feature-partitioning の実施と、承認された分割結果（依存の根拠と順序の導出を含む）の
> `feature-dependency.yaml` への記録を案内する（2026-06-12 反映、MLE-C-002）。

### 2.2 受入 9 の新設（パース不能の遮断）

> 9. ファイルは存在するが YAML として読めない（パース不能）、または最上位が連想配列でない場合は、
> 未定義と区別して遮断する。`next` は `next_action.kind: unknown` を返し、破損ファイルのパスと
> 内容確認を促す理由を `reasons` 配列に列挙し、verdict は DEVIATION（exit code 2、fail-closed）とする。
> 破損を立ち上げ案内で覆い隠さない（2026-06-12 反映、MLE-DEC-005。同日の triad-review F4 では
> 現挙動の明文化（案 a）をいったん採ったが、利用者決定により遮断へ改めた。FUP-2026-06-12-001 の解消）。

### 2.3 Change Intent への追記

reopen R-0（parse-error-failclosed）の経緯と「仕様確定後に TDD で実装する正順」である旨を 1 項目追加。

## 3. 根拠と証跡

- 利用者決定：MLE-DEC-005（2026-06-12「私の判断がまちがっていた。コストはかかるが案ｂが根本対策と考える」。
  reopen handoff package に記録済み）
- 問題の実害：表を編集ミスで壊した利用者に「intent から始めよ」と案内され、本当の原因（破損）が
  隠れる。最悪、案内に従い表を作り直して依存関係の記録を失う
- 同時改訂：design §機能依存マップモデル §7（「パース不能の遮断」項の新設）、tasks T-004（契約文言と
  テスト要件）。これらは後続フェーズの triad-review で扱う
- 整合先：受入 6（探索順・最初の 1 ファイル）、受入 7（整合違反の遮断。出力形式は受入 9 と同型）、
  fail-closed 原則（design 判断 3）

## 4. レビュー観点

1. 受入 8（案内）と受入 9（遮断）の境界が一義に読めるか。「読めない」の定義
   （パース不能・最上位が連想配列でない）に漏れや曖昧さはないか。
2. 受入 9 の出力規定（kind unknown・reasons に破損パスと確認促し・DEVIATION・exit 2）が
   受入 7 の整合違反の出力規定と整合し、検証可能か。
3. 「実装は旧挙動のまま、仕様を先に確定する」という本 reopen の進め方が、文書から誤解なく
   読み取れるか（仕様と実装の一時的な不一致が明示されているか）。
4. 受入 6〜9 全体として、本日の先行 reopen で確定した文言との矛盾がないか。
