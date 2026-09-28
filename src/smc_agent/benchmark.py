"""Benchmark utilities for labelled historical intelligence episodes."""
def score_detection(expected,observed):
    expected=set(expected or []); observed=set(observed or [])
    tp=len(expected & observed); fp=len(observed-expected); fn=len(expected-observed)
    precision=tp/(tp+fp) if tp+fp else 0.0
    recall=tp/(tp+fn) if tp+fn else 0.0
    f1=2*precision*recall/(precision+recall) if precision+recall else 0.0
    return {"true_positive":tp,"false_positive":fp,"false_negative":fn,
            "precision":precision,"recall":recall,"f1":f1}
