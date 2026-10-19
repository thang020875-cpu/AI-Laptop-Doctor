from process_monitor import (
    monitor_processes,
    analyze_process_samples
)


print()
print("=" * 70)
print("       AI LAPTOP DOCTOR - PROCESS MONITOR TEST")
print("=" * 70)


# =========================================================
# MONITOR
# =========================================================

samples = monitor_processes(
    duration_seconds=20,
    interval_seconds=5,
    top_n=10
)


# =========================================================
# ANALYZE
# =========================================================

print()
print("=" * 70)
print("                PROCESS ANALYSIS")
print("=" * 70)


result = analyze_process_samples(
    samples
)


print()
print(
    f"Status       : "
    f"{result.get('status')}"
)

print(
    f"Sample count : "
    f"{result.get('sample_count')}"
)


# =========================================================
# FINDINGS
# =========================================================

print()
print("Findings:")

findings = result.get(
    "findings",
    []
)

if findings:

    for index, finding in enumerate(
        findings,
        start=1
    ):

        print()

        print(
            f"[{index}] "
            f"{finding.get('cause')}"
        )

        print(
            f"    Evidence   : "
            f"{finding.get('evidence')}"
        )

        print(
            f"    Confidence : "
            f"{finding.get('confidence')}"
        )

else:

    print(
        "  - Không phát hiện "
        "process bất thường."
    )


# =========================================================
# RECOMMENDATIONS
# =========================================================

print()
print("Recommendations:")

for recommendation in result.get(
    "recommendations",
    []
):

    print(
        f"  - {recommendation}"
    )


print()
print("=" * 70)
print("              TEST COMPLETED")
print("=" * 70)