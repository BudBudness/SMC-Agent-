WEIGHTS={"weekly_structure":25,"weekly_location":15,"liquidity":10,"inducement":10,"sweep":10,
"structure_shift":10,"displacement":5,"fvg_ob":5,"premium_discount":3,"economic":5,"session":2}

def score(features):
    return sum(WEIGHTS[k] for k,v in features.items() if v and k in WEIGHTS)

def grade(score):
    return "A+" if score>=90 else "A" if score>=80 else "B" if score>=70 else "C" if score>=60 else "NO TRADE"
