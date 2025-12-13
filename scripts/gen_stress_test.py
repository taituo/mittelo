import json

tasks = []
for i in range(1, 51):
    kind = "HARD" if i % 5 == 0 else "EASY" # Every 5th task is hard
    prompt = f"Task #{i} [{kind}]: Please analyze component X and refactor." if kind == "HARD" else f"Task #{i} [{kind}]: Quick fix typo."
    tasks.append({"prompt": prompt})

with open("examples/stress_test.jsonl", "w") as f:
    for t in tasks:
        f.write(json.dumps(t) + "\n")

print(f"Generated {len(tasks)} tasks to examples/stress_test.jsonl")
