# Must-fix clusters: 2026-06-04-workflow-management-implementation-review-run

重要所見を同根問題ごとにまとめた判断材料です。ここでは実装修正は行わず、候補案と推薦案までを示します。

## WM-IMPL-MF-001: raw response と triage 完了を自律実行ガードで機械確認できない

対象所見: 2026-06-04-workflow-management-implementation-review-run-claude-sonnet-4-6-primary-001, 2026-06-04-workflow-management-implementation-review-run-claude-sonnet-4-6-primary-002

平易な説明: レビュー結果の生データと三段階トリアージが本当に揃ったかを、現在の自律実行計画ガードはファイル参照で確認していません。つまり「揃いました」という自己申告だけで次へ進めてしまう余地があります。

候補案:
- A: autonomous-plan に review_run_dir, required_raw_paths, triage_path を追加し、raw存在・hash・未判断0件を検査する（実装量は中程度だが、今回の問題を直接ふさげる）
- B: 既存 review_triage.py の assert 系を autonomous-plan から呼ぶ（重複は少ないが、計画段と実装着手段の責務が混ざる可能性がある）
- C: 運用文書だけで必須化し、機械ガードは追加しない（早いが、同じミスを機械的に防げない）

推薦案: A
理由: 自律実行の開始前に証跡の有無を機械判定できるため。ユーザが求めた「取りこぼしを機械判定に持ち込む」に最も合う。

## WM-IMPL-MF-002: commit / push / spec-set が stages/in-progress を見ていない

対象所見: 2026-06-04-workflow-management-implementation-review-run-gpt-5.4-adversarial-002, 2026-06-04-workflow-management-implementation-review-run-gemini-3.1-pro-preview-judgment-002

平易な説明: 進行中の手続きが残っているときに commit、push、spec-set を通せてしまう、という指摘です。作業途中のまま不可逆操作をしてしまう危険があります。

候補案:
- A: stages/in-progress/ の非空検査を共通関数化し、commit / push / spec-set の直前に必ず見る（実装範囲は明確で、不可逆操作全体に効く）
- B: commit / push だけ先に遮断し、spec-set は後続に回す（小さく始められるが、spec-set の穴が残る）
- C: WARN に留める（自律実行中の事故防止として弱い）

推薦案: A
理由: 要件上の不可逆操作ゲートなので、対象を分けず共通で fail-closed にするのが自然。

## WM-IMPL-MF-003: proxy decision が元 raw と一致しているか確認できない

対象所見: 2026-06-04-workflow-management-implementation-review-run-claude-sonnet-4-6-primary-004, 2026-06-04-workflow-management-implementation-review-run-gemini-3.1-pro-preview-judgment-003

平易な説明: proxy decision は「どのレビュー生データを読んで判断したか」が重要ですが、今は raw ファイルが存在することしか見ていません。別の raw に差し替わっても見抜きにくい、という問題です。

候補案:
- A: decision の source_raw_paths を triage.yaml と rounds.yaml に照合し、raw_sha256 まで一致確認する（証跡の真正性を一番強く守れる）
- B: source_raw_paths が triage の source_raw_path と一致することだけ確認する（軽いが、ファイル内容の差し替えは防げない）
- C: decision に raw_sha256 を追記するだけにする（記録は増えるが検査がなければ防止力が弱い）

推薦案: A
理由: raw response を根拠にした判断代行という契約を守るには、パスとハッシュの両方を照合する必要がある。

## WM-IMPL-MF-004: spec-set が stages/*.yaml の completion_predicate を評価していない

対象所見: 2026-06-04-workflow-management-implementation-review-run-gemini-3.1-pro-preview-judgment-001

平易な説明: spec-set が段階定義 YAML を読まず、コード内の固定順序だけで段の進行可否を見ている、という指摘です。段ごとの「成果物があるか」「author/reviewer が分離しているか」などの述語が効いていない可能性があります。

候補案:
- A: まず実装済み範囲との差分を確認し、completion_predicate 評価不足をT-004残課題として機械検査に追加する（大きな改修に入る前に事実確認できる）
- B: stages/*.yaml パーサと全 predicate 評価を即実装する（正攻法だが影響範囲が大きく、この場の自律実装としては危険）
- C: 今回は誤検出として保留する（CRITICAL 指摘を十分に扱えない）

推薦案: A
理由: CRITICAL だが広範囲。まず現実の実装差分とタスク残を照合し、実装単位を切るのが安全。

## WM-IMPL-MF-005: 自律並列計画で main_session/same_worktree のAPI並列をどう扱うかが曖昧

対象所見: 2026-06-04-workflow-management-implementation-review-run-gpt-5.4-adversarial-001

平易な説明: サブ担当による実装並列は別 worktree が原則ですが、今回の3モデルAPI呼び出しは実装差分を作らない読み取り・生成処理です。この例外を計画ガード上で明示できていない、という問題です。

候補案:
- A: task に writes_repo_diff=false / output_only=true のような区分を追加し、同一 worktree API並列を証跡生成に限定して許可する（今回の実態に合い、実装並列との混同を防げる）
- B: API呼び出しもすべて subthread/separate_worktree 扱いにする（規律は単純だが、raw取得だけでも過剰に重くなる）
- C: この指摘を leave-as-is にする（今後も同じ混乱が起きる）

推薦案: A
理由: 実装差分を作る並列と、raw取得だけの並列を分けて機械判定できるため。

## WM-IMPL-MF-006: commit 承認レコードと push 直前検査の新鮮さが足りない

対象所見: 2026-06-04-workflow-management-implementation-review-run-claude-sonnet-4-6-primary-003, 2026-06-04-workflow-management-implementation-review-run-gpt-5.4-adversarial-003

平易な説明: commit 承認が古いまま使われたり、push 時に直前 commit が正しく検査済みか見ない、という指摘です。人の承認を得たつもりでも、別の差分に承認が流用される危険があります。

候補案:
- A: commit approval に staged file sha256 と作成時刻を記録し、commit/push で監査可能にする（承認の流用を防ぎ、push 監査にも接続できる）
- B: approval record の consumed だけをさらに厳格化する（古い未消費承認の問題は残る）
- C: push 側だけ audit-commit を強制する（commit 承認の新鮮さ問題は直接解決しない）

推薦案: A
理由: コミット対象と承認をハッシュで結びつけるのが、機械判定として最も追跡しやすい。
