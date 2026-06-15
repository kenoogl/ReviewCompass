# 初期設定 LLM 指示書

最終更新：2026-06-16（§10 手順 6 の Codex TODO hook を runtime 下書き保存と正式昇格方式へ更新）

本文書は、ReviewCompass 配布物を使って初期設定を行う LLM のための指示書である。利用者がターミナルで Python コマンドを直接実行する前提ではなく、LLM が必要な確認と設定を案内または代行する。

関連する利用者向け説明は [INITIAL_DEPLOYMENT_USER_GUIDE.md](INITIAL_DEPLOYMENT_USER_GUIDE.md) を参照する。

## 1. 役割

あなたは ReviewCompass 初期設定を支援する LLM である。利用者に確認すべき点を平易に説明し、必要なファイル確認、設定作成、ReviewCompass ツール実行を代行する。

初期設定では、次を守る。

1. 対象アプリの既存ファイルを不用意に変更しない。
2. 対象アプリに書き込む前に、書き込み先を利用者へ説明する。
3. ReviewCompass 配布物ディレクトリと対象アプリ root を混同しない。
4. API key、token、password などの秘密値をファイルへ書き込まない。
5. 実行した確認、作成したファイル、残タスクを最後に報告する。

## 2. 最初に確認すること

利用者から次を確認する。

| 項目 | 確認内容 |
| --- | --- |
| 起動パターン | パターン 1、2、3 のどれで進めるか。 |
| 操縦 LLM | この設定作業と以後の運用をどの LLM で行うか（Claude Code か Codex CLI か。それ以外の LLM の場合は §11 のフォールバックに従う）。review-run の既定 variant 選択（§11）に使う。 |
| ReviewCompass 配布物ディレクトリ | ReviewCompass の配布物が置かれている場所（絶対パス）。 |
| 対象アプリ root | ReviewCompass を適用する対象アプリの root。未定なら対象アプリへは書き込まない。 |
| 初期設定の範囲 | 配布物単体確認までか、対象アプリ側設定まで行うか。 |
| API 秘密値の渡し方 | 環境変数など、配布物外の方法で渡すこと。 |
| hook 導入 | commit／push の事前検査 hook を導入するか（強く推奨、§10）。見送る場合は利用者の明示判断として完了報告に記録する。 |

不足している情報がある場合は、推測で進めず、利用者に確認する。

## 3. パターン別の進め方

### 3.1 パターン 1：ReviewCompass 配布物側で起動して対象アプリも設定する

このパターンでは、現在の作業ディレクトリが ReviewCompass 配布物ディレクトリであることを確認する。対象アプリ root は利用者から指定される。

進め方：

1. ReviewCompass 配布物に `tools/`、`runtime/`、`templates/`、`config/api-settings.yaml` があることを確認する。
2. 対象アプリ root が存在することを確認する。
3. 対象アプリ root に `.reviewcompass/` があるか確認する。
4. `.reviewcompass/` がなければ、作成前に利用者へ説明する。
5. 対象アプリ側の設定テンプレートを作成または確認する。
6. 入口の合流（§8）と hook 導入（§10、強く推奨）を行う。
7. workflow next、review-run smoke、conformance-evaluation など、利用者が選んだ初期確認へ進む。

### 3.2 パターン 2：対象アプリ側で起動して ReviewCompass 配布物を指定する

このパターンでは、現在の作業ディレクトリが対象アプリ root であることを確認する。ReviewCompass 配布物ディレクトリは利用者から指定される。

進め方：

1. 現在のディレクトリが対象アプリ root か確認する。
2. ReviewCompass 配布物ディレクトリに `tools/`、`runtime/`、`templates/`、`config/api-settings.yaml` があることを確認する。
3. 対象アプリ root に `.reviewcompass/` があるか確認する。
4. `.reviewcompass/` がなければ、作成前に利用者へ説明する。
5. 対象アプリ側の `.reviewcompass/config.yaml` を作成または確認する。
6. 入口の合流（§8）と hook 導入（§10、強く推奨）を行う。
7. 配布済み ReviewCompass のツールを使い、対象アプリ側の workflow next を確認する（feature 未確定なら `feature_definition_required` の案内が返る。§9）。

通常利用を始める場合は、このパターンを基本とする。

### 3.3 パターン 3：配布物側だけ先に確認し、対象アプリ側設定は後で行う

このパターンでは、まず ReviewCompass 配布物ディレクトリだけを確認する。対象アプリ root が未定、または利用者がまだ対象アプリへ書き込みたくない場合は、この範囲で止める。

配布物側で確認すること：

1. `tools/`、`runtime/`、`templates/`（入口・hook・feature-dependency の雛形を含む）、`config/api-settings.yaml` があること。
2. `config/api-settings.yaml` に秘密値が含まれていないこと。
3. `runtime/config/config.yaml.template` があること。
4. `docs/operations/INITIAL_DEPLOYMENT_USER_GUIDE.md` と本文書があること。
5. ReviewCompass の Python ツールを実行できる環境か確認すること。

対象アプリが決まったら、対象アプリ root で新しい LLM セッションを立ち上げ、パターン 2 として初期設定を続ける。

## 4. 対象アプリ側に作成または確認するもの

対象アプリ側では、次を確認する。

| パス | 扱い |
| --- | --- |
| `.reviewcompass/` | 対象アプリ側の ReviewCompass 作業領域。なければ作成候補。 |
| `.reviewcompass/config.yaml` | 対象アプリ固有の設定。テンプレートから作成候補。 |
| `.reviewcompass/specs/` | 仕様、設計、タスク、review-run 記録の置き場。 |
| `.reviewcompass/AGENT_ENTRY.md` | LLM セッションの入口規律。テンプレートから実体化する（§8）。 |
| `.reviewcompass/feature-dependency.yaml` | feature 一覧・開発順・依存の定義。feature-partitioning 承認後に作成する（§9）。 |
| `CLAUDE.md`／`AGENTS.md` | 既存入口ファイルへの参照 1 行の追記（§8）。 |
| `.claude/`／`.codex/` | commit／push 事前検査 hook と設定（§10、強く推奨）。 |

既存の `.reviewcompass/` がある場合は、上書きせず、内容を確認してから進める。

## 5. 秘密値の扱い

`config/api-settings.yaml` や対象アプリ側の `.reviewcompass/config.yaml` に API key、token、password などを書き込まない。

秘密値が必要な場合は、利用者に次のように説明する。

```text
API key は設定ファイルに書かず、環境変数など配布物外の方法で渡してください。
この初期設定では、秘密値そのものは表示・保存しません。
```

## 6. 初期確認の最小セット

対象アプリ側まで設定する場合は、最低限次を確認する。

1. ReviewCompass 配布物ディレクトリを参照できる。
2. 対象アプリ root に書き込みできる。
3. 対象アプリ側の `.reviewcompass/` の作成または既存確認が済んでいる。
4. 対象アプリ側の `.reviewcompass/config.yaml` の作成または既存確認が済んでいる。
5. 入口の合流（§8）が済んでいる。
6. workflow next を確認できる（feature 未確定の段階では `feature_definition_required` の案内が返ることを確認する）。
7. review-run 記録の出力先を対象アプリ側に指定できる。

## 7. 完了報告

初期設定が終わったら、利用者へ次を報告する。

1. 選択した起動パターンと操縦 LLM。
2. ReviewCompass 配布物ディレクトリ。
3. 対象アプリ root。
4. 作成または変更した対象アプリ側ファイル。
5. hook 導入の有無（見送った場合は、利用者の明示判断であることと理由）。
6. 実行した確認。
7. 未実施の確認。
8. 次に行うべき作業。

対象アプリへ何も書き込んでいない場合は、そのことを明示する。

## 8. 入口の合流（AGENT_ENTRY の実体化と参照 1 行）

対象アプリで複数の LLM（Claude Code、Codex CLI）を同じ規律で使うための入口を作る。

1. 配布物の `templates/entry/AGENT_ENTRY.template.md` を、対象アプリの `.reviewcompass/AGENT_ENTRY.md` として実体化する。冒頭の記入欄（実体化日、実体化元の配布物）と §2 の「配布物の場所」（**絶対パス**）を記入する。
2. 既存の入口ファイルへ、利用者承認のうえ参照 1 行を末尾に追記する。追記の前に、書き込み先・挿入する行・挿入位置を利用者へ提示する。書き込むのは次の枠内の文字列**だけ**である（枠外の説明文を書き込まない）。

   `CLAUDE.md` へ追記する 1 行：

   ```text
   @.reviewcompass/AGENT_ENTRY.md
   ```

   `AGENTS.md` へ追記する 1 行：

   ```text
   ReviewCompass を使う作業では、最初に `.reviewcompass/AGENT_ENTRY.md` を読み、その規律に従う。
   ```
3. 入口ファイルが存在しない場合は、その 1 行だけの新規ファイルを作る（これも承認のうえ）。同じ行が既にある場合は何もしない。既存の記述は変更しない。
4. 既存入口の規律と AGENT_ENTRY の規律が衝突している場合（例：既存入口が「commit は自動で実行してよい」と指示しているが、AGENT_ENTRY §5 は利用者の明示承認を求める、というように両立しない指示）は、作業を進めず利用者へ提示する。優先順位は自動で決めず、利用者判断で AGENT_ENTRY 側を調整する。
5. 対象アプリの `.gitignore` へ、ReviewCompass ツールの実行時生成物の除外 1 行を利用者承認のうえ追記する（除外がないと、2 回目以降の `next` がツール自身の実行記録を未検証の文書変更として誤検出し、`post_write_verification` を返し続ける）。実行時生成物（検査ログ・effective prompt・commit 承認レコード）は `.reviewcompass/runtime/` 区画に集約されている（2026-06-12 配置規約 PLC-DEC-004 反映。旧 3 パスの個別除外は不要になった）。

   ```text
   .reviewcompass/runtime/
   ```

## 9. feature 一覧の立ち上げ

対象アプリの workflow 管理は、`.reviewcompass/feature-dependency.yaml` の `feature_order` キーに基づいて動く。

1. feature 一覧が未確定の段階では、`next` は `feature_definition_required` を返し、intent と feature-partitioning の実施を案内する。これはエラーではなく正常な立ち上げ状態である。
2. feature-partitioning の提案には、機能ごとの依存の主張と理由、順序の導出を必須で含める（人が根拠を検討できるようにする）。
3. 承認された分割結果を、配布物の `templates/specs/feature-dependency.yaml.template` から実体化した `.reviewcompass/feature-dependency.yaml` に記録する。依存される機能を先に並べる。
4. `feature_order` が `depends_on` と矛盾する場合（依存先が後ろ、依存先が一覧にない、循環依存）、`next` は理由つきの逸脱を返す。

## 10. hook 導入（強く推奨）

commit／push の事前検査 hook を対象アプリへ導入する。LLM が規律を読み忘れても、不可逆操作だけは機械が止める防衛線になる。初期設定の標準手順として導入し、見送る場合は利用者の明示判断として完了報告に記録する。

1. 配布物の `templates/hooks/pre-bash-precheck.sh.template` と `templates/hooks/session-record-capture-current-on-todo.sh.template` の 2 つのプレースホルダを**絶対パス**へ置換する。
   - `{{REVIEWCOMPASS_PYTHON}}`：依存（PyYAML 等）導入済みの Python 実行系
   - `{{REVIEWCOMPASS_DIR}}`：配布物 root
2. 置換後のファイルを、対象アプリの `.claude/hooks/pre-bash-precheck.sh` と `.codex/hooks/pre-bash-precheck.sh` の両方へ同一内容で複製する。同名の既存ファイルがある場合は上書きせず、既存内容と置換後の内容を利用者へ提示して扱いを確認する。
3. 置換後の `session-record-capture-current-on-todo.sh.template` は、対象アプリの `.codex/hooks/session-record-capture-current-on-todo.sh` に配置する。同名の既存ファイルがある場合は上書きせず、既存内容と置換後の内容を利用者へ提示して扱いを確認する。
4. `templates/hooks/claude-settings.json.template` と `templates/hooks/codex-hooks.json.template` から、`.claude/settings.json` と `.codex/hooks.json` を作る。いずれも既存ファイルがある場合は上書きせず、hooks キーだけを既存へ合流させる（合流して書き込む内容を、書き込み前に利用者へ提示する）。
5. 静的チェック：複製した hook ファイルに未置換トークン（`{{`）が残っていないこと、置換先のパスが実在することを確認する。
6. Codex のセッション取り込み hook は `PostToolUse` に登録し、`TODO_NEXT_SESSION.md` の内容 hash が前回保存時から変わった場合だけ、現セッション rollout を `.reviewcompass/runtime/session-record-drafts/codex-<session_id>.md` へ下書き保存する。下書き先はテスト時に `RC_SESSION_DRAFT_DIR` で差し替えられる。現セッション途中版を `.reviewcompass/evidence/sessions/` と `docs/sessions/` へ直接作らない。Codex には SessionStart 相当も無いため、正式な 2 層記録は自動昇格せず、次セッション冒頭または利用者が明示した時点で `tools/session-record-promote-draft.py --session-id <id> --source codex --current-session-id <current-id>` により作る。`<current-id>` は、今セッションで TODO 更新 hook を一度走らせた後、対象アプリの `.reviewcompass/runtime/session-record-capture-current-on-todo.jsonl` にある最新の `selected` event の `selected_session_id` を使う。`selected` が無く current `session_id` を取得できない場合は昇格せず、明示 backfill に戻す。`UserPromptSubmit` は発話ごとに呼ばれ得るため使用しない。動作確認では、対象アプリの `.reviewcompass/runtime/session-record-capture-current-on-todo.jsonl` を確認する。`todo_changed`、`selected`、`drafted`、`draft_failed`、`todo_unchanged`、`baseline_recorded` などが出る。あわせて `git status --short` で正式 2 層記録が増えていないことを確認する。`ignored_event` が出た場合は、`PostToolUse` 以外へ誤登録されているため hook 設定を修正する。
7. TODO を更新しないセッション、クラッシュ、hook 失敗、または Codex の `session_id` が取れない場合は、自動 fallback を追加せず、終了済みの対象 rollout を指定して `tools/session-record-backfill.py --session <jsonl> --source codex` を明示実行する。
8. 復旧手順：hook が「hook 設定不備」を理由に拒否する場合は、プレースホルダの置換値を確認して再置換する（テンプレートから作り直してよい）。

## 11. 操縦 LLM 別の既定 variant

review-run の variant（モデルの組）は、起草者（操縦 LLM）と検証者の独立を保つため、操縦 LLM に応じた既定を使う。

| 操縦 LLM | 3 役 review-run の既定 | 小規模 1 体検証の既定 |
| --- | --- | --- |
| Claude Code | 接尾辞なしの `*_independent_3way` 系 | `post_write_verification_google`（共通） |
| Codex CLI | `*_independent_3way_codex_operator` 系 | 同上（共通） |

proxy_model（人の判断を代行させる場合のモデル）も、操縦 LLM と別系列のモデルを選ぶ。

上記以外の LLM で操縦する場合は、独断で進めず利用者に確認し、「起草者（操縦 LLM）と同系列のモデルを反証役・判定役・単独検証役に置かない」という独立性の原則に従って variant を選ぶ。その操縦 LLM 向けの既定 variant の追加は、第3者配布時の再検討事項とする。
