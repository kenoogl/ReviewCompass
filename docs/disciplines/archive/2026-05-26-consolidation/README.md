# 2026-05-26 統廃合の経緯

退避日：2026-05-26（セッション 27）
退避元：`docs/disciplines/`
統合先：[../../discipline_options_presentation.md](../../discipline_options_presentation.md)
関連コミット：`a5cf32b`

## 退避ファイル

| ファイル | 旧分類 |
|---|---|
| [discipline_dominant_dominated_options.md](discipline_dominant_dominated_options.md) | 参照層 |
| [discipline_choice_presentation.md](discipline_choice_presentation.md) | 参照層 |

## 統廃合の理由

- 旧 `dominant-dominated-options`（参照層）が「決定の瞬間に発火しない」構造的欠陥を持つことが利用者から指摘された（発言：「規律が効いていない」）
- 旧 `choice-presentation` は旧 `dominant-dominated-options` と密接に関連（同じ「複数案提示」の場面で適用される）
- 統合により規律体系を単純化（参照層 5 件 → 3 件）、統合先を active 必読に昇格して起動時に文脈へ載せる
- 統合先で **事前検査宣言義務**（応答内に内部判定結果を明示宣言）を新設し、自己約束より強い構造的拘束力を持たせる

## 利用者明示承認の出典

- 「読み取りは正しい。軽量手続きでよい。効果を測る必要がある」（実施計画方針、2026-05-26 セッション 27）
- 「OK」（短縮版本文確認、2026-05-26 セッション 27）
- 「承認」（実装承認、2026-05-26 セッション 27）

## 関連参照

- 計画書 §5.21.2「退避（archived）：撤廃 README に経緯を記録」
- 統合先本体：[../../discipline_options_presentation.md](../../discipline_options_presentation.md) 末尾「## 統廃合元」節
- 効果測定ログ：[../../../discipline-compliance-reports/options-precheck-log.md](../../../discipline-compliance-reports/options-precheck-log.md)
