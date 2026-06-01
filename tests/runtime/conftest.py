"""runtime テスト共通設定。

runtime 機能のコードは配置先ルート `runtime/` 配下の `runtime_core` パッケージに置く。
テストから `import runtime_core.<module>` で取り込めるよう、`runtime/` を import パスに追加する。
"""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
RUNTIME_ROOT = REPO_ROOT / "runtime"

if str(RUNTIME_ROOT) not in sys.path:
  sys.path.insert(0, str(RUNTIME_ROOT))
