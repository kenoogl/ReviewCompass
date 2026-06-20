# GPT primary 006 post-fix recheck: design status vs implementation status

## 対象所見

- `2026-06-20-workflow-management-design-vertical-redo-review-run-v2-gpt-5.4-primary-006`
- 指摘: Requirement 16、完成判定基準、XDI-WM-003 / XDI-WM-004 付近で、現在の design drafting 状態と、先行実装・運用由来の契約を混在して読める表現があった。これにより、review-wave / alignment / approval / implementation が完了していないのに完了済みと誤読されるリスクがあった。

## 修正内容

- `実装由来契約の採用` 節を `先行実装・運用由来契約の設計入力` に変更した。
- 同節の冒頭に、ここでいう「取り込む」「設計境界とする」は design drafting の入力整理であり、review-wave、alignment、approval、Requirement 13〜16 の tasks / implementation 完了を主張しないことを明記した。
- XDI-WM-001〜005 の導入文を、`採用する` から `設計入力として取り込む` / `後続 tasks / implementation で検査可能な境界へ分解する` へ変更した。
- 変更意図の履歴で、`実装は先行済み、本改訂は設計の追認` と読める文を、先行実装証跡と本 design drafting の状態を分離する表現へ修正した。
- `実装に合わせて確定` と読める文を、先行 maintenance 証跡を設計入力として再記述したものと明記した。

## 再点検結果

- 完成判定基準の末尾にある「現時点の実装完了主張ではない」という既存の線引きと、XDI 節の表現が整合した。
- XDI 節は先行証跡を捨てずに保持しつつ、後続 gate 完了や実装完了の主張から切り離された。
- Requirement 16 の Phase 0〜6 の段階的実装計画と矛盾しない。

## 残リスク

- tasks 段では、XDI-WM-001〜005 のうち既存実装で満たしているものと、Requirement 13〜16 として新規 TDD が必要なものを別タスクとして切り分ける必要がある。
