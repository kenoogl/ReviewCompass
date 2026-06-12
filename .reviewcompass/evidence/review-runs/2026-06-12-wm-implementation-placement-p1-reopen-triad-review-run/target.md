# レビュー対象：reopen D-0（placement-p1-path-contracts）workflow-management implementation 変更

## 0. variant 選定理由（実行前ゲートの記録）

- 使用 variant：`implementation_review_independent_3way`（context: triad_review、API 3 社独立）
- 役割：primary=anthropic-api/claude-sonnet-4-6、adversarial=openai-api/gpt-5.5、judgment=gemini-api/gemini-3.1-pro-preview
- 選定理由：本 reopen の design・tasks triad-review と同一構成（利用者承認 2026-06-12「承認承認」、所見判断は
  proxy_model 委任「proxy_modelで自律実行」。正本は SESSION_WORKFLOW_GUIDE §3.3 (a-3)）

## 1. レビューの位置付け

reopen D-0 の第3過程、workflow-management implementation フェーズの triad-review。design・tasks は各 gate 完了・
利用者承認済み。対象は tasks 確定本文（T-004 の凍結期責務・完了条件 5〔5 観点〕・凍結期挙動テスト〔3 パス × 5 観点〕）
どおりに TDD で実装した working tree 差分。

確定済み上流契約の要点（wm design §実行時生成物の凍結期（P3 まで）の扱い）：

- 3 パスの書き込みは常に新配置：検査ログ `.reviewcompass/runtime/logs/workflow-precheck.log`〔旧 docs/logs/〕、
  effective prompt `.reviewcompass/runtime/effective-prompts/`〔旧 .reviewcompass/effective-prompts/〕、
  commit 承認記録 `.reviewcompass/runtime/approvals/commit-approval.json`〔旧 .reviewcompass/approvals/commit-approval.json〕
- 旧配置への新規書き込みなし（凍結。効力発生は P1 実装反映コミットと同時。互換終了は P3 専用 reopen、暗黙終了なし）
- 読み取りは新→旧の順のフォールバック（P3 まで）。新旧競合時は新配置を採用
- 凍結済み旧成果物の不変性（git 追跡履歴で検出、ce と同一判定規則）

## 2. TDD 経過（実装証跡）

- 赤フェーズ：凍結期挙動テスト 12 件を先行作成し失敗確認（11 失敗・1 件〔承認レコードの旧フォールバック読み取り〕は
  現行でも成立する契約）
- 緑フェーズ：全テスト pass（tools 212 件含むディレクトリ別 計 912 件、回帰なし）。実機 next で effective prompt・
  検査ログが runtime 区画へ生成され gitignore が効くことを確認
- 手戻り：緑フェーズで guarded-git-commit の消費テスト 1 件が失敗 → テストヘルパー _write_commit_approval が
  旧配置へ書いていたため、契約（書き込み常時新配置）どおりヘルパーを新配置へ更新して解消
- 補足（実装上の制約の明示）：ReviewCompass 自身では旧 3 パスはいずれも gitignore 対象（未追跡）のため、
  凍結違反検出器が git 履歴で不変性を立証できるのは旧配置を追跡している構成（対象アプリ等）に限る。
  未追跡の旧成果物の凍結は書き込み経路のテスト（観点 1・2）で担保（placement_freeze.py 冒頭に注記）

## 3. レビュー観点

1. tasks 確定本文（T-004 完了条件 5 の 5 観点・凍結期挙動テスト 15 観点・境界条件）との対応
2. design 凍結期共通契約と実装挙動の一致（書き込み先・読み取り順・競合時新優先・凍結不変性）
3. 旧配置への書き込み経路の残存（切替漏れ。--log-path 上書きは既存仕様として維持）
4. テストが契約を網羅し弱めていないか
5. 例外系・境界条件（新旧競合・旧のみ存在・新旧とも不在時の既存挙動不変・gitignore 下の凍結検出限界）
6. 運用上の整合（.gitignore の runtime 追加、post-write 対象除外の新旧両対応）

## 3.5 round-2 注記：round-1 所見の適用（proxy_model 判断、2026-06-12）

round-1 の 8 所見（6 クラスタ）は proxy_model（gemini-3.1-pro-preview）が判断した（証跡 `proxy-decisions/`・
`approval-proxy-2026-06-12.yaml`）。適用内容（TDD：赤 4 件確認 → 緑、全テスト pass）：

- K1（must-fix・案 A）：共有モジュール `tools/check_workflow_action/runtime_paths.py` を新設し定数と読み取り解決を集約。
  check-workflow-action.py・guarded-git-commit.py が参照し二重定義を解消。run_role.py の
  `_resolve_effective_prompt_sha256`（実運用の読み取り経路）へ新→旧フォールバックを接続
- K2（should-fix・案 B）：ゲート自動統合は見送り（tasks 確定要件は 15 観点のテスト機械検証）、
  WORKFLOW_PRECHECK_DETAILS.md §8.1 に凍結期の扱いと凍結検査の手動実行手順を記載（ce C7-B と同型）
- K3（must-fix・案 A）：検出器の未追跡列挙に `--exclude-standard` を付与し、gitignore 対象として現存する凍結成果物の
  誤検知を排除（ce との規則差＝前提の違いを docstring に明記）。誤検知防止テスト追加
- K4（should-fix・案 A）：approvals の凍結対象を契約どおり `commit-approval.json` 単体へ限定。範囲外ファイルの
  非検出テスト追加
- K5（should-fix・案 A）：削除を `deleted_after_freeze` の専用種別で報告（ステージ前削除が索引に残る点はファイル実体で
  現存判定）。削除テストを専用種別の期待値へ更新。「削除が検出されない」との round-1 主張は事実誤認と注記
- K6（leave-as-is）：旧配置の未消費レコード残置は、新→旧の解決順により新配置の消費済み記録が恒久に遮蔽するため
  再承認リスクなし
- K7（should-fix・案 A）：resolver の docstring へ入力前提（新配置形式の相対パス）を明記

round-2 は適用後差分の収束確認である。

## 3.6 round-3 注記：round-2 所見の適用（proxy_model 判断、2026-06-12）

round-2 の 6 所見は proxy_model が判断した（証跡 `proxy-decisions/round-2/`・`approval-proxy-2026-06-12-round-2.yaml`）。

- M1（ERROR）＝leave-as-is：操縦 LLM の実証検査（リポジトリ外 cwd・スクリプト実行で旧配置 sha を正しく解決、
  run_role が自身の位置からプロジェクトルートを sys.path へ挿入）により主張を反証
- M3（must-fix・案 A）：guarded-git-commit の消費読み取りを共有 resolver（resolve_commit_approval_path）へ置換
- M2（should-fix・案 A）：runtime_paths へ検査ログの読み取り resolver（resolve_precheck_log_read_path、新→旧）を追加し
  テスト 2 件を付与
- M4（should-fix・案 A）：resolver の docstring へ str/Path 受け入れと内部 str 化を明記
- M5（should-fix・案 A）：凍結検査の git 実行失敗を捕捉し、freeze_commit の確認を促す平易なメッセージで再送出
- M6（INFO）＝leave-as-is

追加の追従：フックテストの一時リポジトリ複製対象へ runtime_paths.py を追加（新パッケージへの依存）、
配布一覧 deploy-manifest.yaml へ tools/check_workflow_action/** を追加（配布物での ModuleNotFoundError を防止）。
全テスト green（ディレクトリ別 計 917 件）。round-3 は適用後差分の収束確認である。

## 3.7 round-4 注記：round-3 所見の適用（proxy_model 判断、2026-06-12）

round-3 の 4 所見は proxy_model が判断した（証跡 `proxy-decisions/round-3/`・`approval-proxy-2026-06-12-round-3.yaml`）。
N1（ERROR＋同根 INFO、must-fix・案 A）＝resolver を双方向対応へ：旧形式パス入力（P1 前の記録が保持する
`.reviewcompass/effective-prompts/...`）も新形式へ正規化して新→旧の順で存在確認（新旧競合時は新を正）。
新形式・旧形式・絶対パスの境界テスト 3 件を追加し docstring を追従。N3・N4＝leave-as-is。
round-4 は proxy 判定 R4-A による適用後の収束確認である（全テスト green、tools＋hooks 237 件）。

## 4. 実装差分（git diff、working tree、round-3 所見適用後）

```diff
diff --git a/.gitignore b/.gitignore
index a5a56c58..fea009f5 100644
--- a/.gitignore
+++ b/.gitignore
@@ -5,6 +5,10 @@ __pycache__/
 .pytest_cache/
 *.egg-info/
 
+# 実行時生成物の runtime 区画（検査ログ・effective prompt・commit 承認レコード。
+# 2026-06-12 配置規約 PLC-DEC-004：原則 git 無視。旧配置の個別エントリは凍結期（P3 まで）保持）
+.reviewcompass/runtime/
+
 # 補助層 C 段階 2 スクリプトの判定ログ（実行ごとに増えるため、リポジトリでは管理しない）
 # 仕様：docs/operations/WORKFLOW_PRECHECK.md §8
 docs/logs/workflow-precheck.log
diff --git a/deploy-manifest.yaml b/deploy-manifest.yaml
index 23544cc1..dc1ce150 100644
--- a/deploy-manifest.yaml
+++ b/deploy-manifest.yaml
@@ -88,6 +88,8 @@ include:
 
   - path: tools/check-workflow-action.py
     reason: Workflow state and irreversible-action guard CLI.
+  - path: tools/check_workflow_action/**
+    reason: Runtime placement constants, read resolvers, and freeze checker imported by the guard CLI.
   - path: tools/document_link_lint.py
     reason: Document link and prompt-source reference lint.
   - path: tools/deployment_independence_lint.py
diff --git a/docs/operations/WORKFLOW_PRECHECK_DETAILS.md b/docs/operations/WORKFLOW_PRECHECK_DETAILS.md
index 2e420df2..42fb547a 100644
--- a/docs/operations/WORKFLOW_PRECHECK_DETAILS.md
+++ b/docs/operations/WORKFLOW_PRECHECK_DETAILS.md
@@ -182,10 +182,41 @@ JSON 出力は、少なくとも次のキーを含む。
 
 既定パス：
 
-- `docs/logs/workflow-precheck.log`
+- `.reviewcompass/runtime/logs/workflow-precheck.log`（旧 `docs/logs/workflow-precheck.log` からの変更は
+  2026-06-12 配置規約 PLC-DEC-004〜005・009〜011 反映。旧ログは凍結、読み取り互換は P3 まで）
 
 `--log-path` でテスト用の隔離パスへ上書きできる。
 
+### 8.1 実行時生成物の凍結期（P3 まで）の扱い
+
+検査ログ・effective prompt（`.reviewcompass/runtime/effective-prompts/`、旧 `.reviewcompass/effective-prompts/`）・
+commit 承認レコード（`.reviewcompass/runtime/approvals/commit-approval.json`、旧 `.reviewcompass/approvals/commit-approval.json`）の
+3 パスは、書き込みを常に新配置（runtime 区画、原則 git 無視）へ行い、読み取りは新→旧の順でフォールバックする
+（新旧競合時は新配置を正とする）。契約の正本は workflow-management design §実行時生成物の凍結期（P3 まで）の扱い。
+定数と読み取り解決の実装正本は `tools/check_workflow_action/runtime_paths.py`。
+
+凍結検査の手動実行手順（ゲートへの自動統合は行わず、手動運用とする）：
+
+1. 凍結境界（P1 実装反映コミット＝書き込み先切替のコミット）を特定する。例：
+
+   ```bash
+   git log --reverse --format=%H -S "runtime/logs/workflow-precheck" -- tools/check_workflow_action/runtime_paths.py | head -1
+   ```
+
+2. 旧 3 パスへの凍結違反（追加・変更・削除）を検出する。例：
+
+   ```bash
+   PYTHONPATH=. .venv/bin/python3 -c "
+   from tools.check_workflow_action.placement_freeze import check_runtime_placement_freeze
+   for v in check_runtime_placement_freeze('.', '<freeze-commit>'):
+     print(v)
+   "
+   ```
+
+   注記：ReviewCompass 自身では旧 3 パスは gitignore 対象（未追跡）のため、git 履歴で不変性を立証できるのは
+   旧配置を追跡している構成（対象アプリ等）に限る。未追跡の旧成果物の凍結は書き込み経路のテスト
+   （`tests/tools/test_runtime_placement_freeze.py`）で担保する。
+
 ## 9. テスト観点
 
 主要な判定条件は `tests/tools/test_check_workflow_action.py` で検証する。最低限、次を覆う。
diff --git a/tests/hooks/test_pre_bash_precheck.py b/tests/hooks/test_pre_bash_precheck.py
index 8cdb593e..3e2e7b46 100644
--- a/tests/hooks/test_pre_bash_precheck.py
+++ b/tests/hooks/test_pre_bash_precheck.py
@@ -106,6 +106,12 @@ def _setup_git_repo_with_script(tmpdir):
   # check-workflow-action.py が同階層から import する lint 部品も併せてコピーする
   shutil.copy(REPO_ROOT / "tools" / "deployment_independence_lint.py", tools_dir)
   shutil.copy(REPO_ROOT / "tools" / "document_link_lint.py", tools_dir)
+  # 実行時生成物パスの定数・読み取り解決（check_workflow_action パッケージ）も併せてコピーする
+  package_dir = tools_dir / "check_workflow_action"
+  package_dir.mkdir()
+  shutil.copy(
+    REPO_ROOT / "tools" / "check_workflow_action" / "runtime_paths.py", package_dir
+  )
   subprocess.run(
     [
       "git",
@@ -113,6 +119,7 @@ def _setup_git_repo_with_script(tmpdir):
       "tools/check-workflow-action.py",
       "tools/deployment_independence_lint.py",
       "tools/document_link_lint.py",
+      "tools/check_workflow_action/runtime_paths.py",
     ],
     cwd=str(tmpdir), check=True, capture_output=True,
   )
diff --git a/tests/tools/test_check_workflow_action.py b/tests/tools/test_check_workflow_action.py
index cd11a9a5..b55ee0d4 100644
--- a/tests/tools/test_check_workflow_action.py
+++ b/tests/tools/test_check_workflow_action.py
@@ -3763,8 +3763,8 @@ def _write_commit_approval(
   include_execution_delegation=True,
   execution_instruction="コミット",
 ):
-  """commit 事前検査用のユーザ承認レコードを書く"""
-  approval_dir = Path(tmpdir) / ".reviewcompass" / "approvals"
+  """commit 事前検査用のユーザ承認レコードを書く（書き込みは常に新配置＝runtime 区画）"""
+  approval_dir = Path(tmpdir) / ".reviewcompass" / "runtime" / "approvals"
   approval_dir.mkdir(parents=True, exist_ok=True)
   approval_path = approval_dir / "commit-approval.json"
   if target_sha256 is None:
diff --git a/tools/api_providers/run_role.py b/tools/api_providers/run_role.py
index b9686a5f..b7591b3a 100644
--- a/tools/api_providers/run_role.py
+++ b/tools/api_providers/run_role.py
@@ -403,12 +403,19 @@ def _parse_argv(argv: Optional[List[str]]) -> argparse.Namespace:
 
 
 def _resolve_effective_prompt_sha256(path_value: Optional[str], sha_value: Optional[str]) -> Optional[str]:
-  """effective prompt sha256 を明示値またはファイル内容から返す。"""
+  """effective prompt sha256 を明示値またはファイル内容から返す。
+
+  凍結期（P3 まで）は読み取りを新→旧の順でフォールバックする
+  （正本は check_workflow_action/runtime_paths.py）。
+  """
   if sha_value:
     return sha_value
   if not path_value:
     return None
-  path = Path(path_value)
+  from tools.check_workflow_action.runtime_paths import resolve_effective_prompt_read_path
+
+  resolved = resolve_effective_prompt_read_path(Path.cwd(), path_value)
+  path = Path(resolved)
   if not path.is_file():
     return None
   return _sha256_file(path)
diff --git a/tools/check-workflow-action.py b/tools/check-workflow-action.py
index 8e442cfb..0576b1bb 100644
--- a/tools/check-workflow-action.py
+++ b/tools/check-workflow-action.py
@@ -34,11 +34,22 @@ from document_link_lint import lint_path_texts as lint_document_link_texts
 
 
 # 既定のログファイルパス（呼び出し時の cwd 相対、仕様 §8.2）
-DEFAULT_LOG_PATH = "docs/logs/workflow-precheck.log"
-DEFAULT_COMMIT_APPROVAL_PATH = ".reviewcompass/approvals/commit-approval.json"
+# 実行時生成物 3 パスは runtime 区画へ集約（2026-06-12 配置規約 P1。
+# 旧配置は凍結・読み取り互換のみ P3 まで。定数と読み取り解決の正本は
+# check_workflow_action/runtime_paths.py、契約の正本は wm design §実行時生成物の凍結期（P3 まで）の扱い）
+from check_workflow_action.runtime_paths import (
+  DEFAULT_LOG_PATH,
+  LEGACY_LOG_PATH,
+  DEFAULT_COMMIT_APPROVAL_PATH,
+  LEGACY_COMMIT_APPROVAL_PATH,
+  DEFAULT_EFFECTIVE_PROMPT_DIR,
+  LEGACY_EFFECTIVE_PROMPT_DIR,
+  resolve_commit_approval_path,
+  resolve_effective_prompt_read_path,
+)
+
 DEFAULT_LAST_COMMIT_PRECHECK_PATH = ".git/reviewcompass/last-commit-precheck.json"
 DEFAULT_DISCIPLINE_MAP_PATH = "docs/operations/WORKFLOW_DISCIPLINE_MAP.yaml"
-DEFAULT_EFFECTIVE_PROMPT_DIR = ".reviewcompass/effective-prompts"
 DEFAULT_CARRY_FORWARD_REGISTER_PATH = "learning/workflow/carry-forward-register/reviewcompass-import.yaml"
 DEFAULT_CARRY_FORWARD_SOURCE_PATH = (
   "learning/workflow/carry-forward-register/sources/"
@@ -2391,9 +2402,10 @@ def staged_file_sha256(cwd, filepath):
 
 def validate_commit_approval(cwd, staged_files):
   """commit 用ユーザ承認レコードを検査する"""
-  approval_path = Path(cwd) / DEFAULT_COMMIT_APPROVAL_PATH
+  resolved_relative = resolve_commit_approval_path(cwd)
+  approval_path = Path(cwd) / resolved_relative
   approval_state = {
-    "path": DEFAULT_COMMIT_APPROVAL_PATH,
+    "path": resolved_relative,
     "exists": approval_path.exists(),
     "valid": False,
     "target_files": [],
@@ -3856,8 +3868,9 @@ def is_post_write_verification_target(path):
     return False
   # ツール自身の実行ログは正本文書ではないため対象外
   # （discipline_post_write_verification.md の対象定義「正本文書」に実装を合わせる。
-  #   docs/logs/ 配下の他ファイル（autonomous-parallel の計画記録等）は対象のまま）
-  if path == DEFAULT_LOG_PATH:
+  #   docs/logs/ 配下の他ファイル（autonomous-parallel の計画記録等）は対象のまま。
+  #   凍結済み旧ログも引き続き対象外）
+  if path in (DEFAULT_LOG_PATH, LEGACY_LOG_PATH):
     return False
   if path == "TODO_NEXT_SESSION.md":
     return True
diff --git a/tools/guarded-git-commit.py b/tools/guarded-git-commit.py
index bf52be6e..2b41dfef 100644
--- a/tools/guarded-git-commit.py
+++ b/tools/guarded-git-commit.py
@@ -9,15 +9,25 @@ from datetime import datetime, timezone
 from pathlib import Path
 
 
-DEFAULT_COMMIT_APPROVAL_PATH = ".reviewcompass/approvals/commit-approval.json"
+# 実行時生成物の runtime 区画集約（2026-06-12 配置規約 P1）。旧配置は凍結・読み取り互換のみ P3 まで。
+# 定数と読み取り解決の正本は check_workflow_action/runtime_paths.py
+from check_workflow_action.runtime_paths import (
+  DEFAULT_COMMIT_APPROVAL_PATH,
+  resolve_commit_approval_path,
+)
+
 DEFAULT_LAST_COMMIT_PRECHECK_PATH = ".git/reviewcompass/last-commit-precheck.json"
 
 
 def consume_commit_approval(cwd):
-  """commit 成功後に承認レコードを消費済みにする"""
-  approval_path = Path(cwd) / DEFAULT_COMMIT_APPROVAL_PATH
+  """commit 成功後に承認レコードを消費済みにする
+
+  読み取りは新→旧の順のフォールバック。書き込みは常に新配置へ行い、
+  凍結済み旧記録は変更しない（wm design §実行時生成物の凍結期（P3 まで）の扱い）。
+  """
+  read_path = Path(cwd) / resolve_commit_approval_path(cwd)
   try:
-    approval = json.loads(approval_path.read_text(encoding="utf-8"))
+    approval = json.loads(read_path.read_text(encoding="utf-8"))
   except (OSError, json.JSONDecodeError) as e:
     print(f"warning: 承認レコードの消費済み記録に失敗しました: {e}", file=sys.stderr)
     return
@@ -31,8 +41,10 @@ def consume_commit_approval(cwd):
 
   approval["consumed"] = True
   approval["consumed_at"] = datetime.now(timezone.utc).isoformat()
+  write_path = Path(cwd) / DEFAULT_COMMIT_APPROVAL_PATH
   try:
-    approval_path.write_text(
+    write_path.parent.mkdir(parents=True, exist_ok=True)
+    write_path.write_text(
       json.dumps(approval, ensure_ascii=False, indent=2) + "\n",
       encoding="utf-8",
     )
```

## 5. 新規ファイル全文

--- 新規ファイル: tools/check_workflow_action/runtime_paths.py ---

"""実行時生成物 3 パスの配置定数と読み取り解決（2026-06-12 配置規約 P1）。

正本は workflow-management design §実行時生成物の凍結期（P3 まで）の扱い。
書き込みは常に新配置（runtime 区画）、読み取りは新→旧の順のフォールバック（P3 まで）、
新旧競合時は新配置を採用する。check-workflow-action.py・guarded-git-commit.py・
run_role.py が本モジュールを参照し、定数の二重定義を持たない。
"""
from pathlib import Path

DEFAULT_LOG_PATH = ".reviewcompass/runtime/logs/workflow-precheck.log"
LEGACY_LOG_PATH = "docs/logs/workflow-precheck.log"
DEFAULT_COMMIT_APPROVAL_PATH = ".reviewcompass/runtime/approvals/commit-approval.json"
LEGACY_COMMIT_APPROVAL_PATH = ".reviewcompass/approvals/commit-approval.json"
DEFAULT_EFFECTIVE_PROMPT_DIR = ".reviewcompass/runtime/effective-prompts"
LEGACY_EFFECTIVE_PROMPT_DIR = ".reviewcompass/effective-prompts"


def resolve_precheck_log_read_path(cwd):
  """検査ログの読み取りパスを新→旧の順で解決する（凍結期の読み取り互換、P3 まで）

  ツール自身は新配置へ追記するのみで、本関数は過去ログを読む利用者・外部ツール向けの解決を提供する。
  """
  if (Path(cwd) / DEFAULT_LOG_PATH).exists():
    return DEFAULT_LOG_PATH
  if (Path(cwd) / LEGACY_LOG_PATH).exists():
    return LEGACY_LOG_PATH
  return DEFAULT_LOG_PATH


def resolve_commit_approval_path(cwd):
  """承認レコードの読み取りパスを新→旧の順で解決する（凍結期の読み取り互換、P3 まで）"""
  if (Path(cwd) / DEFAULT_COMMIT_APPROVAL_PATH).exists():
    return DEFAULT_COMMIT_APPROVAL_PATH
  if (Path(cwd) / LEGACY_COMMIT_APPROVAL_PATH).exists():
    return LEGACY_COMMIT_APPROVAL_PATH
  return DEFAULT_COMMIT_APPROVAL_PATH


def resolve_effective_prompt_read_path(cwd, relative_path):
  """effective prompt の読み取りパスを新→旧の順で解決する（凍結期の読み取り互換、P3 まで）

  入力前提：relative_path は cwd 相対の新配置形式または旧配置形式のパスを想定する。
  str と Path のどちらも受け入れ、内部で str 化して扱う。
  どちらの形式で渡されても新配置を先に確認し、無ければ旧配置を確認する
  （新旧競合時は新配置を正とする。P1 前の記録が保持する旧形式パスにも適用）。
  どちらにも実体が無い場合と、新旧いずれの形式でもないパス（絶対パス等）はそのまま返す（変換しない）。
  """
  path_text = str(relative_path)
  if path_text.startswith(DEFAULT_EFFECTIVE_PROMPT_DIR + "/"):
    suffix = path_text[len(DEFAULT_EFFECTIVE_PROMPT_DIR):]
  elif path_text.startswith(LEGACY_EFFECTIVE_PROMPT_DIR + "/"):
    suffix = path_text[len(LEGACY_EFFECTIVE_PROMPT_DIR):]
  else:
    return relative_path
  runtime_relative = DEFAULT_EFFECTIVE_PROMPT_DIR + suffix
  legacy_relative = LEGACY_EFFECTIVE_PROMPT_DIR + suffix
  if (Path(cwd) / runtime_relative).exists():
    return runtime_relative
  if (Path(cwd) / legacy_relative).exists():
    return legacy_relative
  return relative_path

--- 新規ファイル: tools/check_workflow_action/placement_freeze.py ---

"""実行時生成物の旧配置に対する凍結違反検出（wm tasks T-004 観点 5）。

凍結集合の判定基準は git 追跡履歴を正本とする：P1 実装反映コミット時点で旧配置に
存在したファイルが凍結集合であり、それ以降の追加・変更・削除を違反として検出する。
判定規則は conformance-evaluation の凍結違反検出と同一
（正本は wm design §実行時生成物の凍結期（P3 まで）の扱い）。

注記：ReviewCompass 自身では旧 3 パスはいずれも gitignore 対象（未追跡）のため、
git 履歴で不変性を立証できるのは旧配置を追跡している構成（対象アプリ等）に限られる。
未追跡（ignore 対象）の旧成果物の凍結は、書き込み経路の凍結期挙動テスト（観点 1・2）で担保する。
このため未追跡の列挙には --exclude-standard を付け、ignore されたまま現存する凍結成果物を
誤検知しない（conformance-evaluation の検出器は旧記録が git 追跡済みのため ignored 込みで
検出するのが正しく、前提の違いによる意図的な規則差である）。
"""
import re
import subprocess
from pathlib import Path

# 凍結済み旧配置（P3 まで読み取り互換のみ。新規追加・変更・削除は凍結違反。
# 承認記録は契約どおり commit-approval.json 単体に限定する）
LEGACY_RUNTIME_PATTERNS = (
  re.compile(r"^docs/logs/workflow-precheck\.log$"),
  re.compile(r"^\.reviewcompass/effective-prompts/"),
  re.compile(r"^\.reviewcompass/approvals/commit-approval\.json$"),
)


def check_runtime_placement_freeze(cwd, freeze_commit):
  """旧 3 パスへの凍結違反（追加・変更・削除）を理由文字列のリストで返す"""
  violations = []
  for pattern in LEGACY_RUNTIME_PATTERNS:
    frozen = _matching(cwd, pattern, "ls-tree", "-r", "--name-only", freeze_commit)
    tracked = _matching(cwd, pattern, "ls-files")
    untracked = _matching(cwd, pattern, "ls-files", "--others", "--exclude-standard")
    changed = _matching(cwd, pattern, "diff", "--name-only", freeze_commit)
    current = tracked | untracked
    added = sorted(current - frozen)
    # 削除はステージ前だと索引（ls-files）に残るため、現存判定はファイル実体で行う
    deleted = sorted(
      path for path in (changed & frozen) if not (Path(cwd) / path).exists()
    )
    modified = sorted(
      path for path in (changed & frozen) if (Path(cwd) / path).exists()
    )
    violations.extend(f"added_after_freeze: {path}" for path in added)
    violations.extend(f"frozen_file_changed: {path}" for path in modified)
    violations.extend(f"deleted_after_freeze: {path}" for path in deleted)
  return violations


def _matching(cwd, pattern, *args):
  # git ls-tree はワイルドカードを解釈しないため、木全体を列挙して Python 側で絞り込む
  result = subprocess.run(
    ["git", "-C", str(Path(cwd)), *args],
    capture_output=True,
    text=True,
  )
  if result.returncode != 0:
    raise ValueError(
      "凍結検査の git 実行に失敗しました。freeze_commit が有効なコミットか、"
      f"対象が git リポジトリかを確認してください（git {args[0]}: {result.stderr.strip()[:200]}）"
    )
  return {line for line in result.stdout.splitlines() if line and pattern.match(line)}

--- 新規ファイル: tests/tools/test_runtime_placement_freeze.py ---

"""実行時生成物 3 パスの凍結期挙動テスト（wm tasks T-004、3 パス × 5 観点）。

対象契約：workflow-management design §実行時生成物の凍結期（P3 まで）の扱い
- 書き込みは常に新配置（.reviewcompass/runtime/ 配下）
- 旧配置への新規書き込みなし（凍結。効力発生は P1 実装反映コミットと同時）
- 読み取りは新→旧の順のフォールバック（P3 まで）
- 新旧競合時は新配置を採用
- 凍結済み旧成果物の不変性（git 追跡履歴で検出、conformance-evaluation と同一判定規則）

TDD 規律（AGENTS.md）に従い、本テストは実装切替前に作成する。
"""
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "tools" / "check-workflow-action.py"
GUARDED = REPO_ROOT / "tools" / "guarded-git-commit.py"
FIXTURE_BASE = REPO_ROOT / "tests" / "fixtures" / "spec-json-cases"

RUNTIME_LOG = ".reviewcompass/runtime/logs/workflow-precheck.log"
LEGACY_LOG = "docs/logs/workflow-precheck.log"
RUNTIME_PROMPT_DIR = ".reviewcompass/runtime/effective-prompts"
LEGACY_PROMPT_DIR = ".reviewcompass/effective-prompts"
RUNTIME_APPROVAL = ".reviewcompass/runtime/approvals/commit-approval.json"
LEGACY_APPROVAL = ".reviewcompass/approvals/commit-approval.json"


def _load_module(path: Path, name: str):
  tools_dir = str(REPO_ROOT / "tools")
  if tools_dir not in sys.path:
    sys.path.insert(0, tools_dir)
  spec = importlib.util.spec_from_file_location(name, path)
  module = importlib.util.module_from_spec(spec)
  spec.loader.exec_module(module)
  return module


cwa = _load_module(SCRIPT, "cwa_for_placement_tests")
guarded = _load_module(GUARDED, "guarded_for_placement_tests")
placement_freeze = _load_module(
  REPO_ROOT / "tools" / "check_workflow_action" / "placement_freeze.py",
  "placement_freeze_for_tests",
) if (REPO_ROOT / "tools" / "check_workflow_action" / "placement_freeze.py").exists() else None


def run_script(args, cwd):
  return subprocess.run(
    [sys.executable, str(SCRIPT), *args],
    cwd=str(cwd),
    capture_output=True,
    text=True,
  )


def _git(repo: Path, *args: str) -> str:
  result = subprocess.run(
    ["git", "-C", str(repo), *args],
    capture_output=True,
    text=True,
    check=True,
  )
  return result.stdout.strip()


def _git_commit_all(repo: Path, message: str) -> str:
  _git(repo, "add", "-A")
  _git(
    repo,
    "-c", "user.name=test",
    "-c", "user.email=test@example.com",
    "commit", "-m", message,
  )
  return _git(repo, "rev-parse", "HEAD")


def _write_approval(path: Path, marker: str, consumed: bool = False) -> None:
  path.parent.mkdir(parents=True, exist_ok=True)
  path.write_text(
    json.dumps(
      {
        "approved_action": "commit",
        "approved_by": "user",
        "consumed": consumed,
        "rationale": marker,
        "target_files": [],
        "target_sha256": {},
        "execution_delegation": {
          "delegated_to": "llm",
          "approved_by": "user",
          "explicit_instruction": "コミット",
        },
      },
      ensure_ascii=False,
      indent=1,
    ),
    encoding="utf-8",
  )


class PrecheckLogPlacementTests(unittest.TestCase):
  """観点 1〜4：検査ログ"""

  def setUp(self):
    self.tmpdir = tempfile.mkdtemp()
    self.addCleanup(shutil.rmtree, self.tmpdir)

  def _copy_fixture(self, fixture_name):
    src = FIXTURE_BASE / fixture_name
    dst = Path(self.tmpdir) / fixture_name
    shutil.copytree(src, dst)
    return dst

  def test_log_writes_to_runtime_placement_and_not_legacy(self):
    """観点 1・2：--log-path 省略時の既定が新配置で、旧配置に新規書き込みが発生しない"""
    cwd = self._copy_fixture("case-a-ready-for-approval")
    result = run_script(
      ["spec-set", "foundation", "requirements", "approval", "true"],
      cwd=cwd,
    )
    self.assertEqual(result.returncode, 0, result.stderr)
    self.assertTrue((cwd / RUNTIME_LOG).is_file(), "新配置へログ追記されるべき")
    self.assertFalse((cwd / LEGACY_LOG).exists(), "旧配置へ新規書き込みしてはならない")

  def test_log_legacy_only_is_preserved_and_runtime_receives_appends(self):
    """観点 3：旧ログのみ存在しても旧は凍結のまま読め、追記は新配置へ行く"""
    cwd = self._copy_fixture("case-a-ready-for-approval")
    legacy = cwd / LEGACY_LOG
    legacy.parent.mkdir(parents=True, exist_ok=True)
    legacy.write_text("frozen-legacy-line\n", encoding="utf-8")
    result = run_script(
      ["spec-set", "foundation", "requirements", "approval", "true"],
      cwd=cwd,
    )
    self.assertEqual(result.returncode, 0, result.stderr)
    self.assertEqual(
      legacy.read_text(encoding="utf-8"), "frozen-legacy-line\n",
      "凍結済み旧ログは変更されず読み取り可能であるべき",
    )
    self.assertTrue((cwd / RUNTIME_LOG).is_file())

  def test_log_conflict_appends_only_to_runtime(self):
    """観点 4：新旧両方が存在する競合時、追記は新配置のみ（新が現役の正）"""
    cwd = self._copy_fixture("case-a-ready-for-approval")
    legacy = cwd / LEGACY_LOG
    legacy.parent.mkdir(parents=True, exist_ok=True)
    legacy.write_text("frozen-legacy-line\n", encoding="utf-8")
    runtime = cwd / RUNTIME_LOG
    runtime.parent.mkdir(parents=True, exist_ok=True)
    runtime.write_text("runtime-existing-line\n", encoding="utf-8")
    result = run_script(
      ["spec-set", "foundation", "requirements", "approval", "true"],
      cwd=cwd,
    )
    self.assertEqual(result.returncode, 0, result.stderr)
    self.assertEqual(legacy.read_text(encoding="utf-8"), "frozen-legacy-line\n")
    runtime_lines = runtime.read_text(encoding="utf-8").strip().splitlines()
    self.assertGreater(len(runtime_lines), 1, "新配置のログにのみ追記されるべき")


class PrecheckLogReadResolverTests(unittest.TestCase):
  """観点 3・4：検査ログの読み取り解決（M2）"""

  def setUp(self):
    self.tmpdir = tempfile.mkdtemp()
    self.addCleanup(shutil.rmtree, self.tmpdir)

  def test_log_read_falls_back_to_legacy(self):
    cwd = Path(self.tmpdir)
    legacy = cwd / LEGACY_LOG
    legacy.parent.mkdir(parents=True, exist_ok=True)
    legacy.write_text("legacy log\n", encoding="utf-8")
    from check_workflow_action.runtime_paths import resolve_precheck_log_read_path
    self.assertEqual(resolve_precheck_log_read_path(cwd), LEGACY_LOG)

  def test_log_read_conflict_prefers_runtime(self):
    cwd = Path(self.tmpdir)
    legacy = cwd / LEGACY_LOG
    legacy.parent.mkdir(parents=True, exist_ok=True)
    legacy.write_text("legacy log\n", encoding="utf-8")
    runtime = cwd / RUNTIME_LOG
    runtime.parent.mkdir(parents=True, exist_ok=True)
    runtime.write_text("runtime log\n", encoding="utf-8")
    from check_workflow_action.runtime_paths import resolve_precheck_log_read_path
    self.assertEqual(resolve_precheck_log_read_path(cwd), RUNTIME_LOG)


class EffectivePromptPlacementTests(unittest.TestCase):
  """観点 1・3・4：effective prompt"""

  def setUp(self):
    self.tmpdir = tempfile.mkdtemp()
    self.addCleanup(shutil.rmtree, self.tmpdir)

  def test_effective_prompt_write_path_is_runtime(self):
    """観点 1：生成パスが新配置（runtime 区画）を指す"""
    relative = cwa._effective_prompt_relative_path(
      {"decision_point_refs": [{"group": "next_action_kind", "id": "stage"}]}
    )
    self.assertTrue(
      relative.startswith(RUNTIME_PROMPT_DIR + "/"),
      f"生成先は {RUNTIME_PROMPT_DIR}/ 配下であるべき: {relative}",
    )

  def test_effective_prompt_read_falls_back_to_legacy(self):
    """観点 3：新配置に無く旧配置にあるプロンプトは旧から読める"""
    cwd = Path(self.tmpdir)
    legacy = cwd / LEGACY_PROMPT_DIR / "x.prompt.md"
    legacy.parent.mkdir(parents=True, exist_ok=True)
    legacy.write_text("legacy prompt\n", encoding="utf-8")
    resolved = cwa.resolve_effective_prompt_read_path(
      cwd, f"{RUNTIME_PROMPT_DIR}/x.prompt.md"
    )
    self.assertEqual(resolved, f"{LEGACY_PROMPT_DIR}/x.prompt.md")

  def test_effective_prompt_conflict_prefers_runtime(self):
    """観点 4：新旧両方にある場合は新配置を採用する"""
    cwd = Path(self.tmpdir)
    legacy = cwd / LEGACY_PROMPT_DIR / "x.prompt.md"
    legacy.parent.mkdir(parents=True, exist_ok=True)
    legacy.write_text("legacy prompt\n", encoding="utf-8")
    runtime = cwd / RUNTIME_PROMPT_DIR / "x.prompt.md"
    runtime.parent.mkdir(parents=True, exist_ok=True)
    runtime.write_text("runtime prompt\n", encoding="utf-8")
    resolved = cwa.resolve_effective_prompt_read_path(
      cwd, f"{RUNTIME_PROMPT_DIR}/x.prompt.md"
    )
    self.assertEqual(resolved, f"{RUNTIME_PROMPT_DIR}/x.prompt.md")


class EffectivePromptLegacyFormInputTests(unittest.TestCase):
  """N1：旧形式パス入力でも新→旧の順（新旧競合時は新を正）を適用する"""

  def setUp(self):
    self.tmpdir = tempfile.mkdtemp()
    self.addCleanup(shutil.rmtree, self.tmpdir)

  def test_legacy_form_input_prefers_runtime_when_both_exist(self):
    cwd = Path(self.tmpdir)
    legacy = cwd / LEGACY_PROMPT_DIR / "x.prompt.md"
    legacy.parent.mkdir(parents=True, exist_ok=True)
    legacy.write_text("legacy prompt\n", encoding="utf-8")
    runtime = cwd / RUNTIME_PROMPT_DIR / "x.prompt.md"
    runtime.parent.mkdir(parents=True, exist_ok=True)
    runtime.write_text("runtime prompt\n", encoding="utf-8")
    resolved = cwa.resolve_effective_prompt_read_path(
      cwd, f"{LEGACY_PROMPT_DIR}/x.prompt.md"
    )
    self.assertEqual(resolved, f"{RUNTIME_PROMPT_DIR}/x.prompt.md")

  def test_legacy_form_input_returns_legacy_when_runtime_absent(self):
    cwd = Path(self.tmpdir)
    legacy = cwd / LEGACY_PROMPT_DIR / "x.prompt.md"
    legacy.parent.mkdir(parents=True, exist_ok=True)
    legacy.write_text("legacy prompt\n", encoding="utf-8")
    resolved = cwa.resolve_effective_prompt_read_path(
      cwd, f"{LEGACY_PROMPT_DIR}/x.prompt.md"
    )
    self.assertEqual(resolved, f"{LEGACY_PROMPT_DIR}/x.prompt.md")

  def test_absolute_path_is_returned_unchanged(self):
    cwd = Path(self.tmpdir)
    absolute = str(cwd / "somewhere" / "x.prompt.md")
    self.assertEqual(
      cwa.resolve_effective_prompt_read_path(cwd, absolute), absolute,
      "絶対パスは変換せずそのまま返すべき",
    )


class CommitApprovalPlacementTests(unittest.TestCase):
  """観点 1〜4：commit 承認記録"""

  def setUp(self):
    self.tmpdir = tempfile.mkdtemp()
    self.addCleanup(shutil.rmtree, self.tmpdir)

  def test_commit_approval_read_falls_back_to_legacy(self):
    """観点 3：新配置に無い場合は旧配置の承認記録を読む"""
    cwd = Path(self.tmpdir)
    _write_approval(cwd / LEGACY_APPROVAL, "legacy-record")
    state, errors = cwa.validate_commit_approval(cwd, [])
    self.assertTrue(state["exists"], errors)
    self.assertEqual(state["path"], LEGACY_APPROVAL)

  def test_commit_approval_conflict_prefers_runtime(self):
    """観点 4：新旧両方にある場合は新配置の記録を正とする"""
    cwd = Path(self.tmpdir)
    _write_approval(cwd / LEGACY_APPROVAL, "legacy-record")
    _write_approval(cwd / RUNTIME_APPROVAL, "runtime-record")
    state, _ = cwa.validate_commit_approval(cwd, [])
    self.assertTrue(state["exists"])
    self.assertEqual(state["path"], RUNTIME_APPROVAL)

  def test_consume_writes_to_runtime_even_when_record_is_legacy(self):
    """観点 1・2：消費（書き込み）は常に新配置へ行き、凍結済み旧記録は変更しない"""
    cwd = Path(self.tmpdir)
    _write_approval(cwd / LEGACY_APPROVAL, "legacy-record")
    legacy_before = (cwd / LEGACY_APPROVAL).read_text(encoding="utf-8")
    guarded.consume_commit_approval(cwd)
    runtime_path = cwd / RUNTIME_APPROVAL
    self.assertTrue(runtime_path.is_file(), "消費済み記録は新配置へ書かれるべき")
    consumed = json.loads(runtime_path.read_text(encoding="utf-8"))
    self.assertTrue(consumed["consumed"])
    self.assertEqual(
      (cwd / LEGACY_APPROVAL).read_text(encoding="utf-8"), legacy_before,
      "凍結済み旧記録へ書き込んではならない",
    )


class RuntimePlacementFreezeCheckerTests(unittest.TestCase):
  """観点 5：凍結済み旧成果物の不変性（git 追跡履歴判定、ce と同一規則）"""

  def setUp(self):
    self.tmpdir = tempfile.mkdtemp()
    self.addCleanup(shutil.rmtree, self.tmpdir)

  def test_checker_module_exists(self):
    self.assertIsNotNone(
      placement_freeze,
      "tools/check_workflow_action/placement_freeze.py が存在するべき",
    )

  def test_frozen_set_is_not_a_violation(self):
    cwd = Path(self.tmpdir)
    (cwd / LEGACY_LOG).parent.mkdir(parents=True, exist_ok=True)
    (cwd / LEGACY_LOG).write_text("frozen\n", encoding="utf-8")
    (cwd / LEGACY_PROMPT_DIR).mkdir(parents=True, exist_ok=True)
    (cwd / LEGACY_PROMPT_DIR / "x.prompt.md").write_text("frozen\n", encoding="utf-8")
    _write_approval(cwd / LEGACY_APPROVAL, "frozen")
    _git(cwd, "init")
    freeze_commit = _git_commit_all(cwd, "P1 placement switch")
    violations = placement_freeze.check_runtime_placement_freeze(cwd, freeze_commit)
    self.assertEqual(violations, [])

  def test_changes_deletions_and_additions_are_violations(self):
    cwd = Path(self.tmpdir)
    (cwd / LEGACY_LOG).parent.mkdir(parents=True, exist_ok=True)
    (cwd / LEGACY_LOG).write_text("frozen\n", encoding="utf-8")
    (cwd / LEGACY_PROMPT_DIR).mkdir(parents=True, exist_ok=True)
    (cwd / LEGACY_PROMPT_DIR / "x.prompt.md").write_text("frozen\n", encoding="utf-8")
    _write_approval(cwd / LEGACY_APPROVAL, "frozen")
    _git(cwd, "init")
    freeze_commit = _git_commit_all(cwd, "P1 placement switch")

    (cwd / LEGACY_PROMPT_DIR / "x.prompt.md").write_text("edited\n", encoding="utf-8")
    (cwd / LEGACY_LOG).unlink()
    (cwd / LEGACY_PROMPT_DIR / "new.prompt.md").write_text("violation\n", encoding="utf-8")

    violations = placement_freeze.check_runtime_placement_freeze(cwd, freeze_commit)
    self.assertTrue(any("x.prompt.md" in v and "frozen_file_changed" in v for v in violations))
    self.assertTrue(
      any("workflow-precheck.log" in v and "deleted_after_freeze" in v for v in violations),
      f"削除は専用種別 deleted_after_freeze で報告されるべき: {violations}",
    )
    self.assertTrue(any("new.prompt.md" in v and "added_after_freeze" in v for v in violations))

  def test_ignored_preexisting_legacy_artifacts_are_not_violations(self):
    """gitignore 対象として現存する旧成果物（凍結済み・未追跡）は誤検知しない（K3）"""
    cwd = Path(self.tmpdir)
    (cwd / ".gitignore").write_text(
      "docs/logs/workflow-precheck.log\n.reviewcompass/approvals/commit-approval.json\n",
      encoding="utf-8",
    )
    (cwd / LEGACY_LOG).parent.mkdir(parents=True, exist_ok=True)
    (cwd / LEGACY_LOG).write_text("frozen ignored log\n", encoding="utf-8")
    _write_approval(cwd / LEGACY_APPROVAL, "frozen ignored approval")
    _git(cwd, "init")
    freeze_commit = _git_commit_all(cwd, "P1 placement switch")
    violations = placement_freeze.check_runtime_placement_freeze(cwd, freeze_commit)
    self.assertEqual(violations, [], "ignore された既存旧成果物を違反としてはならない")

  def test_approvals_freeze_scope_is_limited_to_commit_approval_record(self):
    """approvals の凍結対象は契約どおり commit-approval.json 単体に限定する（K4）"""
    cwd = Path(self.tmpdir)
    _write_approval(cwd / LEGACY_APPROVAL, "frozen")
    _git(cwd, "init")
    freeze_commit = _git_commit_all(cwd, "P1 placement switch")
    other = cwd / ".reviewcompass" / "approvals" / "unrelated-record.json"
    other.write_text("{}\n", encoding="utf-8")
    violations = placement_freeze.check_runtime_placement_freeze(cwd, freeze_commit)
    self.assertEqual(violations, [], "契約対象外のファイルを凍結違反としてはならない")


class RunRoleEffectivePromptFallbackTests(unittest.TestCase):
  """K1：effective prompt フォールバックの実運用読み取り経路（run_role の sha 解決）への接続"""

  def setUp(self):
    self.tmpdir = tempfile.mkdtemp()
    self.addCleanup(shutil.rmtree, self.tmpdir)

  def test_sha_resolution_falls_back_to_legacy_prompt(self):
    import hashlib
    import os
    sys.path.insert(0, str(REPO_ROOT))
    from tools.api_providers import run_role
    cwd = Path(self.tmpdir)
    legacy = cwd / LEGACY_PROMPT_DIR / "x.prompt.md"
    legacy.parent.mkdir(parents=True, exist_ok=True)
    legacy.write_text("legacy prompt body\n", encoding="utf-8")
    previous = os.getcwd()
    os.chdir(cwd)
    try:
      resolved = run_role._resolve_effective_prompt_sha256(
        f"{RUNTIME_PROMPT_DIR}/x.prompt.md", None
      )
    finally:
      os.chdir(previous)
    expected = hashlib.sha256(legacy.read_bytes()).hexdigest()
    self.assertEqual(resolved, expected, "新配置に無い場合は旧配置のプロンプトから sha を計算するべき")


if __name__ == "__main__":
  unittest.main()
