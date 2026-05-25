---
name: dominant-dominated-options
description: レビュー／設計議論で複数案提示時、明らかにデメリットが大きい dominated 案は提示しない。ただし dominated 判定時は厳密化規律（合理的成立条件 1 文以上＋規模感の数値明示＋暗黙前提明示）を必須化、LLM の自己確認偏向を抑制（2026-04-28 改訂）
metadata: 
  type: feedback
---
修正案候補・選択肢を提示する際、明らかにデメリットが大きな (=他案に dominated されている) 選択肢は提示しない。レビュー作業で合理的選択肢のみに絞る。**ただし dominated 判定そのものを厳密化する規律 (下記) を必須適用**、LLM の自動採択偏向 (X1 一直線生成バイアス) を構造的に抑制する。

**Why:** ユーザーの判断負荷を減らすため。dominated 案を併記すると「比較すべき案」が増え、判断疲れと提示の冗長化を招く。レビューラウンドが何十件にも及ぶ場面では特に顕著。

**Why 厳密化規律追加** (2026-04-28 Spec 1 やり直しセッションで発見): dominated 除外プロンプトの本来意図 (合理的選択肢のみに絞る) が、副作用として LLM の easy wins 偏向を加速させる構造的 bias を生む。具体的症状:

- LLM が「自分が推す X1 をデフォルト採択するために、X2/X3 を dominated として早期排除」する偏向
- 「dominated 判定」が LLM の self-confirmation の隠れ蓑になる
- 結果として「常に X1 一直線」型出力が構造的に量産される
- memory `feedback_review_step_redesign.md` の 4 重検査 + Step 1b-v 5 切り口は「自動採択偏向の構造的抑制」を目的とするが、上流で X1 一直線が生成される限り下流の検査は形式的になる

Spec 1 やり直しセッション (2026-04-28) で 12 件の escalate 案件すべてが「X1 唯一案 (X2/X3 dominated)」で user 反転 0 件、しかし振り返りで 5 件中 3 件 (重-2-1 / 重-3-1 / 重-5-2) で dominated 判定が早急だったことを発見。判断結果は変わらなかったが、dominated 判定根拠の厳密化が必要。

**How to apply:**

## 基本規律 (継続)

- 修正案 (1) / (2) / (3) を提示する前に、各案を簡単に評価し、明らかに他案に劣る案は除外する
- 残った案のメリット・デメリットを公平に提示し、推奨を明示する
- 「現状維持 + design phase 持ち越し」を案として残すかは指摘の重要度次第 (致命級では除外、軽微では残してよい)
- 例: 大きな設計変更案や Requirement 数の大幅増を伴う案は、軽微な指摘に対して dominated になりやすい

## dominated 判定の厳密化規律 (2026-04-28 改訂、必須適用)

dominated と判定する案件ごとに、以下 3 規律を必須適用:

### 規律 1: 合理的成立条件 1 文以上の明示義務

dominated と判定する案 (X2 / X3 等) について、「X が合理的に成立する条件」を最低 1 文記述する義務。条件が思い浮かばない場合のみ「真の dominated」と判定可。

例 (適用前):
```
- X2 (File Structure Plan 変更で G1+G2 別 module 化): 既存設計判断 (G1 1 関数 = 過剰分割回避) を覆す、合理性なし、dominated
```

例 (適用後):
```
- X2 (File Structure Plan 変更で G1+G2 別 module 化): G1 が将来複雑化する高い見込みがある場合 (vocabulary policy 変更 / カテゴリ判定ロジック追加 等) は合理的、ただし現状 G1 = 1 関数規模 ~30 行で複雑化見込み低、YAGNI 原則と整合 → 現状前提下では dominated
```

合理的成立条件の例示 (典型カテゴリ):
- **異なる規模前提**: 「規模 N 倍 / 利用頻度 M 倍では X2 採択合理」
- **異なる UX 重視**: 「機能保持より簡潔運用重視のプロジェクトでは X2 採択合理」
- **異なる将来見込み**: 「将来複雑化見込み高い場合は X2 採択合理」
- **異なる整合性軸**: 「Adjacent Sync 範囲を厳密適用するプロジェクトでは X2 採択合理」

### 規律 2: 性能 / 規模感を根拠とする場合の numerical 明示義務

dominated 根拠に「性能劣化」「実装コスト増」「規模問題」等の量的主張を含む場合、numerical 規模感を明示する義務。抽象論での dominated 判定は禁止。

例 (適用前):
```
- X2 (yaml list of objects 形式統一): Spec 5 normalize_frontmatter API 性能劣化、dominated
```

例 (適用後):
```
- X2 (yaml list of objects 形式統一): 性能劣化 numerical = 1K-5K vocabulary で list iter ~1ms vs dict access ~0.1ms 程度、実用的無視可能。ただし Spec 5 API access pattern (entity_type → shortcut field 名 dict lookup) と整合性で X1 (mapping) 優位 → dominated 根拠は性能ではなく API access pattern integrity
```

numerical 規模感の例:
- 性能: ms / s / ops/sec 単位の見積
- 実装コスト: LOC (lines of code) / 関数数 / module 数
- 運用コスト: user 操作回数 / 認知負荷 (sub-section 数 / nesting level)
- データ規模: vocabulary entry 数 / page 数 / event 数

### 規律 3: 暗黙前提の明示義務

dominated 判定が依存する暗黙前提 (例: 「G1 1 関数規模が変わらない」「user UX 重視」「vocabulary curation 重視」) を明示する義務。前提を変えると dominated 判定が反転する場合は、前提依存性を明記。

例 (適用前):
```
- X2 (未使用カテゴリ INFO 削除): user UX 損失で dominated
```

例 (適用後):
```
- X2 (未使用カテゴリ INFO 削除): 暗黙前提 = 本 spec の vocabulary curation UX 重視方針下では機能保持 (X1) 優位、ただし簡潔運用方針プロジェクト (lint output 冗長性回避優先) では X2 採択も合理的。本 spec 方針下では X1 優位、project 方針依存
```

## dominated 判定の自己診断 (Step 1b-iv 自己診断義務との連携)

memory `feedback_review_step_redesign.md` の Step 1b-iv 自己診断義務 (「もしユーザーが反転したら、その理由は何か」) を dominated 判定にも拡張:

- 各 dominated 判定について、「もし user が X2 を採択したら、それは何故か」を 1 文以上記録する義務
- 納得できる理由 (条件付き合理性) が思い浮かんだら、dominated 判定を「条件付き dominated」へ格下げ、または前提明示で X1 採択根拠を強化
- 「合理的理由が一切思い浮かばない」場合のみ「真の dominated」判定

## escalate 寄せ規律との整合

dominated 判定の厳密化は escalate 必須条件 5 種 (memory `feedback_review_step_redesign.md` L146-154) と連携:

- escalate 必須条件 1 「複数の合理的選択肢が存在 (dominated 除外後も 2 案以上残る)」の判定を厳密化
- 「X2 を dominated と判定したが、規律 1-3 適用後に合理的成立条件が見つかった」場合 → escalate 必須条件 1 該当の可能性を再検討、user 判断委譲

## 関連 memory

- `feedback_choice_presentation.md`: dominated 除外後の合理的選択肢を、ラベル + 階層性のルールで提示
- `feedback_deepdive_autoadopt.md`: 深掘りプロセスで dominated 案除外を実施、自動採択 / escalate を判断
- `feedback_review_rounds.md`: 各レビューラウンドの修正候補提示で本ルール適用
- `feedback_review_step_redesign.md`: Step 1b-iv 自己診断義務と本厳密化規律の連携
- `feedback_review_judgment_patterns.md`: dev-log パターン 22「複数選択肢 trade-off (LLM 単独採択禁止)」と本規律の連携 (escalate 寄せ厳格化)
