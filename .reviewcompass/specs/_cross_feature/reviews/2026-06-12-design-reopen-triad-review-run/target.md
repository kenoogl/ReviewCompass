# レビュー対象：reopen R-0 design 変更（配布側複数 LLM 入口契約の設計反映）

改訂：round-1（2026-06-12）の triad-review 所見（クラスタ G must-fix・should-fix 4 件、利用者発言「了承」）を
design.md へ反映済み。本書の引用は修正後の本文。round-2 は修正の妥当性確認を目的とする。

## 0. variant 選定理由（実行前ゲートの記録）

- 使用 variant：`implementation_review_independent_3way`（context: triad_review、API 3 社独立）
- 役割：primary=anthropic-api/claude-sonnet-4-6、adversarial=openai-api/gpt-5.5、judgment=gemini-api/gemini-3.1-pro-preview
- 選定理由：requirements フェーズの triad-review と同一構成。triad_review の default は CLI 経路を含み
  本実行環境と合わないため、利用者承認済みの「Claude Code 操縦時の API 既定」を採用。

## 1. レビューの位置付け

reopen R-0（docs/reviews/reopen-classification-2026-06-12-multi-llm-entry-spec-reflection.md）第3過程の
design フェーズ triad-review（round-2）。requirements フェーズは利用者 approval 済み。実装コードの変更は
含まない（実装先行の追認）。

## 2. 変更内容（workflow-management design.md、round-1 修正反映後）

### 2.1 §機能依存マップモデル §1（一元保管先の対象アプリ対応）

> 機能間の処理順と依存関係を `feature-dependency.yaml` に一元化する。各フェーズの YAML はこのファイルを
> 参照し、重複させない。開発リポジトリでは `stages/feature-dependency.yaml` に置き、対象アプリでは
> feature-partitioning の承認結果を `.reviewcompass/feature-dependency.yaml` として実体化する
> （テンプレートは `templates/specs/feature-dependency.yaml.template` として配布）。

### 2.2 §機能依存マップモデル §2（キー名の統一）

構造例の最上位キーを `feature_order:` とし、旧称 `phase_order` の由来注記
（requirements Requirement 8 受入 2 参照、過去記録は書き換えない）を追記。

### 2.3 §機能依存マップモデル §7（feature 一覧の解決と立ち上げ案内、round-1 修正反映後）

> - **探索順**：ツール実行時のカレントディレクトリを基準に、相対パス
>   `.reviewcompass/feature-dependency.yaml` → `stages/feature-dependency.yaml` →
>   `feature-dependency.yaml` の順で確認し、最初に存在したファイル 1 つだけを読む
>   （`FEATURE_DEPENDENCY_SEARCH_PATHS`）。親ディレクトリへの遡上探索は行わない。
>   第一探索先の `.reviewcompass/` 配置は「ReviewCompass の物は `.reviewcompass/` に閉じる」原則と
>   整合させるための対象アプリ向け規約で、開発リポジトリは既存の `stages/` 配置のまま互換とする。
>   直下の `feature-dependency.yaml` は標準 2 配置に該当しない配置への後方互換の受け皿であり、
>   標準配置としては使わない。遡上探索を行わない根拠：親ディレクトリに別の `feature-dependency.yaml`
>   が存在すると、対象アプリ内の入れ子作業ディレクトリや一時ディレクトリからの実行で意図しない
>   ファイルを拾う恐れがあり、解決元の予測可能性（カレントディレクトリ基準の 3 パスだけを見れば
>   解決元が確定する）を優先する。
> - **立ち上げ案内**：ファイル不在、`feature_order` 未定義、またはファイルが YAML として読めない場合
>   （パース不能は未定義と同様に扱う。遮断［DEVIATION］への分離は実装改善候補 FUP-2026-06-12-001）、
>   エラーではなく `next_action.kind: feature_definition_required`（verdict OK／exit 0）を返し、
>   intent／feature-partitioning の実施と、承認された分割結果の記録先を案内する。
>   `current_state.feature_dependency_source` に解決元（不在時 null）を含める。
>   **判断 3（fail-closed 全面採用）との両立**：判断 3 は「不可逆操作を誤って許可することによる被害」を
>   防ぐ原則であり、本案内は spec.json 更新・commit・push 等のいかなる操作も許可せず、通常 workflow の
>   次タスク判定も返さない。つまり「作業を進ませない」という安全側の性質は保たれており、fail-closed が
>   守る対象（不可逆操作の誤許可）に抵触しない。立ち上げ案内を DEVIATION にしないのは、対象アプリの
>   初期状態（feature 一覧が未定義であることが正常）で利用者を次の正規手順（intent／feature-partitioning）
>   へ誘導するためである。残る弱点は、パース不能（ファイル破損）と未定義（初期状態）を区別できず、
>   破損を案内で覆い隠しうる点で、これは FUP-2026-06-12-001（パース不能の遮断分離）として
>   改善候補に登録済みである。
> - **整合検査**：`feature_order` と `depends_on` の整合（依存される機能［依存先］を依存する機能
>   ［依存元］より先に置くこと、循環依存なし）を `validate_feature_order_consistency` が検査し、
>   違反時は `next_action.kind: unknown` を返して違反内容を出力の `reasons` 配列に列挙し、
>   verdict DEVIATION（exit code 2、fail-closed）とする。失敗の種類で挙動を分ける：
>   未定義・パース不能 → 案内（OK）、整合違反 → 遮断（DEVIATION）。
> - **判定点の登録**：`feature_definition_required` は `WORKFLOW_DISCIPLINE_MAP.yaml` の
>   `next_action_kind` 判定点として登録し、effective prompt の生成対象とする
>   （登録は 2026-06-12 の本変更セットで実施済み。書き込み後検証 3 系統を通過、
>   manifest post-write-2026-06-12-004）。

### 2.4 §軽量版検査スクリプトモデル §2 への段落追加

> next サブコマンドは、feature 一覧が解決できない場合（`feature-dependency.yaml` 不在または
> `feature_order` 未定義、対象アプリの初期状態を想定）は `feature_definition_required`（verdict OK）を
> 返して intent／feature-partitioning の実施を案内し、`feature_order` と `depends_on` の整合違反
> （依存先行違反・循環）は `kind: unknown`／DEVIATION で遮断する。

### 2.5 §XDI-WM-003（配布側複数 LLM 入口の配布契約、round-1 修正反映後）

> - **対象アプリ入口規律**：`templates/entry/AGENT_ENTRY.template.md` を配布し、対象アプリの
>   `.reviewcompass/AGENT_ENTRY.md` として実体化する。LLM 別差分（入口ファイル・記憶の扱い・設定の
>   置き場）は §10 に 1 ファイル同居とし、別ファイル化しない。既存入口（CLAUDE.md／AGENTS.md）への
>   合流条件（設計記録 2026-06-10 §3.4、方式 A、利用者承認済み）：追記前に書き込み先・挿入行・挿入位置
>   （末尾）を利用者へ提示して承認を得る。同じ行が既にあれば何もしない。ファイルが存在しなければ
>   承認のうえその 1 行のみで新規作成する。既存記述は変更しない。
> - **hook 配布**：`templates/hooks/pre-bash-precheck.sh.template` を 1 本だけ配布する。プレースホルダは
>   `{{REVIEWCOMPASS_PYTHON}}`・`{{REVIEWCOMPASS_DIR}}` の 2 つで、いずれも絶対パス必須。初期設定時に
>   LLM が実パスへ置換し、`.claude/hooks/` と `.codex/hooks/` の両方へ同一内容で複製する。
>   **自己診断の契約**：診断の主体は hook スクリプト自身、実行タイミングは hook 起動時（検査ツール
>   呼び出しの前）。未置換トークンの残存、検査ツール（`tools/check-workflow-action.py`）の不在、
>   Python 実行系の実行不能を検出した場合、「hook 設定不備」という明確な理由を出力して当該 commit／push
>   を拒否する（fail-closed、非 0 終了）。復旧手順（プレースホルダの再置換）は初期設定ガイドに記載する。
>   動作仕様の実体正本はテンプレート本体（`pre-bash-precheck.sh.template` の deny 関数と診断部）とする。
> - **登録雛形**：`.claude/settings.json` の hook 登録断片と `.codex/hooks.json` 雛形を配布する。
>   実体化先は対象アプリの `.claude/settings.json`（既存設定があれば断片を統合）と `.codex/hooks.json`。
>   導入は強推奨であり、有効化確認（hook が commit／push 時に起動すること）の手順と検証責務は
>   `docs/operations/INITIAL_SETUP_LLM_GUIDE.md` を正本とする。導入を見送る場合は利用者の明示判断とし、
>   見送った事実を初期設定の完了報告に記録する。
> - **配布 allowlist**：`deploy-manifest.yaml` に entry／hooks／feature-dependency の各テンプレートを含める。

### 2.6 参照の語彙統一（5 箇所、意味不変）と変更意図への追記

`feature-dependency.yaml#phase_order` 参照 5 箇所を `#feature_order` へ統一。変更意図に
2026-06-12 reopen R-0 の経緯を 1 項目追加。

## 3. 変更内容（conformance-evaluation design.md）

§13.5 の見出しを「feature_order の最後」へ変更し、本文 2 箇所と対応表 1 箇所を文言追従（意味不変）。

## 4. 根拠と証跡

- 承認済み requirements：workflow-management Requirement 8 受入 1〜3・6〜8（2026-06-12 利用者 approval）
- 実装：`tools/check-workflow-action.py`（テスト 155 件＋全群 871 件通過）
- 配布物：templates/（c2903df）、deploy-manifest.yaml allowlist、模擬対象アプリ実証済み
- round-1 トリアージ：クラスタ G must-fix（fail-closed 両立説明）・should-fix 4 件は反映済み、
  leave-as-is 1 件（過去記録の範囲は requirements 由来注記に列挙済み）

## 5. レビュー観点（round-2）

1. クラスタ G の対処：§7 立ち上げ案内の「判断 3 との両立」説明は、矛盾の解消として十分か。
   説明に論理の飛躍や検証不能な主張はないか。
2. クラスタ H の対処：hook 自己診断の契約（主体・タイミング・拒否動作・実体正本）と登録雛形の
   実体化先・検証責務は設計契約として完結したか。
3. 合流条件・遡上根拠・判定点登録状態の追記は一義に読めるか。
4. design の挙動規定が承認済み requirements 受入 6〜8 と意味で一致しているか。
