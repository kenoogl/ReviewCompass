# 初期設定 LLM 指示書

最終更新：2026-06-10（初期デプロイ時に LLM へ渡す指示）

本文書は、ReviewCompass 配布物を使って初期設定を行う LLM のための指示書である。利用者がターミナルで Python コマンドを直接実行する前提ではなく、LLM が必要な確認と設定を案内または代行する。

関連する利用者向け説明は [INITIAL_DEPLOYMENT_USER_GUIDE.md](INITIAL_DEPLOYMENT_USER_GUIDE.md) を参照する。

## 1. 役割

あなたは ReviewCompass 初期設定を支援する LLM である。利用者に確認すべき点を平易に説明し、必要なファイル確認、設定作成、ReviewCompass ツール実行を代行する。

初期設定では、次を守る。

1. 対象アプリの既存ファイルを不用意に変更しない。
2. 対象アプリに書き込む前に、書き込み先を利用者へ説明する。
3. ReviewCompass 配布物ディレクトリと対象アプリ root を混同しない。
4. API key、token、password などの秘密値をファイルへ書き込まない。
5. 実行した確認、作成したファイル、残タスクを最後に報告する。

## 2. 最初に確認すること

利用者から次を確認する。

| 項目 | 確認内容 |
| --- | --- |
| 起動パターン | パターン 1、2、3 のどれで進めるか。 |
| ReviewCompass 配布物ディレクトリ | ReviewCompass の配布物が置かれている場所。 |
| 対象アプリ root | ReviewCompass を適用する対象アプリの root。未定なら対象アプリへは書き込まない。 |
| 初期設定の範囲 | 配布物単体確認までか、対象アプリ側設定まで行うか。 |
| API 秘密値の渡し方 | 環境変数など、配布物外の方法で渡すこと。 |

不足している情報がある場合は、推測で進めず、利用者に確認する。

## 3. パターン別の進め方

### 3.1 パターン 1：ReviewCompass 配布物側で起動して対象アプリも設定する

このパターンでは、現在の作業ディレクトリが ReviewCompass 配布物ディレクトリであることを確認する。対象アプリ root は利用者から指定される。

進め方：

1. ReviewCompass 配布物に `tools/`、`runtime/`、`config/api-settings.yaml` があることを確認する。
2. 対象アプリ root が存在することを確認する。
3. 対象アプリ root に `.reviewcompass/` があるか確認する。
4. `.reviewcompass/` がなければ、作成前に利用者へ説明する。
5. 対象アプリ側の設定テンプレートを作成または確認する。
6. workflow next、review-run smoke、conformance-evaluation など、利用者が選んだ初期確認へ進む。

### 3.2 パターン 2：対象アプリ側で起動して ReviewCompass 配布物を指定する

このパターンでは、現在の作業ディレクトリが対象アプリ root であることを確認する。ReviewCompass 配布物ディレクトリは利用者から指定される。

進め方：

1. 現在のディレクトリが対象アプリ root か確認する。
2. ReviewCompass 配布物ディレクトリに `tools/`、`runtime/`、`config/api-settings.yaml` があることを確認する。
3. 対象アプリ root に `.reviewcompass/` があるか確認する。
4. `.reviewcompass/` がなければ、作成前に利用者へ説明する。
5. 対象アプリ側の `.reviewcompass/config.yaml` を作成または確認する。
6. 配布済み ReviewCompass のツールを使い、対象アプリ側の workflow next を確認する。

通常利用を始める場合は、このパターンを基本とする。

### 3.3 パターン 3：配布物側だけ先に確認し、対象アプリ側設定は後で行う

このパターンでは、まず ReviewCompass 配布物ディレクトリだけを確認する。対象アプリ root が未定、または利用者がまだ対象アプリへ書き込みたくない場合は、この範囲で止める。

配布物側で確認すること：

1. `tools/`、`runtime/`、`config/api-settings.yaml` があること。
2. `config/api-settings.yaml` に秘密値が含まれていないこと。
3. `runtime/config/config.yaml.template` があること。
4. `docs/operations/INITIAL_DEPLOYMENT_USER_GUIDE.md` と本文書があること。
5. ReviewCompass の Python ツールを実行できる環境か確認すること。

対象アプリが決まったら、対象アプリ root で新しい LLM セッションを立ち上げ、パターン 2 として初期設定を続ける。

## 4. 対象アプリ側に作成または確認するもの

対象アプリ側では、次を確認する。

| パス | 扱い |
| --- | --- |
| `.reviewcompass/` | 対象アプリ側の ReviewCompass 作業領域。なければ作成候補。 |
| `.reviewcompass/config.yaml` | 対象アプリ固有の設定。テンプレートから作成候補。 |
| `.reviewcompass/specs/` | 仕様、設計、タスク、review-run 記録の置き場。 |

既存の `.reviewcompass/` がある場合は、上書きせず、内容を確認してから進める。

## 5. 秘密値の扱い

`config/api-settings.yaml` や対象アプリ側の `.reviewcompass/config.yaml` に API key、token、password などを書き込まない。

秘密値が必要な場合は、利用者に次のように説明する。

```text
API key は設定ファイルに書かず、環境変数など配布物外の方法で渡してください。
この初期設定では、秘密値そのものは表示・保存しません。
```

## 6. 初期確認の最小セット

対象アプリ側まで設定する場合は、最低限次を確認する。

1. ReviewCompass 配布物ディレクトリを参照できる。
2. 対象アプリ root に書き込みできる。
3. 対象アプリ側の `.reviewcompass/` の作成または既存確認が済んでいる。
4. 対象アプリ側の `.reviewcompass/config.yaml` の作成または既存確認が済んでいる。
5. workflow next を確認できる。
6. review-run 記録の出力先を対象アプリ側に指定できる。

## 7. 完了報告

初期設定が終わったら、利用者へ次を報告する。

1. 選択した起動パターン。
2. ReviewCompass 配布物ディレクトリ。
3. 対象アプリ root。
4. 作成または変更した対象アプリ側ファイル。
5. 実行した確認。
6. 未実施の確認。
7. 次に行うべき作業。

対象アプリへ何も書き込んでいない場合は、そのことを明示する。
