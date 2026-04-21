import os
import sys
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.agents.parser import parse_single

INPUT_DIR = os.path.join(os.path.dirname(__file__), "gold_standard", "input")
EXPECTED_DIR = os.path.join(os.path.dirname(__file__), "gold_standard", "expected")
FIELDS = ["title", "date", "time", "cost"]

def normalize(value):
    if value is None:
        return "N/A"
    return str(value).strip().replace("'", '"')

def get_cost(parsed):
    if parsed.get("cost_free") is True:
        return "Free"
    elif parsed.get("cost_amount"):
        return f"${parsed.get('cost_amount')}"
    return "N/A"

def run_eval():
    results = []
    for i in range(1, 21):
        input_path = os.path.join(INPUT_DIR, f"event_{i}.json")
        expected_path = os.path.join(EXPECTED_DIR, f"event_{i}.json")

        with open(input_path) as f:
            input_data = json.load(f)
        with open(expected_path) as f:
            expected = json.load(f)

        # Run the Parser on this single event
        parsed = parse_single(input_data["url"], input_data["source"], input_data["trimmed_dict"])
        
        if parsed is None:
            print(f"  [SKIP] Parser returned None for event {i}")
            results.append(False)
            continue

        print(f"\n--- Event {i} ---")
        event_pass = True
        for field in FIELDS:
            if field == "cost": 
                actual = normalize(get_cost(parsed))
            else: 
                actual = normalize(parsed.get(field))
            expected_val = normalize(expected.get(field))
            match = actual == expected_val
            status = "PASS" if match else "FAIL"
            if not match:
                event_pass = False
            print(f"  {field}: [{status}] got '{actual}' | expected '{expected_val}'")

        results.append(event_pass)

    total = len(results)
    passed = sum(results)
    print(f"\n=== RESULTS: {passed}/{total} events fully matched ===")
    print(f"Exact match rate: {passed/total*100:.1f}%")
    if passed >= 16:
        print("✅ PASSED threshold (≥80%)")
    else:
        print("❌ FAILED threshold (<80%)")

if __name__ == "__main__":
    run_eval()
