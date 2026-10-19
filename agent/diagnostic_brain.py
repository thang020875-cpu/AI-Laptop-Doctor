"""
AI Laptop Doctor
Diagnostic Brain

Version: 1.1.0

Nhiệm vụ:
- Nhận triệu chứng
- Nhận bằng chứng chuẩn hóa
- Đối chiếu Knowledge Base
- Chấm điểm và xếp hạng nguyên nhân
- Không khẳng định linh kiện cụ thể bị hỏng khi chưa đủ bằng chứng
"""

from knowledge_base.power import POWER_NO_START


KNOWLEDGE_BASE = {
    "POWER_NO_START": POWER_NO_START
}


EVIDENCE_ALIASES = {
    # Question Engine v2 -> Knowledge Base
    "fan_off": "no_fan",
}


def normalize_evidence(evidence):
    normalized = []

    for item in evidence or []:
        mapped = EVIDENCE_ALIASES.get(item, item)

        if mapped not in normalized:
            normalized.append(mapped)

    return normalized


def calculate_cause_score(cause, evidence):
    evidence_set = set(normalize_evidence(evidence))

    supporting = set(
        cause.get("supporting_evidence", [])
    )

    contradicting = set(
        cause.get("contradicting_evidence", [])
    )

    score = cause.get("priority", 0)

    for item in evidence_set:
        if item in supporting:
            score += 2

        if item in contradicting:
            score -= 2

    return score


def analyze_power_no_start(evidence):
    normalized = normalize_evidence(evidence)

    results = []

    for cause in POWER_NO_START["causes"]:
        score = calculate_cause_score(
            cause,
            normalized
        )

        results.append({
            "cause_id": cause["id"],
            "name": cause["name"],
            "description": cause["description"],
            "score": score
        })

    results.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    return results


def determine_status(results):
    if not results:
        return "UNKNOWN"

    top_score = results[0]["score"]

    if top_score >= 8:
        return "LIKELY"

    if top_score >= 5:
        return "POSSIBLE"

    return "UNKNOWN"


def diagnose(symptom_code, evidence):
    normalized = normalize_evidence(evidence)

    if symptom_code not in KNOWLEDGE_BASE:
        return {
            "status": "UNKNOWN",
            "symptom_code": symptom_code,
            "evidence": normalized,
            "causes": []
        }

    if symptom_code == "POWER_NO_START":
        results = analyze_power_no_start(
            normalized
        )

        return {
            "status": determine_status(results),
            "symptom_code": symptom_code,
            "evidence": normalized,
            "causes": results
        }

    return {
        "status": "UNKNOWN",
        "symptom_code": symptom_code,
        "evidence": normalized,
        "causes": []
    }


if __name__ == "__main__":
    test_evidence = [
        "charger_led_on",
        "no_power_led",
        "fan_off",
        "power_reset_failed"
    ]

    result = diagnose(
        "POWER_NO_START",
        test_evidence
    )

    print("=" * 60)
    print("AI LAPTOP DOCTOR - DIAGNOSTIC BRAIN TEST")
    print("=" * 60)

    print(f"\nStatus: {result['status']}")

    print("\nEvidence:")
    for item in result["evidence"]:
        print(f"  - {item}")

    print("\nRanked causes:")

    for index, cause in enumerate(
        result["causes"],
        start=1
    ):
        print(
            f"{index}. "
            f"{cause['name']} "
            f"(score={cause['score']})"
        )
