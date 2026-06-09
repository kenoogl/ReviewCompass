# Requirements reopen evidence supplement

## 目的

requirements triad-review の所見は、requirements.md 本体の不足を確定したものではなく、review target 上で direct impact 4 feature の本文引用と差分評価が不足している、という指摘だった。

本補足は、direct impact 4 feature の requirements 本文を確認し、今回の intent を既存 requirements で受けられるかを判定する。

## 判定まとめ

| Feature | 判定 | 理由 |
| --- | --- | --- |
| foundation | 追加修正不要 | 固定パターン依存の除外と、証拠・メタデータ契約が requirements 本文に明記済み |
| runtime | 追加修正不要 | 実 LLM 呼び出しによる動的判定、固定パターン依存排除、プロンプト一意解決失敗時の無効化、構造化証拠、検証失敗時の遮断が明記済み |
| evaluation | 追加修正不要 | 有効・無効実行分離、構造化証拠からのメトリクス抽出、メタデータ完全性検査、レビューモード分離が明記済み |
| conformance-evaluation | requirements 本体は追加修正不要、補足記録で足りる | 逆方向推定・二段階照合・3役レビュー・実装由来契約の枠は明記済み。今回 intent による追加責務は、既存 Requirement 1／3／5 の範囲内で扱える |

## foundation

### 該当本文

Requirement 5 は、パターン定義依存の除外を次のように定めている。

- パターン定義ファイルの配置規約を定義しない。
- レビュー検出を実大規模言語モデル呼び出しによる動的判定として位置付ける。
- 固定パターン定義への定常依存を排除する。

Requirement 3 は、レビュー証拠の共通スキーマ集合を定め、`review_case`、`finding`、`impact_score`、`failure_observation`、`necessity_judgment` を要求している。

Requirement 6 は、規約版、プロンプト版、実行時版、対象成果物ハッシュ、レビューモード、実行状態、検証器状態、人間承認状態、証拠区分などのメタデータ契約を定めている。

### 差分評価

今回の intent は「収集処理が事前設定の写像にならない」ことを求める。foundation Requirement 5 は、固定パターン定義への定常依存排除と実大規模言語モデル呼び出しによる動的判定を明記しており、要求の中心を既に表している。

さらに Requirement 3／6 により、観測結果を後段が検査・評価できる証拠とメタデータに載せる契約がある。したがって foundation requirements 本体への追加修正は不要と判定する。

## runtime

### 該当本文

Requirement 3 は、プロンプト解決と版追跡を定めている。特に、必要なプロンプトを一意に解決できない実行を失敗または無効としてマークすることを要求している。

Requirement 4 は、foundation のスキーマに準拠した実行レベル証拠、由来表示と判定連結を持つ所見レベル記録、反証や上書き関連フィールド、生の証拠と派生要約の分離、失敗様式に遭遇した場合の記録を要求している。

Requirement 6 は、検証器失敗と実行制御失敗の区別、必要な検証が失敗した場合の下流「有効実行」処理の阻止、機械可読な無効実行トリアージ成果物を要求している。

Requirement 10 は、パターン定義ファイルの参照規約を持たず、レビュー検出を実大規模言語モデル呼び出しによる動的判定として位置付け、固定パターン定義への定常依存を排除すると定めている。

### 差分評価

runtime は今回 intent の直接所有者である。既存 requirements は、固定パターン定義への依存排除だけでなく、プロンプト解決失敗、構造化証拠、失敗記録、検証失敗時の下流遮断を既に要求している。

judgment 所見が挙げた LLM 非決定論的挙動への堅牢性は、Requirement 3／4／6 の組み合わせで要件レベルの受け皿がある。リトライ等の具体手段は design／implementation 側で扱う内容であり、requirements 本体に新 Requirement を追加する必要は現時点ではない。

## evaluation

### 該当本文

Requirement 1 は、メタデータと無効化マーカーに基づき、実行を valid／invalid／exploratory／analysis_blocked に分類し、無効実行を標準メトリクスから除外することを要求している。

Requirement 3 は、自由記述の要約ではなく、構造化された証拠からメトリクスを計算し、生の証拠から派生メトリクスへの導出経路を保持することを要求している。

Requirement 6 は、標準集計前の必須メタデータ検査、不足時の集計拒否、致命的失敗と探索的部分分析の区別を要求している。

Requirement 9 は、レビューモードを区別し、標準の `runtime_mediated` 比較セットから他レビューモードを除外または別スライスとして扱うことを要求している。

### 差分評価

今回 intent が evaluation に求めるのは、固定写像に見える出力を無批判に評価対象へ混ぜず、実 LLM 判断に基づく観測結果を構造化証拠として扱えること、また実行方式やレビューモードの違いを混ぜないことである。

Requirement 1／3／6／9 はこの条件を既に満たす。evaluation は収集処理そのものを所有しないため、requirements 本体に「写像禁止」を重複追加するより、runtime/foundation の契約を評価時に検査・分離する現在の責務境界が適切である。

## conformance-evaluation

### 該当本文

Requirement 1 は、実装コードを入力として requirements／design を中心に推定または照合する逆方向の機能として動作することを定めている。

Requirement 3 は、照合チェックモードを二段階方式とし、実装コードから design／requirements を推定した後、既存上流文書と比較して食い違いを列挙することを要求している。

Requirement 5 は、推定段階と照合段階の両方に 3役レビュー機構を適用することを要求している。

### 差分評価

conformance-evaluation は今回 intent の直接影響 feature だが、責務は「レビュー収集を実行すること」ではなく、実装コードから上流文書との食い違いを推定・照合することである。

実装が固定パターン照合に寄っているか、実 LLM 判断に基づく収集処理になっているかは、Requirement 1／3 の逆方向推定・比較対象に含められる。推定・照合の妥当性確認は Requirement 5 の 3役レビューで扱う。

したがって requirements 本体に新 Requirement を追加しなくても、今回 intent は既存 Requirement 1／3／5 の範囲で受けられる。もし実装段で、固定パターン依存を検出する具体的 criteria が不足すると判明した場合は、design または tasks 側で検査観点として補う。

## triad-review 所見への対応

| 所見 | 対応 |
| --- | --- |
| 受け皿確認が循環的 | 本補足で requirements 本文に基づく根拠を追加した |
| direct impact 4 feature の本文引用不足 | 本補足で feature ごとの該当本文と差分評価を追加した |
| runtime の LLM 非決定論的挙動への堅牢性 | Requirement 3／4／6 の組み合わせで受けると判定した |
| drafting 完了判定の根拠不足 | 今回の drafting 再実施は、2026-06-08 に追記済みの受け皿確認を前提に、追加修正要否を再確認する作業として扱う |

## 結論

direct impact 4 feature について、requirements.md 本体への追加修正は不要と判定する。

ただし、この判定は本補足の根拠確認を前提とする。次に進むには、利用者が「requirements triad-review の根拠補強により、requirements 本体の追加修正不要としてよいか」を承認する必要がある。
