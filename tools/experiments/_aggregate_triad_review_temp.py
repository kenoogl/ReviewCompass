"""三役レビュー（triad-review）記録の front-matter を集計（セッション40、後で削除予定）。"""
import glob, yaml
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent.parent
FEATS = ["foundation","runtime","evaluation","analysis","workflow-management","self-improvement","conformance-evaluation"]

def load_fm(feat):
    p = sorted(glob.glob(str(ROOT/f".reviewcompass/specs/{feat}/reviews/*tasks*triad*.md")))[0]
    fm = Path(p).read_text(encoding="utf-8").split("---",2)[1]
    return yaml.safe_load(fm)["findings_by_method"]

def sev(d):  # by_severity dict or {}
    return {k: d.get(k,0) for k in ("CRITICAL","ERROR","WARN","INFO")}

def counter(adv):
    c = adv.get("counter_distribution") or adv.get("by_counter_status") or {}
    if "counter_evidence_raised" in c:
        return c.get("counter_evidence_raised",0), c.get("no_counter_evidence_after_challenge",0)
    return None, None

rows=[]; T={k:0 for k in ("p","a","must","should","leave","cr","nc","C","E","W","I")}
for f in FEATS:
    m=load_fm(f); p=m["primary"]; a=m["adversarial"]; jb=m["judgment"]["by_judgment"]
    ps=sev(p.get("by_severity",{}))
    pc=p.get("count", sum(ps.values()))
    ac=a.get("count", sum(sev(a.get("by_severity",{})).values()))
    cr,nc=counter(a)
    rows.append((f,pc,ac,ps,jb,cr,nc))
    T["p"]+=pc; T["a"]+=ac
    T["must"]+=jb["must-fix"]; T["should"]+=jb["should-fix"]; T["leave"]+=jb["leave-as-is"]
    for k,kk in [("C","CRITICAL"),("E","ERROR"),("W","WARN"),("I","INFO")]: T[k]+=ps[kk]
    if cr is not None: T["cr"]+=cr; T["nc"]+=nc

print("=== 三役レビュー集計（全7機能 tasks 段）===\n")
print("| 機能 | 主役 | 敵対役 | 主役 C/E/W/I | must/should/leave | 反証 raised/評価済 |")
print("|---|---|---|---|---|---|")
for f,pc,ac,ps,jb,cr,nc in rows:
    ct=f"{cr}/{cr+nc}" if cr is not None else "—(FM欠)"
    print(f"| {f} | {pc} | {ac} | {ps['CRITICAL']}/{ps['ERROR']}/{ps['WARN']}/{ps['INFO']} | {jb['must-fix']}/{jb['should-fix']}/{jb['leave-as-is']} | {ct} |")
jt=T["must"]+T["should"]+T["leave"]
print(f"| **合計** | **{T['p']}** | **{T['a']}** | {T['C']}/{T['E']}/{T['W']}/{T['I']} | {T['must']}/{T['should']}/{T['leave']} | {T['cr']}/{T['cr']+T['nc']} |")
print(f"\n=== 派生指標 ===")
print(f"- 主役発見 {T['p']} 件 ／ 敵対役発見 {T['a']} 件 ／ 判定 {jt} 件")
print(f"- 主役 severity：CRITICAL {T['C']} ／ ERROR {T['E']} ／ WARN {T['W']} ／ INFO {T['I']}")
print(f"- 判定分布：must {T['must']}({100*T['must']//jt}%) ／ should {T['should']}({100*T['should']//jt}%) ／ leave {T['leave']}({100*T['leave']//jt}%)")
print(f"- 敵対役反証率（counter記載4機能 runtime/evaluation/self-improve/conformance）：{T['cr']}/{T['cr']+T['nc']}={100*T['cr']//(T['cr']+T['nc'])}%")
print(f"- leave-as-is 率（敵対役の反証等で「直さなくてよい」と判定された割合）：{100*T['leave']//jt}%")
