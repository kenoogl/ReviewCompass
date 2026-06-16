# 配布側複数 LLM 入口整備の設計記録

作成日：2026-06-10

位置付け：配布側（対象アプリ）で複数 LLM をセッション操縦者として使うための入口整備の設計記録。2026-06-03 の「各社モデル向け作業入口 adapter 方針メモ」（開発リポジトリ側の共通正本＋adapter 分離）を、配布側へ拡張するもの。利用者との一問一答検討で各論点を個別承認済み。実装は本記録に基づき、ツール変更は workflow-management 機能の再オープン手続きで行う。

## 1. 背景と目的

- 利用者の方針決定：配布側（対象アプリ）でも複数 LLM（Claude Code、Codex CLI 等）をセッション操縦者として使う。
- 現状の配布物は LLM 別入口をすべて除外しており（`deploy-manifest.yaml` の exclude：`AGENTS.md`、`.claude/**`、`.codex/**`。FOR_CLAUDE／FOR_CODEX 手引きも allowlist 外）、対象アプリ側に日常運用の入口規律が存在しない。配布物内の LLM 向け文書は初期設定専用の `INITIAL_SETUP_LLM_GUIDE.md` のみ。
- 進め方は「pilot 前に最小整備」。

## 2. 調査で確認した事実

1. 開発リポジトリの入口は「共通正本 `AGENTS.md` ＋ LLM 別の薄い adapter 2 系統（Claude：`CLAUDE.md` 取り込み＋`.claude/`、Codex：`AGENTS.md` 直読み＋`.codex/`）」の構造である。
2. 規律文書・規律マップ・effective prompt 元資料の解決は「実行場所 → 配布物（スクリプト位置）」の 2 段フォールバックが実装済みで、配布物経由でも動作する（模擬対象アプリで effective prompt が対象アプリ側 `.reviewcompass/effective-prompts/` に生成されることを確認）。
3. feature 一覧（`FEATURE_ORDER`）は `tools/check-workflow-action.py` にソース直書きで、設定上書き機構がない。定数のコメントに「ReviewCompass 現行 dogfooding 用の機能順（stages/feature-partitioning/2026-05-24-proposal.md と整合）」とあり、ReviewCompass 自身の feature-partitioning 成果物の埋め込みである。
4. 模擬対象アプリ実験（2026-06-10、生成済み配布物 `build/deploy/ReviewCompass` を使用、feature 名 `demo` の spec.json を配置した一時ディレクトリで `next --json` を実行）で、対象アプリ独自の feature 構成では `DEVIATION`／`kind: unknown`（ReviewCompass の 7 feature の spec.json 不足）になることを確認。現状の配布物では対象アプリが自分の機能構成で workflow 管理を使えない。
5. hook `pre-bash-precheck.sh` は検査ツールを相対パス `python3 tools/check-workflow-action.py` で呼ぶ。対象アプリへ無変更で複製すると、Python の「ファイルを開けない」終了コードが偶然 2（DEVIATION と同値）になり、すべての commit／push を不明瞭な理由で拒否し続ける。
6. 通常進行（`resolve_next_action`）の順序構造は 3 層：(a) phase は固定直列（intent → feature-partitioning → requirements → design → tasks → implementation、全機能バリア）、(b) phase 内の drafting・triad-review のみ feature_order の直列、(c) intent・feature-partitioning（横断 phase）と review-wave・alignment・approval（横断段）は全機能一括。`depends_on` は通常進行で参照されず、自律・並列モードの計画検査でのみ使用される。機能間依存は phase バリア＋feature_order の並び（partitioning 段の人間判断）＋横断段の recheck で担保されている。

## 3. 決定事項

### 3.1 論点 1：入口正本の汎用版

- 内容：フル規律をデフォルトで持ち込む。TDD、post-write 検証、TODO 運用、review-run の実行前ゲート（variant と役ごとの provider／model の提示）・実行後ゲート（raw・モデル別要約・三段階トリアージの提示）、不可逆操作の承認、配布物と対象アプリ root の境界、秘密値の扱い、完了レポート契約を含む。対象アプリの方針と合わない節は利用者判断で調整可と冒頭に明記する。落とすのは開発リポジトリの環境固有部分のみ（§10 LLM 別の注意へ分離）。
- 置き場：対象アプリの `.reviewcompass/AGENT_ENTRY.md`（案 1）。`.reviewcompass/` は既定義の対象アプリ側作業領域であり、新しい置き場を増やさない。発見性は入口ファイルからの参照 1 行で担保する。
- 配布物の場所の記録：入口ファイル内の記入欄方式。`.reviewcompass/config.yaml` への項目追加は、必須 5 項目が承認済み仕様（runtime design.md §10、tasks.md T-007）で確定しており再オープン手続きが必要になるため見送り。将来正式化する場合は runtime の再オープンで移す。
- テンプレート：`templates/entry/AGENT_ENTRY.template.md` として配布。

### 3.2 論点 2：LLM 別 adapter

- AGENT_ENTRY.md の §10「LLM 別の注意」に 1 ファイル同居（案 2-A）。LLM 固有差分は実質 3 点（入口ファイル、記憶の扱い、設定の置き場）で各 3〜4 行のため、別ファイル化の管理負担に見合わない。
- 記憶の扱いは「効果は同じ・リスクの形が非対称」：原則（規律と恒久記録の正本は repo 内のみ）は共通節に置き、LLM 別節は機能固有の注意のみとする。Claude は project memory の自動読み込みがあるため読む側・書く側の両方を規律し、Codex は自動読み込み機能がないため repo 外記録の禁止のみ。
- 第3者配布で LLM や固有注意が増えた場合のファイル分離は、DEPLOYMENT.md §4 の再検討リストで扱う。

### 3.3 論点 3：hook の配布方針

- `templates/hooks/pre-bash-precheck.sh.template` を 1 本だけ配布し、プレースホルダは `{{REVIEWCOMPASS_DIR}}`（配布物 root）と `{{REVIEWCOMPASS_PYTHON}}`（依存導入済み Python 実行系）の 2 つとする。記入規則：いずれも**絶対パス必須**（基準点の曖昧さを排除する。venv の Python やシンボリックリンクは可）。初期設定時に LLM が実パスへ置換し、対象アプリの `.claude/hooks/` と `.codex/hooks/` の両方へ同一内容で複製する。1 本のテンプレートからの機械複製のため、対象アプリ側に複製同一性の機械検査は持ち込まない。
- 失敗時挙動：hook は起動時に未置換トークンの残存と検査ツールの存在を自己診断し、不備がある場合は「hook 設定不備」という明確な理由で commit／push を拒否する（fail-closed）。復旧手順（プレースホルダの再置換）は初期設定ガイドに記載する。相対パス起因の不明瞭な誤拒否（§2-5）を、原因が読める拒否に置き換える。
- `.claude/settings.json` の hook 登録断片と `.codex/hooks.json` の雛形も配布する。
- 導入は強推奨：初期設定の標準手順として導入する。見送る場合は利用者の明示判断とし、見送った事実を初期設定の完了報告に記録する。

### 3.4 論点 4：既存入口との合流

- 承認つき 1 行追記（方式 A）。追記前に書き込み先・挿入行・挿入位置（末尾）を利用者へ提示して承認を得る。
- Claude 用 `CLAUDE.md`：取り込み行 `@.reviewcompass/AGENT_ENTRY.md`（自動読み込みで読み忘れを構造的に防ぐ）。
- Codex 用 `AGENTS.md`：指示文 1 行「ReviewCompass を使う作業では、最初に `.reviewcompass/AGENT_ENTRY.md` を読み、その規律に従う。」
- ファイルが存在しない場合はその 1 行のみの新規作成（承認のうえ）。同じ行が既にある場合は何もしない。既存記述は変更しない。

### 3.5 ツール一般化（案 A-1、補強込み）

- feature 一覧・順序のソース直書きをやめ、`feature-dependency.yaml` の `feature_order` キー（新設）から読む。探索順は実行場所基準で `.reviewcompass/feature-dependency.yaml` → `stages/feature-dependency.yaml` → 直下の `feature-dependency.yaml` とする（第一探索先の `.reviewcompass/` 配置は「ReviewCompass の物は `.reviewcompass/` に閉じる」原則と整合させるための新設。開発リポジトリは既存の `stages/` 配置のまま互換）。内容はアプリ毎に異なる（開発リポジトリ＝ReviewCompass の 7 機能、対象アプリ＝そのアプリの機能）。
- 配置契約：テンプレートは `templates/specs/feature-dependency.yaml.template` として配布し、対象アプリでは feature-partitioning の承認結果を `.reviewcompass/feature-dependency.yaml` として実体化する。`deploy-manifest.yaml` の allowlist へテンプレートを追加する。
- キー名・型・必須／任意の区別などの詳細仕様は、workflow-management 再オープンの成果物（requirements／design／tasks の改訂と TDD テスト）で確定し、本記録はその入力とする。
- 立ち上げ挙動：`feature_order` 未定義のときはエラーではなく、intent／feature-partitioning の実施と、承認された分割結果の `feature-dependency.yaml` への記録を案内する。
- 根拠の必須提示：feature-partitioning 提案には「機能ごとの依存の主張と理由（hard／review の別を含む）」と「順序の導出」を必須節とする。人が検討するのは依存の主張の正しさであり、LLM は根拠を提示する。
- 整合の機械検査：`feature_order` が `depends_on` と矛盾しない順序（依存される機能が先）であること、循環依存がないことをツールが検査し、矛盾時は理由つきで指摘する。
- 開発リポジトリの `stages/feature-dependency.yaml` に 7 機能の `feature_order` を追記し、既存挙動を回帰テストで担保する。
- workflow-management の完了済み仕様に触れるため、再オープン手続き＋TDD（テスト先行）で実施する。

### 3.6 論点 5：操縦 LLM 別の API 既定設定（2026-06-11 追補）

- 背景：従来の 3 役 variant 構成は「操縦（セッションを動かし起草する）LLM＝Claude」を暗黙の前提にしており、Codex（GPT 系）が操縦すると adversarial（反証役）が起草者と同系列になり独立性が下がる。利用者の指摘により論点 5 として検討し、各項目を個別承認した。
- 独立性の原則：
  1. 単独検証役（1 体での post-write 検証など）は、操縦 LLM と別系列を必須とする。
  2. 3 役構成の adversarial と judgment は、操縦 LLM と別系列を必須とする。
  3. 3 役構成の primary（検出役）は、操縦 LLM と同系列を許容する（最終判定を持たず、残り 2 役の独立で全体の独立性が保たれるため。開発実績と同型）。
  4. proxy_model（人の判断の代行）は、操縦 LLM と別系列を必須とする。設定ファイル上の既定キーは現状存在しないため、利用時の選択規則として扱い、AGENT_ENTRY テンプレート §10 の共通節に明記する。
- 既定 variant の構成（`config/api-settings.yaml` 反映済み）：
  - 接尾辞なしの `*_independent_3way` 系（post_write_verification／yaml_audit／implementation_review）＝ **Claude Code 操縦時の既定**。adversarial を gpt-5.4 から gpt-5.5 へ変更（利用者判断。反証役へより強いモデルを充てるため。Codex 操縦既定の adversarial に claude-opus-4-8 を充てたのと同趣旨）。構成：primary=anthropic-api/claude-sonnet-4-6、adversarial=openai-api/gpt-5.5、judgment=gemini-api/gemini-3.1-pro-preview。
  - 新設の `*_independent_3way_codex_operator` 系（同 3 用途）＝ **Codex CLI 操縦時の既定**。構成：primary=openai-api/gpt-5.4、adversarial=anthropic-api/claude-opus-4-8、judgment=gemini-api/gemini-3.1-pro-preview。
  - judgment（gemini-3.1-pro-preview）と小規模 1 体検証（`post_write_verification_google`＝gemini-3.5-flash）は両操縦で共用し、操縦を切り替えても判定基準の連続性を保つ。
  - 既存 variant の改名は行わない（規律文書・過去 run 記録・spec からの参照を保全するため）。Gemini が操縦する場合（将来）は同じ原則で役を回転して対応し、今回は variant を追加しない。
- 反映先：`config/api-settings.yaml`（実施済み）、`templates/entry/AGENT_ENTRY.template.md` §10 への操縦 LLM 別既定の案内（実施済み）、初期設定ガイドへの操縦 LLM 確認手順（実装計画 4 で実施）。

### 3.7 追補：Codex TODO hook の下書き化と正式記録への昇格（2026-06-15 設計、2026-06-16 実装）

- 背景：Codex には Claude の `SessionEnd` 相当がなく、TODO 更新を合図に現セッション rollout を保存する設計自体は維持する。ただし、2026-06-15 時点で実装・運用していた方式では `PostToolUse` hook が現セッションの途中記録を `.reviewcompass/evidence/sessions/` と `docs/sessions/` に直接生成していたため、セッション中ずっと `git status` に未追跡ファイルとして出続けた。commit guard は進行中セッション記録を除外できるが、正式証跡置き場へ途中版を出すことがノイズと誤運用の原因になるため、2026-06-16 実装では runtime 下書き方式へ変更した。
- 設計変更：TODO 更新 hook は、現セッションを正式記録へ直接書かず、`.reviewcompass/runtime/session-record-drafts/` 配下の下書き領域へ保存する。runtime は git 管理対象外であり、作業中に TODO を複数回更新しても正式証跡の dirty を増やさない。下書きは `codex-<session_id>.md` とし、`session_id` ごとに 1 件を更新対象とする。TODO が 1 セッション内で複数回更新された場合は同じ下書きを追記専用マージで伸ばす。下書きは正式昇格後に削除してよく、必要なら元 rollout から再生成する。
- 正式化：Codex 公式 hook 仕様では `SessionStart` が利用可能であるため、次の Codex `SessionStart` で、現 `session_id` と異なる最新下書き 1 件を `.reviewcompass/evidence/sessions/` と `docs/sessions/` へ昇格する。実装済み hook は `.codex/hooks/session-record-promote-previous-draft.sh`、実装済み CLI は `tools/session-record-promote-draft.py --session-id <id> --source codex --current-session-id <current-id>` である。契約は「対象 `session_id` 明示」「現在実行中の `session_id` を明示できること」「対象が現在実行中の `session_id` と同一なら拒否」「終了済みセッションだけを正式記録にする」の 4 点とする。hook は、選んだ最新下書きの `source_sha256` と現在の元 rollout の sha256 が一致する場合だけ CLI へ進む。不一致の場合は進行中の可能性があるため正式化せず、古い候補へフォールバックしない。自動昇格できない場合は安全側に倒し、終了済み rollout を指定した明示 backfill 手順へ戻す。
- 既存ルールとの関係：`UserPromptSubmit` を使わない方針、`session_id` が無い場合に推測しない方針、TODO を更新しないセッションや hook 失敗時は明示 `--session` backfill に倒す方針は維持する。変更するのは「現セッションをどこに書くか」と「正式記録へ昇格する時点」である。
- 実装変更対象：
  - `.codex/hooks/session-record-capture-current-on-todo.sh`：`tools/session-record-backfill.py` の正式出力先を直接使わず、runtime 下書き出力へ切り替える。診断ログは `captured`／`capture_failed` ではなく `drafted`／`draft_failed` へ改め、正式記録と区別できる event 名にする。
  - `templates/hooks/session-record-capture-current-on-todo.sh.template`：配布先でも同じ runtime 下書き方式へ変更する。
  - `.codex/hooks/README.md`、`docs/operations/INITIAL_SETUP_LLM_GUIDE.md`、`TODO_NEXT_SESSION.md`：hook が現セッションを下書き保存し、正式記録は昇格操作で作ることを明記する。
  - 新規 helper：下書き生成と正式昇格を分離する。既存の `tools/session-record-backfill.py` は終了済みセッションの明示回収として据え置き、下書き機能は付けない。2026-06-16 実装では、下書き生成 helper と昇格 helper を分ける方式を採用した。
  - `tests/hooks/test_codex_session_record_capture_current_on_todo.py`、`tests/tools/test_session_record_promote_draft.py`、`tests/deployment/test_hook_templates.py` 等：TODO 更新時に evidence/docs へ直接生成しないこと、hook 経由で `tools/session-record-draft.py` が呼ばれ runtime 下書きが更新されること、現 `session_id` の昇格が拒否されることを TDD で固定する。
- 実装反映（2026-06-16）：下書き生成 helper は `tools/session-record-draft.py`、正式昇格 helper は `tools/session-record-promote-draft.py` として分離した。hook 本体と配布テンプレートは `session-record-draft.py` を呼び、成功 event は `drafted`、失敗 event は `draft_failed` とする。昇格 helper は `--current-session-id` が対象 `--session-id` と同じ場合に exit 2 で拒否する。

## 4. 実装計画

1. 本設計記録の作成と post-write 検証（本ファイル）。
2. ツール一般化：workflow-management の再オープン手続き（変更分類 → 上流影響判定）→ TDD テスト作成 → 実装 → 全テスト通過。
3. テンプレート群の作成：`templates/entry/AGENT_ENTRY.template.md`、`templates/hooks/` 3 点、feature-dependency.yaml テンプレート、`deploy-manifest.yaml` への追加。
4. ガイド更新：`INITIAL_SETUP_LLM_GUIDE.md`（入口合流手順、hook 導入強推奨、feature 立ち上げ、操縦 LLM の確認と既定 variant の案内）、`INITIAL_DEPLOYMENT_USER_GUIDE.md`（利用者向け説明）、`DEPLOYMENT.md` §4（「Codex アダプタ」行を「LLM 別 adapter 一式」へ拡張）。
5. 配布物の再生成 → 配布前 smoke → 模擬対象アプリで「対象アプリ独自の feature 構成で `next` が機能する」ことの実験確認（§2-4 の実験の再現による解消確認）。§2-4 の実験は再オープンの TDD テストとして `tests/` に固定化し、成功基準（対象アプリ独自 feature 構成で `next` が DEVIATION にならず stage 判定を返すこと）もテストで表現する。
6. TODO_NEXT_SESSION.md の更新。

commit・push は各停止点で利用者指示により実行する。

## 5. 関連記録

- `docs/notes/2026-06-03-agent-adapter-strategy.md`：開発リポジトリ側の共通正本＋adapter 分離方針（本記録はその配布側拡張）。
- `docs/operations/DEPLOYMENT.md` §4：第3者配布で再検討する配布単位（Codex アダプタ行の拡張対象）。
- `docs/operations/INITIAL_DEPLOYMENT_USER_GUIDE.md`／`INITIAL_SETUP_LLM_GUIDE.md`：初期デプロイの利用者向け・LLM 向け手引き（更新対象）。
