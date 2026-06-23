---
date: 2026-06-20
record_type: working-memo
status: active
topic: APIレビュー用プロンプト監査の議論経緯と評価
related:
  - docs/notes/working/2026-06-20-api-review-prompt-quality-side-track.md
  - docs/notes/working/2026-06-20-api-review-prompt-method-comparison.md
  - docs/operations/API_REVIEW_PROMPT_QUALITY.md
  - docs/operations/SESSION_WORKFLOW_GUIDE.md#vertical-intent-transfer-review
  - templates/review/api_review_criteria_template.md
  - templates/review/api_review_prompt_quality_criteria_template.md
  - templates/review/main_preanalysis_sufficiency_audit_criteria_template.md
  - .reviewcompass/specs/workflow-management/reviews/2026-06-20-workflow-management-implementation-req14-approval-gate-preanalysis-audit-run/
---

# APIレビュー用プロンプト監査の議論経緯と評価

## 目的

このメモは、2026-06-20 の長時間の議論で整理した「APIレビューへ投げるプロンプト自体をどう作り、どう監査するか」を記録する。

実装済みのアイデアだけでなく、途中で出た問題意識、失敗、却下・保留された案、運用上の地雷、検討結果の評価を残す。

結論だけを残すと、なぜこの監査が必要になったのか、どこで判断を誤ったのか、次に同じ失敗を避けるには何を機械化すべきかが失われる。そのため、本メモは作業結果ではなく、議論の経緯と判断根拠を主対象にする。

## 大前提

API review-run の品質は、reviewer model の能力だけで決まらない。

レビュー用プロンプトが不適切だと、優れたモデルでも次のような結果を返す。

- 実 target を見ず、作成者の要約だけを審査する
- 上流意図との接続を見落とす
- 利用者が求めたレビュー要件を、main が無意識に狭める
- 複数の独立判断を 1 prompt に押し込み、注意が発散する
- `findings: []` が「問題なし」ではなく「見るべきものを見ていない」結果になる

したがって、APIレビュー用プロンプトの監査は追加的な贅沢ではない。レビュー品質を成立させる前処理である。

## 議論の発端

workflow-management reopen では、Requirement 13〜16 の意図を requirements / design / tasks / implementation へ縦方向に再伝達する作業を進めていた。

その過程で design triad-review を API review-run で実施したが、旧方式では `--criteria-file` と `--target` に同じ author-written `review-target.md` を渡していた。

この旧方式では全モデルが `findings: []` を返した。しかし後で確認すると、実際の `design.md` 本文が target になっておらず、モデルは設計本文ではなくレビュー用要約の自己整合性を見ていた可能性が高かった。

利用者は、ここで「レビュー結果そのものより前に、APIレビュー用プロンプトの品質が課題」と指摘した。

## 初期の問題認識

最初に確認された問題は大きく 2 つだった。

1. 一般的な API review / LLM-as-Judge の基本要件が守られていない。
2. この場面固有の要件、つまり上流フェーズの意図が現フェーズへ正しく伝達されているかを見る縦方向レビュー要件が弱い。

一般要件は `docs/disciplines/discipline_llm_as_judge_prompting.md` にあり、少なくとも次を要求する。

- main が先に問題を直接検討し、材料と判断点を把握する
- 判断に必要な情報を prompt に含める
- 非誘導的な問いを立てる
- 範囲を広げすぎず狭めすぎない
- 出力契約を固定する
- API送信前に機微情報を確認する

場面固有要件は `docs/operations/SESSION_WORKFLOW_GUIDE.md#vertical-intent-transfer-review` にあり、次を要求する。

- target / source materials / out of scope を分離する
- 現フェーズ成果物だけを review target とする
- source materials は背景・意図伝達確認に使い、target の代替にしない
- source materials を path-only にしない
- 上流の目的、責務境界、受入条件、禁止事項、未確定事項、対象 phase への引き継ぎ判断をモデルが読める形で含める

この 2 系統を総合しないと、レビュー用プロンプトとしては不十分である。

## レビュー体制の整理

議論の中で、プロンプト作成と監査は次の体制に整理された。

| 役割 | 目的 |
|---|---|
| main | 材料を読み、判断点を整理し、APIレビュー用プロンプト素案を作る |
| adversarial | プロンプト素案の欠落、誘導、範囲ミス、材料不足、上流接続不足を探す |
| judgment | adversarial 所見の反映後、その prompt を実 review-run に使ってよいか判定する |

利用モデルについては、adversarial は `claude-sonnet-4-6`、judgment は `gemini-3.1-pro-preview` を既定とする。

`claude-opus-4-8` は挙動が怪しいとの利用者判断により当面不採用とした。

この既定は手作業で毎回選ぶのではなく、`config/api-settings.yaml` の `operation_defaults.api_review_prompt_quality.variant` に固定し、実行時は `--default-variant-for api_review_prompt_quality` で解決する方針になった。

途中で `gemini-3.5-pro-preview` と取り違えたが、これは誤りであり、正しい既定は `gemini-3.1-pro-preview` である。

## 旧方式から新方式への変化

旧方式では、criteria と target が同じ author-written summary になっていた。

新方式では、次を分離する。

- `User Review Requirements`: 利用者が求めた目的、対象、焦点、範囲、禁止事項、出力要件
- `--criteria-file`: レビュー観点、上流材料、必須チェック、範囲外、finding policy
- `--target`: 実際に審査する本文または実装 artifact

この分離により、モデルは author-written summary の自己整合ではなく、実 target と source materials の照合を行える。

実際に design review の再実行では、旧方式が `findings: []` だったのに対し、新方式では C1〜C7 の設計課題が検出された。

この差は、モデル性能差だけではなく、prompt 構造の差で説明される。

## 汎用テンプレート化の議論

当初は、今回の問題専用のプロンプトレビュー方法として始まった。

その後、利用者は「このプロンプトレビューは現在の問題限定か、汎用的に作られているか」を確認した。

結論は、汎用コアと場面別カスタマイズに分けるべき、である。

汎用コア:

- main が先に問題を検討する
- criteria と target を分離する
- source materials を model-readable にする
- 利用者要件を保持し、prompt へ写す
- 1 prompt 1 primary judgment
- API送信可能材料と機微情報を確認する
- adversarial / judgment で prompt quality review を行う

場面別カスタマイズ:

- 縦方向レビューなら上流意図伝達チェックを入れる
- proxy_model 判断なら候補案・raw 所見・判断範囲・不可逆操作の不許可を入れる
- implementation review なら requirements / design / tasks / implementation の接続を見る
- post-write なら実際の変更差分と verifier coverage を見る

この整理に基づき、次が作成された。

- `docs/operations/API_REVIEW_PROMPT_QUALITY.md`
- `templates/review/api_review_criteria_template.md`
- `templates/review/api_review_prompt_quality_criteria_template.md`

## proxy_model 判断との関係

途中で proxy_model 判断のプロンプト作成にも同じ問題が出た。

proxy_model は「ユーザが関与しない」ための別モデル判断であり、proxy_model に投げる前にユーザへ細かな判断を求めるのは前提を崩す。

ただし、proxy_model に投げる prompt の品質が低いと、proxy_model の判断も使えない。

そのため、proxy_model 用 prompt でも、通常の APIレビュー用 prompt と同じく次を守る必要がある。

- main が先に材料を読む
- raw review 所見や source materials を入れる
- main の preanalysis は仮説として扱う
- 判断項目を分割する
- 1 prompt に複数の独立判断を押し込まない
- output contract が proxy decision 用であることを確認する

ここで一度、proxy_model 本判断に使うべき `run_proxy_decision.py` ではなく、`run_role.py` / `run_review.py` 系の prompt quality 経路を混同し、余計な時間を使った。

これは思想の失敗ではなく、runner 選択と出力契約の機械化不足である。

必要な機械化:

- review purpose から runner を一意に選ぶ
- prompt quality review と proxy decision を出力契約で区別する
- proxy decision なのに `findings` が返ったら誤経路として停止する
- `decisions`、`proxy_model_id`、finding / cluster traceability を preflight する

## sandbox / API実行経路の議論

API実行時、sandbox や承認経路の問題で外部API呼び出しが拒否・停止する場面があった。

利用者は、過去にも同様の問題に対応できたこと、sandbox外の経路があること、問題解決の視点が狭かったことを指摘した。

ここで確認された教訓:

- proxy_model は本来ユーザの逐次関与なしで動くべきである
- 実行前に API 経路、variant、runner、出力契約を機械的に確定すべきである
- 手作業で ad hoc に手順を組むと、sandbox、runner、approval の落とし穴に落ちる
- 承認を毎回要求する設計では proxy_model の意味が薄れる

ただし、外部API送信そのものには明示承認が必要であり、ReviewCompass 内部仕様・設計・レビュー材料は、秘密情報・個人情報・第三者送信禁止情報を含まない限り、利用者が API review / proxy_model 判断を承認した場合の通常レビュー材料として扱う方針になった。

## 判断粒度の議論

大きな失敗として、1つの prompt に複数の独立判断を押し込んでいた。

利用者は、注意が発散するため「判断すべき項目ごとにプロンプトを作成し、レビューさせる」と指摘した。

これにより、次の方針になった。

- Req 14 のように approval gate / side track stack / workflow-state snapshot が独立している場合は分割する
- C1〜C7 のような複数クラスタ判断も、原則としてクラスタごとに prompt を分ける
- 各 prompt について prompt quality review を行う
- 一括 summary は後段で作ってよいが、個別判断の raw / parsed / decision 証跡を上書きしない

Req 14 では、最初は1つの combined prompt として扱い、prompt quality review で granularity risk が出た。

その後、approval gate / side track stack / workflow-state snapshot に分割した。

## リスク判断基準の議論

一時期、外部APIに repo 内設計・レビュー文脈を送ることが過剰に高リスク扱いされた。

利用者は、未公開の repo 内設計・レビュー文脈そのものを外部 API に送ることは許可する修正をしたはずだ、と指摘した。

整理結果:

- ReviewCompass 内部仕様・設計・タスク・レビュー所見・証跡パスは、通常のレビュー材料として送信可能
- ただし、API key、token、password、nonce、個人情報、第三者送信禁止情報、不要な全文ログは送らない
- リスク判断は「未公開 repo だから禁止」ではなく、「秘密値・個人情報・第三者契約・不要過多か」で見る
- 過剰な拒否は運用不能に直結する

## effective prompt / next --json との関係

本線では、`next --json` で唯一の地点を定め、その地点で行う機械処理を実装し、必要な規律を読ませる作業が進んでいた。

議論の中で、地点が戻ってきたら、その地点でどの作業ルールを有効化するかを機械的に確定する必要があると確認した。

当初は規律文書への pointer を返し、それをその場で読む構想だった。

その後、毎回 pointer を辿らせるより、判定点ごとの `effective prompt` として予め展開し、それを読むようにする方針になった。

ただし、今回の APIレビュー用プロンプト作成では、1本の大きな effective prompt だけでは足りない可能性が出た。

利用者は「もっと小さい処理にして、適宜読ませる方法は有効か」と問題提起した。

ここから、APIレビュー用プロンプト作成は単一の巨大指示ではなく、次の小さな処理列として扱うべきと整理された。

1. main preanalysis
2. preanalysis sufficiency audit
3. criteria draft
4. prompt quality review
5. 実 review-run
6. triage / proxy decision

## main preanalysis の位置づけ

利用者は、APIに渡す prompt を作る前段階として、main LLM が自分で triad-review の結果や関連資料をレビューし、必要な情報を検索してデータにアクセスし、その過程で利用したデータ元を含めることを提案した。

この案は有効と評価された。

理由:

- main LLM は会話文脈と repo context を持っている
- source materials の発見に強い
- 判断項目の分割候補を先に見つけられる
- prompt に入れるべき材料と不要材料を切り分けられる
- どのデータソースを使ったかを記録できる

一方、bias risk もある。

- main preanalysis を正解扱いすると、reviewer が独立判断しなくなる
- main の見落としが prompt 全体へ伝播する
- stale な所見が残ると、すでに解決済みの問題に reviewer が引っ張られる

結論:

- main preanalysis は必須に近い材料揃え工程として有用
- ただし、reviewer には「main preanalysis は仮説」と明示する
- reviewer には source materials から独立再構成させ、その後で preanalysis と比較させる

## preanalysis sufficiency audit の発想

main preanalysis 自体のバイアスが気になるため、preanalysis と proposed prompt を検査する別の prompt が必要になった。

検査側へ渡すもの:

- 利用者または workflow の review requirement
- requirements / design / tasks などの source materials
- main preanalysis
- proposed API review criteria / prompt
- 検査観点

検査側に要求する output:

- `verdict`
- `independent_reconstruction`
- `preanalysis_assessment`
- `prompt_sufficiency`
- `required_prompt_changes`
- `findings`

このために、`run_role.py` / `run_review.py` は `findings` 以外の top-level keys を保存できる必要があると分かった。

実装では、`parse_response_data()` を追加し、`format_response()` が `extra_fields` を保持できるようにした。

また、共通 API prompt template が「top-level key は findings だけ」と命じていたため、これも「findings は必須。ただし criteria が明示した追加 top-level keys は許可」に変更した。

この修正により、preanalysis sufficiency audit の構造化出力を raw / parsed に保存できるようになった。

## 実験: Req14 approval gate preanalysis audit

実ケースとして、Req 14 approval gate を対象にした。

作成した bundle:

- `.reviewcompass/specs/workflow-management/reviews/2026-06-20-workflow-management-implementation-req14-approval-gate-preanalysis-audit-run/preanalysis-audit-bundle.md`

使った criteria:

- `templates/review/main_preanalysis_sufficiency_audit_criteria_template.md`

実行:

- `--default-variant-for api_review_prompt_quality`
- adversarial: `claude-sonnet-4-6`
- judgment: `gemini-3.1-pro-preview`

結果:

- 2役とも parse 成功
- 両方 `sufficient_with_revisions`
- 合計 8 findings
- 共通して、source summary の原文対応不足と Check 5 の抑制的文言を指摘

## 実験で検出された問題

### 1. source summary の原文対応不足

source paths は provenance として置かれていたが、structured summary がどの requirements / design / tasks の箇所に対応するかが弱かった。

このため、reviewer が structured summary の漏れや歪みを検出しにくい。

対応:

- source_cross_references を追加
- requirements.md lines 238-255
- design.md lines 1788-1833
- design.md lines 2225-2236
- tasks.md lines 127-128
- anchors は provenance とし、hash をレビュー時に検証しないことも明示

### 2. Check 5 の抑制文言

誤検出を避けるために「workflow-operation code の mere presence を violation としない」と書いたが、これが繰り返されることで、重要な gate bypass まで見逃す方向に働く危険があった。

対応:

- mere presence だけで violation にしない、という限定は残す
- ただし、approval-gate behavior の omission / weakening / contradiction / bypass は積極的に検査すると明示
- proxy_model decision、non-approved decision、stale digest、missing binding、wrong actor/source が human-only boundary を満たしてしまう indirect path を見るよう追記

### 3. target 未注入時の severity

target path content が injected prompt にない場合、旧 criteria では ERROR としていた。

しかし target が欠けている review-run は実質無効であり、CRITICAL にすべきと指摘された。

対応:

- `report CRITICAL against Review Target and do not return findings: []` に変更

### 4. 禁止操作の severity anchor

commit / push / spec.json mutation / phase transition / gate completion は User Review Requirements や Out Of Scope にあったが、Finding Policy の severity mapping に明示されていなかった。

対応:

- これらを approve / delegate / imply authorization する model output or criteria は CRITICAL と明記

### 5. stale preanalysis

main preanalysis には「Req14 cannot be reviewed as one combined judgment」という finding が残っていた。

しかし approval gate bundle ではすでに split が適用済みだった。

このような stale finding は auditor を誤誘導する。

対応方針:

- preanalysis は仮説として扱う
- bundle 作成時に、resolved / still-open を区別する
- 今回は実装としては criteria 修正を優先し、preanalysis 本体の整理は残課題

## テスト結果の評価

今回の preanalysis sufficiency audit は、非常に有効だった。

理由は、実際にレビュー品質を歪める prompt 欠陥を検出したためである。

検出された欠陥は形式的なものではない。

- source summary の原文対応不足は、上流意図レビューの根拠を弱める
- Check 5 の抑制文言は、最重要の approval gate bypass 検出を鈍らせる
- target 未注入 severity の弱さは、無効な review-run を継続させる
- stale preanalysis は、reviewer を古い問題へ anchor する

したがって、この audit は「余裕があるときの高リスク対応」ではなく、APIレビュー品質を成立させるための標準ゲートとして扱うべきである。

前回、「高リスク条件でだけ発動」と評価したが、それは弱い。利用者指摘どおり、プロンプト監査はレビュー品質に大きく影響するため、ここにはコストをかけるべきである。

## コスト評価

この監査はコストがかかる。

- bundle 作成が重い
- source materials の選定と cross-reference が必要
- 2役 API を使うため時間と API コストがかかる
- findings 反映後に再レビューが必要になる

しかし、旧方式で `findings: []` を得て誤って gate 完了扱いするコストの方が大きい。

レビューの入口で prompt が歪んでいると、その後の raw / parsed / triage / proxy decision / implementation すべてが汚染される。

結論:

- prompt監査コストは、レビュー品質の保険ではなく、レビュー品質の本体コストである
- APIレビューを本線判断に使うなら、このコストは払うべきである
- ただし、手作業で毎回 bundle を作るのは持続不能なので、bundle generation と source cross-reference 生成は機械化対象である

## 標準手順としての位置づけ

今後の API review prompt 作成は、次を標準手順にする。

1. main preanalysis
2. preanalysis sufficiency audit
3. API review criteria draft
4. prompt quality review
5. 実 review-run
6. raw / parsed / model summary / triage
7. 必要なら proxy_model decision

preanalysis sufficiency audit は、main preanalysis を使う場合だけでなく、実質的にはほぼ常に必要になる可能性がある。

理由:

- main は必ず何らかの材料選択を行う
- source selection に漏れがあると prompt 全体が歪む
- 1 prompt 1 judgment の粒度判定もここで行う必要がある

## 移設済み項目

未実装の機械化項目と、既に実装済みの成果一覧は本メモから削除した。

未実装の後続作業は次の backlog plan に移した。

- `.reviewcompass/backlog/plans/plan-2026-06-23-api-review-run-hardening.yaml`
- `.reviewcompass/backlog/plans/plan-2026-06-23-proxy-decision-mechanization.yaml`

post-write verification 固有の prompt 機械化は、既存の次の plan で扱う。

- `.reviewcompass/backlog/plans/plan-2026-06-23-postwrite-prompt-mechanization-completion.yaml`

## 重要な反省

今回の議論では、ユーザから何度も「視点が狭い」「実装前に相談すべき」「無駄な時間とコストをかけている」と指摘された。

主な原因:

- 手作業で ad hoc に手順を組んだ
- 規律に書かれているのに、実際の prompt 作成時に読ませきれていなかった
- runner / variant / output contract を機械化せず、人間記憶に頼った
- 1つの prompt に複数判断を押し込んだ
- proxy_model の「ユーザが関与しない」前提を崩しかけた
- sandbox / API 実行経路の問題を、実装前に十分相談せずに進めた
- model 名の取り違えなど、機械設定で防げる混乱を起こした

これらは個別の注意で解消するより、workflow 上の preflight / effective prompt / runner selection / output contract validation として機械化するべきである。

## 結論

APIレビュー用プロンプト監査は、今回の議論を通じて標準ゲートに格上げすべきものと評価する。

理由:

1. 旧方式の `findings: []` が、実際には target / criteria 設計ミスによる偽陰性だった可能性が高い。
2. prompt quality review により、実 target を見る再レビューで C1〜C7 の設計課題が検出された。
3. preanalysis sufficiency audit により、source cross-reference 不足と抑制的文言という、実レビュー品質を直接歪める欠陥を検出できた。
4. main preanalysis は有用だが、仮説として扱わないと bias source になることが確認された。
5. 1 prompt 1 judgment、source materialization、target/source/out-of-scope separation は、レビュー品質の中核条件である。

したがって、API review-run に進む前には、main preanalysis と prompt audit に十分なコストをかけるべきである。

このコストはレビューの外側にある余分なコストではなく、レビューそのものの品質を確保するための必須コストである。
