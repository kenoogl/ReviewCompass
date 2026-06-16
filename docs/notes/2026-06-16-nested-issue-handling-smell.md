# nested issue handling smell

日付：2026-06-16

## 目的

ある作業中に別の問題が見つかり、その問題対応を先に行う必要がある場合の手戻りを記録する。
これは横方向の workflow 混線ではなく、作業が縦方向に深くネストする型である。

## 今回発生したこと

最初の作業は、`criteria / prompt が弱い` という点を
`docs/notes/2026-06-16-workflow-recovery-smell-inventory.md` に起票することだった。

その post-write verification 中に、別の問題が見つかった。

- manifest は 2 ファイルを検証済みと表現していた
- しかし参照 review-run の `target-manifest.yaml` は 1 ファイルだけを対象にしていた
- そのため、manifest coverage と review-run 実 target set のずれを B-14 として追加した
- B-14 を確認するには、workflow recovery smell inventory だけでなく、
  operation registry / preflight 設計メモとの整合も見る必要が出た
- 結果として、B-14 発見時点では 2 文書を runtime bundle にまとめて
  post-write verification する流れになった

なお、本メモを追加した後の post-write verification では、この新規メモ自体も対象に入るため、
検証 bundle は 3 文書になる。上の 2 文書という記述は、B-14 発見時点の経緯を指す。

これは、元タスクの実施中に別問題が発生し、その対応がさらに別文書や別検証を要求した例である。

## 問題の型

問題の型は次である。

```text
主作業 A
  -> 問題 B を発見
      -> B 対応を先に実施
          -> B 対応中に問題 C または対象拡大を発見
              -> C 対応または追加検証が必要
```

この型では、作業が正当な理由で深くなる一方、元作業の完了条件、検証範囲、
利用者への報告単位が曖昧になりやすい。

## 横方向の混線との違い

既存の worktree 混線 preflight は、主に横方向の混在を扱う。

例：

- post-write pending 中に別件のコード変更が混ざる
- reopen 手続き中に無関係な作業差分を追加する
- commit approval 作成後に別ファイルを staged へ混ぜる

今回の問題はこれとは違う。

今回の問題は、元作業と関係のある発見から始まり、対応のために対象範囲が段階的に広がる。
そのため、単に「別件だから止める」だけでは処理できない。

## 危険

1. 元タスクの完了条件がぼやける。

   例：最初は B-13 起票だったが、途中から B-14、multi-target bundle、
   operation registry メモ修正まで広がった。

2. 検証対象が広がる。

   例：1 文書の post-write verification だったはずが、B-14 発見時点では
   2 文書を同時に検証する必要が出た。本メモ追加後の検証では、このメモも含めて
   3 文書を一括確認する。

3. post-write verification が設計壁打ちへ変質しやすい。

   例：メモの確認中に schema、parser adapter、operation kind の詳細設計へ入り始めた。

4. 報告単位が曖昧になる。

   元作業、途中で見つかった問題、追加修正、追加検証のどこまでを同じ作業として報告するかが
   手判断になる。

5. review-run / manifest / bundle の証跡が増え、途中成果物の整理が必要になる。

## 直接原因

今回の直接原因は、post-write verification 中に manifest coverage と review-run 実 target set の
ずれを見つけ、その対応を先に行う必要が出たことである。

## 本質原因

本質原因は、作業中に見つかった問題を次のどれとして扱うかを機械的に分ける仕組みが弱いことである。

- 今すぐ直す blocker
- 後続メモへ送るだけでよい issue
- 元作業とは別の side-track
- 元作業の scope を広げる必要がある dependent issue

現状では、この分類が会話上の判断に依存している。

## 対策候補

### 1. nested issue stack

作業中に新しい問題を見つけたら、次を記録する。

- parent task
- discovered issue
- relation to parent
- blocker or follow-up
- allowed files
- return condition
- maximum nesting depth

例：

```yaml
parent_task: record_review_criteria_prompt_smell
issue_id: post_write_manifest_coverage_mismatch
relation: blocks_parent_verification
handling: fix_now
allowed_files:
  - docs/notes/2026-06-16-workflow-recovery-smell-inventory.md
  - docs/notes/2026-06-16-operation-registry-preflight-design.md
return_condition: post_write_manifest_target_set_matches_actual_review_target_set
max_depth: 2
```

### 2. issue 分類 preflight

新しい問題を見つけた時点で、次を判定する。

- 元作業の完了を妨げるか
- 今修正しないと証跡が不正になるか
- 修正対象ファイルが増えるか
- review scope が増えるか
- 後続 SDD へ送るだけでよいか

### 3. ネスト深度の上限

一定以上深くなったら、実装や修正を続けず、棚卸しに切り替える。

候補：

- depth 1：元作業中に見つかった blocker は対応可
- depth 2：対応可だが、return condition を必須にする
- depth 3：原則停止し、別課題メモ化する

### 4. return condition の明示

side issue を先に扱う場合、元作業へ戻る条件を先に決める。

例：

- B-14 を起票したら元の B-13 post-write に戻る
- multi-target bundle review が completed になったら作業終了判定へ戻る
- WARN が詳細仕様化の指摘だけになったら後続 SDD 送りとして triage する

### 5. review 変質検出

post-write verification が確認ではなく設計補助になっている兆候を検出する。

兆候：

- round 数が増える
- schema 詳細の指摘が増える
- parser adapter や enum の厳密化へ入り始める
- 元作業の文書タイプを超えた仕様化を要求される

この場合、document-type preflight / review criteria preflight と連動して、
「post-write 継続」ではなく「後続 SDD 論点化」へ切り替える。

## 機械処理できる範囲

機械処理できる。

- nested issue stack の記録
- parent / child issue の関係
- allowed files の差分検査
- target files の増加検出
- review-run / manifest / bundle の scope 増加検出
- nesting depth の警告
- return condition 未設定の検出
- depth 超過時の停止

機械処理しにくい。

- 問題が本当に blocker かどうかの意味判断
- 後続 SDD 送りでよいかどうかの最終判断
- review 指摘の意味的妥当性

## 後続対応案

operation registry / preflight の後続 SDD では、独立項目として
`nested_issue_stack` または `side_track_stack` を検討する。

候補 operation：

- `issue_discovered`
- `issue_classify`
- `issue_push`
- `issue_return`
- `issue_abort_to_followup`

最初は runner ではなく、read-only preflight と記録だけでよい。

## 既存 preflight 項目との関係

この課題は、既存の post-write / review scope 系 preflight を置き換えるものではない。
役割分担は次の通りである。

- `document_type_preflight`：文書タイプと review 期待値を決める
- `review_criteria_preflight`：API reviewer に渡す scope / out-of-scope / finding policy を決める
- `post_write_manifest_coverage_preflight`：manifest の target set と review-run / bundle の実 target set を照合する
- `nested_issue_stack`：作業中に見つかった別問題を、今すぐ扱う blocker か後続 issue かに分類し、
  parent task、allowed files、return condition、depth を記録する

つまり、B-12 / B-13 / B-14 は個別の検証品質を守る preflight であり、
`nested_issue_stack` はそれらが作業中に連鎖したときの親子関係と戻り条件を守る。

完了条件も分けて考える。

- B-12 / B-13 / B-14 側の完了条件：文書タイプ、review criteria、manifest coverage が正しく判定されること
- nested issue 側の完了条件：それらの問題が作業中に発見されたとき、親作業との関係、
  先に扱う理由、戻り条件、深さ上限が記録されること

## 期待する完了条件

- 作業中に別問題を見つけた時、今すぐ直すか後続化するかを記録できる
- 問題対応で対象ファイルや review scope が広がった時、機械的に検出できる
- ネストが深くなりすぎた時に停止できる
- side issue 対応後、元作業へ戻る条件が明示されている
- post-write verification が設計壁打ちへ変質した場合、後続 SDD 論点として切り出せる
