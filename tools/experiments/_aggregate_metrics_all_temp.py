"""全機能の生データから、裁定の質に関わる指標を算出（セッション40、後で削除予定）。"""
import re
from collections import Counter
from pathlib import Path
R = Path(__file__).resolve().parent.parent.parent / "tools" / "experiments" / "results"
def extract(text):
    m = re.search(r'decision:\s*\\?["\']?\s*(採用[：:]?\s*案\s*[12]|別案を提示|深掘り要求)', text)
    if not m: return "?"
    d = m.group(1).replace(" ","").replace(":","：")
    return {"採用：案1":"案1","採用：案2":"案2","別案を提示":"別案","深掘り要求":"深掘"}.get(d,d)
def mdec(topic, suf, use_final):
    if use_final:
        p=R/f"topic-{topic}-{suf}-final.yaml"
        if p.exists(): return extract(p.read_text(encoding="utf-8"))
    p=R/f"topic-{topic}-{suf}.yaml"
    if p.exists(): return extract(p.read_text(encoding="utf-8"))
    return "欠"
M7=[("opus-4-7","Opus"),("sonnet-4-6-cli","Sonnet-CLI"),("sonnet-4-6-api","Sonnet-API"),("gpt-5-5","GPT-5.5"),("gpt-5-4","GPT-5.4"),("gemini-3-5-flash","G-flash"),("gemini-3-1-pro-preview","G-pro")]
M6=[m for m in M7 if m[0]!="opus-4-7"]; M5=[m for m in M6 if m[0]!="sonnet-4-6-cli"]
FEATS=[("evaluation",range(34,53),M6),("analysis",range(53,76),M7),("wf-mgmt",range(76,99),M7),("self-imp",range(99,111),M7),("conf",range(111,121),M7),("横断2",range(121,123),M5)]
# 1ターン目の?/深掘（質問返し率）と 最終の別案率
print("=== モデル別：1ターン目の質問返し率（?＝質問返し・深掘）/ 最終の別案率 ===")
q1=Counter(); n1=Counter(); altf=Counter(); nf=Counter()
for fn,rng,models in FEATS:
    for t in rng:
        for suf,lbl in models:
            d1=mdec(t,suf,False)
            if d1!="欠":
                n1[lbl]+=1
                if d1 in ("?","深掘"): q1[lbl]+=1
            df=mdec(t,suf,True)
            if df!="欠":
                nf[lbl]+=1
                if df=="別案": altf[lbl]+=1
for _,lbl in M7:
    print(f"  {lbl:12} 質問返し1T: {q1[lbl]}/{n1[lbl]}={100*q1[lbl]//n1[lbl] if n1[lbl] else 0}%  最終別案: {altf[lbl]}/{nf[lbl]}={100*altf[lbl]//nf[lbl] if nf[lbl] else 0}%")
# 機能別 完全一致/割れ（最終）
print("\n=== 機能別 分岐度（最終判定）===")
for fn,rng,models in FEATS:
    full=0; tot=0
    for t in rng:
        ds=[mdec(t,suf,True) for suf,_ in models]
        ds=[d for d in ds if d not in ("欠",)]
        if not ds: continue
        tot+=1
        if len(set(d for d in ds if d!="?"))<=1: full+=1
    print(f"  {fn:10} 完全一致 {full}/{tot}={100*full//tot if tot else 0}%")
