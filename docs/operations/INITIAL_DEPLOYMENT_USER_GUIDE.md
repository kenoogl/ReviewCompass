# 初期デプロイユーザーガイド（ドラフト）

最終更新：2026-06-10（実アプリ pilot 前の初期検証用ドラフト）

本文書は、利用者本人が ReviewCompass を実アプリに適用して初期検証するための手順書である。第3者配布用の導入ガイドではない。配布方針の正本は [DEPLOYMENT.md](DEPLOYMENT.md) に置く。

本ガイドは、利用者がターミナルで Python コマンドを直接実行する運用を前提にしない。実際の作業は、ReviewCompass 側または対象アプリ側で LLM セッションを立ち上げ、その LLM が必要な ReviewCompass ツールを呼び出す形を前提にする。

## 1. 目的

ReviewCompass は、対象アプリの仕様、設計、タスク、レビュー記録を `.reviewcompass/` 配下に管理し、review-run、workflow-management、conformance-evaluation、self-improvement、analysis、evaluation を実行するためのツール群である。

初期デプロイでは、ReviewCompass 開発リポジトリを対象アプリへそのままコピーしない。`deploy-manifest.yaml` で許可されたファイルだけを配布物として切り出し、その配布物を使って実アプリ上の動作を確認する。

## 2. リポジトリの分担

デプロイ時は、ReviewCompass 側リポジトリと対象アプリ側リポジトリを分けて扱う。

| リポジトリ | 扱うもの |
| --- | --- |
| ReviewCompass 側 | ツール本体、スキーマ、テンプレート、プロンプト、配布 manifest、配布物生成処理 |
| 対象アプリ側 | 対象アプリ固有の `.reviewcompass/config.yaml`、仕様、workflow state、review-run 記録 |

対象アプリで ReviewCompass を実行しても、ReviewCompass 側リポジトリの workflow state を暗黙に変更しない。対象アプリ側に生成された `.reviewcompass/` 配下の変更を commit するかは、対象アプリ側の運用判断として扱う。

## 3. 作業場所の考え方

初期検証では、作業場所を次のように分ける。

| 場面 | LLM セッションを立ち上げる場所 | 主な目的 |
| --- | --- | --- |
| 配布物を作る | ReviewCompass 開発リポジトリ | `deploy-manifest.yaml` から配布物を生成し、混入検査を行う。 |
| 実アプリを検証する | 対象アプリリポジトリ | 対象アプリ側の `.reviewcompass/` を作成・更新し、review-run や workflow-management を実行する。 |
| ReviewCompass 本体を直す | ReviewCompass 開発リポジトリ | pilot で見つかった ReviewCompass 側の不具合や固有依存を修正する。 |

「対象アプリに対して ReviewCompass を実行する」とは、対象アプリリポジトリで LLM セッションを立ち上げ、その LLM が配布済み ReviewCompass のツールを使って、対象アプリ側の `.reviewcompass/` を読み書きすることを指す。

ReviewCompass のプログラム本体は配布物ディレクトリにある。一方で、仕様、workflow state、review-run 記録は対象アプリリポジトリの `.reviewcompass/` に作られる。

## 4. LLM セッションの起動パターン

初期デプロイでは、LLM セッションを立ち上げる場所に複数の選択肢がある。利用者は、作業の目的に合わせて次のいずれかを選ぶ。

| パターン | LLM を立ち上げる場所 | 対象アプリの扱い | 向いている場面 |
| --- | --- | --- | --- |
| パターン 1 | ReviewCompass 配布物ディレクトリ | LLM に対象アプリ root を伝える | 配布物側から一括で初期設定したい場合 |
| パターン 2 | 対象アプリリポジトリ | LLM に ReviewCompass 配布物ディレクトリを伝える | 実アプリで通常利用を始める場合 |
| パターン 3 | ReviewCompass 配布物ディレクトリ、その後に対象アプリリポジトリ | 先に配布物側だけ確認し、後で対象アプリ側を設定する | 初回検証や慎重に段階を分けたい場合 |

### 4.1 パターン 1：ReviewCompass 配布物側で起動する

ReviewCompass 配布物を任意のディレクトリに配置し、そのディレクトリで LLM セッションを立ち上げる。利用者は対象アプリ root を LLM に伝える。

依頼例：

```text
このディレクトリは ReviewCompass 配布物です。
対象アプリ root は <対象アプリroot> です。
INITIAL_SETUP_LLM_GUIDE.md を読んで、対象アプリで ReviewCompass を使えるように初期設定してください。
```

このパターンでは、LLM は ReviewCompass 配布物側を起点にしながら、対象アプリ側の `.reviewcompass/` を作成または確認する。配布物確認と対象アプリ初期設定を同じセッションで進めたい場合に使う。

### 4.2 パターン 2：対象アプリ側で起動する

ReviewCompass 配布物を任意のディレクトリに配置したあと、対象アプリリポジトリで LLM セッションを立ち上げる。利用者は ReviewCompass 配布物ディレクトリを LLM に伝える。

依頼例：

```text
このディレクトリは対象アプリ root です。
ReviewCompass 配布物は <ReviewCompass配布物ディレクトリ> にあります。
ReviewCompass の INITIAL_SETUP_LLM_GUIDE.md を読んで、この対象アプリで ReviewCompass を使えるように初期設定してください。
```

このパターンでは、仕様、workflow state、review-run 記録が対象アプリ側に作られることを確認しやすい。実アプリでの通常利用は、このパターンを基本とする。

### 4.3 パターン 3：配布物側だけ先に初期設定する

まず ReviewCompass 配布物ディレクトリで LLM セッションを立ち上げ、対象アプリには触れずに配布物単体の確認だけを行う。その後、対象アプリリポジトリで別の LLM セッションを立ち上げ、ReviewCompass 配布物ディレクトリを伝えて対象アプリ側の初期設定を行う。

配布物側での依頼例：

```text
このディレクトリは ReviewCompass 配布物です。
まだ対象アプリには書き込まないでください。
INITIAL_SETUP_LLM_GUIDE.md を読んで、配布物単体の初期確認だけを行ってください。
```

対象アプリ側での依頼例：

```text
このディレクトリは対象アプリ root です。
確認済みの ReviewCompass 配布物は <ReviewCompass配布物ディレクトリ> にあります。
ReviewCompass の INITIAL_SETUP_LLM_GUIDE.md を読んで、この対象アプリの初期設定を行ってください。
```

このパターンは、いきなり対象アプリへ書き込まず、先に ReviewCompass 配布物が使える状態かを確認したい場合に使う。

初期設定時に LLM へ渡す指示は [INITIAL_SETUP_LLM_GUIDE.md](INITIAL_SETUP_LLM_GUIDE.md) にまとめる。

## 5. 初期検証版の位置づけ

初期検証版は、利用者本人が実アプリで全機能を確認するための検証用配布物である。第3者配布用の最小セットではない。

そのため、初期検証版には review-run、workflow-management、conformance-evaluation、self-improvement、analysis、evaluation など、実アプリ pilot で確認したい機能を広めに含める。一方で、開発メモ、レビュー証跡、post-write verification 記録、実験ログなどは対象アプリへ持ち込まない。

## 6. 事前条件

初期検証の前に、次を確認する。

1. 配布物生成は ReviewCompass 開発リポジトリで立ち上げた LLM セッションに依頼すること。
2. 生成後の初期検証と日常運用は、対象アプリリポジトリで立ち上げた LLM セッションに依頼すること。
3. LLM が配布済み ReviewCompass の場所を参照できること。
4. LLM が ReviewCompass の Python ツールを実行できる環境を持つこと。
5. 対象アプリ側の LLM セッションに、配布済み ReviewCompass の配置場所を伝えること。
6. `config/api-settings.yaml` に API key、token、password などの秘密値が含まれていないこと。
7. API key などの秘密値は、環境変数など配布物外の仕組みで渡すこと。
8. 実アプリ pilot で使う対象アプリ root を決めていること。

秘密値の確認は、ReviewCompass 開発リポジトリ側の LLM に依頼する。

依頼例：

```text
config/api-settings.yaml に API key、token、password などの秘密値が含まれていないか確認してください。
```

実秘密値が見つかった場合は、配布物を作る前に `config/api-settings.yaml` から除く。

## 7. 配布物の作成

配布物は `deploy-manifest.yaml` から生成する。これは ReviewCompass 開発リポジトリ側の LLM セッションに依頼する。

依頼例：

```text
deploy-manifest.yaml に基づいて初期検証用の ReviewCompass 配布物を生成してください。
出力先は一時ディレクトリにし、--clean と --verify 相当の確認も実施してください。
```

`--clean` は出力先を作り直す。出力先には、既存リポジトリの root や対象アプリ root を指定しない。`--verify` は、配布物に allowlist 外ファイル、exclude 対象ファイル、欠落ファイルがないことを確認する。

既定の出力先は `deploy-manifest.yaml` の `output.default_directory` である。初期検証では、作業の取り違えを避けるため、一時ディレクトリを明示する。

## 8. 配布前 smoke

配布物だけで対象アプリ側へ review-run 記録を書けることを、実アプリ pilot 前に確認する。この smoke は、ReviewCompass 開発リポジトリ側の LLM に依頼する配布前検査である。対象アプリ側の日常運用で `tools/build-deploy-package.py` を使うという意味ではない。

依頼例：

```text
ReviewCompass 開発リポジトリ側で、配布物を生成し、対象アプリ root に対する配布前 smoke test を実行してください。
tools/build-deploy-package.py を使い、--clean、--verify、--smoke-external-app-root <対象アプリroot> を指定してください。
実行には、システムの python3 ではなく、依存導入済みの .venv/bin/python3 を使ってください。
対象アプリ側の .reviewcompass/specs/demo/reviews/smoke-run/ に review-run 記録を書けることを確認してください。
```

この smoke test は、対象アプリ root に次のような記録を書き込む。

```text
.reviewcompass/specs/demo/reviews/smoke-run/
```

現行の smoke test は、ReviewCompass 開発リポジトリ側の `tools/build-deploy-package.py` に `--clean`、`--verify`、`--smoke-external-app-root <対象アプリroot>` を指定して実行する。これは LLM が内部で使う実行指定であり、利用者がターミナルへ直接入力する手順ではない。この処理は、生成済み配布物を Python import path として使い、対象アプリ root に検証用の `app.md` を自動で用意し、そのファイルを対象に review-run 記録を書き込む。

smoke test は、`tools/build-deploy-package.py` を起動した Python と同じ Python で配布物内のツールを実行するため、その Python に `httpx` と `PyYAML` が導入されている必要がある。ReviewCompass 開発リポジトリでは、システムの `python3` ではなく、依存導入済みの `.venv/bin/python3` で実行する。システムの `python3` で実行すると、`ModuleNotFoundError: No module named 'httpx'` で smoke が失敗する。

配布前 smoke が終わったあとの実アプリ pilot では、対象アプリ側で LLM セッションを立ち上げ、配布済み ReviewCompass の `tools/api_providers/run_review.py` や `tools/check-workflow-action.py` などを使う。対象アプリ側 LLM は、配布物生成ツールではなく、配布物に含まれる実行ツールを使う。

主な生成物は次の通り。

| ファイル | 意味 |
| --- | --- |
| `raw/*.txt` | provider 応答の生テキスト |
| `parsed/*.yaml` | 整形済みレビュー結果 |
| `rounds.yaml` | 実行 round と model result の記録 |
| `model-result-summary.yaml` | モデル別の要約 |
| `target-manifest.yaml` | 対象ファイルと sha256 |

smoke test は対象アプリ側に変更を作る。不要であれば、対象アプリ側の LLM に削除または確認を依頼する。

## 9. 配布物の配置

配布前 smoke が通ったら、対象アプリ側の LLM が参照できる場所に生成済み配布物を配置する。配置先は対象アプリリポジトリの中ではなく、対象アプリ側 LLM から読める別ディレクトリにする。

配置後、対象アプリ側の LLM セッションには次の 2 点を伝える。

1. 対象アプリ root。
2. 配布済み ReviewCompass の配置場所。

対象アプリ側 LLM は、この配置済み ReviewCompass を道具として使い、対象アプリ側の `.reviewcompass/` を読み書きする。

## 10. 対象アプリ側に作られるもの

ReviewCompass の実行により、対象アプリ側には次のファイルやディレクトリが作られる可能性がある。

- `.reviewcompass/config.yaml`
- `.reviewcompass/specs/<feature>/requirements.md`
- `.reviewcompass/specs/<feature>/design.md`
- `.reviewcompass/specs/<feature>/tasks.md`
- `.reviewcompass/specs/<feature>/spec.json`
- `.reviewcompass/specs/<feature>/reviews/`

これらは対象アプリの仕様、状態、レビュー記録である。ReviewCompass 側の開発証跡ではない。

## 11. workflow-management の基本

対象アプリ側の実作業は、まず workflow-management で次に必要な action を確認する。対象アプリリポジトリで立ち上げた LLM セッションに依頼する。LLM は、配布済み ReviewCompass の `check-workflow-action.py` を使って、対象アプリ側の `.reviewcompass/` を読む。

依頼例：

```text
配布済み ReviewCompass を使って、この対象アプリの workflow next を確認してください。
```

commit 前検査を使う場合も、対象アプリ側の LLM セッションに依頼する。ReviewCompass 側リポジトリと対象アプリ側リポジトリを取り違えない。

## 12. review-run の基本

review-run は、対象文書に対するレビュー結果を記録する処理である。workflow-management で必要なレビュー対象が明らかになったら、対象アプリ側の LLM セッションに、対象文書、phase、criteria、review-run 出力先を指定して依頼する。

例：

```text
配布済み ReviewCompass を使って、.reviewcompass/specs/demo/requirements.md の review-run を実行してください。
phase は requirements、criteria は initial_pilot_review、出力先は .reviewcompass/specs/demo/reviews/initial-pilot にしてください。
```

review-run の結果に `triage_pending` や `human_required` がある場合は、`tools/api_providers/review_triage.py` で未処理所見を確認し、人の判断を記録する。

## 13. conformance-evaluation の基本

conformance-evaluation は、実装や実行契約と要件・設計・タスクの整合を確認する機能である。初期検証では、実アプリの既存コードや生成された仕様に対して、照合チェックが使えるかを確認する。

初期 pilot では、conformance-evaluation による提案が出ても、対象アプリ側の要件・設計・タスクを自動で書き換えない。変更が必要な場合は、通常の reopen 手続きに乗せる。

## 14. analysis / evaluation の基本

evaluation は review-run の実行結果を受け取り、有効・無効の切り分けや比較可能な成果物への変換を扱う。analysis は、評価結果から報告や分析用の構造化成果物を作る。

初期 pilot では、review-run 記録を入力として evaluation / analysis の最小経路が動くかを確認する。

## 15. self-improvement の基本

self-improvement は、ReviewCompass の運用結果から改善提案、承認済み更新、却下、rollback、metrics、carry-forward register を扱う機能である。

初期 pilot では、実アプリ側に改善提案の記録が作れるか、schema と配置が成立するかを確認する。改善案を採用するかは、人の判断として扱う。

## 16. pilot 中の更新と終了時の片付け

pilot 中に ReviewCompass 側の不具合や固有依存を見つけた場合は、ReviewCompass 開発リポジトリに戻って修正する。修正後は配布物を作り直し、配布前 smoke を再実行してから、対象アプリ側 LLM が参照する配置済み ReviewCompass を差し替える。

pilot 終了後、対象アプリ側に作られた smoke 用の `.reviewcompass/specs/demo/reviews/smoke-run/` や検証用 `app.md` が不要であれば、対象アプリ側の判断で削除する。実アプリの仕様やレビュー記録として残すものと、一時検証用に消すものを分けて確認する。

## 17. トラブルシュート

| 症状 | 確認すること |
| --- | --- |
| `--verify` が失敗する | 配布物に allowlist 外ファイル、exclude 対象ファイル、欠落ファイルがないか確認する。 |
| smoke test が失敗する | `--smoke-external-app-root` の指定先が存在するか、書き込み可能か確認する。 |
| API 呼び出しが失敗する | API key を環境変数で渡しているか、`config/api-settings.yaml` の variant が正しいか確認する。 |
| review-run が `triage_pending` になる | `review_triage.py list-pending` で未判断所見を確認する。 |
| `next --json` が `post_write_verification` を返す | 対象文書の書き込み後検証が未完了である。 |
| commit guard が止まる | 対象リポジトリ、staged ファイル、承認レコード、post-write verification 状態を確認する。 |
| LLM が ReviewCompass を見つけられない | 対象アプリ側の LLM セッションに、配布済み ReviewCompass の配置場所を伝える。 |
| 対象アプリではなく ReviewCompass 側に記録が作られた | LLM セッションを立ち上げた場所と、出力先 `.reviewcompass/` の場所を確認する。 |

## 18. 禁止事項

- ReviewCompass 開発リポジトリ全体を対象アプリへコピーしない。
- API key、token、password などの秘密値を配布物に入れない。
- ReviewCompass 側の開発証跡、実験ログ、過去 review-run 記録を対象アプリ側へ持ち込まない。
- 対象アプリ側の workflow state を理由なく手で書き換えない。
- ReviewCompass 側リポジトリと対象アプリ側リポジトリを取り違えて commit / push しない。
- 対象アプリ側の日常運用を ReviewCompass 開発リポジトリ上で続けない。

## 19. 実アプリ pilot 前のチェックリスト

- [ ] 実アプリ pilot で使う対象アプリ root を決めた。
- [ ] LLM セッションの起動パターンを選んだ。
- [ ] `config/api-settings.yaml` に秘密値が含まれていないことを確認した。
- [ ] ReviewCompass 開発リポジトリ側の LLM に依頼して、配布物を生成した。
- [ ] ReviewCompass 開発リポジトリ側の LLM に依頼して、対象アプリ root への配布前 smoke を確認した。
- [ ] 対象アプリ側 LLM が参照できる場所に、検証済み配布物を配置した。
- [ ] 対象アプリ側で LLM セッションを立ち上げ、配布済み ReviewCompass の場所を伝えた。
- [ ] 対象アプリ側に作られた `.reviewcompass/` 配下の変更を確認した。
- [ ] 実アプリ pilot で見つけた ReviewCompass 固有依存を記録する場所を決めた。
