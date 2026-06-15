"""tools/session-record-backfill.py の追記専用マージ（消さずに足す）の単体テスト。

maintenance-2026-06-14-session-record-append-merge（side track）に対応。
現状の丸ごと上書きでは、元ログ（jsonl）が縮んだ場合に取り込み済み記録が失われ得る。
追記専用マージ＝「既存は保全し、増えた分だけ反映する」へ改める。

判定は層 1（整形済み転写）の本文（front-matter を除く）の行を順序保存で比較する：
  same   : 本文一致 → 書き込みを起こさない
  extend : 旧本文が新本文の部分列（増えただけ）→ 更新する
  shrink : 旧本文の行が新本文に順序保存で含まれない（消える方向）→ 保全して警告

TDD 規律（AGENTS.md 入口規律）に従い、本テストは実装前に作成する。
実行：
  cd /Users/Daily/Development/ReviewCompass
  python3 -m unittest tests.tools.test_session_record_append_merge -v
"""

import json
import hashlib
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
BACKFILL = REPO_ROOT / "tools" / "session-record-backfill.py"

TS = "2026-06-14T10:00:00.000Z"


def _user(text):
  return {"type": "user", "timestamp": TS,
          "message": {"role": "user", "content": text}}


def _commit(msg):
  return {"type": "assistant", "timestamp": TS,
          "message": {"role": "assistant", "content": [
            {"type": "tool_use", "name": "Bash",
             "input": {"command": f'git commit -m "{msg}"'}}]}}


def _objs(statements, commits=()):
  objs = [_user(s) for s in statements]
  objs += [_commit(m) for m in commits]
  return objs


def _write_fixture(path, objs):
  path.parent.mkdir(parents=True, exist_ok=True)
  body = "\n".join(json.dumps(o, ensure_ascii=False) for o in objs) + "\n"
  path.write_text(body, encoding="utf-8")


def _run_session(session_path, evidence_dir, docs_dir, source="claude"):
  return subprocess.run(
    [
      sys.executable, str(BACKFILL),
      "--session", str(session_path),
      "--source", source,
      "--evidence-dir", str(evidence_dir),
      "--docs-dir", str(docs_dir),
    ],
    cwd=str(REPO_ROOT),
    capture_output=True,
    text=True,
    errors="replace",
    timeout=60,
  )


class AppendOnlyMergeTests(unittest.TestCase):
  def setUp(self):
    self.tmp = Path(tempfile.mkdtemp())
    self.addCleanup(shutil.rmtree, self.tmp)
    self.evidence = self.tmp / "evidence"
    self.docs = self.tmp / "docs"

  def _record_path(self, stem):
    return self.docs / f"auto-2026-06-14-claude-{stem}.md"

  def test_same_content_is_not_rewritten(self):
    """既存と同一なら書き込みを起こさない（更新なし）。"""
    stem = "mergesame-0001"
    sess = self.tmp / f"{stem}.jsonl"
    _write_fixture(sess, _objs(["最初の指示"]))
    r1 = _run_session(sess, self.evidence, self.docs)
    self.assertEqual(r1.returncode, 0, f"1回目 stdout={r1.stdout}\nstderr={r1.stderr}")
    # 内容を変えずに 2 回目
    r2 = _run_session(sess, self.evidence, self.docs)
    self.assertEqual(r2.returncode, 0, f"2回目 stdout={r2.stdout}\nstderr={r2.stderr}")
    self.assertIn("更新なし: 1", r2.stdout,
                  f"同一は更新なしと報告するはず。stdout={r2.stdout}")

  def test_same_body_refreshes_stale_frontmatter_hash(self):
    """本文が同一でも source_sha256 が古ければ frontmatter だけ更新する。"""
    stem = "mergehash-0001"
    sess = self.tmp / f"{stem}.jsonl"
    _write_fixture(sess, _objs(["最初の指示"]))
    r1 = _run_session(sess, self.evidence, self.docs)
    self.assertEqual(r1.returncode, 0, f"1回目 stdout={r1.stdout}\nstderr={r1.stderr}")

    # parser が本文へ出さない summary を足し、記録本文は同一のまま source hash だけ変える。
    original = sess.read_text(encoding="utf-8")
    sess.write_text(
      original + json.dumps({"type": "summary", "summary": "ignored"}, ensure_ascii=False) + "\n",
      encoding="utf-8",
    )
    r2 = _run_session(sess, self.evidence, self.docs)
    self.assertEqual(r2.returncode, 0, f"2回目 stdout={r2.stdout}\nstderr={r2.stderr}")
    self.assertIn("更新: 1", r2.stdout,
                  f"frontmatter だけ古い場合も更新として報告するはず。stdout={r2.stdout}")

    tpath = self.evidence / f"2026-06-14-claude-{stem}.md"
    rpath = self._record_path(stem)
    source_sha = hashlib.sha256(sess.read_bytes()).hexdigest()
    for path in (tpath, rpath):
      text = path.read_text(encoding="utf-8")
      self.assertIn(f"source_sha256: {source_sha}", text,
                    f"{path} の source_sha256 が最新であること")
      self.assertEqual(1, len(re.findall(r"最初の指示", text)),
                       f"{path} の本文は追記重複しないこと")
    self.assertIn("再現性チェック: ok 2", r2.stdout,
                  f"frontmatter 更新後は再現性 ok のはず。stdout={r2.stdout}")

  def test_grown_log_extends_record(self):
    """元ログが伸びたら拡張と判定し、増分が反映される。"""
    stem = "mergegrow-0001"
    sess = self.tmp / f"{stem}.jsonl"
    _write_fixture(sess, _objs(["指示その1"]))
    r1 = _run_session(sess, self.evidence, self.docs)
    self.assertEqual(r1.returncode, 0, f"1回目 stdout={r1.stdout}")
    # 伸ばす（発言を追記）
    _write_fixture(sess, _objs(["指示その1", "指示その2"]))
    r2 = _run_session(sess, self.evidence, self.docs)
    self.assertEqual(r2.returncode, 0, f"2回目 stdout={r2.stdout}")
    self.assertIn("更新: 1", r2.stdout, f"拡張は更新と報告するはず。stdout={r2.stdout}")
    body = self._record_path(stem).read_text(encoding="utf-8")
    self.assertIn("指示その1", body, "既存の発言が残る")
    self.assertIn("指示その2", body, "増えた発言が反映される")

  def test_shrunk_log_preserves_existing(self):
    """元ログが縮んだら縮小と判定し、既存を保全する（上書きしない＋警告）。"""
    stem = "mergeshrink-0001"
    sess = self.tmp / f"{stem}.jsonl"
    _write_fixture(sess, _objs(["指示その1", "指示その2"]))
    r1 = _run_session(sess, self.evidence, self.docs)
    self.assertEqual(r1.returncode, 0, f"1回目 stdout={r1.stdout}")
    # 縮める（発言を消す）
    _write_fixture(sess, _objs(["指示その1"]))
    r2 = _run_session(sess, self.evidence, self.docs)
    self.assertEqual(r2.returncode, 0, f"2回目 stdout={r2.stdout}")
    self.assertIn("保全（縮小検出）: 1", r2.stdout,
                  f"縮小は保全と報告するはず。stdout={r2.stdout}")
    body = self._record_path(stem).read_text(encoding="utf-8")
    self.assertIn("指示その2", body,
                  "縮小時は既存記録を保全する（消えた発言が残る）")

  def test_placeholder_to_data_is_extend_not_shrink(self):
    """空欄（コミットなし）が実データ（コミットあり）に変わるのは拡張で、保全にしない。"""
    stem = "mergeph-0001"
    sess = self.tmp / f"{stem}.jsonl"
    _write_fixture(sess, _objs(["指示その1"]))  # コミットなし → 層2は（なし）
    r1 = _run_session(sess, self.evidence, self.docs)
    self.assertEqual(r1.returncode, 0, f"1回目 stdout={r1.stdout}")
    _write_fixture(sess, _objs(["指示その1"], commits=["コミットc1"]))
    r2 = _run_session(sess, self.evidence, self.docs)
    self.assertEqual(r2.returncode, 0, f"2回目 stdout={r2.stdout}")
    self.assertIn("更新: 1", r2.stdout,
                  f"空欄→実データは拡張（更新）。保全にしない。stdout={r2.stdout}")
    body = self._record_path(stem).read_text(encoding="utf-8")
    self.assertIn("コミットc1", body, "増えたコミットが反映される")


if __name__ == "__main__":
  unittest.main()
