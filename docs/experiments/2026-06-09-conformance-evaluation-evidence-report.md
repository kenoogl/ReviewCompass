# Conformance Evaluation 論文用エビデンスレポート

作成日: 2026-06-09

## 論文用エビデンスの範囲

本レポートは、2026-06-09 に実施した conformance-evaluation の作業を、論文用の
dogfooding エビデンスとして整理する。観察対象は、ReviewCompass が自分自身の
conformance-evaluation 機構を用いて、implementation-first に進んだ follow-up 作業を点検し、
文書化 gap を特定し、requirements/design 正本へ反映し、最終的な契約確認まで行った一連の作業である。

これは単一プロジェクトの dogfooding evidence である。統計的一般性、独立リポジトリでの有効性、
他の仕様復元手法に対する優位性は主張しない。価値は process evidence にある。つまり、
implementation-first の成果物を、追跡可能な監査証跡を保ったまま、明示的な requirements/design
契約へ戻す過程を示している。

## 証跡一覧

| 証跡 | パス | 論文上の役割 |
| --- | --- | --- |
| 初期 conformance 記録 | `.reviewcompass/specs/conformance-evaluation/conformance/2026-06-09-completed-followup-conformance.md` | 実装証跡は存在するが、requirements/design coverage に specification gap と design gap がある、という初期診断を示す。 |
| formal follow-up summary | `docs/notes/2026-06-09-formal-completed-followup-summary.md` | 9 件の昇格候補を formal completed follow-up outputs として記録する。 |
| contract ownership note | `docs/notes/2026-06-09-completed-followup-contract-ownership.md` | requirements gap と design gap をどの文書で扱うかを記録する。 |
| requirements 更新 | `.reviewcompass/specs/conformance-evaluation/requirements.md` | Requirement 11 として completed follow-up prerequisite set と formal completed follow-up outputs を追加する。 |
| design 更新 | `.reviewcompass/specs/conformance-evaluation/design.md` | §13.8 として output の責務、相互関係、handoff summary との接続を定義する。 |
| 最終 conformance 確認 | `.reviewcompass/specs/conformance-evaluation/conformance/2026-06-09-completed-followup-contract-confirmation.md` | `requirements gap: resolved` と `design gap: resolved` を記録する。 |
| requirements/design 衝突レビュー | `.reviewcompass/specs/conformance-evaluation/reviews/2026-06-09-completed-followup-requirements-design-conflict-review.md` | Requirement 11 と design §13.8 が既存要件・設計事項と衝突していないかを確認し、最小修正の範囲を記録する。 |
| regression tests | `tests/conformance-evaluation/test_completed_followup_conformance.py` and `tests/conformance-evaluation/test_conformance_evidence_report.py` | 期待される証跡リンクと、過大主張を避ける境界条件を固定する。 |

## 観察された workflow

作業は、将来計画候補として実装・テスト済みになっていた implementation-first の成果物群から始まった。
conformance-evaluation は、具体的な実装証跡が requirements/design の文章正本より先に進んでいることを
明示した。

修復は次の 4 段階で進んだ。

1. 初期 conformance result を `gap_found` として記録する。
2. formal completed follow-up outputs を 1 つの handoff note に要約する。
3. 残った requirements gap と design gap の target document を決める。
4. requirements/design 正本を更新し、統合契約が conformance したことを確認する。

最終確認記録では `status: conforms` とし、`requirements gap: resolved` および
`design gap: resolved` を記録している。

その後、requirements/design 衝突レビューを実施した。レビュー結果は `minor_conflict_found` である。
Requirement 11 自体は既存の Requirement 9 / Requirement 10 とコンフリクトしていないと判断した。
一方で、design.md §20.3 に Requirement 件数を `全 10 件` とする古い表記が残っていたため、
design.md §20.3 の `全 10 件` を `全 11 件` に修正した。この修正は、既存項目の意味を変更しない最小修正として扱った。

## 有用性

この事例は、implementation-first の作業から明示的な仕様成果物へ戻る具体的な経路を示している点で、
論文用エビデンスとして有用である。単なる回顧メモではなく、名前付きの conformance 記録、
target document の決定、requirements/design 更新、テスト、最終 conformance 確認を生成している。

また、conformance-evaluation が境界管理の役割を果たせることも示している。完了済みの実装証跡と、
まだ文書化されていない前提を分離し、文書化不足を明示した上で、requirements/design 契約へ戻した。

さらに、追跡性がある。論文で使う主張は、初期の `gap_found` 記録から、ownership note、
requirements/design 更新、最終 `conforms` 記録までたどれる。これにより、記憶やセッション内説明に頼らず、
外部評価者が証跡を確認できる。

## 限界と課題

最大の限界は、単一プロジェクトの dogfooding evidence である点である。同じチーム、同じツール、
同じリポジトリで成果物の作成と評価を行っている。そのため、process observability の証拠としては有用だが、
外的妥当性の証拠としては弱い。

第二の限界は、この事例が implementation-first である点である。この性質自体が本事例の観察対象だが、
同時に、これはきれいな事前仕様駆動の場面ではなく、後から仕様へ戻す recovery setting の評価である。

第三の限界は、文言の射程に敏感なことである。作業中には、合意範囲を超えた今後の作業を示唆する表現が
いくつか混入した。それらは修正され、現在のテストでは requirements/design 正本の主張が bounded claims
に留まることを確認している。これは修正行動のエビデンスとして有用だが、方法論上の課題でもある。
conformance 記録は、範囲を注意深く確認しないと次の作業を過大に示唆しうる。
追加の requirements/design 衝突レビューでも、既存項目を原則変更せず、件数表記だけを直す方針を明示した。
この点は、conformance-evaluation が仕様修復を支援する一方で、既存仕様を過剰に書き換えないための
レビュー手順が必要であることを示している。

第四の限界は、下流効果を測っていないことである。更新後の契約が後続の欠陥を減らしたか、レビュー時間を
短縮したか、独立導入を改善したかは示していない。それらには、後続の比較研究または縦断研究が必要である。

## 論文での使い方

この事例は、たとえば次のような主張を支える補助証拠として使える。

> 自己適用事例において、conformance-evaluation は implementation-first の follow-up 成果物が
> requirements/design 正本を先行していることを検出し、不足していた契約を正本へ戻し、
> requirements/design gap が解消されたことを最終 conformance 記録として残した。

推奨される使い方:

- traceable specification recovery の定性的エビデンスとして使う。
- gap detection と remediation の case study として使い、定量的な有効性証明としては使わない。
- single-project dogfooding evidence と implementation-first sequencing の caveat を併記する。
- 初期の `gap_found` 記録と最終の `conforms` 記録をセットで参照し、読者が問題と修復の両方を確認できるようにする。

## 今後の研究質問

- ReviewCompass で開発されていないリポジトリでも、同じ conformance-evaluation pattern は機能するか。
- 最終 conformance confirmation は、後続レビュー所見や手戻りを減らすか。
- workflow のどの要素が本質的か。初期 gap 記録、ownership note、requirements/design 更新、テスト、
  最終 confirmation のどれが欠かせないか。
- conformance confirmation を内部の作業記録ではなく論文用エビデンスとして信頼するには、どの程度の独立レビューが必要か。
