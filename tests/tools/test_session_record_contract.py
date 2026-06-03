"""セッション記録手順の正本化を検査するテスト。"""
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SESSION_GUIDE = REPO_ROOT / "docs" / "operations" / "SESSION_WORKFLOW_GUIDE.md"
WORKFLOW_REQUIREMENTS = (
  REPO_ROOT / ".reviewcompass" / "specs" / "workflow-management" / "requirements.md"
)
WORKFLOW_DESIGN = (
  REPO_ROOT / ".reviewcompass" / "specs" / "workflow-management" / "design.md"
)
WORKFLOW_TASKS = (
  REPO_ROOT / ".reviewcompass" / "specs" / "workflow-management" / "tasks.md"
)


def test_session_workflow_guide_declares_session_record_contract():
  """セッション運営正本が docs/sessions への経緯記録を要求する。"""
  text = SESSION_GUIDE.read_text(encoding="utf-8")

  assert "docs/sessions/session-<N>-<YYYY-MM-DD>.md" in text
  assert "重要な判断・承認・レビュー結果・修正経緯" in text
  assert "セッション終了時または重要判断後" in text


def test_session_workflow_guide_defines_record_numbering_and_responsibility():
  """セッション記録の採番・作成責任・必須条件が明記されている。"""
  text = SESSION_GUIDE.read_text(encoding="utf-8")

  assert "既存の最大セッション番号に 1 を加えた番号" in text
  assert "採番が衝突した場合" in text
  assert "利用者が採番を確定" in text
  assert "原則として毎セッション" in text
  assert "メインセッション LLM" in text
  assert "草案作成責任" in text


def test_session_workflow_guide_links_previous_record_and_template_shape():
  """開始時確認と記録フォーマットがセッション記録に接続している。"""
  text = SESSION_GUIDE.read_text(encoding="utf-8")

  assert "直近の `docs/sessions/session-*.md`" in text
  assert "既存 session 記録と同型" in text
  assert "サマリ（このセッションでやったこと）" in text
  assert "気づき・特筆点" in text
  assert "次セッションへの引き継ぎ" in text


def test_session_workflow_guide_defines_one_file_and_draft_fallback():
  """1 session 1 ファイルと中断・採番衝突時の草案退避を定義する。"""
  text = SESSION_GUIDE.read_text(encoding="utf-8")

  assert "1 session につき 1 ファイル" in text
  assert "同じファイルへ追記" in text
  assert "docs/sessions/drafts/" in text
  assert "session-<YYYY-MM-DD>-<short-topic>.md" in text
  assert "正式番号確定後" in text
  assert "次セッションが草案を引き継ぐ" in text


def test_workflow_management_specs_track_session_record_contract():
  """workflow-management 仕様が session record を機械化対象として追跡する。"""
  requirements = WORKFLOW_REQUIREMENTS.read_text(encoding="utf-8")
  design = WORKFLOW_DESIGN.read_text(encoding="utf-8")
  tasks = WORKFLOW_TASKS.read_text(encoding="utf-8")

  assert "セッション記録" in requirements
  assert "docs/sessions/session-<N>-<YYYY-MM-DD>.md" in design
  assert "session record 作成手順" in tasks


def test_proxy_review_decision_workflow_is_canonicalized():
  """review-run 後の proxy_model 判断代行手順を正本が定義する。"""
  guide = SESSION_GUIDE.read_text(encoding="utf-8")
  requirements = WORKFLOW_REQUIREMENTS.read_text(encoding="utf-8")
  design = WORKFLOW_DESIGN.read_text(encoding="utf-8")
  tasks = WORKFLOW_TASKS.read_text(encoding="utf-8")

  assert "review-run 後の proxy_model 判断代行手順" in guide
  assert "メインセッション LLM は raw レビューを集約し、三段階トリアージの下書きを作る" in guide
  assert "proxy_model は重要件の採用案・判断理由・最終ラベルを決定する" in guide
  assert "機械ガードは proxy decision の充足を検査する" in guide
  assert "重要件の判定閾値" in guide
  assert "元 review raw" in guide
  assert "候補案セット" in guide
  assert "コミット・プッシュ・spec.json 更新・フェーズ移行は人間の明示承認を要求する" in guide

  assert "review-run 後の proxy_model 判断代行" in requirements
  assert "proxy decision" in design
  assert "approval-proxy-<日付>.yaml" in design
  assert "candidate_options" in design
  assert "source_raw_paths" in design
  assert "proxy_model 判断代行ゲート" in tasks


def test_proxy_review_workflow_defines_parallelizable_units():
  """メインセッション LLM の実装作業から並列化可能な単位を切り出す。"""
  guide = SESSION_GUIDE.read_text(encoding="utf-8")
  design = WORKFLOW_DESIGN.read_text(encoding="utf-8")

  assert "並列化可能な単位" in guide
  assert "同根所見クラスタ単位" in guide
  assert "互いに同じファイルを更新しない実装単位" in guide
  assert "共通スキーマ・共通ビルダー・同一ファイルを触る修正は直列" in guide
  assert "生成物、共有 helper、推移的契約" in guide
  assert "未承認の便乗リファクタ" in guide
  assert "parallelizable_units" in design


def test_proxy_review_workflow_defines_subthread_worktree_and_outputs():
  """並列実装の担当形態と生成物の扱いを正本が定義する。"""
  guide = SESSION_GUIDE.read_text(encoding="utf-8")
  design = WORKFLOW_DESIGN.read_text(encoding="utf-8")

  assert "別スレッドかつ分離 worktree" in guide
  assert "同じ repo での並列実装は原則禁止" in guide
  assert "実装差分、検証結果、判断根拠、作業ノイズ" in guide
  assert "判断に影響した失敗試行" in guide
  assert "作業ノイズは本線 repo に取り込まない" in guide
  assert "subimplementation_outputs" in design
