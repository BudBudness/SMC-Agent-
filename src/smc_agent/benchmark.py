"""Benchmark utilities for labelled historical intelligence episodes."""

def score_detection(expected, observed):
    expected=set(expected or []); observed=set(observed or [])
    tp=len(expected & observed); fp=len(observed-expected); fn=len(expected-observed)
    precision=tp/(tp+fp) if tp+fp else 0.0
    recall=tp/(tp+fn) if tp+fn else 0.0
    f1=2*precision*recall/(precision+recall) if precision+recall else 0.0
    return {"true_positive":tp,"false_positive":fp,"false_negative":fn,
            "precision":precision,"recall":recall,"f1":f1}

def score_sequence(expected, observed):
    """Score whether observed events preserve the reference relative order."""
    expected=list(dict.fromkeys(expected or [])); observed=list(dict.fromkeys(observed or []))
    if not expected:
        return {"reference_events":0,"matched_events":0,"order_pairs":0,"correct_order_pairs":0,"order_accuracy":0.0}
    pos={name:i for i,name in enumerate(observed)}
    pairs=correct=0
    for i,a in enumerate(expected):
        for b in expected[i+1:]:
            if a in pos and b in pos:
                pairs += 1
                correct += int(pos[a] < pos[b])
    matched=sum(name in pos for name in expected)
    return {"reference_events":len(expected),"matched_events":matched,
            "order_pairs":pairs,"correct_order_pairs":correct,
            "order_accuracy":correct/pairs if pairs else 0.0}

def aggregate_detection(rows):
    keys=("true_positive","false_positive","false_negative")
    totals={k:sum(int(r.get(k,0)) for r in rows) for k in keys}
    tp,fp,fn=totals.values()
    p=tp/(tp+fp) if tp+fp else 0.0; r=tp/(tp+fn) if tp+fn else 0.0
    return {**totals,"precision":p,"recall":r,"f1":2*p*r/(p+r) if p+r else 0.0}
