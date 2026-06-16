---
date: 2026-06-16
classifier: codex_main_session
classification: R-0（workflow-management）
trigger_source: 利用者が、手戻り削減候補を個別タスクではなく operation registry / preflight として統一的に扱い、SDD スタイルで着手するよう指示した。
feature: workflow-management
finding: operation-registry-preflight-unified-design
---

## 分類根拠

本件は、review-run 作成、post-write manifest coverage、document-type 判定、
review criteria 生成、triage approval、正本コマンド確認、worktree 混線、commit approval chain、
nested issue handling などを、個別 helper ではなく operation registry / preflight として
統一的に扱うための workflow-management 変更である。

既存の `docs/notes/2026-06-16-operation-registry-preflight-design.md` は、これらを
operation contract、read-only preflight、command registry、runner / wrapper の段階へ
整理した設計入口メモである。
`docs/notes/2026-06-16-workflow-recovery-smell-inventory.md` は、同じ問題群を
手戻り削減候補として棚卸しし、`docs/notes/2026-06-16-nested-issue-handling-smell.md` は、
作業中に別問題が深くネストする型を別課題として記録した。

この変更は、workflow-management の既存意図である「作業順序、承認、不可逆操作、
post-write verification、reopen などの workflow gate を機械強制する」責務の範囲内である。
新しい feature 境界は不要であり、requirements に新しい受入条件を追加してから、
design、tasks、implementation へ連鎖するのが妥当である。

ただし、operation registry / preflight は workflow 操作の共通入口であり、利用側は
特定 feature に閉じない。そのため、意図から読める要件への要求として、全 feature を
impact review 対象として一度開く。これは全 feature の正本を同じ深さで書き換えるという意味ではない。
`workflow-management` を主対象とし、それ以外の feature は、operation contract の consumer または
派生検査対象として「既存契約を変える必要があるか」を明示的に確認する。

ここでいう「開く」は、2 種類に分けて記録する。

- **reopen scope**：正本を再オープンする feature。該当 feature は対象 phase 以降の
  workflow flag を false に戻し、drafting から approval までを再実施する。
- **impact review scope**：影響確認だけを行う feature。該当 feature は
  `indirect_check_only` として扱い、正本変更が必要と判定されない限り workflow flag を
  false に戻さない。review-wave / alignment / downstream impact decision で
  「変更不要」または「既存契約で十分」を記録する。

今回の reopen scope は `workflow-management` のみである。foundation／runtime／evaluation／analysis／
self-improvement／conformance-evaluation は impact review scope には含めるが、現時点では
reopen scope ではない。

手戻り種別：**R-0（requirements 起点。intent・feature-partitioning へは遡らない）**。

- intent（意図）：workflow-management の意図は、手順と gate の機械強制である。
  operation registry / preflight はこの意図の範囲内であり、意図文書の改訂は不要。
- feature-partitioning（機能分割）：対象は workflow-management の既存責務で受けられる。
  新 feature 境界は不要。
- requirements：operation registry / preflight の目的、対象 operation、read-only preflight、
  command validation、pending conflict、artifact policy、nested issue stack の受入条件を追加する必要がある。
- design：operation contract の構造、preflight response、Phase 1 / Phase 2 の境界、
  command registry との責務分担、multi-target bundle / manifest coverage 検査を定義する必要がある。
- tasks／implementation：最初の実装対象を小さく切り、TDD で read-only preflight から実装する必要がある。

## 事実

- 2026-06-16 の作業では、post-write manifest が review-run の実 target set より広い
  coverage を表現できる問題が見つかった。
- API review の criteria / prompt が文書タイプを十分に制御しないと、
  post-write verification が設計壁打ちへ変質し、round 数が増えることが分かった。
- 作業中に別問題が見つかり、その対応がさらに別文書や別検証を要求する
  nested issue handling の課題も見つかった。
- これらは個別の不具合ではなく、作業前・生成前に operation 単位で対象、前提、
  衝突、生成物、停止条件を確認する共通層が弱いことに起因する。
- 利用者は、これらを個別タスクではなく統一的な operation registry / preflight として
  SDD スタイルで進めることを指示した。

## feature impact 判定

### scope 切り分け

- reopen scope：`workflow-management`
- impact review scope：foundation／runtime／evaluation／analysis／workflow-management／self-improvement／conformance-evaluation
- false 化する workflow flag：`workflow-management` の requirements 後段および
  design／tasks／implementation の対象 gate
- false 化しない workflow flag：`indirect_check_only` の 6 feature。正本変更要否は
  review-wave / downstream impact decision で記録する

| feature | decision | impact_basis | rationale |
| --- | --- | --- | --- |
| workflow-management | reopen_existing_feature | contract_ownership | `next`、post-write verification、commit approval、reopen、review-run、workflow precheck の操作契約と gate を所有するため。 |
| foundation | indirect_check_only | consumer_or_derivative_only | operation contract の語彙・証跡・安全側停止の考え方を参照し得るため、共通契約の変更要否を確認する。ただし現時点の実装所有は workflow-management。 |
| runtime | indirect_check_only | consumer_or_derivative_only | session capture、hook、runtime artifact と接続し得るため、実行時契約の変更要否を確認する。ただし本件の主変更は workflow 操作前検査。 |
| evaluation | indirect_check_only | consumer_or_derivative_only | review-run、post-write verification、triage などの利用側であり、preflight contract の consumer として確認対象にする。 |
| analysis | indirect_check_only | consumer_or_derivative_only | operation record や review evidence を後段で読む可能性があるため、分析入力契約の変更要否を確認する。 |
| self-improvement | indirect_check_only | consumer_or_derivative_only | 手戻り削減候補を出す側・読む側として operation registry を参照し得るため、規律改善ループへの影響を確認する。 |
| conformance-evaluation | indirect_check_only | consumer_or_derivative_only | workflow-management の新しい preflight 契約を検査対象として参照し得るため、照合対象として確認する。ただし実装所有責務は変わらない。 |

新 feature 判定：no_new_feature。

## 再実施対象

- **workflow-management（R-0）**：requirements に operation registry / preflight の受入条件を追加し、design／tasks／implementation へ連鎖する。これは reopen scope なので、対象 gate は false に戻す。
- **全 feature impact review**：foundation／runtime／evaluation／analysis／self-improvement／conformance-evaluation は、正本変更を前提にせず、consumer／derivative として契約変更要否を各 gate で確認する。これは impact review scope であり、reopen scope ではない。
- impacted_downstream_phases：design／tasks／implementation。

## 停止点

`reopen-start` により in-progress ファイルを発行し、`workflow-management/spec.json` の
requirements 後段と recheck を差し戻す。
第1過程の停止点として、利用者が手戻り種別・再実施範囲・差し戻し内容を承認するまで、
requirements 本文、design 本文、tasks 本文、テスト、実装には進まない。
