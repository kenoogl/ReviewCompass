# commit operation failure cases

作成日：2026-06-20

## 目的

本メモは、commit 操作の機械処理化を実装する際の参照情報として、2026-06-20 セッションで発生した commit 周辺の失敗を整理する。

記録する主眼は、個別の会話ログではなく、次の 3 点である。

1. どの条件で不要な再試行や追加確認が発生したか
2. どの不変条件を機械処理で先に検出すべきか
3. 利用者に見せるべき情報と、見せるべきでない内部手順の境界

## 背景

Requirement 13〜16 を基点にした reopen R-0 の途中で、requirements 段の triad-review / review-wave / alignment / approval を進めた。同じ流れの中で、Codex の commit 実行環境、利用者向け報告文、TODO 更新、commit 中の進行報告最小化など、複数の運用規律修正も実施した。

この過程で、commit guard 自体は正しく停止したが、LLM 側が commit 前に必要条件を先読みできず、次のような無駄が発生した。

- post-write verification が必要な文書変更で、先に commit を試してから止まった
- reopen 中の本筋外変更で、maintenance 完了記録を後から追加した
- staged 対象が変わった後に approval を作り直す必要が生じた
- WARN / DEVIATION の出力をそのまま会話に近い形で出しすぎた
- 「内部再準備は黙る」と「対象変更は再承認を要する」の境界が曖昧だった

## 代表的な失敗パターン

### 1. strict 文書変更の post-write verification 後回し

発生条件：

- `docs/operations/` 配下を変更した
- commit を試した
- guard が post-write verification 未完了として停止した

問題：

- post-write verification は commit guard に止められてから行うものではなく、strict 文書変更が見えた時点で commit 前に済ませるべきだった
- 初回の確認で所見が出た場合、再修正と再確認が必要になり、commit 試行が余分になる

機械処理で防ぐ不変条件：

- staged / unstaged の commit 候補に strict post-write 対象が含まれる場合、commit 実行準備より前に post-write verification 状態を確認する
- completed manifest が現在 sha256 を覆っていなければ、approval 作成へ進ませない

### 2. 本筋 reopen 中の保守変更に maintenance 記録がない

発生条件：

- `stages/in-progress/reopen-procedure-2026-06-19.yaml` が存在した
- 本筋の requirements/design/tasks 進行とは別に、運用規律や TODO を変更した
- maintenance 完了記録なしで commit しようとした

問題：

- 本筋の途中で side track 的な保守変更を行う場合、その変更が本筋を進めないことを記録する必要がある
- 記録を後から足すと staged 対象が増え、approval の作り直しが必要になる

機械処理で防ぐ不変条件：

- in-progress reopen がある状態で、本筋ファイル以外を commit 候補に含める場合、対応する `stages/completed/maintenance-*.yaml` が必要
- maintenance 記録の `mainline_blocked_by` は現在の reopen in-progress ファイルを覆る必要がある
- maintenance 記録の `allowed_files` は staged 対象を覆る必要がある

### 3. approval 作成後の staged 対象変更

発生条件：

- approval nonce を作成した後に、post-write manifest や maintenance 記録を追加した
- staged exact index が approval の target digest と一致しなくなった

問題：

- approval は staged exact index に束縛されるため、対象変更後の再利用はできない
- これは内部再準備として黙ってよい場合と、利用者判断が必要な場合を区別しなければならない

機械処理で防ぐ不変条件：

- approval 作成前に commit 候補ファイル集合を final にする
- approval 作成後に staged file set または staged content digest が変わったら、既存 approval を invalid として扱う
- 追加ファイルが機械生成の必須証跡であっても、approval 対象変更として扱い、再 approval 前に理由を短く示す

### 4. WARN / DEVIATION の扱いが会話上で過剰

発生条件：

- `spec.json` の workflow_state 更新が WARN として止まった
- post-write 未完了や in-progress により DEVIATION で止まった
- guard の詳細出力に近い情報を会話へ多く出した

問題：

- 利用者に必要なのは、続行できない理由、判断が必要な点、次に返すべき操作である
- staged 件数、nonce、approval 作成手順などは通常不要

機械処理で防ぐ不変条件：

- 正常系 commit は成功結果だけを報告する
- WARN / DEVIATION は、1〜3 点の理由と次操作だけに要約する
- 詳細ログは保存または参照可能にし、通常の会話には出さない

### 5. 「内部再準備は黙る」の安全境界が曖昧

発生条件：

- commit 中の進行報告を減らす規律を追加した
- 初稿では「コミット対象が増えたため approval を再作成する」ことまで、利用者に報告しない内部再準備に含めてしまった
- post-write verification が安全上の矛盾として指摘した

問題：

- 承認済み対象範囲内の内部再準備は黙ってよい
- しかし、コミット対象の増加、staged 内容変更、再承認が必要な場合は安全境界を越える

機械処理で防ぐ不変条件：

- 「黙ってよい内部再準備」は、承認済み対象範囲内で、staged digest が変わらない場合に限定する
- staged 対象が増えた場合は内部再準備ではなく、再承認を要する状態として扱う
- 利用者への報告は「対象が変わったため再承認が必要」のように短くする

## commit 機械処理に入れるべき事前判定

commit 実行前に、少なくとも次を機械的に確認する。

1. 変更ファイル集合を分類する
   - 本筋 reopen 変更
   - maintenance / side track 変更
   - strict post-write 対象
   - lightweight self-check 対象
   - runtime / evidence / generated 証跡

2. post-write verification 要否を判定する
   - strict 対象があれば completed manifest が現在 sha256 を覆うこと
   - 未完了なら commit approval 作成へ進まない

3. in-progress 状態との整合を判定する
   - reopen 停止点 commit か
   - maintenance 完了 commit か
   - 通常 commit として許可できるか

4. maintenance 完了記録を検査する
   - `process_id: maintenance`
   - `mainline_blocked_by` が現在の in-progress を覆う
   - `allowed_files` が staged 対象を覆う
   - completion / verification / return_to がある

5. staged 対象を final にする
   - approval 作成後に対象を変えない
   - post-write manifest や evidence を含める必要があるなら approval 前に含める

6. approval を作成する
   - staged exact index に束縛する
   - approval 作成後に別の承認系操作を挟まない

7. commit を実行する
   - Codex では最初から許可された実行環境で実行する
   - 正常系は成功結果だけを報告する

## 利用者向け出力の期待形

正常完了：

```text
コミットしました。

<hash> <message>

作業ツリーは clean です。次は <自然な日本語の次作業> です。
```

WARN 停止：

```text
コミットはまだ完了していません。

理由: <利用者判断が必要な要点>

次に必要な操作: 承認
```

DEVIATION 停止：

```text
コミットは実行していません。

理由: <続行できない要点>
次に必要な作業: <先に実施すべき作業>
```

出さない情報：

- nonce / challenge の値
- approval 作成や作り直しの通常手順
- staged 件数の詳細
- guard の全文
- provider / model の内部実行ログ
- 「対象が増えたので承認内容を作り直す」のような内部手順説明

ただし、対象変更や再承認が必要な場合は、内部手順ではなく停止理由として短く示す。

## 実装時のテスト候補

- strict post-write 対象がある場合、completed manifest なしでは commit approval 作成前に止まる
- in-progress reopen 中の maintenance commit は、completed maintenance YAML が現在の reopen を覆う場合だけ許可される
- approval 作成後に staged 対象が増えた場合、既存 approval を再利用できない
- approval 作成後に証跡 manifest を追加する必要がある場合、approval 作成前の候補確定へ戻す
- `spec.json` workflow_state 更新は WARN として利用者承認を要求する
- WARN / DEVIATION の会話向け要約は、理由 1〜3 点と次操作だけを含む
- 正常 commit の会話向け要約は、commit hash / message / clean 性 / 次作業だけを含む
- 承認済み対象範囲内の nonce 更新や delegation 再利用は会話へ出さない

## 位置づけ

このメモは正本文書ではない。後続で operation contract、commit preflight、commit operation runner、user-facing summary formatter を実装するときの失敗ケース集として参照する。

正本化する場合は、以下へ分解して反映する。

- operation contract / registry：commit 前判定と副作用順序
- preflight：post-write / maintenance / staged digest / approval 状態の検査
- runner：approval 作成から guarded commit までの一括実行
- summary formatter：正常系、WARN、DEVIATION の利用者向け短縮出力
