---
date: 2026-06-15
gate: stages/design.yaml#alignment
feature: workflow-management
reopen: R-0
reopen_topic: commit-approval-nonce
decision: existing_sufficient
---

# design alignment（整合確認）：commit 承認 nonce challenge 設計

reopen R-0 の第3過程、workflow-management design フェーズの alignment 段。Requirement 4 受入 6〜7 と、design.md §不可逆操作の直前ゲートモデル §2.1、および既存設計節・下流 recheck 状態の整合を確認する。

## Requirement 4 受入 6〜7 との整合

| 要件 | 設計での受け方 | 整合判定 |
| --- | --- | --- |
| Req 4 受入 6（nonce challenge・target digest・consume） | design.md §2.1 で challenge 保存先、承認レコード保存先、staged file set、ファイル別 `target_sha256`、全体 target digest、nonce、TTL、未消費状態、形式不正時 fail-closed、commit path 内 validation、commit 成功後 consume を定義した。 | 整合。要件の入力・検査・消費責務を設計へ展開済み。 |
| Req 4 受入 7（LLM 非依存・保証範囲） | design.md §2.1 で `llm`、`provider`、`model`、`model_id`、`proxy_model_id` を schema 禁止とし、判定入力を staged file set、staged blob hash、target digest、nonce、expiry、consumed 状態に限定した。 | 整合。操縦 LLM への依存なし。 |
| 出典文保存と秘匿情報 | design.md §2.1 で承認文を argv に載せず stdin または no-store mode とし、保存時は既存 redaction helper と residual secret 検査を通す。 | 整合。秘匿文字列のみを redaction 対象とし、通常文を一律に秘密扱いしない。 |

## 既存設計節との整合

| 既存設計節 | 関係 | 整合判定 |
| --- | --- | --- |
| §軽量版検査スクリプトモデル（Req 2） | commit approval prepare / record / invalidate は検査スクリプトの commit 系入口に接続する。欠落・形式不正・期限切れ・不一致は fail-closed とする。 | 整合。Req 2 の fail-closed 方針と一致。 |
| §起草者と判定者の分離モデル（Req 3） | 本件は commit 実行前の承認対象束縛であり、review の起草者・判定者分離を変更しない。 | 整合。改訂不要。 |
| §不可逆操作の直前ゲートモデル（Req 4） | 既存 commit 承認レコード検査を nonce challenge と target digest で強化する。不可逆操作の最小集合は増やさない。 | 整合。既存節内の拡張で足りる。 |
| §reopen 機械強制モデル（Req 5） | 本 reopen 自体は R-0 として進行中ファイルに記録済み。nonce 機能は reopen 機構の段集合を変えない。 | 整合。改訂不要。 |
| §session 跨ぎ状態管理モデル（Req 6） | challenge / approval record は `.reviewcompass/runtime/approvals/` 配下の runtime 承認状態であり、`stages/in-progress/` の workflow 進行状態とは責務が別。 | 整合。両者は衝突しない。 |
| §多層防御の位置付けモデル（Req 7） | nonce challenge は第1層の機械ゲート強化であり、古い承認・別対象承認・承認後差し替えを遮断する。 | 整合。保証範囲の限界も設計に明記済み。 |
| §機能依存マップモデル（Req 8） | 機能順・依存解決に変更なし。 | 整合。改訂不要。 |
| §review-wave 要約コマンドモデル（Req 10） | 対象・責務が異なる。 | 整合。改訂不要。 |
| §Req 11 重要決定の出典検査モデル | Req 11 は重要決定の出典検査、今回の Req 4 受入 6〜7 は commit 承認対象の staged 内容束縛であり、どちらも commit 前の防御に関わるが責務は別。 | 整合。重複なし。 |

## 下流 recheck との整合

- `docs/reviews/reopen-classification-2026-06-15-wm-commit-approval-nonce.md` は R-0、feature は workflow-management、下流影響は design／tasks／implementation と判定している。
- design.md は Requirement 4 受入 6〜7 を §不可逆操作の直前ゲートモデル §2.1 と要件追跡表へ展開済み。
- tasks／implementation では TDD で、challenge schema、canonical target digest、expiration、redaction、invalidated / consumed 状態、commit path 内 validation を具体タスクと実装へ再展開する必要がある。

## 判定

- **decision：existing_sufficient**。
- design.md の今回追加設計は Requirement 4 受入 6〜7 および既存設計節と整合し、追加の design 改訂は不要。
- tasks／implementation の recheck は維持する。
