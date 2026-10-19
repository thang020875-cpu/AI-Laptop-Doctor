import json

from fault_diagnosis import diagnose_fault


# =========================================================
# LOAD SYSTEM REPORT
# =========================================================

with open(
    "system_report.json",
    "r",
    encoding="utf-8"
) as file:

    report = json.load(file)


# =========================================================
# TEST USER PROBLEM
# =========================================================

user_problem = input(
    "\nNhập vấn đề của laptop: "
)


# =========================================================
# DIAGNOSIS
# =========================================================

result = diagnose_fault(
    user_problem,
    report
)


# =========================================================
# DISPLAY
# =========================================================

print()
print("=" * 65)
print("              AI LAPTOP DOCTOR")
print("              FAULT DIAGNOSIS")
print("=" * 65)

print()

print(
    f"Problem : "
    f"{result['user_input']}"
)

classification = result[
    "classification"
]

print()

print(
    f"Fault ID  : "
    f"{classification['fault_id']}"
)

print(
    f"Category  : "
    f"{classification['category']}"
)

print(
    f"Title     : "
    f"{classification['title']}"
)

print()

analysis = result[
    "analysis"
]

print(
    f"Status    : "
    f"{analysis['status']}"
)

print(
    f"Severity  : "
    f"{analysis['severity']}"
)

# =========================================================
# FINDINGS
# =========================================================

findings = analysis.get(
    "findings",
    []
)

if findings:

    print()
    print("Possible causes:")

    for finding in findings:

        print(
            f"  - {finding['cause']}"
        )

        print(
            f"    Evidence   : "
            f"{finding['evidence']}"
        )

        print(
            f"    Confidence : "
            f"{finding['confidence'] * 100:.0f}%"
        )

# =========================================================
# RECOMMENDATIONS
# =========================================================

recommendations = analysis.get(
    "recommendations",
    []
)

if recommendations:

    print()
    print("Recommendations:")

    for recommendation in recommendations:

        print(
            f"  - {recommendation}"
        )

# =========================================================
# SAFETY
# =========================================================

print()

print("Safety:")

print(
    f"  Automatic repair : "
    f"{result['safety']['automatic_repair']}"
)

print(
    f"  Action level     : "
    f"{result['safety']['action_level']}"
)

print(
    f"  Message          : "
    f"{result['safety']['message']}"
)

print()
print("=" * 65)