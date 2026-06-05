# 今後開発検討すべき項目リスト

作成日：2026-06-05

## 0. 位置づけ

本メモは、ReviewCompass の implementation phase 完了後に、これまで作成した計画書、議論メモ、review-wave 記録、実装レビュー記録、TODO、learning/workflow 配下の配布用構造を調査し、今後開発検討すべき項目を整理したものである。

これは作業順序の正本ではない。通常ワークフロー上の正本は、引き続き `tools/check-workflow-action.py next --json` と各 feature の `spec.json` である。2026-06-05 時点の直近確認では `next_action.kind == "completed"` であり、通常ワークフロー上の未完了タスクはない。

本メモの目的は、次に何を開発・研究・運用改善として検討するかを、議論の出発点として一覧化することである。特に論文化に向けた次段階では、単一の自己適用事例を深掘りするだけでなく、ReviewCompass を安定して外部デプロイし、多くのケースから同じ形式のデータを取得し、分析できる状態を作ることを優先する。

## 1. 調査対象

主に次を確認した。

- `TODO_NEXT_SESSION.md`
- `docs/plan/reconstruction-plan-2026-05-21.md`
- `.reviewcompass/specs/_cross_feature/reviews/2026-06-04-implementation-phase-summary.md`
- `.reviewcompass/specs/_cross_feature/reviews/2026-06-04-implementation-review-wave.md`
- `.reviewcompass/specs/_cross_feature/reviews/2026-06-04-implementation-alignment.md`
- `docs/notes/2026-06-04-implementation-review-wave-improvements.md`
- `docs/notes/2026-06-03-agent-adapter-strategy.md`
- `docs/notes/2026-06-03-discipline-adapter-revision-candidates.md`
- `docs/notes/2026-06-03-dogfooding-deployment-metrics.md`
- `docs/notes/2026-06-05-workflow-navigator-webui-plan.md`
- `docs/notes/2026-05-31-item2-proxy-and-postwrite-verification-trial.md`
- `docs/notes/2026-05-30-section-5-12-revision-log.md`
- `docs/notes/2026-06-01-implementation-phase-approach.md`
- `docs/operations/WORKFLOW_PRECHECK.md`
- `docs/operations/SESSION_WORKFLOW_GUIDE.md`
- `docs/disciplines/discipline_implementation_autonomy.md`
- `AGENTS.md`
- `learning/workflow/` 配下の proposals / metrics / carry-forward register 関連 README
- implementation review-run の `triage.yaml` 群

## 2. 全体判断

現時点の次フェーズは「通常ワークフローの未完了処理」ではなく、「completed 後の追加改善・配布準備・研究データ化」である。

論文化に向けた主眼は、レビュー能力そのものをさらに増やすことよりも、安定したデプロイ、反復可能なデータ取得、分析パイプラインの確立に置く。ReviewCompass 自身で得た dogfooding 証跡は重要な初期事例だが、効果を論じるには、複数リポジトリ・複数タスク・複数 review-run で同じ測定設計を再現できる必要がある。

大きく分けると、検討項目は次の 9 群に整理できる。

1. 安定デプロイと外部展開 readiness
2. ケース横断のデータ取得・記録 schema
3. 取得データの分析パイプライン
4. TDD サイクルと修正効果の記録
5. Navigator WebUI と workflow 現在位置の可視化
6. side track / post-write / 復帰経路の機械化強化
7. review-wave / triage / evidence の機械化強化
8. proxy_model / 自律・並列実行の監査性強化
9. 規律・adapter・運用文書の整理と feature 個別 review-run で should-fix として残った品質改善

以下、項目ごとに、目的、背景、議論内容、検討すべき実装案を記録する。

## 3. 優先検討項目

### D-001 review-wave summary command の実装

優先度：高

目的：

review-wave の横断確認で使った指標を手動集計ではなく、機械的に生成できるようにする。

背景：

implementation review-wave では、feature coverage、triage completeness、recheck state、dependency status、carry-forward count が有効だった。一方で、これらの多くは手動で読み取り・記録した。今後同じ作業を繰り返すと、集計漏れや報告の揺れが起こりうる。

議論内容：

review-wave は単なる再レビューではなく、feature-local review の完了感を横断的に検査する gate として機能した。特に workflow-management の draft triage、evaluation の証跡配置ずれ、foundation の recheck pending を検出した点は大きい。この gate を安定運用するには、サマリ指標をコマンド化する必要がある。

検討する実装：

- `tools/check-workflow-action.py` または別 helper に `review-wave-summary` 相当のサブコマンドを追加する。
- 出力項目は、feature coverage、phase/stage 状態、triage unresolved count、draft count、human_required count、recheck state、dependency status、carry-forward unresolved count とする。
- 出力は Markdown と JSON の両方を検討する。
- `.reviewcompass/specs/_cross_feature/reviews/` に保存できる形式を用意する。

主な根拠：

- `docs/notes/2026-06-04-implementation-review-wave-improvements.md`
- `.reviewcompass/specs/_cross_feature/reviews/2026-06-04-implementation-phase-summary.md`

### D-002 recheck clearing criteria の正本化

優先度：高

目的：

`recheck.upstream_change_pending` をいつ解除してよいかを、明文化・機械化する。

背景：

foundation の recheck pending は review-wave を止めるブロッカーになった。今回の解除は、下流 implementation review evidence が揃ったことを確認し、利用者承認を得て進めた。しかし、今後も同型の upstream change が起こるため、解除基準を毎回手作業で判断すると揺れが残る。

議論内容：

recheck flag は、上流変更が downstream phase に影響しうることを示す安全側のフラグである。一方で、下流証跡が揃った後も残り続けると、完了判定を不必要に止める。重要なのは、解除そのものではなく、解除に必要な downstream evidence の種類と承認条件を正本化することである。

検討する実装：

- `stages/feature-dependency.yaml` と `spec.json.recheck` を突き合わせる検査を追加する。
- impacted phase ごとに必要な downstream evidence を定義する。
- `spec-set` で recheck を解除する場合に、根拠ファイルまたは approval record を要求する。
- review-wave summary に recheck clearing evidence を表示する。

主な根拠：

- `.reviewcompass/specs/_cross_feature/reviews/2026-06-04-implementation-review-wave.md`
- `docs/notes/2026-06-04-implementation-review-wave-improvements.md`

### D-003 feature-local API review-run pointer の一般化

優先度：高

目的：

API review-run の raw / parsed / triage 証跡が `docs/notes/review-runs/` にある場合でも、feature 側から安定して辿れるようにする。

背景：

evaluation の implementation review evidence は実体として存在していたが、`.reviewcompass/specs/evaluation/reviews/` にポインタがなかったため、review-wave で traceability concern になった。

議論内容：

証跡は「存在する」だけでは不十分である。後続の review-wave や論文用分析で再利用するには、feature namespace から機械的に辿れる必要がある。生証跡を移動せず、feature-local pointer を置く方式は、証跡の保存場所と workflow evidence namespace を分離できる。

検討する実装：

- API review-run を phase evidence として使う場合の pointer template を定義する。
- pointer に run path、purpose、triage_status、items count、decision status、raw / parsed / summary / triage の存在確認を含める。
- `next` または review-wave summary で pointer 欠落を検出する。
- 新規 API review-run 作成時に feature-local pointer 生成を補助する。

主な根拠：

- `.reviewcompass/specs/evaluation/reviews/2026-06-03-implementation-triad-review.md`
- `docs/notes/2026-06-04-implementation-review-wave-improvements.md`

### D-004 normalized finding schema の設計

優先度：高

目的：

Markdown review と API review-run の findings を同じ分析軸で比較できるようにする。

背景：

implementation phase summary では、foundation / runtime の Markdown 記録と、analysis / workflow-management / self-improvement / conformance-evaluation の構造化 triage で、集計可能性に差があった。論文用データとして扱うには、所見の単位、ラベル、根拠、修正状態を揃える必要がある。

議論内容：

三段階 triage は有効だったが、feature 間で所見粒度や severity の扱いが完全には標準化されていない。review の価値を定量化するには、各 finding がどの観点に属し、どの証拠に基づき、どう判定され、どの commit で直ったかを追跡できる必要がある。

検討する実装：

候補フィールドは次のとおりである。

- `finding_id`
- `source_model`
- `review_role`
- `inspection_criterion`
- `severity`
- `initial_recommendation`
- `final_label`
- `decision_status`
- `decision_actor`
- `observed_at`
- `decided_at`
- `resolved_at`
- `evidence_refs`
- `affected_files`
- `resolution`
- `resolution_commit`
- `false_positive_reversal`

これらを持つ schema を設計する。

D-004 着手時には、各 field の type、required / optional、許容値、一意性、時刻形式、相互参照先を schema comparison table に含める。特に `finding_id` の一意性、`severity` / `final_label` の列挙値、`observed_at` / `decided_at` / `resolved_at` の時刻形式、`evidence_refs` / `resolution_commit` / `linked` 系参照の解決可能性を最低契約として扱う。

実装前には、既存の `learning/workflow/schemas/` 配下の schema と重複・衝突しないかを確認する。最低限の確認対象は、`proposal.schema.json`、`metrics.schema.json`、`carry-forward-register.schema.json`、`rollback.schema.json`、`README.md` と、既存 review-run の `triage.yaml` 構造とする。特に proposal / metrics / carry-forward register の既存 field policy、rollback schema が扱う戻し操作の記録、triage.yaml が持つ finding 相当 field と、finding schema が扱う decision / evidence / resolution の責務境界を整理する。

この確認は現時点では未実施であり、D-004 着手時の design note または schema comparison table に結果を記録する。少なくとも `decision_status`、`decision_actor`、`observed_at`、`decided_at`、`resolved_at`、`evidence_refs`、`resolution_commit`、`false_positive_reversal` が既存 schema のどの field と重なるか、どの field を finding schema 固有に残すかを明示する。

主な根拠：

- `.reviewcompass/specs/_cross_feature/reviews/2026-06-04-implementation-phase-summary.md`
- `learning/workflow/schemas/` 配下の既存 schema 群

### D-005 finding-to-fix traceability の強化

優先度：高

目的：

accepted finding がどのテスト、どの変更ファイル、どの commit で解消されたかを追跡できるようにする。

背景：

implementation phase では、多数の must-fix / should-fix が修正されたが、論文用分析や監査では、finding と修正 commit の対応が機械的に取れる必要がある。

議論内容：

LLM レビューの効果を測るには、「指摘が出た」だけでなく、「その指摘がどのような修正へ変換されたか」が必要である。修正追跡性があれば、検出率だけでなく修正コスト、テスト追加率、再発率も見られる。

検討する実装：

- triage item に `resolution_commit`、`test_refs`、`changed_files` を追加する。
- commit message または commit approval record に finding IDs を含める。
- review report 生成時に finding-to-commit matrix を出す。
- dogfooding metrics extractor が修正追跡性を集計できるようにする。

主な根拠：

- `docs/notes/2026-06-03-dogfooding-deployment-metrics.md`
- `.reviewcompass/specs/_cross_feature/reviews/2026-06-04-implementation-phase-summary.md`

### D-025 TDD cycle evidence の正本化

優先度：高

目的：

TDD が実装品質とレビュー指摘の修正にどの程度寄与したかを、論文用データとして追跡できるようにする。

背景：

今回の実装フェーズでは、TDD は実践上うまく機能した。`AGENTS.md`、`WORKFLOW_PRECHECK.md`、`SESSION_WORKFLOW_GUIDE.md`、`discipline_implementation_autonomy.md`、implementation approach note には、テスト先行、失敗確認、実装、全テスト green という手順が明記されている。一方で、これは主に入口規律・運用ガイド・作業メモとして記録されており、workflow requirements や論文用 event schema の中核契約としてはまだ十分に構造化されていない。

議論内容：

TDD は単なる開発スタイルではなく、LLM review と組み合わせたときに「指摘がテストへ変換され、実装で green になった」ことを示す重要な証跡である。レビューの効果を論じるには、finding が出たことだけでなく、どの finding が failing test を生み、どの commit で green になり、その後の review-wave / post-write verification で再発しなかったかを追える必要がある。

これは SDD を TDD で置き換えるという意味ではない。ReviewCompass では、意図、責務、依存関係、証跡構造、承認境界のように論理的に見通せる部分は SDD で先に整理する。一方で、CLI 入出力、guard の失敗条件、schema validation の境界値、複合エラー、実ファイル配置、例外メッセージのように、実際にテストを書くことで初めて曖昧さが減る部分がある。今回の実装では、SDD で構造を定め、TDD で実行可能性と境界条件を具体化する併用が有効だった。

検討する実装：

- implementation drafting の完了条件に TDD cycle evidence を含めるか検討する。
- event ledger に `tdd_cycle` event type を追加する。
- `test_first_commit`、`implementation_commit`、`failing_test_command`、`failing_test_result`、`green_test_command`、`green_test_result`、`linked_finding_ids`、`changed_files` を記録する。
- finding-to-fix traceability と連携し、review finding から test addition / implementation / verification までを matrix 化する。
- 論文用メトリクスとして、テスト先行率、red-to-green cycle count、finding-to-test conversion count、review 指摘後の回帰防止率を集計する。

主な根拠：

- `AGENTS.md`
- `docs/operations/WORKFLOW_PRECHECK.md`
- `docs/operations/SESSION_WORKFLOW_GUIDE.md`
- `docs/disciplines/discipline_implementation_autonomy.md`
- `docs/notes/2026-06-01-implementation-phase-approach.md`

### D-026 ReviewCompass Navigator WebUI の設計・試作

優先度：中

目的：

ReviewCompass の機械判定済み workflow 状態を、人間が一目で把握できる WebUI として可視化する。現在位置、標準ルート、内側工程、根拠、次 action、復帰点をグラフィックで表示し、将来の独立アプリ化の入口にする。

背景：

複雑な workflow では、プロセス全体における現在位置が分からなくなりやすい。一方、ReviewCompass は `workflow_state`、`next --json`、post-write manifest、reopen in-progress file などにより、現在位置を機械判定できる。この情報を UI で視覚化できれば、全体計画と進捗をリアルタイムに近い形で把握できる。

議論内容：

WebUI は ReviewCompass 本体の内部ファイルを場当たり的に読むのではなく、ReviewCompass Core が出力する workflow-state snapshot を読む。UI は状態正本にならず、状態判定は Core 側に残す。開発対象アプリによって機能軸・工程軸が異なるため、Navigator は固定段階名ではなく、任意の nodes / edges / lanes / status / evidence refs を描画できる汎用ビューアとして設計する。

名称は Atlas ではなく Navigator とする。目的は地図帳のような静的俯瞰ではなく、現在位置、次に進む方向、side track からの復帰点を示すことだからである。外側 workflow と内側 workflow の二層構造を明示し、標準ルートと実際の状態、例外的進行、復帰経路を同時に表示する。

詳細計画：

- 独立計画メモ：`docs/notes/2026-06-05-workflow-navigator-webui-plan.md`

検討する実装：

- `workflow-state` snapshot schema を設計する。
- snapshot に outer / inner workflow、current node、lanes、evidence refs、git state、active side track、return_to を含める。
- 初期 WebUI は静的 Navigator とし、snapshot を読み込んで React + SVG 等で描画する。
- グラフィックは Subway Map と System Monitor の混合を目指し、current / completed / waiting / blocked / deviation / side_track を色と形で区別する。
- 右ペインに選択ノードの根拠、ログ、次 action、関連ファイルを表示する。
- 将来拡張として LLM 対話ペイン、ログ保持、live reload、manifest 生成補助、branch / worktree 分離補助を検討する。

主な根拠：

- `docs/notes/2026-06-05-workflow-navigator-webui-plan.md`
- `docs/notes/2026-06-02-workflow-navigation-implementation-plan.md`
- `docs/disciplines/discipline_workflow_state_truth_source.md`

### D-027 side track / BTW Track の状態モデル化

優先度：高

目的：

正規 workflow の途中で例外的な文書修正、post-write verification、sandbox 試行、補助作業が発生した場合に、それを side track として機械判定・可視化し、完了後に元の workflow へ復帰できるようにする。

背景：

既存の post-write-verification は、正規 workflow 外の正本文書書き込みを検出し、通常 workflow より優先して検証へ入り、manifest 完了後に通常 workflow へ戻る仕組みを持つ。これは、ユーザが LLM に例外的な作業を指示しても、状態から復帰点を一意に再構成できるという ReviewCompass の強みの原型である。

議論内容：

side track は「脱線」ではなく、作業を止めずに一時分岐する状態である。UI 上では BTW Track として見せてもよい。重要なのは、標準ルート、実際の git tree、対象変更、manifest 状態、禁止変更、復帰先を同時に扱うことである。

同一 worktree で扱える小さい side track と、別 branch / worktree に分離すべき大きい side track は区別する。初期実装では branch / worktree 自動分離までは行わず、git diff、post-write 対象、manifest coverage、非対象変更を状態として表示・判定する。

検討する実装：

- workflow-state snapshot に `active_track`、`track_kind`、`return_to`、`target_files`、`manifest_status`、`policy_violations`、`required_action` を追加する。
- post-write-verification pending 中の状態を side track として正規化する。
- `git_state` として dirty / clean、target changes、non-target changes、blocked changes を出力する。
- side track 中の許可操作と禁止操作を、D-009 / post-write verification policy と接続して整理する。
- sandbox を使った TDD 仕様探索も、必要に応じて side track または inner workflow の探索ループとして表現できるようにする。
- Navigator WebUI では Main Track と Side Track を同時表示し、復帰先を明示する。

主な根拠：

- `docs/notes/2026-06-05-workflow-navigator-webui-plan.md`
- `docs/notes/2026-06-02-workflow-navigation-implementation-plan.md`
- `docs/disciplines/discipline_post_write_verification.md`

### D-006 proxy_model decision auditability の強化

優先度：高

目的：

proxy_model による判断代行が、raw response、候補案、採用案、判断理由、最終ラベルまで改変検出可能に追跡できるようにする。

背景：

proxy_model は自律実行の実用性を上げた。一方で、判断代行は証跡が弱いと危険である。workflow-management review では、decision file と raw response の sha256 照合、triage.yaml との相互参照が should-fix / must-fix として繰り返し問題になった。

議論内容：

proxy_model 判断は、人間承認の代替ではなく、証跡を伴う限定的な判断代行である。したがって、どの raw を読んで、どの候補から何を採用し、なぜその final_label になったかが、後から再構成できなければならない。

検討する実装：

- decision file に source raw path と raw sha256 を必須化する。
- triage.yaml / rounds.yaml 側の raw_sha256 と照合する。
- approval record に proxy_model_id、decision file path、approved finding IDs を含める。
- decision file と raw の不一致時は fail-closed にする。

主な根拠：

- `.reviewcompass/specs/workflow-management/reviews/2026-06-04-workflow-management-implementation-review-run/triage.yaml`
- `.reviewcompass/specs/_cross_feature/reviews/2026-06-04-implementation-phase-summary.md`

### D-007 自律・並列実行 ledger の強化

優先度：高

目的：

自律・並列実行の計画、担当、判断根拠、統合結果を、会話ログに頼らず監査できるようにする。

背景：

review-wave では自律・並列の読取専用 evidence collection が有効だった。一方で、workflow-management / self-improvement の review では、ledger が計画時点の task ID や設定だけを残し、各 task の実行結果・担当別判断根拠・統合結果が不足するリスクが指摘された。

議論内容：

自律・並列実行で最も危険なのは、並列に進めた後で、何を根拠に統合判断したかが曖昧になることである。安全な並列化は、まず読取専用証跡収集に限定し、統合判断では依存関係と raw / triage / decision evidence を確認する必要がある。

検討する実装：

- ledger schema に `task_result`、`decision_basis_refs`、`raw_refs`、`triage_refs`、`proxy_decision_refs`、`integration_result` を追加する。
- `autonomous-plan` / ledger guard で必須 field を検査する。
- allowed_paths overlap と依存 DAG 上の並列可能性を検査する。
- 実装 diff を並列に作る場合は、統合前に main session review を必須化する。検査候補は ledger guard または pre-integration check とし、統合前に `integration_result`、対象 diff refs、main session review refs が欠落していないことを確認する。

主な根拠：

- `docs/logs/autonomous-parallel/`
- `.reviewcompass/specs/workflow-management/reviews/2026-06-04-workflow-management-implementation-review-run/triage.yaml`
- `.reviewcompass/specs/_cross_feature/reviews/2026-06-04-implementation-phase-summary.md`

### D-008 dogfooding event ledger と論文用メトリクスの本格化

優先度：高

目的：

運用記録を論文用データへ正規化し、ReviewCompass の効果を測定できるようにする。

背景：

既に `evaluation/metrics/dogfooding_metrics_extractor.py` に最小抽出器があるが、本格分析ではない。dogfooding deployment metrics note では、専用 event ledger へ正規化するかをデプロイ時に判断するとしている。

議論内容：

実装フェーズのレポートでは、triad-review、review-wave、post-write verification、commit guard などが実際にプロセス欠陥を止めた証拠がある。しかし論文にするには、個別事例だけでなく、時系列のイベントとして抽出できる必要がある。

検討する実装：

- dogfooding event ledger schema を設計する。
- event type として review_run、triage_decision、proxy_decision、workflow_precheck、post_write_verification、reopen、commit_guard、push_guard を定義する。
- 指標として、上流 reopen 件数、手戻り深さ、遮断された workflow check、post-write 所見、triage 結果、修正追跡性、検証コストを扱う。
- analysis 機能が読み取れる出力形式にする。

主な根拠：

- `docs/notes/2026-06-03-dogfooding-deployment-metrics.md`
- `learning/workflow/metrics/README.md`

## 4. 中優先度の検討項目

### D-009 post-write verification の収束基準の再検討

優先度：中

目的：

実質的な誤りと逐語・好みレベルの指摘を切り分け、収束しない検証ループを避ける。

背景：

proxy mode と post-write verification の試行では、2 系統が ALL_CLEAR でも 1 系統が逐語的・検証可能性レベルの指摘を出し続ける挙動が観察された。

議論内容：

post-write verification の価値は、起草者が見落とす実質誤りを捕捉する点にある。一方で、表現の好みや逐語的な差分で収束不能になると、運用コストが上がる。現在は逐語的指摘と本質的指摘の切り分けが規律化されているが、実運用データを使って収束基準をさらに調整する余地がある。

今回の future-development-candidates memo では、候補リストに対して、後半の post-write verification が各候補の完了条件、schema field の型、担当、受入基準まで求め始め、検討メモの確認範囲を越えた。これは文書種別ごとの検証強度が足りないことを示している。discussion note / candidate list では、明白な矛盾、数の不一致、参照切れ、明示合意との衝突、意味を変える重大な脱落を主対象にし、詳細設計・完了条件・schema field 型・担当・テスト計画の要求は原則 `leave-as-is` として扱う。

D-010 の各社モデル向け作業入口 adapter 化は `docs/disciplines/` の変更を含むため、実施時に post-write verification が必要になる。したがって、D-009 は D-010 の完全な前提ではないが、D-010 の本文変更に入る前に先行確認すると検証ループの扱いが安定する。

検討する実装：

- 文書種別ごとに post-write verification の検査強度を分ける。候補は `discussion_note`、`candidate_list`、`plan`、`task_proposal`、`spec`、`contract`、`schema`、`operation`、`discipline` とする。
- `discussion_note` / `candidate_list` では、詳細設計要求や受入条件要求を原則 `leave-as-is` に分類する。
- `spec` / `contract` / `schema` では、型、必須性、列挙値、検査方法まで確認対象に含める。
- `operation` / `discipline` では、停止条件、承認ゲート、例外処理、実行手順の不足を確認対象に含める。
- 多数決的収束、深刻度フィルタ、繰り返し指摘の扱いを再評価する。
- 検証プロンプトで「実質誤りのみ報告」をより明示する。
- triage に literal / substantive classification を保存する。
- triage に document_type / verification_level を保存し、同じ所見でも文書種別に応じて `should-fix` と `leave-as-is` の境界を変えられるようにする。
- post-write metrics と連動して、収束ループ回数を記録する。

再現条件は D-009 着手時に、対象 prompt、variant、model assignment、raw response path を含む検討メモとして記録する。baseline input は、`docs/notes/2026-05-31-item2-proxy-and-postwrite-verification-trial.md` と、post-write verification の実行履歴が残る `docs/notes/review-runs/` 配下の関連 run とする。D-009 着手前に baseline locator を作成し、少なくとも参照する note、candidate review-run directory、variant、role assignment、raw response paths の候補を列挙する。

主な根拠：

- `docs/notes/2026-05-31-item2-proxy-and-postwrite-verification-trial.md`

### D-010 各社モデル向け作業入口 adapter 化改訂

優先度：中

目的：

Claude Code 固定の説明や workflow_state 直接 Read 前提を、Codex / Claude / Gemini など複数社・複数環境の作業入口に対応する adapter 表現へ改める。

背景：

Codex adapter migration 以後、実行環境、sandbox、approval、hook adapter の扱いが変わった。既存規律には Claude Code 前提の記述が残っている。一方で、将来は Claude、Codex、Gemini など複数社・複数環境のモデルで ReviewCompass を運用できるようにしたい。

議論内容：

規律を単に Codex 用へ置き換えるのではなく、共通原則と実行環境固有の adapter を分離する必要がある。Claude adapter には Claude Code 固有の memory、hook、Agent / Task ツール、permission 設定を閉じ込める。Codex adapter には sandbox、approval、network 制限、git directive、repo 外 memory を前提にしない運用を書く。Gemini など将来の作業環境についても、同じ共通正本を読み、環境固有の入口手順と制約だけを adapter として追加できる構造にする。

また、作業順序は `workflow_state` 直接 Read ではなく `next --json` を入口にする方が、post-write / maintenance / reopen を見落としにくい。モデルをレビュー対象として使う場合の model assignment と、モデルをメイン作業セッションとして使う場合の agent adapter は分けて扱う。

検討する対象：

- `discipline_workflow_state_truth_source.md`
- `discipline_workflow_precheck_invocation.md`
- `discipline_pre_action_precheck.md`
- `discipline_avoid_compound_bash.md`
- `docs/operations/WORKFLOW_NAVIGATION_FOR_CLAUDE.md`
- `docs/operations/WORKFLOW_NAVIGATION_FOR_CODEX.md`
- Gemini 等の将来 adapter を置く文書構造

主な根拠：

- `docs/notes/2026-06-03-agent-adapter-strategy.md`
- `docs/notes/2026-06-03-discipline-adapter-revision-candidates.md`

### D-011 proxy assignment のモデル選定と外形指標チューニング

優先度：中

目的：

proxy assignment の発火条件、モデル割当、深掘り対話の方式を dogfooding 結果に基づいて調整する。

背景：

§5.12 改訂ログでは、外形指標の重み・閾値、アサイン先モデル、標準裁定 3 系統への深掘りか追加独立モデルかが観察課題として残っている。

議論内容：

自己申告 confidence は過信が多いため使わず、割れ・別案・僅差・質問返しといった外形指標を使う方針は妥当だった。一方で、各指標の重みや、割れを二値にするか連続値にするかは、実運用で調整すべきである。

検討する実装：

- proxy assignment scoring の実データを保存する。
- 外形指標ごとの寄与を decision record に保存する。
- GPT / Claude / Gemini の役割分担を実績に基づいて再評価する。
- 膠着時に追加独立モデルを呼ぶ設定を検証する。

主な根拠：

- `docs/notes/2026-05-30-section-5-12-revision-log.md`
- `docs/notes/2026-05-25-triad-review-model-allocation-experiment.md`

### D-012 review record / human explanation の説明品質強化

優先度：中

目的：

レビュー結果や proxy decision を、人間が判断できる平易な説明として常に提示・保存できるようにする。

背景：

§5.12 改訂ログでは、actor_chain だけでは「なぜその結論に至ったか」が十分に再構成できないとされ、`human_explanation` の必要性が議論された。実装フェーズ中にも、利用者から「平易に説明して」「モデル割当や variant を提示すべき」といった指摘があった。

議論内容：

raw response や構造化 YAML は監査には必要だが、人間の承認判断には不十分である。どのモデルが何を言い、どこで割れ、どの案が採用・棄却されたかを平易に説明する層が必要である。

検討する実装：

- review report 生成に `human_explanation` セクションを必須化する。
- variant、role assignment、model IDs、raw paths、triage 三分類を自動表示する。
- approval gate 前に提示すべき情報を machine-check する。

主な根拠：

- `docs/notes/2026-05-30-section-5-12-revision-log.md`
- `docs/operations/WORKFLOW_NAVIGATION.md`

### D-013 triage important item 判定の拡張

優先度：中

目的：

severity や must-fix label だけでなく、文脈上重要な should-fix を見落とさないようにする。

背景：

workflow-management review では、`_is_important_item` が CRITICAL / ERROR / must-fix だけを重要扱いし、文脈上重要な should-fix を機械的に見落とす可能性が指摘された。

議論内容：

運用上、should-fix でも、承認証跡、raw response 真正性、並列実行 ledger などに関わるものは重要度が高い。単純な label ベースの判定は扱いやすいが、安全側に倒すには context signal も必要である。

検討する実装：

- important 判定に `requires_approval`、`affects_auditability`、`affects_raw_integrity` などの構造化 flag を導入する。
- should-fix でも特定 flag が立つ場合は利用者提示 gate を要求する。
- triage parser / proxy decision prompt に flag 付与を求める。

主な根拠：

- `.reviewcompass/specs/workflow-management/reviews/2026-06-04-workflow-management-implementation-review-run/triage.yaml`

### D-014 commit / push guard の複合失敗テスト強化

優先度：中

目的：

commit approval 不備と post-write manifest 不備など、複数の遮断理由が同時にある場合の表示・検査を強化する。

背景：

workflow-management review では、missing approval record と missing post-write manifest の複合ケースをテストしていないことが should-fix として残った。

議論内容：

不可逆操作 gate は、最初に見つけた理由だけで止めるより、利用者が次に何を直せばよいか分かるように、複数理由を明確に提示する方が実用的である。

検討する実装：

- commit precheck の複合エラーケースを追加する。
- approval failure と post-write failure の reason を両方出す。
- push precheck でも同型ケースを確認する。

主な根拠：

- `.reviewcompass/specs/workflow-management/reviews/2026-06-04-workflow-management-implementation-review-run/triage.yaml`

## 5. feature 個別の品質改善候補

### D-015 analysis の downstream 安定性・境界検査強化

優先度：中

目的：

analysis の下流成果物が、空ケース、除外ケース、境界ケースでも安定して読めるようにする。

背景：

analysis implementation review では、should-fix として、caveat register の常時生成、structured artifact_ref の利用、write path 境界検査、staleness entry の扱い、invalid / analysis_blocked evidence の exclusion report 化、追加のみ検査などが残った。

議論内容：

analysis は downstream reader に渡す成果物を作る役割を持つため、ファイルが存在しない、参照形式が揺れる、除外理由が silent drop されると、後続の論文用分析や監査で再現性が落ちる。

検討する実装：

- caveat register を空でも生成する。
- hardcoded path を structured artifact_ref へ置き換える。
- non-interference test を文字列検査ではなく write path 境界検査へ寄せる。
- stale false でも timestamp 更新があれば dependency source として扱う。
- invalid / analysis_blocked evidence を silent drop せず exclusion report に残す。
- caveat_register の append-only をより厳密に検査する。

主な根拠：

- `.reviewcompass/specs/analysis/reviews/2026-06-03-implementation-review-run/triage.yaml`

### D-016 conformance-evaluation のテスト網羅強化

優先度：中

目的：

conformance-evaluation の境界値、任意分岐、traceability 検査を強くし、将来退行を見逃しにくくする。

背景：

conformance-evaluation implementation review では、採番境界、`--check-partitioning` enabled branch、運用文書の説明ずれ、traceability 双方向整合 smoke の弱さが should-fix として残った。

議論内容：

現状の指摘は中核契約の即時破壊ではないが、検証の薄さに関わる。完了後の品質改善として、境界値と肯定分岐を押さえておく価値が高い。

検討する実装：

- `CF-999 -> CF-1000` の counter transition をテストする。
- `--check-partitioning enabled` の肯定確認テストを追加する。
- 運用文書で intent / tasks が自動推定対象のように見える記述を修正する。
- traceability smoke を双方向整合の実効検査へ強化する。

主な根拠：

- `.reviewcompass/specs/conformance-evaluation/reviews/2026-06-04-conformance-evaluation-implementation-review-run/triage.yaml`

### D-017 self-improvement の拒否語彙・authorization snapshot 強化

優先度：中

目的：

承認・却下判断の語彙と、自律実行時の承認証跡をより監査可能にする。

背景：

self-improvement implementation review では、拒否語彙の正本化と autonomous ledger の authorization snapshot 監査性が should-fix として残った。一部は即時対応されたが、ledger / schema / workflow guard の強化課題は残る。

議論内容：

承認語彙だけでなく却下語彙も明確でないと、否定形を含む発言の扱いが揺れる。また、authorization snapshot が会話参照だけに依存すると、後から承認根拠を機械的に検査しにくい。

検討する実装：

- 承認語彙と対称な拒否語彙を、運用語彙として明確化する。
- English `reject` の扱い、日本語の自然な拒否表現、否定形優先のルールを整理する。
- autonomous ledger に authorization snapshot を保存し、会話参照に依存しないようにする。
- ledger schema / guard で snapshot 欠落を検出する。

主な根拠：

- `.reviewcompass/specs/self-improvement/reviews/2026-06-04-self-improvement-implementation-review-run/triage.yaml`

## 6. 研究評価・外部展開の検討項目

### D-018 false-positive reversal の明示記録

優先度：中

目的：

triad-review が誤指摘をどれだけ除去したかを測れるようにする。

背景：

foundation / runtime では、主役レビューの ERROR / WARN が敵対役・判定役により覆された。これは複数 LLM レビューの precision 向上を示す重要な事例である。

議論内容：

複数 LLM レビューの価値を「所見数」だけで測ると、誤指摘を止めた効果が見えない。false-positive reversal を明示記録すれば、敵対役・判定役の precision 面の貢献を評価できる。

検討する実装：

- triage item に `counter_evidence_raised`、`false_positive_reversal`、`reversal_reason` を追加する。
- review summary に reversal count を出す。
- dogfooding metrics に false-positive reversal rate を追加する。

主な根拠：

- `.reviewcompass/specs/foundation/reviews/2026-06-01-implementation-triad-review.md`
- `.reviewcompass/specs/runtime/reviews/2026-06-02-implementation-triad-review.md`
- `.reviewcompass/specs/_cross_feature/reviews/2026-06-04-implementation-phase-summary.md`

### D-019 時間・コスト・モデル割当の記録

優先度：中

目的：

モデル別・役割別の費用対効果を分析できるようにする。

背景：

triad-review model allocation experiment では、モデル多様化だけでなく、どの役にどの能力が必要かが課題として残った。論文用には、指摘品質だけでなく、実行時間・コスト・収束までの回数も重要である。

議論内容：

モデル割当は品質だけでなく費用・時間との tradeoff で決まる。role assignment ごとの貢献を測れなければ、3 系統レビューや追加独立モデルの費用対効果を評価しにくい。

検討する実装：

- review-run に elapsed time、token usage、API cost、retry count を保存する。
- role assignment と検出・反証・判定の貢献を集計する。
- モデル割当を config と結果の両方から分析できるようにする。

主な根拠：

- `docs/notes/2026-05-25-triad-review-model-allocation-experiment.md`
- `.reviewcompass/specs/_cross_feature/reviews/2026-06-04-implementation-phase-summary.md`

### D-020 cross-repository replication

優先度：高

目的：

ReviewCompass 内 dogfooding の単一事例から、複数リポジトリでの比較評価へ進める。

背景：

implementation phase summary は「instrumented case study」として有用だが、統制群や複数事例はまだない。論文として効果を主張するには、異なるコードベースやタスクへの適用が必要になる。

議論内容：

ReviewCompass 内 dogfooding は濃い証跡を提供するが、単一事例である。外部化・配布を見据えるなら、project-independent な入力形式と adapter checklist を整備し、別リポジトリで同じ指標を再現できるかを確認する必要がある。

D-020 は D-021 の deployment readiness を前提にする。D-021 は「配置できるか」を確認し、D-020 は「配置後に複数ケースで比較可能なデータを取れるか」を確認する。重複する adapter checklist や same-schema metrics は、D-021 の readiness report から D-020 の replication plan へ引き継ぐ。

検討する実装：

- carry-forward register と workflow state input を project-independent にする。
- feature partitioning / requirements / design / tasks / implementation の最小テンプレートを切り出す。
- 別リポジトリ適用時の adapter checklist を作る。
- 指標を同じ schema で比較する。
- 最小実施単位は、少なくとも 2 つの外部リポジトリ、各 1 つ以上の実装タスク、各 1 件以上の review-run / triage / fix / test evidence を含む pilot とする。
- 比較対象リポジトリは、言語・規模・既存テスト有無・仕様文書の有無を記録し、ReviewCompass が対象アプリ側に配置できることを D-021 で確認済みのものから選ぶ。
- 成功条件は、同一 schema で event / finding / TDD cycle / cost / model assignment を取得でき、analysis 側で同じ集計表へ取り込めることとする。検証は D-020 pilot report が担当し、各対象リポジトリについて deployment smoke、data acquisition run、analysis import の 3 結果を記録する。

主な根拠：

- `learning/workflow/carry-forward-register/README.md`
- `learning/workflow/proposals/README.md`
- `learning/workflow/metrics/README.md`

## 7. 再構築計画からの追加検討項目

### D-021 deployable reconstruction readiness の再点検

優先度：高

目的：

ReviewCompass が「自己適用で動いた仕組み」ではなく、「外部リポジトリへ安定して配置し、複数ケースから研究用データを取得できる仕組み」になっているかを点検する。

背景：

`docs/plan/reconstruction-plan-2026-05-21.md` は、旧リポジトリが自己適用前提で複雑化したことを受け、ReviewCompass をデプロイ可能な独立成果物として再構築する方針を定めていた。implementation phase は ReviewCompass 自身を対象に完了したが、外部対象アプリでの配置可能性、複数ケースでのデータ取得可能性、取得データの分析可能性はまだ別途確認が必要である。

議論内容：

再構築計画の中心は、単に機能を移すことではなく、自己適用前提の歪みを取り除くことだった。現在の completed 判定は ReviewCompass 内の workflow 完了を示すが、対象アプリの任意の場所に置いて動くか、対象アプリ側とツール側の責務分離が保たれているか、同じ測定設計でケースを増やせるかは、別の readiness として扱う必要がある。

論文化の観点では、D-021 は単なる配布前点検ではなく、以後の D-004 / D-005 / D-008 / D-019 / D-020 を成立させる前提である。デプロイが不安定であれば、データ取得は偏り、分析結果の再現性も弱くなる。

検討する実装：

- 外部サンプルリポジトリまたは最小 fixture を使った deployment smoke を用意する。
- `.reviewcompass/specs/`、設定、テンプレート、review-run 出力が対象アプリ側とツール側に正しく分かれるかを確認する。
- `reviewcompass` 相当の CLI 経路で、対象アプリ root を明示して処理できるかを検査する。
- review-run、triage、decision、fix、cost、elapsed time、model assignment を同じ形式で取得できるかを deployment smoke に含める。
- deployment readiness report と data acquisition readiness report を生成し、self-dogfooding completed とは別の状態として記録する。

主な根拠：

- `docs/plan/reconstruction-plan-2026-05-21.md`

### D-022 抽出と再構築の分離原則の監査

優先度：中

目的：

旧素材リポジトリ由来の記述や自己適用前提が、ReviewCompass の正本文書・規律・テンプレートへ混入していないかを確認する。

背景：

再構築計画では、旧リポジトリを素材として保全し、新リポジトリ ReviewCompass へは知見だけを抽出して設計し直す方針が示されていた。コードや構造の機械的移植ではなく、自己適用前提の表現を一般化することが重要だった。

議論内容：

実装が進むほど、旧名、旧パス、旧プロジェクト前提の文言が残っていても見えにくくなる。とくに docs / disciplines / templates / config に残る具体パスや旧名称は、外部展開時の誤解につながる。

検討する実装：

- 旧プロジェクト名、旧パス、自己適用前提語彙の grep 監査を追加する。
- 監査結果を `docs/operations/` または `docs/notes/` に定期記録する。
- 許容される外部参照は URL またはコミットハッシュとして明示し、ローカルパス参照と区別する。
- 正本文書・規律・テンプレートの責務を「素材由来」「ReviewCompass 正本」「対象アプリ側配置物」に分類する。

主な根拠：

- `docs/plan/reconstruction-plan-2026-05-21.md`

### D-023 相対リンク・配置非依存性の機械検査

優先度：中

目的：

ReviewCompass の文書・設定・スキーマ・テンプレートが、配置先ディレクトリに依存しない参照だけで構成されているかを検査する。

背景：

再構築計画では、ReviewCompass は対象アプリの任意の場所にデプロイされる前提のため、絶対パスや特定作業ディレクトリ前提のパスを禁止していた。現在の post-write manifest や review-run 記録では相対パスを主に使っているが、全体監査としての検査は独立項目にしておく価値がある。

議論内容：

相対リンク方針は表記の好みではなく、デプロイ可能性の条件である。自己適用中は `/Users/...` のようなパスが会話や一時ファイルに現れても作業できるが、成果物に混入すると外部展開時に破綻する。

検討する実装：

- 成果物対象ディレクトリに対する absolute path lint を追加する。
- Markdown link、YAML path、JSON path、manifest path を対象にする。
- 例外として許容する外部 URL と一時監査ファイルを明示的に分ける。
- commit / push guard で配置非依存性違反を警告または遮断できるようにする。

主な根拠：

- `docs/plan/reconstruction-plan-2026-05-21.md`

### D-024 フェーズ 4 後の宿題 backlog の再整理

優先度：中

目的：

再構築計画で意図的にスコープ外とした項目を、completed 後の開発候補として再評価する。

背景：

再構築計画では、self-improvement の prompt / policy / schema / runtime の 4 層改善、多層防御の第 2 から第 5 層、API 経路の本格化、3 方式比較データなどを、段階的に後回しにした。implementation phase 完了後は、これらを「忘れた宿題」ではなく、改めて優先順位を付ける対象に戻す必要がある。

議論内容：

当時スコープ外にした理由は、不要だからではなく、効果測定機構や基本 workflow が未成熟だったからである。現在は review-run、triage、post-write verification、dogfooding metrics の土台ができたため、どれを次に取り込むかを再判断できる。

検討する実装：

- self-improvement 他 4 層を、prompt / policy / schema / runtime ごとに小さな提案へ分割する。
- 多層防御の第 2 から第 5 層を、git hook、利用者監査、定期事後監査、処理表面積抑制として再評価する。
- 3 方式比較データを manual / subagent / runtime-mediated の軸で保存できるか確認する。
- 既存の D-008 / D-011 / D-019 と重複しないように、event type、schema field、測定対象、モデル割当情報の 4 軸で backlog schema を整理する。別セッションで実装されても追跡できるよう、各 backlog item に `related_candidate_ids` と `overlap_resolution` を記録する。

主な根拠：

- `docs/plan/reconstruction-plan-2026-05-21.md`

## 8. 推奨着手順

現時点での推奨は次の順である。D 番号は安定識別子であり、本文の配置順や優先度順ではない。各項目の優先度ラベルは重要度の目安であり、高優先度群の中で何から着手するかは本節の推奨着手順を正とする。推奨着手順は論文化に向けた依存関係、デプロイ安定性、データ取得可能性、分析可能性を加味した実行順である。これは全候補の存在を否定するものではなく、先に外部展開と測定基盤を固めるための着手順である。D-012 は proxy / autonomous 判断を人間が検査できる説明へ変換するため D-006 / D-007 に近接させる。D-011、D-013、D-014 は proxy assignment、triage、guard の後続品質改善として扱う。D-019 と D-020 は、時間・コスト・モデル割当の記録と複数リポジトリ展開に直結するため、研究評価・展開準備の中でも早めに扱う。D-025 は、レビュー指摘がテストと実装修正へ変換された過程を測るため、finding-to-fix traceability と dogfooding event ledger の間に置く。D-027 は post-write / sandbox / 例外作業から通常 workflow へ復帰する状態モデルであり、Navigator WebUI の前提にもなるため D-026 より先に置く。D-026 は WebUI 試作であり、状態 snapshot と side track モデルがある程度固まった後に扱う。D-018 は false-positive reversal 分析であり、finding / event / cost schema が固まった後に扱う。

1. D-021 deployable reconstruction readiness
2. D-004 normalized finding schema
3. D-005 finding-to-fix traceability
4. D-025 TDD cycle evidence
5. D-027 side track / BTW Track の状態モデル化
6. D-008 dogfooding event ledger
7. D-019 時間・コスト・モデル割当の記録
8. D-020 cross-repository replication
9. D-023 相対リンク・配置非依存性の機械検査
10. D-001 review-wave summary command
11. D-002 recheck clearing criteria
12. D-003 feature-local API review-run pointer
13. D-006 proxy_model decision auditability
14. D-007 自律・並列実行 ledger 強化
15. D-012 review record / human explanation の説明品質強化
16. D-026 ReviewCompass Navigator WebUI の設計・試作
17. D-009 post-write verification の収束基準
18. D-010 各社モデル向け作業入口 adapter 化改訂
19. D-015 から D-017 の feature 個別品質改善
20. D-011 proxy assignment のモデル選定と外形指標チューニング
21. D-013 から D-014 の triage / guard 品質改善
22. D-018 false-positive reversal の明示記録
23. D-022 と D-024 の再構築計画由来 backlog 整理

理由：

- D-021 は ReviewCompass が自己適用だけで閉じていないことを確認し、複数ケースからデータを取る前提を作るため最初に置く。
- D-004、D-005、D-025、D-027、D-008、D-019 は、論文用・監査用のデータ取得、復帰可能な運用状態、分析に直結するため近接して扱う。
- D-025 は、TDD が実装品質に寄与したことを単なる作業慣習ではなく、red-to-green cycle と finding-to-test conversion の証跡として残すために扱う。
- D-027 は、post-write verification や sandbox 探索のような例外的処理を通常 workflow へ復帰可能な side track として扱うため、event ledger と Navigator の前に置く。
- D-020 は、単一 dogfooding 事例から複数ケース評価へ進むため、データ取得基盤の直後に置く。
- D-023 は、外部デプロイ時の配置依存性を減らすため、cross-repository replication と近い位置で扱う。
- D-001 から D-003 は、completed 後に次の review-wave / approval を安全に回すための基盤であり、外部データ取得にも有用である。
- D-006 から D-007 は、proxy / 自律実行の監査性を高める。D-012 はそれらの判断を人間が検査できる説明へ変換する役割を持つため、近接して扱う。
- D-026 は、状態 snapshot と side track モデルを人間が読めるグラフィックへ変換する UI である。初期段階では静的 Navigator に絞り、詳細計画は `docs/notes/2026-06-05-workflow-navigator-webui-plan.md` を参照する。
- D-009 は D-010 の規律変更時に post-write verification の収束を安定させるため、D-010 の本文変更に入る前に先行確認する。
- D-010 は運用事故を減らすが、規律本文変更を含むため所定手続きと post-write verification が必要である。
- D-015 から D-017 は中核 workflow 完了の blocker ではないが、後続品質改善として価値がある。
- D-011、D-013、D-014 は D-006 から D-008 の監査基盤を使うと評価しやすいため、後続品質改善として扱う。D-013 と D-014 は proxy の説明品質ではなく、triage の重要項目検出と commit / push guard の品質改善として分けて扱う。
- D-018 は論文評価の価値があるが、先に finding / event / cost の記録 schema を整える必要がある。
- D-022 と D-024 は中優先度の整理項目であり、再構築計画の宿題を落とさないために残す。D-023 は相対リンク・配置非依存性の検査として 8 番で扱う。D-021 で旧素材前提の混入、外部配置失敗、相対リンク違反、またはスコープ外宿題がデプロイを妨げると分かった場合は、D-021 の readiness report に escalation note を記録し、D-022、D-023、または D-024 を D-004 より前へ繰り上げる。

## 9. 今回の議論メモとしての結論

ReviewCompass の通常 workflow は completed に到達したため、次の開発は「未完了タスクの処理」ではなく、「完成した仕組みを安定してデプロイし、多くのケースから同じ形式のデータを取り、分析できる状態にする」方向へ移るのが自然である。

特に重要なのは、レビューそのものを増やすことではなく、レビューから得た判断と証跡を、複数ケースで同じ粒度・同じ形式で取得できるようにすることである。implementation phase で見えた弱点は、コード品質だけではなく、証跡探索、判断代行、横断依存、記録再現性に集中していた。同時に、TDD がレビュー指摘を実装可能な検証単位へ変換する実践として機能したことも、論文化に向けて記録対象にする価値がある。さらに、機械判定できる workflow 状態を Navigator WebUI で可視化し、post-write verification や sandbox 探索のような例外処理を side track として復帰可能に扱うことは、柔軟な運用と迷子防止の両方に効く。したがって、今後の開発は deployable reconstruction readiness、normalized finding schema、finding-to-fix traceability、TDD cycle evidence、side track 状態モデル、dogfooding event ledger、cost / model allocation recording、cross-repository replication、Navigator WebUI を中心に据えるのがよい。
