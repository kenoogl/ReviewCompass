---
review_type: requirements_design_conflict_review
target: completed_followup_prerequisite_set
status: minor_conflict_found
review_date: 2026-06-09
---

# Completed follow-up requirements/design conflict review

## 目的

conformance-evaluation の completed follow-up prerequisite set について、requirements.md と design.md に追加された項目が、既存の要件および設計事項とコンフリクトしていないかを確認する。

本レビューでは、既存項目は原則変更しない。既存項目への直接変更は、衝突または整合性崩れを直す最小差分に限る。

## レビュー対象

- `.reviewcompass/specs/conformance-evaluation/requirements.md` Requirement 11
- `.reviewcompass/specs/conformance-evaluation/requirements.md` Change Intent / Cross-Document Interface
- `.reviewcompass/specs/conformance-evaluation/design.md` §13.8
- `.reviewcompass/specs/conformance-evaluation/design.md` §20.2 / §20.3 / Cross-document wave trace

## 判定

判定は `minor_conflict_found` とする。

completed follow-up prerequisite set の追加そのものは、既存の主要境界とコンフリクトしていない。ただし、design.md §20.3 に requirements.md の Requirement 件数を `全 10 件` とする古い表記が残っており、Requirement 11 の追加後の `全 11 件` と整合していない。

## 確認結果

### 1. Requirement 9 / Requirement 10 との関係

Requirement 9 は、実装由来契約を contract ownership map、spec update proposals、draft-only spec update artifacts として扱い、正式な requirements/design/tasks 本体更新とは分離する。

Requirement 10 は、既存システムに後追いで intent を追加した場合のコード由来差分抽出を扱い、正式な tasks 反映は workflow-management 側の reopen 手続きに委ねる。

Requirement 11 は、ユーザ指示に基づいて completed follow-up prerequisite set を formal completed follow-up outputs として正式化した項目である。そのため、Requirement 9 / Requirement 10 が禁止している自動的な requirements/design 本体更新とは扱わない。

結論として、Requirement 11 は Requirement 9 / Requirement 10 の draft-only 境界とコンフリクトしていない。既存の Requirement 9 / Requirement 10 本文は変更しない。

### 2. 既存の機能境界との関係

Requirement 11 は、completed follow-up outputs の正式化と handoff summary への接続を扱う。既存の 2 モード構造、6 criteria、tasks.md 本体の範囲外扱い、実装適合レビューとの分離は変更していない。

結論として、既存の 2 モード構造、6 criteria、tasks.md 本体の範囲外扱いとのコンフリクトはない。既存項目は変更しない。

### 3. design.md §20.3 の件数表記

design.md §20.3 には、`requirements.md の全 10 件の Requirement` という表記が残っている。

requirements.md は Requirement 11 を含む状態になっており、design.md 冒頭でも `11 件の Requirement` と記録している。そのため、§20.3 の `全 10 件` は `全 11 件` と整合していない。

これは設計意味論の変更ではなく、件数表記の整合性崩れである。修正する場合は、design.md §20.3 の `全 10 件` を `全 11 件` に変更するだけの最小差分に留める。

## 推奨対応

1. 次の作業では、design.md §20.3 の `全 10 件` を `全 11 件` に変更する。
2. Requirement 9 / Requirement 10 の本文は変更しない。
3. Requirement 11 / design.md §13.8 の内容は、現時点では追加修正しない。
4. 修正後に conformance-evaluation 関連テストと workflow guard を再実行する。

## 残リスク

`completed follow-up prerequisite set` という用語は、前提条件という読みを含む。ただし、requirements.md と design.md では completed follow-up outputs の正式化に範囲を限定しており、作業開始条件や実アプリ pilot の開始条件としては扱っていない。現時点では用語変更を必須とはしない。
