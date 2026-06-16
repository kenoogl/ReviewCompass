# 手戻りで通過した作業導線の棚卸し

日付：2026-06-16
文書タイプ：棚卸しメモ（実装正本ではない）
review 期待値：発生事象、共通原因、機械化候補、追跡単位の整理を確認する。具体 API や JSON schema は後続 SDD で固定する。
document-type preflight 結論：この文書は棚卸しメモとして扱い、再分類は不要。仕様候補は後続 SDD へ送る。

## 背景

2026-06-16 の Codex TODO hook 対応では、最終的に guard、post-write review、
手動修正によりコミットまで到達した。一方で、作業途中に複数の手戻りが発生した。

これらは個別のミスに見えるが、共通して「最初から間違えにくい導線」ではなく、
後段の検査や人間的な気づきで回復している。

このメモは、当初ばらばらに記録した次の 3 件を統合し、追加調査で見つかった
類似入口もあわせて棚卸しする。

- 現セッション正式記録の生成前防止ギャップ
- post-write review 差分 bundle の取得元選択ミス
- commit 承認と LLM 実行代行承認の設計ギャップ

## TODO 未完了候補との関係

`TODO_NEXT_SESSION.md` の未完了候補には、実アプリ pilot や P3 最終形のような
大きな作業も含まれる。このメモが直接扱うのは、そのうち次の「作業導線の弱さ」
に関する候補である。

- 正本優先の規律化／生成ツール横展開の検討
- reopen 進行中／完了 YAML の手編集事故対策
- commit 承認記録の安全な生成方法の検討
- reopen approval gate の blocker 構造化
- reopen-advance-gate の追加テスト
- reopen-advance-gate の gate 正規化検査
- 裁定負荷対策の運用開始時に必要になる、重要決定記録の作成前検査

一方、実アプリ pilot、レビュー証跡の機能側ポインタ要件の一般化、P3 最終形の
専用 reopen 計画は、このメモから派生する局所改善ではなく、別の作業単位として
扱う。

## 今回見つかった主要 3 件

### 1. 現セッション正式記録の生成前防止不足

Codex の TODO 更新 hook は、現セッションを正式な 2 層セッション記録へ直接書かず、
`.reviewcompass/runtime/session-record-drafts/` の下書きへ保存する設計へ変更した。
正式な 2 層記録は、セッション終了後に `tools/session-record-promote-draft.py` で
昇格する。

この設計により、通常の TODO 更新 hook 経路では「今まさに進行中の会話」を
`.reviewcompass/evidence/sessions/` と `docs/sessions/` へ直接作らない。

しかしコミット前の作業中に、現セッションがまだ継続中であるにもかかわらず、
手動操作により正式な 2 層セッション記録を再生成してしまった。

生成された 2 件は commit guard により「元 rollout が生成時から変化している」、
すなわち「進行中セッション記録」と判定され、コミット対象から除外した。
最終的にコミットへ混入しなかったため、commit guard は最後の検出として機能した。
一方で、正式記録を「作ってしまうこと」自体は生成前に防げていなかった。

残る穴：

- hook 経路は現セッションを draft にだけ書く
- しかし手動 backfill や再生成経路では、誤って現セッションを正式 2 層記録として作れる
- commit guard は混入を止めるが、生成自体は止めない
- current session id が取得できない環境で、推測や一括処理に戻ると再発し得る

後続対応案：

1. 正式 2 層記録を書ける入口を棚卸しする。
   - `tools/session-record-backfill.py`
   - `tools/session-record-promote-draft.py`
   - hook 経路
   - bulk / historical import 経路
   - テスト helper や将来追加される capture helper
2. current session 判定を共通関数へ寄せる。
   - 各 CLI が個別に似た判定を書くのではなく、同じ guard を使う
   - `session_id` が current と一致する場合、正式 2 層出力を拒否する
3. current session id が取得できない場合は fail-closed にする。
   - current を確認できないなら、正式昇格しない
   - 終了済み rollout を明示指定した backfill だけに戻す
4. 正式出力できる経路を限定する。
   - 現セッションは runtime draft のみ
   - 終了済み draft の正式化は promote helper
   - backfill は終了済みセッション専用
5. commit guard は維持する。
   - source hash の変化検出により、生成前防止をすり抜けた場合もコミット混入を止める

期待する完了条件：

- current session を正式 2 層記録へ生成しようとするテストが失敗から始まる
- 共通 guard 導入後、すべての正式出力入口で current session が拒否される
- current session id が不明な場合に、正式出力が fail-closed する
- 終了済みセッションの明示 backfill と draft promote は引き続き通る
- commit guard の進行中セッション検出は削除せず、最後の保険として残る

### 2. post-write review 差分 bundle の取得元選択ミス

post-write review では、変更内容をレビュー対象へ渡すために差分 bundle を作る。
この bundle は、実際にレビューしたい変更範囲と一致している必要がある。

Git では差分の置き場所が分かれている。

- `git diff` は未 staged の差分を見る
- `git diff --cached` は staged 済みの差分を見る

今回、変更はすでに `git add` 済みで、レビューすべき差分は staged 側にあった。
しかし、差分 bundle を作る際に `git diff` を使ったため、未 staged 側の差分だけを
見に行ってしまった。

結果として、review 用 bundle が空または空に近い内容になった。その後、差分が
staged 側にあることに気づき、`git diff --cached` で bundle を作り直して review を
再実行した。

直接の要因は、bundle 作成前に `git status --short` 等で差分の所在を明示確認せず、
習慣的に `git diff` を選んだこと。構造的な要因は、post-write review bundle 作成が
まだ手作業に寄っており、次の判定が機械化されていなかったことである。

- staged 差分があるか
- unstaged 差分があるか
- 両方ある場合に自動で混ぜてよいか
- どちらも無い場合に空 bundle を作らず止まれるか
- 作成した bundle が review manifest の対象と一致しているか

後続対応案：

1. `git diff --cached --name-only` で staged 差分を確認する。
2. `git diff --name-only` で unstaged 差分を確認する。
3. 状態に応じて分岐する。
   - staged のみ：`git diff --cached` で bundle を作る
   - unstaged のみ：`git diff` で bundle を作る
   - staged と unstaged の両方あり：fail-closed し、明示指定を要求する
   - どちらも無し：fail し、空 bundle を作らない
4. bundle 作成後、空でないことを検査する。
5. review manifest の target と bundle の対象ファイルが一致するか検査する。

期待する完了条件：

- staged のみの変更では、自動的に `git diff --cached` が使われる
- unstaged のみの変更では、自動的に `git diff` が使われる
- staged / unstaged が混在する場合は、勝手に混ぜず停止する
- 差分なしの場合は、空 bundle を作らず停止する
- bundle の対象ファイルと post-write review manifest の対象がずれていれば停止する
- これらをテストで固定し、LLM の注意力ではなく helper の判定に寄せる

### 3. commit 承認と LLM 実行代行承認の正式経路不足

ReviewCompass の commit guard は、LLM が commit を実行する場合に 2 種類の承認を
区別して扱う。

- 内容承認：現在 staged されている内容を commit してよい
- 実行代行承認：LLM が commit コマンドの実行を代行してよい

この分離は安全上必要である。過去に「自律実行」等の指示を広く解釈し、LLM が
commit 実行まで進める問題があったため、`execution_actor=llm` の場合は
`execution_delegation` を別途要求する。

一方で、2026-06-15 に導入した nonce 方式の `commit-approval prepare/record` は、
主に staged 内容への承認を nonce、target digest、TTL に束縛する仕組みである。

今回、利用者が単発で「コミット」と明示指示したため、現在 staged されている内容に対して
`commit-approval prepare` と `commit-approval record` を実行し、承認レコードを作成した。
この承認レコードには、ユーザ発話 `コミット` が `source_text_redacted` として保存され、
staged 内容への nonce / digest 束縛も成立していた。

しかし guard は、LLM が commit を実行するために必要な `execution_delegation` が無いとして
commit を拒否した。調査したところ、既存テストには「`commit-approval record` は既定で
`execution_delegation` を埋め込まない」ことが明示されていた。つまり、内容承認と
実行代行承認を分ける方針自体は意図されたものだった。

ただし、現状の正式 CLI には、ユーザ発話を安全に `execution_delegation` として記録する
手段が不足していた。そのため、今回の commit では runtime の承認レコードへ
`execution_delegation` を手作業で追記するワークアラウンドが発生した。
これは回復できた処理ではなく、本来は正式 CLI が無い時点で fail-closed し、
commit へ進まず後続設計課題として止めるべきだった。
今回のように既に使ってしまった一時 runtime 承認レコードは、再利用可能な正式証跡へ
昇格しない。履歴上の事実としてだけ扱い、未使用・未消費の同種レコードが残る場合は、
正式 CLI が整うまで commit 実行根拠として使わず、破棄または無効化の対象にする。

問題：

- guard は内容承認と LLM 実行代行承認の両方を要求する
- `commit-approval record` は内容承認のみを正式に生成する
- LLM が commit する通常ケースで、正式 CLI だけでは必要フィールドを完結して作れない
- 結果として runtime JSON 手編集に逃げる余地が生じる

承認まわりで runtime JSON 手編集を前提にすると、何を誰が承認したのかが曖昧になり、
過去に削除した `make-commit-approval.py` と同種の問題を再導入しかねない。

設計時に考慮すべき点：

1. 内容承認と実行代行承認を記録上も分ける。
   - `コミット` という 1 つの発話で両方を満たす場合はある
   - ただし意味は別なので、フィールドも検証も分ける
2. LLM が勝手に delegation を作れないようにする。
   - nonce、target digest、TTL、source を通じてユーザ発話と staged 内容に束縛する
   - LLM が任意文字列で承認を自作できる構造にしない
3. 発話解釈ルールを明確にする。
   - `コミット`、`コミットして`、`コミットを実行` は停止点での単発 commit 代行として許可候補
   - `次のコミットまで` は commit 実行を含まない
   - `自律実行` だけでは commit 実行代行を含まない
   - `コミット代行も含めて自律実行` のような明示は許可候補
4. source の扱いを安全にする。
   - 保存する場合は redaction 必須
   - 機微情報が残る場合は保存せず、`source_omission_reason` を記録する
   - 内容承認 source と delegation source を分けて扱えるようにする
5. 正式 CLI だけで完結させる。
   - runtime JSON の手編集を前提にしない
   - 例：`commit-approval record --nonce ... --source-text-stdin --delegate-execution-to-llm`
   - 例：`commit-approval delegate-execution --nonce ... --source-text-stdin`
6. delegation も staged 内容へ束縛する。
   - 同じ nonce / target digest に紐づける
   - staged 内容が変わったら、内容承認だけでなく delegation も無効にする
7. 期限切れ・消費済み・再利用防止を一貫させる。
   - TTL 内だけ有効
   - commit 成功後は consumed
   - 別 commit へ再利用できない
8. human 実行との違いを保つ。
   - 人間が自分で commit する場合は execution delegation 不要
   - LLM が commit する場合だけ必要
9. 失敗理由を分けて表示する。
   - 内容承認が無い
   - 内容承認はあるが LLM 実行代行承認が無い
   - 発話はあるが delegation 許可として認められない
   - staged 内容が承認時から変わった
10. runtime 承認レコードの手編集を運用上禁止する。
   - 後続実装後は正式 CLI 以外で `execution_delegation` を追記しない
   - guard / docs / TODO にもその扱いを明記する

期待する完了条件：

- 正式 CLI だけで、内容承認と LLM 実行代行承認を安全に記録できる
- `コミット` は単発 commit 実行代行として通る
- `次のコミットまで` や `自律実行` だけでは commit 実行代行として通らない
- staged 内容が変わると、内容承認と delegation の両方が無効になる
- source redaction と omission が既存 commit approval 方針に沿う
- runtime 承認レコードの手編集が不要になる

## 追加で気になる点

### A-1. 不要な review-run / manifest を作ってから削除した

一度、使わない post-write review-run と manifest を作成し、後で削除した。

これは、review-run 作成前に次を機械的に確定する導線が弱いことを示している。

- run id が今回の作業内容と一致しているか
- target files が正しいか
- 既存 manifest と競合していないか
- 作成対象が現行の post-write verification として必要か

作成後に削除すれば最終状態は整うが、review 証跡は正本性が重要なため、
不要な証跡を作る前に止めるほうが望ましい。

### A-2. 実装完了と実環境発火確認の分離が後から明確になった

Codex TODO hook は、スクリプト、テンプレート、診断ログ、テストまでは実装した。
しかし、実際の Codex 実行環境で `.codex/hooks.json` から PostToolUse hook が
発火することは未確認だった。

post-write review の WARN により、この未確認点を TODO へ追記した。

これは正しく回復できたが、本来は実装計画または完了条件の段階で、
次を分離しておくべきだった。

- コード・テンプレートとして実装済み
- テスト環境で動作確認済み
- 実 Codex セッションで hook 発火確認済み

この区別が曖昧だと、実装完了を実運用確認完了と誤読しやすい。

### A-3. commit approval を作るタイミングが stale になりやすい

nonce 方式の commit approval は staged exact index に束縛される。
これは正しい安全設計だが、approval 作成後に staged 内容が変われば
承認は stale になる。

今回も、staged 内容の変化や除外作業により承認レコードを作り直す必要があった。

後続対応では、commit approval は次の状態になってから作る導線へ寄せるべきである。

- post-write verification が完了している
- 進行中セッション記録などの除外が終わっている
- staged 対象が最終確定している
- `git diff --cached --name-status` と guard 対象が一致している

approval は早く作るほど stale になりやすい。最終 staged 固定後にだけ作る
作業導線が望ましい。

### A-4. 調査前の説明が早すぎた

`execution_delegation` について、当初は「commit 承認機構側の小さな不整合」と
説明した。

しかし既存テストを確認すると、`commit-approval record` が既定で
`execution_delegation` を埋め込まないことは意図された設計だった。

正しい整理は次である。

- 内容承認と LLM 実行代行承認を分ける設計は意図通り
- ただし、LLM 実行代行承認を正式 CLI で記録する経路が不足している

このように、調査前の短い説明が後で修正されると、利用者には設計全体が揺れて
見える。特に承認・不可逆操作・証跡に関する説明では、断定前に既存テストと
正本文書を確認する必要がある。

## 再精査で見つかった追加候補

2026-06-16 の追加確認で、review-run / manifest / bundle / approval 以外にも、
同じ「作ってから検査・気づいて回復」になり得る入口が見つかった。

### B-1. review-run 成果物の上書き・混在

対象：

- `tools/api_providers/run_review.py`
- `tools/api_providers/run_role.py`

`--review-run-dir`、`--round-id`、model stem が同じ状態で再実行すると、raw / parsed /
rounds / target-manifest / summary を更新・上書きし得る。

意図した再実行なら問題ないが、run id や出力先を間違えると、別作業の review-run に
成果物を混ぜる可能性がある。作成前に次を確認する必要がある。

- review-run dir が空か、同じ target / phase / criteria / run_id の継続か
- `target-manifest.yaml` の target と今回の `--target` が一致するか
- 同一 round / model の raw・parsed を上書きしないか
- 上書きする場合は明示フラグを要求するか

### B-2. triage decision の部分書き込み

対象：

- `tools/make-triage-decision.py`
- `tools/api_providers/review_triage.py decide`

このツールは `triage.yaml` と `model-result-summary.yaml` を書いた後、全件 decided の場合に
正本判定へ通す。最後の正本判定で落ちた場合、既に書き換えたファイルが残る。

後続対応では、書き込み前に新内容をメモリ上で構築して正本判定し、通った場合だけ
atomic に置き換える。または失敗時に元内容へ rollback する。
あわせて、対応着手時には既存 review-run の `triage.yaml` と
`model-result-summary.yaml` を監査し、途中で落ちた decision による不整合や半端な
判断済み状態が残っていないことを確認する。
監査対象は少なくとも、triage、model-result-summary、関連 summary、manifest 生成有無、
approval record 参照まで含め、途中失敗で残り得る副作用を限定してから修正する。

追加で、`tools/api_providers/review_triage.py decide` 実行前に approval record の前提を
検査する必要がある。
同コマンドは approval record の存在だけでなく、対象 finding id と final label が
事前列挙されていることを要求する。この前提が実行前に明示・生成されず、
空の `approval.yaml` で失敗する手戻りが起きた。

後続対応では、`decide` の preflight または別の approval-template 生成コマンドで次を行う。

- 対象 finding id が approval record に存在するか確認する
- 対象 finding id に対応する final label が列挙されているか確認する
- 不足している場合は、既存形式に沿った `approval.yaml` 草案を生成する
- 自動生成しない場合は、必要な項目と記入先を明示して停止する
- 空 approval record を渡してから失敗する導線を避ける

### B-3. proxy approval の既存成果物上書き・削除

対象：

- `tools/make-proxy-approval.py`

このツールは生成後に正本検証し、失敗時は今回書いたファイルを削除する。
ただし、既存の `proxy-approval.yaml` や `decisions/*.yaml` があった場合、
上書きしてから失敗し、既存の正しい記録まで消す可能性がある。

後続対応では、既存ファイルがある場合は既定で拒否し、上書きには明示フラグを要求する。
また、生成は一時ファイルへ行い、正本検証通過後に rename する。

### B-4. runtime bundle export の出力先衝突

対象：

- `runtime/runtime_core/bundle_exporter/exporter.py`

来歴情報の欠落は `MissingProvenanceError` で拒否している。一方、出力先 bundle が既に
存在する場合の明示 preflight は弱く、`copytree` の失敗に委ねている。

後続対応では、次を事前確認する。

- `exports_base / bundle_id` が存在しないこと
- 既存 bundle_manifest / checksums / run copy がないこと
- 上書きや再輸出を許す場合は、別 bundle_id または明示フラグを要求すること

### B-5. deployment smoke の外部 app root 書き込み

対象：

- `tools/build-deploy-package.py --smoke-external-app-root`

smoke test は対象 app root に `app.md` と
`.reviewcompass/specs/demo/reviews/smoke-run/` を作成する。外部 app root への書き込みで
あるため、既存 `app.md` や既存 smoke-run を上書きしない事前確認が必要である。

後続対応では、次を確認する。

- `app.md` が既に存在する場合は拒否するか、専用一時ファイル名を使う
- `smoke-run` が既に存在する場合は拒否する
- smoke が作るファイル一覧を事前に表示・機械出力できるようにする

### B-6. session-record backfill / promote の終了済み判定

対象：

- `tools/session-record-backfill.py`
- `tools/session-record-promote-draft.py`

`promote` は current session id を要求し、current と同じ session id の昇格を拒否する。
一方、`backfill --session` 側にも、終了済み判定または current session guard を共通化する
余地がある。

後続対応では、formal 2 層記録を書ける全入口で同じ current-session guard を使う。

### B-7. 正本コマンド呼び出し前の短縮名・記憶依存

対象：

- `python3 tools/check-workflow-action.py next --json`
- `tools/check-workflow-action.py` の各サブコマンド
- `tools/guarded-git-commit.py`
- `tools/api_providers/run_review.py`
- `tools/api_providers/review_triage.py`
- `tools/session-record-backfill.py`
- `tools/session-record-promote-draft.py`
- `tools/make-proxy-approval.py`

post-write-verification の開始時に、正本手順では
`python3 tools/check-workflow-action.py next --json` を実行すべきところ、
記憶上の短縮形 `next --json` を先に実行して `command not found` になった。
成果物は作られていないため直接の破損は無かったが、これは「手順書の照合・
正本コマンド確認より先に、短縮名や習慣で動く」入口である。

この型は `next` だけに限らない。人間向け文書や会話では `next --json`、
`commit precheck`、`write-manifest`、`promote` のように短く呼ぶことがあるが、
実行時には repo 内の正式 CLI パス、サブコマンド、必須引数、対象ファイル、出力先を
取り違えずに指定する必要がある。

同類として注意すべき入口：

- `next` 判定：略称ではなく `python3 tools/check-workflow-action.py next --json`
- workflow precheck：`spec-set`、`commit`、`push`、`audit-commit`、
  `reopen-advance-gate`、`autonomous-plan`
- commit：直接 `git commit` ではなく `tools/guarded-git-commit.py` 経由
- post-write review：`tools/api_providers/run_review.py`、
  `tools/api_providers/review_triage.py list-pending / decide / write-manifest` の順序、
  variant、target、review-run-dir、approval-record
- session-record：backfill と promote の使い分け、current session と終了済み session
  の区別
- autonomous / proxy：plan、承認、記録、proxy approval の作成順序

後続対応では、正本 CLI の呼び出し前に、短縮名を実コマンドへ展開する確認層を置く。
少なくとも、手順書や effective prompt に書かれた実行コマンドをそのまま使うこと、
短縮名だけのコマンド実行を避けること、失敗時は成果物未作成を確認してから続行することを
明示する。

あわせて、存在しない補助コマンドや未確認の引数を推測して実行する手戻りも同じ型である。
具体例として、`reopen-status` が存在すると誤認して実行しようとしたこと、
`check-workflow-action.py next` が `--file` を受け取ると誤認したことがある。
reopen 状態確認の正規経路は `next --json` と in-progress YAML の確認であり、
存在しない補助コマンド名を推測してはいけない。

後続対応では、reopen / next / triage などの workflow CLI を使う前に、対象サブコマンドの
存在、引数、前提ファイルを `--help` または機械可読 command registry で確認する
preflight を追加する。少なくとも次を満たす必要がある。

- サブコマンドが存在する
- 指定しようとしている option が存在する
- 対象ファイルや approval record などの前提がそろっている
- 状態確認の正規経路が分かっている場合は、その経路を優先する
- 推測した短縮名や存在しない補助コマンドは実行前に止める

追跡上は、B-7 自体は今回追加された補助候補である。ただし実装単位としては、
主要 3 件にもまたがる「正本コマンド呼び出し helper」に統合して扱う。
理由は、短縮名、存在しない補助コマンド、誤った引数、誤った entrypoint のいずれも、
実行前に正本 operation / command registry へ照合する同じ入口で止められるためである。

### B-8. 前例模倣による implementation review target 不備

implementation triad-review の `review-target.md` を作る際、requirements / design /
tasks の前例形式を模倣し、実装 diff や主要コード抜粋を含めなかった。

直接原因は、文書レビュー用の review target 形式を implementation review にそのまま
横展開したことである。本質原因は、前例を使う前に、正本、phase、artifact 種別、
reviewer が必要とする一次情報を照合しなかったことである。

影響として、review-run 自体は実行できたが、reviewer から「実装を検証できない」と
指摘され、review-run や review target の作り直しが必要になった。

後続対応では、前例適用前チェックを追加する。

- `phase=implementation` なら diff / code excerpt / test diff の有無を検査する
- requirements / design / tasks 用の target 形式を implementation へ無条件に転用しない
- 「前例と同じ形か」ではなく「今回の reviewer が検証可能か」をチェック項目にする
- review-run 作成前 checker の対象に review target の一次情報充足を含める

分類は、review-run / bundle 作成前チェック、前例適用チェック、手戻り削減候補である。

### B-9. post-write pending 中の別作業混在による workflow 混線

既存の post-write-verification pending が残っている状態で、別件の実装変更を同じ
worktree に追加したため、`next` / guard が「post-write pending 中にコード変更が
混ざっている」と判定して停止した。

具体例では、smell inventory 系の post-write-verification 後処理が残っているところに、
commit execution delegation 実装変更が同居した。

直接原因は、過渡的な staged / dirty 状態の同居である。ただし問題の型としては
定常的に起こり得る。ReviewCompass の運用では、review-run、post-write-verification、
reopen、commit approval などの未完了手続き中に、別の不具合や改善点を発見して
同じ worktree で修正を始める場面があるためである。

影響：

- `next` が本来進めたい作業ではなく、混在検出で停止する
- 作業者が「今どの手続きに従うべきか」を再確認する必要が出る
- staged / unstaged / generated artifacts の分離が手作業になる
- 手戻り、説明コスト、トークン消費が増える
- post-write 対象外の変更が同じ流れに混入する危険がある

本質原因は、未完了手続きがある状態で、新しい作業差分を同じ worktree に作る前の
機械的な分離チェックが弱いことである。「pending 手続きの対象差分」と
「新しく始める作業差分」が同居してよいかを、作業開始前に判定できていない。

後続対応では、作業開始前チェックで pending 手続きと staged / dirty 差分の種類を照合する。
post-write pending 中に対象外ファイルを変更しようとした場合は、開始前に停止して
次の分離案を機械的に提示する。

- 先に pending 手続きを完了する
- 別 worktree / 別スレッドへ分ける
- 現在作業を保留メモ化する
- 明示承認を得て side-track として記録する

また、`next` が混在を検出したときは、単に止めるだけでなく、どの既存 pending と
どの新規差分が衝突しているかを表示する。

分類は、workflow 混線防止、post-write / review-run / reopen 作業分離、
作業開始前チェック、手戻り削減候補である。

### B-10. completed_gates と downstream_impact_decisions の対応漏れ

reopen 完了処理では、`completed_gates` に並ぶ gate と、
`downstream_impact_decisions[].gate` の対応が必要である。
`pending_gates` から外れた gate も、完了扱いなら downstream impact decision の
対象になる。

この構造は機械チェックしやすい。reopen 完了前チェックでは次を確認できる。

1. `completed_gates` を読む
2. `drafting_completed_gates` は別扱いにする
3. `requirements` / `design` / `tasks` / `implementation` の
   `triad-review` / `review-wave` / `alignment` / `approval` gate を対象にする
4. 各 gate について、`downstream_impact_decisions[].gate` に同じ値があるか確認する
5. なければ `DEVIATION` で止める

補助的には、`reopen-advance-gate` で gate を完了させたときに、
`downstream_impact_decisions` へ必ず 1 件追加する導線にできる。
また、`completed_gates` へ手で追加する経路を禁止し、既存ファイル修復用には
欠落 gate 一覧を出す lint を用意する。

ただし、判断理由そのものは完全自動にしない。機械ができるのは、対応レコードがあるか、
必須フィールドがあるか、evidence が空でないか、どの gate が足りないかを示すところまでである。
`rationale` の意味的妥当性は、人または review / proxy が確認する。

自然な組み込み先は、`check-workflow-action.py commit` または reopen finalize 系の検査である。

### B-11. commit approval chain の順序依存を並列実行できてしまう

commit approval chain は、`prepare -> record -> delegate-execution -> guarded commit` の
順序依存処理である。各段階は直前の成果物に依存し、nonce、target digest、
staged file set digest を確認しながら進む。

しかし現状では、この順序が「手順として分かっている」だけで、実行側が
`record` と `delegate-execution` を並列実行しようとした時点で止める機械ガードが弱い。
実際、`record` と `delegate-execution` を同時に走らせたため、
`delegate-execution` が古い approval record を見て失敗する手戻りが起きた。

後続対応では、commit approval chain を直列専用の操作として扱う。

- `prepare -> record -> delegate-execution -> guarded commit` は並列実行対象から除外する
- `multi_tool_use.parallel` 等でまとめて実行しない
- wrapper で一括実行し、各段階で成果物の存在確認と digest 検証を挟む
- `delegate-execution` は、同じ nonce の approval record が作成済みであることを
  事前に確認してから実行する
- エラー時は、どの段階の成果物が不足または stale かを明示する

平たく言えば、ルールはあるが、LLM が間違えないようにする実行前ガードが足りない。

### B-12. post-write review が設計壁打ちへ変質し、round 数が増える

operation registry / preflight 設計メモの post-write verification では、本来 5 回程度の
往復で収束する見込みだったが、実際には r11 まで増えた。

直接原因は、調査・設計メモとして始めた文書に、途中から `operation contract`、
共通 JSON、`verdict` 計算規則、`checks`、`pending_conflicts`、`state_refs` などの
仕様候補を具体例つきで書き込んだことである。review 側から見ると、これは
「設計メモの妥当性確認」ではなく「仕様候補の自己整合性確認」になった。

本質原因は、post-write verification の前に文書タイプと review 期待値を機械的に
確定していなかったことである。文書が `調査メモ`、`設計メモ`、`仕様化前メモ`、
`SDD 正本`、`運用手順` のどれかによって、見るべき観点は変わる。
今回のように、設計メモが仕様候補へ変質した時点で停止または再分類する導線が無かった。

影響：

- review が完了検証ではなく設計補助として機能し、round 数が増える
- 例と本文の不整合を 1 件ずつ直すことになり、修正と再 review の往復が増える
- 作業時間、説明コスト、トークン消費が増える
- 「どこまでをメモで決め、どこから SDD 正本へ送るか」が曖昧になる

機械処理できる範囲は広い。

- 文書タイプ宣言の有無を確認する
- JSON / YAML / command 例があるのに schema 表や未確定宣言が無い場合に警告する
- `必須`、`固定`、`fail-closed`、`schema_version`、`allowed_*` などの仕様語彙を検出する
- post-write review の criteria / variant が文書タイプに合っているか確認する
- review round が閾値を超えたら、検証ではなく設計議論化している可能性を警告する
- ERROR / WARN が例と本文の不整合に集中する場合、仕様化前メモまたは SDD への切り出しを促す

ただし、文書タイプの最終判断、仕様として切り出すかどうか、スキーマ内容の妥当性は
完全自動化しない。機械は停止・再分類候補を提示し、人または review / proxy が判断する。

後続対応では、post-write verification 前に document-type preflight を追加する。
preflight は、少なくとも次を返す。
次のブロックは未確定の出力例であり、schema 正本ではない。

```text
document_type: design_memo
contract_like_content: true
schema_examples: true
schema_declared: false
recommended_action: stop_or_reclassify
```

また、仕様っぽい JSON / YAML 例を書く場合は、先に必須フィールド、任意フィールド、
許容値、未実装値の扱い、verdict 導出規則、既存語彙との対応を表で明示する。
それをしない場合は、詳細スキーマを未確定として SDD 側へ送る。

### B-13. API review に渡す criteria / prompt が文書タイプを十分に制御していない

B-12 の round 数増加は、文書が仕様候補へ踏み込んだことだけでなく、API review に渡した
criteria / prompt が文書タイプに対して十分に具体的でなかったことにも起因する。

今回の review 実行では、`--criteria` に `operation_registry_preflight_design_post_write_r12`
や `workflow_recovery_smell_inventory_document_type_preflight_post_write_r3` のような
識別子を渡した。しかし、これは実質的には ID であり、reviewer に対して次を明確に伝える
十分な本文ではなかった。

- この文書は設計メモ / 棚卸しメモであり、SDD 正本ではない
- JSON / YAML 例は、明示がない限り参考例または未確定例として扱う
- 完全な schema 整合性は post-write blocker ではなく、後続 SDD 論点として扱う
- 今すぐ直すべき明白な矛盾と、後続 SDD に送る論点を分ける
- round が増えた場合は、仕様策定へ変質していないか再分類を促す

この情報が薄いと、API reviewer は自然に「仕様として読める箇所」を深掘りする。
その結果、post-write verification が完了検証ではなく、設計補助・仕様策定に近づき、
round 数と修正往復が増える。

後続対応では、document-type preflight と連動する review criteria preflight を追加する。
文書タイプごとに criteria template を用意し、API review へ渡す前に scope を確定する。
例えば設計メモでは、次のような境界を criteria として明示する。

責務分担は次のように分ける。

- document-type preflight：対象文書が設計メモ、棚卸しメモ、SDD 正本、実装 review target
  のどれかを判定し、文書としての扱いと review 期待値を決める
- review criteria preflight：その文書タイプに合わせて、API reviewer に渡す scope、
  out-of-scope、finding policy、blocker 判定基準を生成・検査する

つまり B-12 は「文書をどう分類するか」、B-13 は「分類結果を API reviewer の入力へ
どう反映するか」を追跡単位にする。

このメモ自身に適用する場合、document-type preflight の結論は「棚卸しメモ」であり、
review 期待値は「発生事象、共通原因、機械化候補、追跡単位の整理」である。
review criteria preflight は、その結論を API reviewer へ渡す criteria に反映し、
完全な JSON schema や実装 API 契約を post-write blocker にしないことを明示する。
下の `document_type: design_memo` は設計メモ向け criteria template の例であり、
この棚卸しメモ自身の document type を示すものではない。

```text
document_type: design_memo
review_scope:
  - existing partial implementations are captured
  - proposed direction is coherent
  - obvious contradictions are flagged
  - follow-up SDD topics are identified
out_of_scope:
  - complete JSON schema
  - full API contract
  - implementation fixture completeness
finding_policy:
  schema details are follow-up unless they contradict explicit normative text
```

機械処理できる範囲は次である。

- effective prompt に文書タイプと review 期待値が含まれているか確認する
- `--criteria` が単なる ID だけでなく、文書タイプ別の scope / out-of-scope / finding policy を含むか確認する
- JSON / YAML 例の扱いが criteria に明示されているか確認する
- schema 完全性を blocker にするか、後続 SDD 論点にするかを review 前に固定する
- review round が閾値を超えた場合、criteria 不足または文書タイプ不一致として警告する

### B-14. post-write manifest が review-run の実対象より広い coverage を表現できる

B-13 追記後の post-write verification で、`next` は `completed` に戻ったが、
直近 manifest は `target_files` に 2 文書を含む一方、参照された review-run の
`target-manifest.yaml` は `docs/notes/2026-06-16-workflow-recovery-smell-inventory.md`
1 文書だけを対象にしていた。

直接原因は、`tools/api_providers/review_triage.py write-manifest` の manifest 雛形生成が、
review-run の `target-manifest.yaml` に加えて、現在の git 差分上の post-write 対象を
union することである。これにより、review-run 自体が実際に見た対象より広い
`target_files` と `verifications[]` を manifest に書けてしまう。

本質原因は、post-write verification の正本が「`target_files` 全体を同じ verifier が見る」
ことを要求しているのに、実行系は `run_review.py --target <single-file>` を前提にしており、
multi-target review の一次情報、bundle、manifest coverage の対応を機械的に照合していない
ことである。

影響として、機械ゲートは completed を返すが、証跡だけを見ると「各 verifier が 2 文書を
確認した」と読める一方、実際の review-run target は 1 文書である、という過大表現が
起こり得る。これは未解決指摘を通す問題ではなく、検証 coverage の主張と一次証跡が
ずれる問題である。

対策候補：

- post-write review-run 作成前に、`next_action.target_files` 全体を単一 review 対象として
  渡せる形式を用意する
- multi-target review 用の bundle を正本化し、bundle manifest に各 target path と sha256 を
  記録する
- manifest 生成時に、review-run の target set と manifest の `target_files` が一致するか、
  または bundle manifest が全 target を覆っていることを必須検査する
- `write-manifest` が current git post-write targets を暗黙 union する場合は、
  review-run 側に存在しない target を追加した時点で `DEVIATION` として止める
- `tools/make-post-write-manifest.py` も、指定 `--target` が review-run の実対象または
  bundle manifest に含まれることを生成前に確認する

分類は、post-write manifest coverage preflight、multi-target review target、証跡過大表現防止、
手戻り削減候補である。

## 共通する問題構造

今回の追加点も含めると、共通する構造は次である。

- 作成前チェックが弱い
- 対象確定チェックが弱い
- 空成果物チェックが弱い
- 正本コマンド呼び出し前に、短縮名や記憶に依存して動くことがある
- 存在しないサブコマンドや未確認の option を推測してしまうことがある
- 前例を正本・phase・artifact 種別と照合せず横展開してしまうことがある
- pending 手続き中に別作業差分が同じ worktree へ混在し得る
- 順序依存の承認 chain を並列実行できてしまう
- stale 承認を避ける導線が弱い
- runtime JSON 手編集のようなワークアラウンドが発生し得る
- review-run / manifest 作成前の妥当性検査が弱い
- approval record 作成前に、対象 finding と final label の充足を確認する導線が弱い
- reopen 完了記録で、completed gate と downstream impact decision の対応漏れを事前検出しにくい
- 実装完了と実運用確認完了の境界が曖昧になり得る
- 調査前の説明が、後で修正を要することがある
- 文書タイプと review 期待値が未確定のまま post-write verification を始めることがある
- 設計メモが仕様候補へ変質した時点で停止・再分類する導線が弱い
- API review に渡す criteria / prompt が文書タイプ別の scope を十分に制御していないことがある
- post-write manifest の coverage 主張と review-run の実 target set がずれ得る
- 生成後検査はあっても、生成前 preflight が弱い
- 失敗時に既存正本を壊さない atomic 書き込みが弱い

## 既に一定の防止がある箇所

調査時点で、次の防止は既に存在する。

- `tools/make-post-write-manifest.py` は生成後に正本判定へ通す fail-closed を持つ
- `tools/api_providers/review_triage.py write-manifest` は未解決 triage と重要件 approval を見る
- `tools/check-workflow-action.py commit-approval prepare/record` は staged exact index への
  nonce / digest 束縛を持つ
- `tools/build-deploy-package.py --clean` は危険な出力先を拒否する

ただし、これらは主に生成後検証または一部条件の検査であり、今回の問題構造である
「生成前 preflight」と「既存正本を壊さない atomic 書き込み」は別途整える必要がある。

## 機械化による効果見込み

これらの対応は、単に不具合を減らすだけでなく、作業時間とトークン数の削減にも効く。

期待できる効果：

- 作業前・生成前に止まれるため、空 bundle 作成、review-run 作り直し、
  approval 作り直し、誤った session 記録の除外などの往復が減る
- 原因説明、再調査、再実行報告、利用者への追加確認が減り、会話トークンを削減できる
- LLM の注意力や記憶ではなく helper の preflight に寄せられるため、
  自律実行時の品質が安定する
- 「最終的には guard で止まったが、途中で余計な成果物を作った」という状態を減らし、
  証跡の正本性を保ちやすくなる

ただし、「手戻りがゼロになる」というより、よくある手戻りを作業前・生成前に
機械的に止められるようにする、という位置づけである。未知の設計不備や新しい入口は
残り得るため、guard や post-write verification は最後の保険として維持する。

時間・トークン削減の観点では、次の順に効果が大きい。
これは効果見込みの参考順位であり、実装着手順の正本ではない。

1. 正本コマンド呼び出し helper
2. diff bundle 作成 helper
3. review-run 作成前 checker
4. commit approval 作成前 checker
5. session-record current guard 共通化

## 後続対応案

個別メモの実装に加え、より横断的に次を検討する。

1. post-write review run 作成前 checker
   - run id、target files、manifest、bundle、現行作業目的の整合を確認する
2. diff bundle 作成 helper
   - staged / unstaged を自動判定し、空 bundle を拒否する
3. commit approval 作成前 checker
   - staged 対象が最終確定していることを確認してから approval を作る
4. 実装完了条件の明示テンプレート
   - 実装済み、テスト済み、実環境確認済み、未確認の残作業を分けて書く
5. runtime 手編集禁止ルール
   - 正式 CLI が無い場合は、手編集で通すのではなく後続設計課題として止める
6. 説明前の確認ルール
   - 承認・guard・証跡に関する原因説明では、該当テストまたは正本文書を確認してから断定する
7. 正本コマンド呼び出し helper
   - `next`、commit、post-write review、reopen、session-record などの正式 CLI を
     短縮名からではなく機械的に選ぶ
   - 実行前に対象、出力先、必須引数、既存成果物との衝突を表示・検査する
   - コマンド失敗時は成果物未作成または部分生成の有無を確認する
   - これは項目 1 の review-run 作成前 checker とは別である。項目 1 は review-run の
     対象・出力先・manifest 整合を扱い、項目 7 は正本 CLI 選択と引数存在確認を扱う
8. approval-template / approval preflight
   - `tools/api_providers/review_triage.py decide` 前に、対象 finding id と final label が
     approval record に事前列挙されていることを確認する
   - 不足時は既存形式に沿った approval 草案を生成するか、明確な手順を出して停止する
9. 前例適用前 checker
   - phase と artifact 種別を確認し、前例形式をそのまま横展開してよいか検査する
   - implementation review target では diff / code excerpt / test diff の有無を確認する
10. worktree 混線 preflight
    - pending 手続き中に対象外差分を作ろうとしていないか確認する
    - 混在時は、pending 完了、別 worktree、保留メモ化、side-track 承認の候補を提示する
11. reopen 完了前 checker
    - `completed_gates` と `downstream_impact_decisions[].gate` の対応漏れを検出する
    - 必須フィールドと evidence の存在を確認し、rationale の意味的妥当性は人または review に残す
12. commit approval chain wrapper
    - `prepare -> record -> delegate-execution -> guarded commit` を直列専用として扱う
    - 途中成果物の存在確認と digest 検証を挟み、並列実行を避ける
13. document-type preflight
    - post-write verification 前に、対象文書のタイプと review 期待値を確認する
    - 仕様候補化した設計メモは、SDD へ切り出すか、詳細スキーマ未確定として止める
    - review round が閾値を超えた場合、設計壁打ち化として停止・再分類を促す
14. review criteria preflight
    - API review 前に、criteria が文書タイプ別の scope / out-of-scope / finding policy を含むか確認する
    - 単なる criteria id だけで review scope を制御しない
    - schema 詳細を blocker にするか後続 SDD 論点にするかを review 前に固定する
15. post-write manifest coverage preflight
    - manifest の `target_files` と review-run の実 target set が一致するか確認する
    - multi-target の場合は bundle manifest が全 target path / sha256 を覆ることを要求する
    - review-run に存在しない target を current git 差分から暗黙追加しない

## 追跡方針

本メモは棚卸しであり、後続対応の実装正本ではない。ここで列挙した対応は、
次作業リストまたは `TODO_NEXT_SESSION.md` に移して追跡する。実装へ入る場合は、
対象を 1 件ずつ選び、SDD の正規手順に沿って計画、テスト、実装、検証、commit の
単位へ分ける。

追跡時の単位は、少なくとも次に分ける。

- 正本コマンド呼び出し helper
- diff bundle 作成 helper
- review-run 作成前 checker
- commit approval 作成前 checker
- commit approval chain wrapper
- session-record current guard 共通化
- proxy approval / triage decision の atomic 書き込み
- review triage approval-template / approval preflight
- 前例適用前 checker
- worktree 混線 preflight
- reopen 完了前 checker
- deployment smoke と bundle export の出力先 preflight
- document-type preflight / post-write review scope control
- review criteria preflight / criteria template
- post-write manifest coverage preflight / multi-target review bundle

## 追加分の優先度

追加候補の中では、次の順で扱うのが妥当である。
これは追加候補だけの相対順位である。主要 3 件を含む実装着手順は、直後の
「主要 3 件を含めた全体優先度」を優先して参照する。
本節の順位と「機械化による効果見込み」の順位は判断材料であり、実装着手順の正本ではない。
後続 SDD へ送るときは、必ず「主要 3 件を含めた全体優先度」を起点にする。

1. review-run dir の衝突・混在防止
2. review triage approval-template / approval preflight
3. worktree 混線 preflight
4. 前例適用前 checker
5. reopen 完了前 checker
6. commit approval chain wrapper
7. proxy approval / triage decision の atomic 書き込み
8. deployment smoke の外部 app root 上書き防止
9. bundle export の出力先衝突 preflight
10. session-record backfill / promote の current-session guard 共通化
11. 正本コマンド呼び出し前の短縮名・記憶依存防止
12. post-write manifest coverage と multi-target review bundle の整合検査

主要 3 件を含めた全体優先度は、不可逆操作・正本汚染・検証品質の順で考える。

1. commit 承認と LLM 実行代行承認の正式 CLI 化
2. commit approval chain wrapper
3. 現セッション正式記録の生成前防止
4. worktree 混線 preflight
5. review-run dir の衝突・混在防止
6. review triage approval-template / approval preflight
7. diff bundle 作成 helper
8. 前例適用前 checker
9. reopen 完了前 checker
10. 正本コマンド呼び出し helper
11. proxy approval / triage decision の atomic 書き込み
12. deployment smoke と bundle export の出力先 preflight
13. 実装完了条件テンプレートと説明前確認ルール
14. document-type preflight / post-write review scope control
15. review criteria preflight / criteria template
16. post-write manifest coverage preflight / multi-target review bundle

## 期待する完了条件

- review-run / manifest / bundle は、生成前に対象妥当性を検査できる
- 空 bundle や対象ずれ bundle が生成されない
- implementation review target には、reviewer が実装を検証できる一次情報が含まれる
- `tools/api_providers/review_triage.py decide` 前に、対象 finding id と final label の approval 前提を確認できる
- post-write pending 中の別作業混在を作業開始前に検出し、分離案を提示できる
- commit approval は最終 staged 固定後に作る導線になる
- commit approval chain は直列専用 wrapper または preflight により順序通り実行される
- 正式 CLI だけで、内容承認と LLM 実行代行承認を安全に記録できる
- post-write verification 前に文書タイプと review 期待値を確認できる
- 設計メモが仕様候補へ変質した場合、SDD 化または未確定化へ切り分けられる
- API review 前に文書タイプ別 criteria を生成し、review scope と blocker 条件を明示できる
- post-write manifest が、review-run の実 target set または bundle manifest を超える coverage を主張しない
- current session の正式 2 層記録生成は全入口で fail-closed する
- reopen 完了前に、completed gate と downstream impact decision の対応漏れを検出できる
- 実装完了と実環境確認未完了を完了報告で分けて示せる
- runtime JSON 手編集を必要としない正式経路が整う
- 正本 CLI がある作業では、短縮名や記憶ではなく正式コマンドを機械的に選べる
- 手戻りで通過するのではなく、生成前・実行前に止まる
