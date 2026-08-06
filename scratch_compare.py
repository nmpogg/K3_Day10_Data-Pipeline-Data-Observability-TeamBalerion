import json

with open('data/results/baseline_answers.json') as f:
    b = json.load(f)
with open('data/results/repaired_answers.json') as f:
    r = json.load(f)
    
for x, y in zip(b, r):
    if x['token_f1'] != y['token_f1'] or x['judge']['score'] != y['judge']['score']:
        print(f"{x['id']}: Baseline F1={x['token_f1']:.3f} Score={x['judge']['score']} | Repaired F1={y['token_f1']:.3f} Score={y['judge']['score']}")
        print(f"  B Ans: {x['answer']}")
        print(f"  R Ans: {y['answer']}")
