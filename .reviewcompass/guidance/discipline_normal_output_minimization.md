---
name: normal-output-minimization
description: CLI / tool の正常系出力を最小化し、異常系と機械可読出力には必要情報を残す
metadata:
  type: feedback
---

# 正常系出力最小化

CLI / tool の人間可読出力は、正常系では利用者が次に進むために必要な最小情報だけを出す。異常系では原因、現在状態、次に取れる行動を省略しない。機械可読出力は `--json` などの明示オプションに集約し、詳細情報を保持する。

## 原則

- 正常系の人間可読出力は 1 行から数行に抑える。
- 正常系では内部判定、全入力、詳細な current state、長い候補一覧を既定出力に出さない。
- 異常系では、判定結果、原因、対象ファイル、現在状態、次の許可 action を出す。
- `--json` は詳細を落とさない。自動処理、監査、デバッグ、ログ連携は `--json` を使う。
- `--verbose` がある場合だけ、正常系でも詳細ログを出してよい。
- 非定型処理は、利用者が状況を理解するために必要な短い説明を許容する。ただし定型化できる処理は CLI 側へ寄せる。

## CLI 実装契約

新規または改修する CLI / tool は、次の出力面を分ける。

| 出力面 | 契約 |
|---|---|
| 正常系 human output | 成功事実と対象 action だけを短く出す |
| 警告系 human output | 警告理由、続行可否、必要な人間判断を出す |
| 異常系 human output | 停止理由、壊さないために行わなかった処理、次 action を出す |
| `--json` output | 判定、理由、対象、状態、証跡パスを完全に出す |
| `--verbose` output | 調査・保守に必要な詳細を出す |

## 適用手順

1. 既存 CLI / tool を棚卸しし、正常系出力が多いもの、対話で頻出するもの、不可逆操作に近いものを優先する。
2. 正常系 human output の期待をテストに固定する。
3. 異常系 human output と `--json` の情報量が落ちていないことをテストする。
4. 実装では、判定データの生成と human formatter を分ける。
5. 正常系の詳細を削る場合も、JSON / log / manifest のどこかに監査可能な詳細を残す。

## 棚卸し

共通棚卸しの正本は `docs/notes/working/2026-06-19-normal-output-minimization-tool-inventory.yaml` とする。各 tool の対応状態、優先度、次 action はこの YAML を更新する。

## 既存規律との関係

- [[concise-complete-report]]: 最終報告は簡潔かつ漏れなく行う。本規律は CLI / tool の通常出力を対象にし、LLM の最終報告そのものを省略しない。
- [[facts-vs-interpretation]]: 正常系で省略した詳細も、必要なら JSON / log / manifest から事実確認できるようにする。
- [[workflow-precheck-invocation]]: 不可逆操作直前の検査は維持する。ただし OK の既定 human output は最小にする。
