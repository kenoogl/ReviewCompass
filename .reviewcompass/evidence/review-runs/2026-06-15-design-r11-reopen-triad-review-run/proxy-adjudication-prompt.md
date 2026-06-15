# design triad-review round-1 proxy 裁定プロンプト

## 背景
- feature: workflow-management
- phase: design
- reopen: R-0（decision-source-lint）
- variant: implementation_review_independent_3way
- 利用者委任：自律実施（2026-06-15）

## 所見クラスタ

所見 17 件（primary 7 件 + adversarial 10 件）を整理した。

### クラスタ 1：--verify-pending と受入 5「読み取り専用」の矛盾（F-002 / A-001）
- primary: WARN、adversarial: ERROR（同根）
- 問題：requirements 受入 5「決定記録そのものを書き換えない」と design §5 の `--verify-pending`（verification_status・verified_at を書き換える）が矛盾。設計文書に例外の根拠がない。

### クラスタ 2：束ね例外後も multiplicity が bundled のままになる問題（F-001）
- primary: ERROR
- 問題：§2 の例外承認手順が「承認レコード存在＋decision_id 包含」で通過させるが、各決定が `multiplicity: single` になることを強制していない。要件「個別出典なしには確定させない」の機械強制漏れ。

### クラスタ 3：照合不合格時の遷移先未定義（A-002）
- adversarial: ERROR
- 問題：`--verify-pending` が不合格だった場合の挙動が §1〜5 に記述なし。§6 の委譲事項にも含まれていない（"design で固定する契約"の穴）。

### クラスタ 4：bundle-exceptions 承認レコードのスキーマ未定義（A-003）
- adversarial: ERROR
- 問題：lint は「承認レコードが存在し decision_id リスト包含なら通過」と定めるが、承認レコードのスキーマが未定義のため lint の実装が不可能。§6 の委譲事項にも未記載。

### クラスタ 5：locator のターン番号定義なし（A-004 / F-006）
- adversarial: ERROR、primary: INFO（同根、adversarial が広い指摘）
- 問題：ターン番号が転写内の何番目の単位を指すか未定義。また lint が照合にロケータを使うかどうか（§3 は全文検索）が明示されていない。

### クラスタ 6：--all のサブディレクトリ（bundle-exceptions/）も検査してしまう（A-005）
- adversarial: WARN
- 問題：`--all` は「配下の全 YAML」とあり、bundle-exceptions/ が誤って検査対象になる。unverifiable → DEVIATION → commit 遮断の誤動作が発生しうる。

### クラスタ 7：category の境界細目が未確定（A-006）
- adversarial: WARN
- 問題：requirements 受入 1 が「境界の細目は design で確定」と明示委任しているが、design §1 に具体的な判定基準例が書かれていない。

### クラスタ 8：session_id と locator の正本関係（A-007）
- adversarial: WARN
- 問題：session_id（ベース名、拡張子なし）と locator（フルパス）が同一ファイルを二重参照。ファイル移動・改名時にどちらを正本とするか不明。

### クラスタ 9：unverifiable の定義・設定主体（F-003 / A-008）
- primary: WARN、adversarial: WARN（同根）
- 問題：§1 スキーマに `unverifiable` の定義条件・設定主体が書かれていない。lint が外側から判定する値なのか、記録者が手書きする値なのか不明。

### クラスタ 10：内容なし語の判定ロジック（トークン化）曖昧（F-004 / A-009）
- primary: WARN、adversarial: INFO（同根）
- 問題：「語のみで構成される」のトークン化・句読点処理方法が未定義。

### クラスタ 11：テスト戦略に Req 11 のケース未追加（F-005）
- primary: WARN
- 問題：§テスト戦略節に Req 11 のテストケースが未追加。

### クラスタ 12：bundle_exception_id が §1 スキーマに未記載（F-007）
- primary: INFO
- クラスタ 4（A-003）の対処で包含される。

### クラスタ 13：--verify-pending の並行書き込み防止を implementation 委譲（A-010）
- adversarial: INFO
- §6 で「並行書き込み防止」として既に委譲済み。インターロック方針のヒントを追記するかどうか。

## 裁定依頼事項

各クラスタを must-fix / should-fix / leave-as-is で分類し、修正方針を述べてください。

重要な判断点：
1. クラスタ 1（--verify-pending vs 受入 5）をどう解消するか。requirements 改訂か design 内例外明示か。
2. クラスタ 2（F-001）は requirements の必要条件「個別出典必須」の機械強制漏れ。design §2 の修正で対処可能か。
3. クラスタ 5（locator ターン番号）：逐語照合が全文検索ならロケータは「人向け位置情報」に過ぎず、定義は should-fix 程度か。
4. クラスタ 11（テスト戦略）：tasks フェーズで対処するか、今 design.md のテスト戦略節に追記するか。
