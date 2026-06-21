#!/bin/bash
# UserPromptSubmit hook: レビュー関連の発話を検出してガイドラインを注入する
#
# キーワードに一致した場合のみ発動し、意図の判断はメインの Claude に委ねる

JQ="$(command -v jq)"
[ -z "$JQ" ] && exit 0

# stdin からユーザーの発話と作業ディレクトリを取得
input=$(cat 2>/dev/null)
prompt=$(echo "$input" | "$JQ" -r '.prompt // ""' 2>/dev/null)
[ -z "$prompt" ] && exit 0

# 一次フィルタ（広めのキーワードで拾う）
if ! echo "$prompt" | grep -qE "(レビュー|審査|3者|triad|proxy|プロンプト|判定)"; then
  exit 0
fi

# ガイドラインファイルを読み込む（cwd が JSON に含まれているので絶対パスで参照）
cwd=$(echo "$input" | "$JQ" -r '.cwd // ""' 2>/dev/null)
guide_file="$cwd/.reviewcompass/guidance/discipline_llm_as_judge_prompting.md"

[ -f "$guide_file" ] || exit 0

guide_content=$(cat "$guide_file")

message="【ガイドライン参照】以下はレビュー用プロンプトを作成する場合に適用するガイドラインです。今の文脈がレビューと無関係であれば無視してください。

$guide_content"

"$JQ" -n --arg msg "$message" '{
  hookSpecificOutput: {
    hookEventName: "UserPromptSubmit",
    additionalContext: $msg
  }
}'
