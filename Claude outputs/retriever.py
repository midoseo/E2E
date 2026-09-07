"""
retrieval v2 — IDF 가중 + KB별 개념 키워드(concept) 매칭
v1(단순 단어 겹침 개수) 대비 개선점:
  1) 흔한 단어(AI·보안·서비스·보도·영상 등)는 여러 KB에 나타나므로 IDF로 가중치를 낮춘다.
  2) KB마다 '핵심 개념 키워드'를 큐레이션해, 기사에 그 개념이 있으면 크게 가산한다.
     → 겹치는 단어가 아니라 '판단 규칙의 본질'로 매칭.
"""
import json, re, math

kb = json.load(open('/home/claude/out/kb_seed.json'))['entries']
arts = json.load(open('/home/claude/out/experiment/articles.json'))

# KB별 핵심 개념 키워드 (사람이 큐레이션 — KB 품질 향상 겸용)
CONCEPT = {
 "KB-260904-001": ["공공","지자체","조달","발주","노후","교체","예산","관제민간위탁"],
 "KB-260904-002": ["급증","증가","개화","공급","실수요","성장","시범사업","보급"],
 "KB-260904-003": ["벤더","공급사","제조사","자사브랜드","매각형","한화비전","공급망"],
 "KB-260904-004": ["경쟁사","캠페인","소상공인","창업","점주","인플루언서","2030","선점"],
 "KB-260904-005": ["홈쇼핑","유통","반려로봇","제휴","구독","B2C","벤치마킹"],
 "KB-260904-006": ["경쟁사","홍보","보도자료","일상홍보","솔루션출시"],
 "KB-260904-007": ["행정","조례","의무화","시정","건설현장","규제제한"],
 "KB-260904-008": ["세대","20대","트렌드","영포티","소비층"],
 "KB-260904-009": ["규제","법규","중대재해","산업안전","의무","처벌","안전"],
}

STOP = set("그리고 그러나 하지만 대한 위한 통해 관련 등의 있는 있다 없다 되는 하는 이번 최근 대비 함께 및 등 것 수 더 를 은 는 이 가 에 의 로 과 와 도 만 큰 늘 넘어".split())

def toks(*texts):
    s=" ".join(t for t in texts if t)
    out=set()
    for w in re.findall(r"[가-힣A-Za-z0-9]+", s):
        if len(w)<2 or w in STOP: continue
        out.add(w)
        if re.match(r"[가-힣]+$",w) and len(w)>=3: out.add(w[:2]); out.add(w[:3])
    return out

# IDF: 각 KB의 (trigger+judgment+rationale) 를 문서로 보고 df 계산
docs=[toks(e['trigger'],e['judgment'],e['rationale']) for e in kb]
N=len(docs)
df={}
for d in docs:
    for w in d: df[w]=df.get(w,0)+1
def idf(w): return math.log((N+1)/(df.get(w,0)+0.5))

def concept_hits(art_tokens, kbid):
    hits=[c for c in CONCEPT.get(kbid,[]) if any(c in t or t in c for t in art_tokens) or c in art_tokens]
    # 개념 키워드가 기사 토큰에 부분 포함되는지도 관대하게 체크
    hits2=set()
    joined=" ".join(art_tokens)
    for c in CONCEPT.get(kbid,[]):
        if c in joined: hits2.add(c)
    return sorted(hits2)

def score_v1(at,e):  # 단순 겹침 개수 (기존)
    return len(at & toks(e['trigger'],e['judgment'],e['rationale']))

def score_v2(at,e):
    # 규칙 게이트: 개념 키워드가 하나도 안 맞으면 이 KB는 후보에서 제외(점수 0).
    # 어휘 겹침(IDF)은 '개념이 맞은 것들 사이의 순위'에만 쓴다.
    kt=toks(e['trigger'],e['judgment'],e['rationale'])
    inter=at & kt
    idf_overlap=sum(idf(w) for w in inter)
    ch=concept_hits(at,e['id'])
    if not ch:
        return 0.0, round(idf_overlap,2), ch   # 게이트 탈락
    score=10*len(ch)+0.3*idf_overlap           # 개념 매칭이 지배, 어휘는 미세 조정
    return round(score,2), round(idf_overlap,2), ch

print("="*70)
for a in arts:
    at=toks(a['title'],a['summary'])
    for axis in a['run_axes']:
        cand=[e for e in kb if axis in e['axis_tag']]
        v1=sorted(((score_v1(at,e),e['id']) for e in cand), reverse=True)
        v2=sorted(((score_v2(at,e)[0], score_v2(at,e)[2], score_v2(at,e)[1], e['id']) for e in cand), reverse=True)
        print(f"\n[{a['id']} · {axis}]  (기사: {a['title']})")
        print("  v1(단순겹침) 순위:", [f"{i}({s})" for s,i in v1])
        print("  v2(개념게이트+IDF) 순위:")
        for s,ch,ov,i in v2:
            gate="" if ch else "  ✗게이트탈락(개념0)"
            print(f"     {i}  score={s}  개념매칭={ch}  어휘IDF={ov}{gate}")
        v1top=v1[0][1] if v1 and v1[0][0]>0 else None
        v2top=v2[0][3] if v2 and v2[0][0]>0 else None
        flag="  ✅ 선택 KB 변경됨" if v1top!=v2top else ""
        print(f"  → v1 선택={v1top} / v2 선택={v2top}{flag}")
