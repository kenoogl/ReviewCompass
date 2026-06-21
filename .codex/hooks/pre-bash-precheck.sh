#!/bin/bash
# 補助層 C 段階 3：Bash の git commit／git push を事前検査する PreToolUse フック
#
# 仕様：.reviewcompass/guidance/WORKFLOW_PRECHECK.md §12
# 設計：
#   - stdin から PreToolUse の JSON ペイロードを読み、tool_input.command を取得
#   - git commit／git push を検出した場合のみ tools/check-workflow-action.py を呼ぶ
#   - git commit は .reviewcompass/approvals/commit-approval.json がない場合 deny される
#   - check スクリプトの exit 2（DEVIATION）のときのみ deny を返す
#   - それ以外は exit 0 で通過（exit 1 WARN は警告だが通過、stage 1 規律が判断を担う）
#
# 入力 JSON 形式：
#   {"tool_name": "Bash", "tool_input": {"command": "git commit -m ..."}}
#
# 出力 JSON 形式（deny の場合）：
#   {"hookSpecificOutput": {"hookEventName": "PreToolUse",
#                            "permissionDecision": "deny",
#                            "permissionDecisionReason": "..."}}
#   通過の場合は何も出力せず exit 0
#
# 利用者明示承認：「イは前倒しだが、取り組む」「ア」（推奨セット採用、
# 2026-05-25 セッション 24）

# 入力 JSON を読む
INPUT=$(cat)

# tool_name が Bash でなければ通過（matcher で絞っているはずだが念のため）
TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name // empty')
if [ "$TOOL_NAME" != "Bash" ]; then
  exit 0
fi

# tool_input.command を取得
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')
if [ -z "$COMMAND" ]; then
  exit 0
fi

# git commit／git push の検出
# パイプや &&、&|、; のあとに git commit／push が続くケースも検出
SUBCOMMAND=""
if echo "$COMMAND" | grep -qE '(^|[;&|][[:space:]]*)git[[:space:]]+commit'; then
  SUBCOMMAND="commit"
elif echo "$COMMAND" | grep -qE '(^|[;&|][[:space:]]*)git[[:space:]]+push'; then
  SUBCOMMAND="push"
fi

# 対象外（git status／log 等の読み取り専用や、git 以外）は通過
if [ -z "$SUBCOMMAND" ]; then
  exit 0
fi

# 段階 2 スクリプトを呼び出す
# rationale には「stage-3 hook 自動発動」と元コマンドを含めてログに残す
RESULT=$(python3 tools/check-workflow-action.py "$SUBCOMMAND" \
  --rationale "[stage-3 hook auto-invocation] $COMMAND" --json 2>&1)
EXIT_CODE=$?

# exit 2（DEVIATION）のみ deny。exit 0／1 は allow（仕様 §12.3）
if [ "$EXIT_CODE" -eq 2 ]; then
  # 理由を抽出（jq が失敗しても deny は維持）
  REASONS=$(echo "$RESULT" | jq -r '.reasons | join("; ")' 2>/dev/null)
  if [ -z "$REASONS" ] || [ "$REASONS" = "null" ]; then
    REASONS="DEVIATION 検出（詳細は段階 2 スクリプト出力参照）"
  fi
  # deny の JSON を出力
  jq -n --arg reason "段階 3 フック：DEVIATION 検出（$REASONS）" \
    '{
      hookSpecificOutput: {
        hookEventName: "PreToolUse",
        permissionDecision: "deny",
        permissionDecisionReason: $reason
      }
    }'
  exit 0
fi

# allow（exit 0 と 1）：何も出力せず exit 0
exit 0
