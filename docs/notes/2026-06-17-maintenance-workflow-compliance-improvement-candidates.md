# maintenance workflow 遵守の修正候補メモ

作成日: 2026-06-17

## 背景

D-003 reopen 以降、`next --json` 改修、commit approval 改修、rollback 整理、退避資料の再取り込みが連続し、作業の途中で maintenance と reopen の文脈が混線した。

特に、利用者から「ワークフロー規約に沿って進める」「メンテモードで対応」と明示されていたにもかかわらず、maintenance を通常の workflow unit と同等に扱う手順が徹底されず、レビュー工程の扱いが曖昧になった。

このメモは、直ちに実装する仕様ではなく、今後の修正候補として記録する。

## 観測された問題

1. maintenance が「短い修正」扱いになり、要件・設計・タスク・レビューの確認を省略しやすかった。
2. maintenance YAML は scope、files、completion を記録できるが、review process の必須性を明示する構造が弱い。
3. post-write verification と、実装・設計に対する review process が混同された。
4. `next --json` が completed を返した後、maintenance を始める場合の正規入口が弱く、LLM の判断に寄りやすかった。
5. commit approval、post-write manifest、review-run 証跡、staged index の問題が重なり、commit 手続きへの注意で workflow 手順確認が後景化した。
6. `TODO_NEXT_SESSION.md` などの引き継ぎ資料が最新状態に追随せず、直近の正本が分かりにくくなった。
7. D-003 reopen、commit process、next --json、rollback recovery の文脈が混ざり、どの作業単位を完了扱いにしてよいかが曖昧になった。
8. Codex sandbox では、workflow 的な commit approval が通った後に、実際の `git commit` が `.git/index.lock` 作成権限で失敗することがある。この場合、利用者からは「承認したのに別の確認で止まった」ように見え、commit 手続き全体が壊れているように感じられる。

## 修正候補

1. maintenance workflow protocol を明文化する。
   - in-progress maintenance 作成
   - 要件・設計・タスク相当の確認
   - TDD が必要な場合の test-first
   - 実装後 review
   - post-write verification
   - completed maintenance 化

2. maintenance YAML に review evidence を表すフィールドを追加する。
   - `workflow_steps`
   - `required_reviews`
   - `review_evidence`
   - `post_write_verification`
   - `completion_criteria`

3. `next --json` が maintenance 中の不足工程を一意に返せるようにする。
   - maintenance review required
   - maintenance post-write required
   - maintenance completion required
   - wait for human decision

4. post-write verification と implementation/design review を別工程として扱う。
   - post-write は「書いた文書・証跡の整合確認」
   - review は「変更内容そのものの妥当性確認」

5. commit 前 guard に maintenance workflow の未充足検出を追加する。
   - code または SDD に触れた maintenance は review evidence がないと完了扱いにしない。
   - docs note だけの記録作業は軽量 post-write で足りるかを明示する。

6. 大きな maintenance、rollback、reopen 中断後は、引き継ぎ資料の更新を workflow の一部にする。
   - `TODO_NEXT_SESSION.md`
   - 関連する `docs/notes`
   - workflow state / maintenance YAML

7. completed 状態から maintenance を開始する標準手順を定義する。
   - completed は「作業不要」ではなく、「利用者指示により maintenance / reopen / new workflow を開始可能」と扱う。
   - その際の最初の required action を機械的に決める。

8. maintenance、reopen、新規 workflow unit の使い分け基準を定義する。
   - 既存成果物の軽微な修正、運用手順の補正、証跡整理は maintenance とする。
   - 完了済み workflow unit の要求・設計・タスク・実装判断を再開して見直す場合は reopen とする。
   - 既存 feature / phase に属さない新しい目的を開始する場合は新規 workflow unit とする。
   - 判断が分かれる場合は候補だけを返し、人間判断を required action とする。

9. Codex sandbox の Git 書き込み権限を commit 実行前に preflight する。
   - `guarded-git-commit.py` が `git commit` 直前に `.git/index.lock` の作成可否を確認する。
   - 作成不可の場合は、approval を消費せず、`required_action=rerun_commit_with_escalation` を返す。
   - 同じ staged digest / approval を保持したまま、sandbox 外実行で guarded commit を再試行できるようにする。
   - sandbox 外で再試行する直前にも、承認時の staged digest と現在の staged digest を完全一致で再照合する。
   - staged digest が一致しない場合は、既存 approval を使わず、新しい challenge / approval からやり直す。
   - `git commit` 実行後に `.git/index.lock` / permission 系エラーが返った場合も、通常の commit failure ではなく `sandbox_git_write_denied` として分類する。
   - 利用者への表示は「承認は保持された」「staged digest が変わらなければ再承認不要」「sandbox 外 commit 再実行が必要」に絞る。

10. 手続きの比例性を、まず軽い運用規則として試す。
   - 仕様駆動と TDD 主導の二択を機械分類へ直ちに組み込まない。
   - 影響範囲が局所的で、既存仕様境界を変えず、入出力が明確な変更は、TDD 主導の軽量手順を許容する。
   - workflow 中核、承認、状態機械、reopen、post-write、`next --json` の意味を変える変更は、仕様駆動で扱う。
   - 作業開始時に、LLM が次の 3 行だけを宣言する運用から始める。
     - `変更分類: 局所 / 中核`
     - `理由: <影響範囲と既存仕様境界の説明>`
     - `手順: TDD 主導 / 仕様駆動`
   - 最初から guard、schema、`next --json` の機械機能へ入れない。数件の運用実例を観察し、必要な最小部分だけ後で機械化する。

## 変更対象候補

現時点の候補であり、実装時には改めて workflow に沿って確定する。

- `docs/operations/WORKFLOW_NAVIGATION.md`
- `docs/operations/WORKFLOW_PRECHECK.md`
- `docs/operations/SESSION_WORKFLOW_GUIDE.md`
- `tools/check-workflow-action.py`
- `tools/guarded-git-commit.py`
- `tools/check_workflow_action/commit_approval.py`
- `tests/tools/test_check_workflow_action.py`
- `tests/tools/test_guarded_git_commit.py`
- `learning/workflow/schemas/side-track-state.schema.json`
- maintenance YAML 専用 schema / validation は現時点で未特定。存在しない場合は、上記 side-track schema に寄せるか、新規 schema と validator を追加する。

## 優先度

D-003 reopen を再開する前に、少なくとも maintenance workflow protocol の明文化、commit sandbox preflight の扱い、直近 maintenance commit の retrospective review を行うべきである。

対象候補は、ReviewCompass リポジトリの `main` ブランチ上の以下の commit とする。

- `7f346075 Reuse active commit approval transactions`
- `0d611816 Make next json action selection unique`
- `0183005e Import next json redesign note`

`0183005e` は資料取り込みが主目的だが、post-write 証跡と workflow 上の扱いは確認対象に含める。

## 今回は実施しないこと

- maintenance workflow protocol の実装
- `next --json` の追加改修
- guard の追加改修
- D-003 reopen の再開

今回の範囲は、修正候補として記録することに限定する。
