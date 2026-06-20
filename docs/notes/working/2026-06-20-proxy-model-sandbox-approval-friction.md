# proxy_model sandbox 外実行承認の摩擦メモ

作成日: 2026-06-20

## 背景

design triad-review の C1 proxy_model 判断で、`tools/api_providers/run_proxy_decision.py`
を使い OpenAI API / gpt-5.5 へ C1 判断用 prompt を送信しようとした際、
Codex の sandbox escalation auto_review に複数回拒否された。

最終的には、送信先・モデル・送信対象ファイル・目的を明示した承認を利用者から受け、
同じ正式 entrypoint で実行できた。

## 実際の問題

問題は「sandbox 外経路がないこと」ではなかった。

既存成功例と同じ `run_proxy_decision.py` の sandbox 外実行経路は存在した。
拒否の主因は、外部送信について auto_review が要求する承認粒度に対し、
メイン LLM が送信先・モデル・送信ファイル・目的を十分に明示していなかったこと。

## 悪かった進め方

- 過去に成功した proxy_model / API review の正規実行経路を先に確認しなかった。
- 利用者の「承認」を作業文脈上の承認として扱い、auto_review が読める外部送信承認へ具体化しなかった。
- 拒否後に、手動 raw response import という proxy_model の前提を崩す案へ逸れた。
  - proxy_model の意図は、利用者が個別判断・転記に関与しないこと。
  - ユーザ手動取得を前提にする案は要件のすり替えであり不適切。
- 実装前に相談せず、不要な実装・撤回・検証コストを発生させた。

## 次回の必須手順

proxy_model / API review を sandbox 外で実行する前に、必ず次を確認する。

1. 過去の成功例と同じ正式 entrypoint / variant / 証跡形式かを確認する。
2. prompt の送信対象ファイル、送信先 provider、モデル、目的を明文化する。
3. prompt に認証情報、個人情報、第三者非公開機密、不要な全文ログが含まれないことを確認する。
4. 利用者承認が必要な場合は、auto_review が読める粒度で承認対象を提示する。
5. 拒否された場合、proxy_model の前提を崩す代替案を実装しない。まず拒否理由と正規経路を再確認する。

承認文言は最低限、次の粒度を含める。

```text
承認。<送信先 provider> の <モデル> に、
<prompt ファイルパス>
の内容を送信し、<目的> の raw/parsed/metadata 証跡を生成することを許可する。
```

## 今回の正しい実行条件

- entrypoint: `tools/api_providers/run_proxy_decision.py`
- variant: `proxy_model_openai_gpt_55`
- provider: `openai-api`
- model: `gpt-5.5`
- prompt:
  `.reviewcompass/specs/workflow-management/reviews/2026-06-20-workflow-management-design-vertical-redo-proxy-decision-c1-prompt-quality-run/proxy-decision-c1-prompt.md`
- purpose: C1 proxy_model 判断の raw / parsed / metadata 証跡生成

## 教訓

API review / proxy_model 周りは、アドホックに手順を組み立てると承認粒度・sandbox・証跡契約の
落とし穴にはまりやすい。

実行前に正規経路と承認文言を揃えること。拒否されたときは、要件を変えるのではなく、
承認粒度・正規経路・送信材料のどこが不足しているかを先に見る。
