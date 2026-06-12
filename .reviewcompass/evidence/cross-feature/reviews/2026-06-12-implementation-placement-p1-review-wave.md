# review-wave 実施記録：implementation placement-p1（reopen R-0 第3過程）

- feature: all_features（確認範囲）／変更主体は conformance-evaluation
- 対象 phase/stage: implementation / review-wave
- 日付: 2026-06-12
- 位置付け: reopen-procedure-2026-06-12-placement-p1-ce の第3過程。implementation triad-review（3 round、収束）後の機能横断確認

## 確認内容と実行した検証コマンド

1. 他機能のコード・テストからの旧 conformance 配置参照：
   `grep -rn "specs/[a-z_-]*/conformance" tools/ --include="*.py"`（conformance_evaluation 除外）→ **0 件**
2. 旧推定ログ `logs/estimation/` への参照（conformance-evaluation 以外）：
   `grep -rln "logs/estimation" tools/ tests/ templates/` → 実験記録 `tools/experiments/results/topic-116-*.yaml` 2 件のみ
   （topic-116 設計検討時の凍結済み履歴記録。現役コードの参照ではなく影響なし）
3. 全 7 機能の仕様 3 文書（requirements/design/tasks）での旧パス現役参照（凍結・由来注記を除く）：grep → **0 件**
4. 配布物（deploy-manifest.yaml）：旧配置 `.reviewcompass/specs/*/conformance/**` と `logs/**` は除外済み。
   **新配置 `.reviewcompass/evidence/**` の除外が未追加**で、現状のままだと開発証跡（review-runs・
   features/*/conformance・estimation ログ）が配布物に同梱され得る。
5. テスト：全スイート（ディレクトリ別）計 900 件 pass、回帰なし

## 持ち越し

- 新規の carry-forward 登録：**0 件**
- 既計画タスクへの経路付け：**1 件** — deploy-manifest.yaml への `.reviewcompass/evidence/**` 除外追加。
  利用者決定済みの P1 残作業 #9（配布物再生成＋smoke、`docs/notes/2026-06-12-document-placement-stage4-migration.md` の移行計画）で対応する。
  新規所見ではなく、配置規約 P1 の段階 4 計画に含まれる追従作業の具体化である

## 判断結果

- decision: **no_impact**（他機能の仕様正本・実装への波及なし。配布 manifest の追従は既計画 P1 残作業 #9 の範囲）
- 根拠: 上記 grep 結果（旧パス現役参照 0 件）、本実装の変更が conformance-evaluation の所有モジュールと
  その運用文書・テストに閉じていること、全テスト green
