# memory リンク是正と段階 3 フック実運用観察（2026-05-25 セッション 24 末）

最終更新：2026-05-25 セッション 24

本メモは ReviewCompass の 2026-05-25 セッション 24 末で実施した次の 2 件を記録する：

1. 段階 3 フック導入に関連した memory 既存ファイルの再検討と更新
2. 段階 3 フックの本セッション内自動発動の観察結果

## 1. memory ファイル更新（規律 4／5 と旧リンク是正）

### 1.1 規律 4「workflow precheck を必ず呼ぶ」への追記

ファイル：`~/.claude/projects/.../memory/feedback_workflow_precheck_invocation.md`

追記：「段階 1 と段階 3 の責務分担（2026-05-25 セッション 24 段階 3 導入後）」節を新設。

要点：

- 段階 3 フック（`.claude/hooks/pre-bash-precheck.sh`）が Bash の git commit／push を PreToolUse で自動検査するようになった
- **依然として LLM が必ず呼ぶ**：spec.json 修正（Edit／Write）の直前。段階 3 は範囲案 2 のうち Bash 系のみ実装のため、Edit／Write の spec.json 検知は未対応
- **LLM が呼ぶことが望ましい**：git commit／git push の直前。段階 3 が自動発動するが、LLM が事前に呼べば応答内で verdict／reasons を共有でき、人間判断との連携が滑らか
- **「呼び忘れ」の救済**：段階 3 フックが exit 2 で遮断するため、LLM の見落とし時も Bash 系はブロックが効く

合わせて旧リンク 2 件を修正：
- `[[approval-required]]` → `[[approval-operation]]`
- `[[no-unilateral-approach-change]]` → `[[no-unilateral-action]]`

### 1.2 規律 5「承認の運用」への追記

ファイル：`~/.claude/projects/.../memory/feedback_approval_operation.md`

追記：「機械検査は承認の代替ではない（2026-05-25 セッション 24 段階 3 導入後）」節を新設。

要点：

- 段階 3 フックの exit 0（OK）判定は「機械的整合は通過」を意味するだけで、「利用者承認が取れている」とは別問題
- 利用者明示承認の出典は依然として LLM が応答内で引用する責務
- フック通過を承認の代替として扱わない

### 1.3 旧リンク是正（派生対処）

統廃合の見落としを発見し是正：

| ファイル | 旧リンク | 新リンク |
|---|---|---|
| `feedback_concise_complete_report.md` | `[[completion-verification-protocol]]` ×2 | `[[facts-vs-interpretation]]` |
| `feedback_concise_complete_report.md` | `[[no-unilateral-approach-change]]` ×2 | `[[no-unilateral-action]]` |
| `feedback_concise_complete_report.md` | `[[separate-facts-from-interpretation]]` ×1 | `[[facts-vs-interpretation]]` |
| `feedback_concise_complete_report.md` | `[[reactive-rewriting-model]]` | （撤去済み、参照行ごと削除） |
| `feedback_reopen_procedure_for_settled_topics.md` | `[[no-implicit-approval]]` | `[[approval-operation]]` |
| `feedback_reopen_procedure_for_settled_topics.md` | `[[explicit-approval-citation-required]]` | `[[approval-operation]]` |

最終確認：旧リンク残存なし。

### 1.4 規律 6 据え置き理由

「事実と解釈の分離」への「stage-3 hook 自動発動エントリは別扱い」の追記候補は、本セッション内では据え置き。次セッション以降の実運用観察後に判断（利用者明示承認 論点 c＝(い)、2026-05-25 セッション 24）。

## 2. 段階 3 フックの本セッション内自動発動の観察

### 2.1 観察結果（重要な発見）

セッション 24 末（フック導入から約 1 時間後）に `docs/logs/workflow-precheck.log` を確認したところ：

- 総エントリ数：24
- **stage-3 hook 自動発動エントリ：8 件**（rationale が `[stage-3 hook auto-invocation]` で始まる）
- 内訳：commit 系 4 件 ＋ push 系 4 件
- 全 8 件すべて verdict=OK（exit 0）で通過

### 2.2 当初想定との差分

当初の WORKFLOW_PRECHECK.md §12 では、`.claude/settings.json` の hooks 設定は session 開始時の状態で固定されると想定していた。しかし実測では：

- 本セッション中に `.claude/settings.json` を更新（hooks セクションを追加、コミット `9456085`）した直後から、Claude Code が新しい hooks 設定を読み込み、Bash 呼び出しごとに自動発動を開始していた
- これは update-config スキルの注意書き（「the settings watcher isn't watching `.claude/` — it only watches directories that had a settings file when this session started」）の挙動とは異なる
- 推測：`.claude/settings.json` 自体は session 開始時から存在していた（事前にコミット `662bffb` で許可ルールのみで作成済み）ため、watcher の対象に既に入っていた。hooks セクションの追加は既存ファイルへの編集として認識され、設定が再読み込みされた可能性

### 2.3 段階 3 フックの実運用上の正しさ

8 件すべて：

- 適切な subcommand 検出（commit／push）
- `rationale` プレフィックスは `[stage-3 hook auto-invocation]` で正しく付与
- 後続に元コマンド全文を引用（commit メッセージや push の引数を含む）
- 段階 2 スクリプトが正しく実行され OK 判定
- ログに JSON Lines 形式で記録

実運用で仕様どおり機能していることを確認。

### 2.4 副次効果

- **段階 1（LLM）と段階 3（フック）の二重発動**：私が手動で段階 2 を呼んだ後、フックがツール呼び出し時に再度段階 2 を呼ぶ二重発動が発生。ただしログには別エントリとして記録され、双方の rationale プレフィックスで区別できる（手動は `--rationale "...利用者明示承認「ア」..."`、フックは `--rationale "[stage-3 hook auto-invocation] ..."`）
- **無害な性能影響**：二重発動による追加コストは無視可能（段階 2 スクリプトは数百ミリ秒で完了）
- **ログの肥大化**：1 つの git 操作で 2 エントリ書かれるため、長期運用ではログサイズが増える。`.gitignore` 対象のためリポジトリには影響しないが、個別環境のディスク使用量に注意

## 3. 残課題（次セッション以降）

### 3.1 規律 6 への追記判断

段階 3 フック自動発動エントリと LLM 主体エントリの区別を規律 6「事実と解釈の分離」に追記するか、次セッション開始時の実運用観察後に判断。

### 3.2 二重発動の最適化（任意）

段階 1（LLM）と段階 3（フック）の二重発動が無害だが冗長。最適化案：

- 段階 3 フックが過去 30 秒以内に同操作の段階 2 ログがあれば skip する（仕様 §12.2 旧案、却下された案）
- 現状は無害なため最適化は不要、ただし長期運用で再検討

### 3.3 Edit／Write の spec.json 検知（範囲案 3 への拡張）

仕様 §3.3 で範囲案 3 への拡張は別仕様改訂として位置付け。前倒し検討の余地あり（フェーズ 4 以降）。

## 4. 関連参照

- 計画書 §5.8 補助層 C：`docs/plan/reconstruction-plan-2026-05-21.md`
- 段階 2 仕様：`docs/operations/WORKFLOW_PRECHECK.md`
- 段階 3 フック：`.claude/hooks/pre-bash-precheck.sh`、`.claude/hooks/README.md`
- セッション 24 振り返り：`docs/notes/2026-05-25-session-24-retrospective.md`
- 共存モデル議論：`docs/notes/2026-05-25-workflow-pre-check-and-discipline-consolidation.md`
- 効果測定：`docs/notes/2026-05-25-discipline-consolidation-effect-measurement.md`
