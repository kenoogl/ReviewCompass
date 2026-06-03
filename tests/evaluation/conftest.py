"""evaluation テスト共通設定。

evaluation 機能のコードは配置先ルート `evaluation/` 配下の各パッケージに置く。
テストから `import intake.<module>` で取り込めるよう、`evaluation/` を
import パスに追加する。
"""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
EVALUATION_ROOT = REPO_ROOT / "evaluation"

if str(EVALUATION_ROOT) not in sys.path:
  sys.path.insert(0, str(EVALUATION_ROOT))
