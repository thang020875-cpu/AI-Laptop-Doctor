from performance_monitor import (
    monitor_performance,
    analyze_performance_samples
)


print()
print("=" * 70)
print("          AI LAPTOP DOCTOR - PERFORMANCE TEST")
print("=" * 70)


# ---------------------------------------------------------
# MONITOR
# ---------------------------------------------------------

samples = monitor_performance(
    duration_seconds=30,
    interval_seconds=5
)


# ---------------------------------------------------------
# ANALYZE
# ---------------------------------------------------------

print()
print("=" * 70)
print("              PERFORMANCE ANALYSIS")
print("=" * 70)

result = analyze_performance_samples(samples)


print()
print(f"Status       : {result.get('status')}")
print(f"Sample count : {result.get('sample_count')}")


# ---------------------------------------------------------
# FINDINGS
# ---------------------------------------------------------

print()
print("Findings:")

findings = result.get("findings", [])

if findings:

    for index, finding in enumerate(findings, start=1):

        print()
        print(f"[{index}] {finding.get('cause')}")
        print(f"    Evidence   : {finding.get('evidence')}")
        print(f"    Confidence : {finding.get('confidence')}")

else:

    print("  - Không phát hiện dấu hiệu bất thường.")


# ---------------------------------------------------------
# RECOMMENDATIONS
# ---------------------------------------------------------

print()
print("Recommendations:")

for recommendation in result.get(
    "recommendations",
    []
):

    print(f"  - {recommendation}")


print()
print("=" * 70)
print("              TEST COMPLETED")
print("=" * 70)