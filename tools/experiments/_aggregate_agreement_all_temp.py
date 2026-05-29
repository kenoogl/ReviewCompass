"""全機能タスクフェーズのモデル別人本人一致率を統合算出（セッション40、後で削除予定）。
人本人判定：topic-NN-human.yaml があればそれ、無ければ完全一致＝多数派として扱う。"""
import re
from collections import Counter
from pathlib import Path

R = Path(__file__).resolve().parent.parent.parent / "tools" / "experiments" / "results"

def extract(text):
    m = re.search(r'decision:\s*\\?["\']?\s*(採用[：:]?\s*案\s*[12]|別案を提示|深掘り要求)', text)
    if not m: return "?"
    d = m.group(1).replace(" ", "").replace(":", "：")
    return {"採用：案1":"案1","採用：案2":"案2","別案を提示":"別案","深掘り要求":"深掘"}.get(d, d)

def model_dec(topic, suf):
    for p in (R/f"topic-{topic}-{suf}-final.yaml", R/f"topic-{topic}-{suf}.yaml"):
        if p.exists(): return extract(p.read_text(encoding="utf-8"))
    return "欠"

def human_dec(topic, decs):
    p = R/f"topic-{topic}-human.yaml"
    if p.exists():
        d = extract(p.read_text(encoding="utf-8"))
        if d != "?": return d
    # 完全一致＝多数派
    valid = [d for d in decs if d not in ("?","欠")]
    if valid:
        c = Counter(valid).most_common()
        return c[0][0]
    return "?"

M7 = [("opus-4-7","Opus"),("sonnet-4-6-cli","Sonnet-CLI"),("sonnet-4-6-api","Sonnet-API"),
      ("gpt-5-5","GPT-5.5"),("gpt-5-4","GPT-5.4"),("gemini-3-5-flash","G-flash"),("gemini-3-1-pro-preview","G-pro")]
M6 = [m for m in M7 if m[0]!="opus-4-7"]
M5 = [m for m in M6 if m[0]!="sonnet-4-6-cli"]

FEATS = [
  ("evaluation", range(34,53), M6),
  ("analysis", range(53,76), M7),
  ("workflow-mgmt", range(76,99), M7),
  ("self-improve", range(99,111), M7),
  ("conformance", range(111,121), M7),
  ("横断2回目", range(121,123), M5),
]

# per-model per-feature 一致率
agree = {lbl:{} for _,lbl in M7}
for fname, rng, models in FEATS:
    for topic in rng:
        decs = [model_dec(topic, suf) for suf,_ in models]
        h = human_dec(topic, decs)
        for (suf,lbl), d in zip(models, decs):
            agree[lbl].setdefault(fname, [0,0])
            agree[lbl][fname][1]+=1
            if d==h and d not in ("?","欠"): agree[lbl][fname][0]+=1

print("=== モデル別 人本人一致率（機能別、完全一致は人本人＝多数派として扱う）===")
hdr = ["モデル"]+[f for f,_,_ in FEATS]+["全体"]
print(" | ".join(hdr))
for _,lbl in M7:
    cells=[lbl]; tm=0; tt=0
    for fname,_,_ in FEATS:
        if fname in agree[lbl]:
            m,t = agree[lbl][fname]; tm+=m; tt+=t
            cells.append(f"{m}/{t}={100*m//t if t else 0}%")
        else:
            cells.append("—")
    cells.append(f"{tm}/{tt}={100*tm//tt if tt else 0}%")
    print(" | ".join(cells))
