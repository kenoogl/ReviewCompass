# レビュー対象（round-4 収束確認）：design §review-wave 要約コマンドモデル（全文）

## 0. 経緯
round-3 の must-fix 3 件（§3⇔§6 のキー名規範衝突、draft 件数定義の不一致、insufficient 対象範囲の必須/任意の不整合）を反映済み。本 round-4 は全文での収束確認。variant=implementation_review_independent_3way。利用者「コミット点まで自律で進める」。

## 1. 確定設計の規範本文（design.md より、全文）

## review-wave 要約コマンドモデル（Review-Wave Summary Command Model）— Req 10

reopen R-0（2026-06-14、D-001）で新設。review-wave（機能横断段）の横断確認で使う指標を、手動集計ではなく機械生成する。Req 1 の「段集合 YAML の静的列挙」と Req 2 の検査スクリプトを土台にした、機能内の静的検査である（実装は仕様確定後に TDD で行う正順）。

### 1. 配置と原則（Req 10 受入 1・5）

- サブコマンド `review-wave-summary` を `tools/check-workflow-action.py` に追加する（`next`／`spec-set`／`commit` と同じ CLI 体系。Req 2 の検査スクリプトのサブコマンド）。
- 読み取りに徹し、`spec.json`・フェーズ状態・トリアージを書き換えない（Req 3 受入 5・Req 4 受入 1 と整合）。書き込みは自身の要約出力に限る。

### 2. 読み取り元と指標の算出定義（Req 10 受入 1・2）

| 指標 | 読み取り元 | 算出定義 |
| --- | --- | --- |
| feature coverage | 各 feature の spec.json `workflow_state` | feature ごとに、全 phase × 全 stage のうち true の比率、および「全 phase approval 済みか」。`FEATURE_ORDER` の全 feature を対象。 |
| phase／stage 状態 | 同上 | feature × phase × stage の真偽をそのまま展開。 |
| triage 未解決／draft／human_required 件数 | review-run の `triage.yaml` 群（`.reviewcompass/evidence/review-runs/*/triage.yaml`、互換で旧 `.reviewcompass/specs/_cross_feature/reviews/*/triage.yaml`） | unresolved／human_required は `items[]` の `decision_status` で集計、draft は run 単位（補足の判定規則を正とする）。 |
| recheck 状態 | 各 feature の spec.json `recheck` | `upstream_change_pending` と `impacted_downstream_phases` をそのまま。 |
| 依存状況 | `feature-dependency.yaml` の `feature_order` と各 feature の依存記述 | `feature_order` を提示し、上流が未 approval の依存（未充足依存）を列挙。解決は Req 8 受入 6 の探索順を再利用。 |
| carry-forward 未消化件数 | carry-forward register（`learning/workflow/carry-forward-register/*.yaml`） | `items[]` のうち `status` が `resolved` 以外の件数。 |

補足（集計規則）：

- **triage の重複排除**：重複排除は `triage.yaml` ファイル（＝`run_id`）単位で行う。同一 `run_id` の `triage.yaml` が新旧両パスに見つかった場合は、新パス（`evidence/review-runs/`）を優先して 1 ファイルだけ採用する（旧パスは互換読みのみ）。各 finding item は単一の run に属するため、item レベルでの状態競合（同一 item が複数 run で異なる状態）は生じない。
- **triage 件数の判定規則**（定義はここを正とする）：
  - `unresolved`（item 単位）＝全 run の `items[]` のうち `decision_status` が `decided` 以外の item 数（`review_triage` の既存定義に一致）。
  - `human_required`（item 単位）＝全 run の `items[]` のうち `decision_status: human_required` の item 数。
  - `draft`（**run 単位**）＝`triage.yaml` の `triage_status: draft` である run の数。item 個別の draft は数えない。
  - unresolved は human_required を内包しうる（重なりを許す内訳。合計は取らない）。draft は run 単位のため item 単位の 2 つとは集計軸が異なる点を Markdown でも明示する。
- **carry-forward 未消化**：register の各 item の `status` が `resolved` 以外（`in_progress`・`deferred`・未設定などを含む）を未消化として数える。

各指標の集計には既存関数（`load_all_feature_specs`、`feature_order` 解決、`collect_recheck_items`、`review_triage` の集計）を再利用し、二重定義を避ける。

### 3. 出力形式とスキーマ（Req 10 受入 3）

- `--json` で JSON、既定は Markdown。両者は同一情報源から生成し**情報同等**とする。
- JSON の安定スキーマ（キー名・型を固定。追加は後方互換＝既存キーを変えない）：

```
{
  "schema_version": int,                  # 本設計の初版は 1
  "generated_at": str|null,               # ISO8601。実行時刻は呼び出し側が渡す。省略時 null
  "status": "ok" | "insufficient",
  "features": [                           # FEATURE_ORDER 順
    {
      "name": str,
      "coverage": {"completed": int, "total": int, "all_approved": bool},
      "phases": {                         # phase 名をキーとするオブジェクト
        "<phase>": {"<stage>": bool, ...}  # 各 phase の stage→真偽
      },
      "recheck": {"upstream_change_pending": bool, "impacted_downstream_phases": [str]}
    }
  ],
  "triage": {"unresolved": int, "draft": int, "human_required": int},
  "dependencies": {"feature_order": [str], "unmet": [{"feature": str, "depends_on": str}]},
  "carry_forward": {"unresolved": int},
  "errors": [str]                         # insufficient 時に対象と理由を列挙
}
```

- `features[].phases` は **phase 名をキーとするオブジェクト**（配列ではない）で、各値は stage 名→真偽（bool）のオブジェクト。stage キーの集合はその phase が spec.json `workflow_state` に持つ stage 群をそのまま用いる（requirements／design／tasks／implementation は drafting・triad-review・review-wave・alignment・approval、intent は drafting・review・approval、feature-partitioning は candidate-proposal・approval）。bool は当該 stage の完了真偽。spec.json に存在しない stage はキーに含めない。
- **`status` の判定基準**（必須記録と任意記録を区別）：
  - **必須記録**＝全 feature の spec.json と feature-dependency.yaml。これらの欠落・解析不能は `insufficient`。
  - **任意記録**＝triage.yaml 群と carry-forward register。これらの**非在**（glob ゼロ件・ディレクトリ/ファイル欠落＝レビュー未実施の初期状態）は当該件数を 0 として正常に扱い `ok` を妨げない（非在を欠落と同一視しない）。ただし**存在するが解析不能**な任意記録があれば `insufficient`。
  - 必須記録がすべて読め、存在する任意記録もすべて解析できたとき `ok`。
- Markdown は同じ項目を見出し＋表で表し、JSON と情報同等とする。

### 4. fail-closed（Req 10 受入 4）

- **不能とする入力範囲（design で一意化）**：(a) **必須記録**（spec.json・feature-dependency.yaml）の欠落、(b) 読み取った記録（必須・任意いずれも）が YAML として解析不能（パース不能）、(c) 最上位が連想配列でない等の構造異常。**任意記録**（triage.yaml 群・carry-forward register）の非在は不能に含めず 0 件として扱う（§3 の status 判定と一致）。これは Req 8 受入 9（パース不能の遮断）と同型で、Req 2 受入 4（結論不能は fail）に従う。
- これらの場合、`status: insufficient` とし、`errors[]` に対象パスと理由を列挙、**非ゼロ終了コード**を返す。**終了コード規約**は既存サブコマンド（`next`／`spec-set`／`commit`）と整合させ、`0`＝ok、`2`＝insufficient（fail-closed、DEVIATION 相当）とする。`1` は本コマンドの集計判定では使わず、想定外の実行時例外（呼び出し誤り等）にのみ割り当てる。
- Markdown では見出しに不完全である旨を明示し、完了と誤読させない。
- 部分的に読めた集計値があっても `status: ok` にしない（部分集計を完了扱いしない）。第 1 層の限界（Req 7・中身の妥当性は判定しない）と整合。

### 5. 保存（Req 10 受入 5）

- 既定は標準出力（保存しない）。オプションで自身の要約出力のみ書き出す：
  - `--out <path>`：指定パスへ書き出す（パスは呼び出し側が決める）。
  - `--save`：既定の保存先 `.reviewcompass/specs/_cross_feature/reviews/` に既定命名で書き出す。命名は `<generated_at の日付>-review-wave-summary.<md|json>`（`generated_at` 省略時は連番や日付の付与方法を implementation で確定）。
- 保存先 `.reviewcompass/specs/_cross_feature/reviews/` は承認済み requirements 受入 5 で定めた現行の横断レビュー記録置き場であり、旧配置ではない（review-run 生成物の `evidence/review-runs/` とは別系統の、人が読む横断記録の置き場）。
- いずれも spec.json・triage・phase 状態を書き換えない。自身の要約出力の書き出しは状態変更に当たらない（Req 3 受入 5・Req 4 受入 1 と整合）。

### 6. implementation へ委譲する未確定事項

§3 の JSON スキーマ（キー名・型・構造）は**本 design で固定する契約**であり、implementation は変更しない（将来の追加は後方互換でのみ）。implementation 段で確定するのは契約に属さない次の細部に限る：

- `--save` 既定命名の連番・タイムスタンプ付与方法（`generated_at` 省略時の扱い）と、保存先ファイル名が衝突した場合の振る舞い（上書きするか・エラーにするか）。呼び出し側が保存先の一意性を保証する前提とする。
- 既存関数の具体的な呼び出し・統合方法（`load_all_feature_specs` 等の再利用）。
- Markdown の具体的な表レイアウト（情報同等を満たす範囲で）。

## 2. レビュー観点（criteria: design_r10_round4_convergence）
1. round-3 の 3 件（キー名の固定契約と委譲範囲の分離、draft の run 単位定義、必須記録 vs 任意記録の insufficient 判定）が一意に解消されたか。
2. 規範どうしの衝突・二重定義が残っていないか。
3. 残存する must-fix 級の欠陥がないか（収束したか）。
