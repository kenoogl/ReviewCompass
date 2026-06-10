---
name: avoid-compound-bash
description: 読み取り目的の複合 Bash コマンドを避ける。Read／Glob／Grep ツールで代替するか、Bash は単一コマンド 1 つに留める
metadata:
  type: feedback
---

読み取り目的（ファイル列挙、行数集計、文字列検索、ログ末尾確認など）で Bash を呼ぶときは、次の優先順位で対応する：

1. **Read ／ Glob ／ Grep ツールを使う**（Bash を呼ばない、許可プロンプト発生せず）
   - ファイル内容を見る → Read
   - パス・ファイル列挙 → Glob
   - 文字列検索 → Grep
2. Bash が必要な場合は **単一コマンド 1 つ** に留める
3. 複数情報が必要なら **複数の独立した Bash 呼び出しに分ける**（並列実行可、許可リストが効く）

**避けるべきパターン**：`;`／`&&`／`|` で複数コマンドを繋ぐ複合 Bash。例：`tail file.log; ls dir/ | grep pattern | wc -l`

**Why**：

Claude Code の permission 機構（許可リスト）は **単一コマンドのシグネチャ単位** で効く。複合コマンドは組み合わせごとに別シグネチャ扱いとなり、毎回新規承認プロンプトが発生する。利用者は毎セッション「許可をとるのが多すぎる」「同じ議論を何度もしている」と指摘してきたが、私の習慣として複合 Bash を多用し改善されていなかった。2026-05-28 セッション 36 で再指摘を受けて確立。利用者明示承認の出典：「案 イを処理」（規律本体を repo `docs/disciplines/` に新設、memory はシンボリックリンクで参照、2026-05-28 セッション 36）。

**How to apply**：

- Bash 呼び出しを書く前に自問：「Read／Glob／Grep ツールで代替できないか？」
- 代替できない場合：複合せず単一コマンドにする。`;`／`&&`／`|` の使用を最小化
- 複数情報を取りたい場合：複数の独立した Bash 呼び出しを並列発行（同じ応答内に複数 Bash ブロック）
- 例外：パイプが本質的に必要な場合（`grep | wc` の集計など）のみ複合を許容、ただし利用者承認の負担を意識
- 削除・書き込み・移動などの不可逆操作は規律 [[approval-operation]] に従い別途明示承認

**典型例**：

- × `cat file.log | tail -20`
- ○ Read file.log offset=… で末尾を読む
- × `ls dir/ | grep pattern | wc -l`
- ○ Glob で列挙、結果を Bash 不要でカウント
- × `git log --oneline; git status; git diff`
- ○ 3 つの独立した Bash 呼び出しを並列発行

関連：[[plain-japanese]]（平易な日本語）、[[concise-complete-report]]（簡潔・もれなく報告）、[[approval-operation]]（不可逆操作の明示承認）
