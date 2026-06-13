# 書き込み後検証対象：機械が吐く捕捉物のディレクトリ単位対象外（規律改訂・(い)）

検証者へ渡すのは合意内容（決定の箇条書き）と書き込み結果のみ（情報最小化）。

## 合意内容（決定の箇条書き）

- 機械が吐く捕捉物（review-run 一式の生出力・parsed・triage、自律並列の走行台帳、書き込み後検証の API 結果ログ）は、書き込み後の独立検証の対象外とする。
- 理由：独自の主張ではなく走行・実行の忠実な捕捉であり、独立検証ではなく走行・再実行・再生成で担保できる。
- docs 配下の凍結旧配置はディレクトリ単位で対象外とする：`**/review-runs/**`、`docs/logs/autonomous-parallel/`、`docs/notes/post-write-verification-review/`。新規分は `.reviewcompass/evidence/` 配下に置かれ docs 配下に出ない。
- 台帳の `authorization` 等の埋め込み値は、承認レコードや autonomous-plan 検査など別の層で守られる。
- 監査・計測記録（例：`docs/discipline-compliance-reports/`）は主張を含むため対象に残す（迷えば対象側）。

## 書き込み結果（docs/disciplines/discipline_post_write_verification.md の適用範囲節）

- 対象：運用文書、規律文書、作業メモ、監査記録、再オープン記録など、通常ワークフロー段の成果物ではない正本文書
- 対象外：`.reviewcompass/specs/`（ワークフロー段で検証）、spec.json 状態変更（workflow precheck で検証）、`docs/archive/`、テスト用一時ファイル
- 対象外（性質ベース）：機械生成され引用元を明記した派生記録（front-matter に `generated_by: session-record-extractor` 等の来歴を持つもの）。独立検証ではなく「来歴の刻印＋引用元からの再生成突き合わせ（再現性）」で担保する。判定はディレクトリでなく来歴マーカーで行う
- 対象外（性質ベース）：**機械が吐く捕捉物**（API 生出力・parsed・triage の review-run 一式、自律並列の走行台帳、書き込み後検証の API 結果ログ）。独立検証ではなく走行・再実行・再生成で担保する。台帳の `authorization` 等の埋め込み値は承認レコードや autonomous-plan 検査など別の層で守られる。新規分は `.reviewcompass/evidence/` 配下へ置かれ docs 配下に出ない。docs 配下の凍結旧配置はディレクトリ単位で対象外とする（`**/review-runs/**`、`docs/logs/autonomous-parallel/`、`docs/notes/post-write-verification-review/`）。なお監査・計測記録（例：`docs/discipline-compliance-reports/`）は主張を含むため対象に残す
- 新規ディレクトリ：判定に迷えば対象側に倒す
