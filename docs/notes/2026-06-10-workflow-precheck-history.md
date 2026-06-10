# workflow precheck 履歴メモ

このメモは、`docs/operations/WORKFLOW_PRECHECK.md` から外した採用経緯、実測記録、作業順序メモを保存する。運用上の正本ではない。

## 採用承認の出典

- 「共存モデルの採用」（2026-05-25 セッション 24）
- 「A から順に進める」（2026-05-25 セッション 24）
- 「次に進む」（2026-05-25 セッション 24）
- 「範囲案 2」（2026-05-25 セッション 24）
- 「論点 A は、実装テスト段階でも効果測定やデバッグで必要になるのではないか？」（2026-05-25 セッション 24）
- 「論点 B は、渡す」（2026-05-25 セッション 24）
- 「論点 C は別文書」（2026-05-25 セッション 24）
- 「ア」（2026-05-25 セッション 24）

## 実測結果

2026-05-25 セッション 24 に、段階 2 スクリプトの実装と動作確認を実施した。

### 実測の範囲

- 実 `.reviewcompass/specs/<feature>/spec.json` に対する spec-set サブコマンド
- 一時 git リポジトリでの commit／push サブコマンド
- 引数妥当性検査の挙動

### 実測シナリオと結果

14 シナリオを実行し、すべて想定どおりの判定（OK／WARN／DEVIATION）になった。

| 番号 | 種別 | 入力概要 | 想定 | 実測 |
|---|---|---|---|---|
| 1 | spec-set | foundation design drafting true | OK | OK |
| 2 | spec-set | foundation tasks drafting true（design 未承認） | DEVIATION | DEVIATION |
| 3 | spec-set | foundation requirements alignment false（reopen） | WARN | WARN |
| 4 | spec-set --json | foundation design drafting true | OK の JSON 出力 | OK の JSON |
| 5 | commit | 実 repo、staged 0、未消化 0 | OK | OK |
| 6 | push | 実 repo、tree clean、ahead 0 | OK | OK |
| 7 | spec-set | conformance-evaluation design drafting true | OK | OK |
| 8 | spec-set | foundation intent approval true（機能横断段） | OK | OK |
| 9 | spec-set | foundation requirements drafting false（reopen） | WARN | WARN |
| 10 | spec-set 引数 | foundation nonexistent-phase | 非 0 ＋ エラー | 非 0、有効値列挙 |
| 11 | commit | 未消化所見 1 件 | WARN | WARN |
| 12 | commit | spec.json 変更含む | WARN | WARN |
| 13 | commit | credentials.json 含む（危険変更） | DEVIATION | DEVIATION |
| 14 | push | dirty tree | DEVIATION | DEVIATION |

### 確認できた仕様準拠

- spec-set の判定：同フェーズ前段依存・上流フェーズ approval 依存・reopen 警告が期待どおり動作
- commit の分類：通常／要注意／危険の 3 分類が機能
- push の clean 性検査：未追跡ファイル 1 件でも dirty 検知、origin 未設定時も処理続行
- 終了コード体系：0／1／2 が想定どおり
- ログ取得：JSON Lines 形式で判定が追記される
- 引数妥当性検査：無効な値で適切なエラーメッセージと有効値を列挙

### 実測中に発見・是正した小さな問題

- 人間可読出力の真偽値表記を Python 慣習の `True/False` から `true/false` に統一
- `docs/logs/workflow-precheck.log` を `.gitignore` に追加

### 観察事項

- `origin/main` 未設定時の push は処理続行
- commit で staged ファイル 0 件の場合、スクリプトは OK 判定だが、実際の git commit はファイルなしで失敗する
- 直近 5 コミットの表示は 1 行表示を優先

## 作業順序メモ

当時の残作業順序は次のとおり。

1. 段階 2 のスクリプト実装
2. 段階 2 の小規模運用による実測
3. 段階 1 の規律化
4. 規律統廃合の本格議論
5. 段階 3 のフック導入
