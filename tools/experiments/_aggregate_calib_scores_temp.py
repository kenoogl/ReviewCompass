"""confidence 較正と case_scores 分離度を算出（セッション40、後で削除予定）。"""
import re
from collections import Counter, defaultdict
from pathlib import Path
R = Path(__file__).resolve().parent.parent.parent / "tools" / "experiments" / "results"
def rd(topic,suf,final):
    for p in ([R/f"topic-{topic}-{suf}-final.yaml"] if final else [])+[R/f"topic-{topic}-{suf}.yaml"]:
        if p.exists(): return p.read_text(encoding="utf-8")
    return None
def dec(t):
    m=re.search(r'decision:\s*\\?["\']?\s*(採用[：:]?\s*案\s*[12]|別案を提示|深掘り要求)',t)
    if not m:return "?"
    d=m.group(1).replace(" ","").replace(":","：")
    return {"採用：案1":"案1","採用：案2":"案2","別案を提示":"別案","深掘り要求":"深掘"}.get(d,d)
def conf(t):
    m=re.search(r'confidence:\s*([01](?:\.\d+)?)',t); return float(m.group(1)) if m else None
def cs(t):
    a=re.search(r'case_1:\s*(\d+)',t); b=re.search(r'case_2:\s*(\d+)',t)
    return (int(a.group(1)),int(b.group(1))) if a and b else None
M7=[("opus-4-7","Opus"),("sonnet-4-6-cli","Sonnet-CLI"),("sonnet-4-6-api","Sonnet-API"),("gpt-5-5","GPT-5.5"),("gpt-5-4","GPT-5.4"),("gemini-3-5-flash","G-flash"),("gemini-3-1-pro-preview","G-pro")]
M6=[m for m in M7 if m[0]!="opus-4-7"]; M5=[m for m in M6 if m[0]!="sonnet-4-6-cli"]
FEATS=[("eval",range(34,53),M6),("analysis",range(53,76),M7),("wf",range(76,99),M7),("si",range(99,111),M7),("conf",range(111,121),M7),("x2",range(121,123),M5)]
def human(topic,decs):
    p=R/f"topic-{topic}-human.yaml"
    if p.exists():
        d=dec(p.read_text(encoding="utf-8"))
        if d!="?":return d
    v=[d for d in decs if d not in("?","欠")]
    return Counter(v).most_common(1)[0][0] if v else "?"
# confidence 較正
cagree=defaultdict(list); cdis=defaultdict(list)
# case_scores 分離度（完全一致 vs 割れ topic）
gap_full=[]; gap_split=[]
for fn,rng,models in FEATS:
    for t in rng:
        texts={lbl:rd(t,suf,True) for suf,lbl in models}
        decs=[dec(texts[lbl]) if texts[lbl] else "欠" for _,lbl in models]
        h=human(t,decs)
        is_full=len(set(d for d in decs if d not in("?","欠")))<=1
        for (suf,lbl),d in zip(models,decs):
            tx=texts[lbl]
            if not tx:continue
            c=conf(tx)
            if c is not None and d not in("?","欠"):
                (cagree if d==h else cdis)[lbl].append(c)
            sc=cs(tx)
            if sc:
                g=abs(sc[0]-sc[1])
                (gap_full if is_full else gap_split).append(g)
print("=== confidence 較正（人本人一致時 vs 不一致時の平均信頼度）===")
for _,lbl in M7:
    a=cagree[lbl]; d=cdis[lbl]
    ma=sum(a)/len(a) if a else 0; md=sum(d)/len(d) if d else 0
    print(f"  {lbl:12} 一致時 {ma:.2f}(n={len(a)})  不一致時 {md:.2f}(n={len(d)})  差 {ma-md:+.2f}")
print("\n=== case_scores 分離度（採用案と非採用案のスコア差|case_1-case_2|）===")
print(f"  完全一致 topic：平均ギャップ {sum(gap_full)/len(gap_full):.2f}（n={len(gap_full)}）")
print(f"  割れ topic    ：平均ギャップ {sum(gap_split)/len(gap_split):.2f}（n={len(gap_split)}）")
