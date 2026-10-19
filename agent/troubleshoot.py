# =========================================================
# AI LAPTOP DOCTOR - END-TO-END TROUBLESHOOTING
# Version: 0.5.0
# =========================================================

from datetime import datetime

from fault_diagnosis import (
    classify_fault,
    diagnose_fault
)

from question_engine import (
    run_question_engine
)

from collector_plan import (
    create_collector_plan
)

from collector_runner import (
    run_collectors
)

from performance_monitor import (
    monitor_performance,
    analyze_performance_samples
)


# =========================================================
# DISPLAY HELPERS
# =========================================================

def print_header(title):
    print()
    print("=" * 70)
    print(f" {title}")
    print("=" * 70)


def print_classification(classification):

    print_header("FAULT CLASSIFICATION")

    print(
        f"Fault ID  : "
        f"{classification.get('fault_id')}"
    )

    print(
        f"Category  : "
        f"{classification.get('category')}"
    )

    print(
        f"Title     : "
        f"{classification.get('title')}"
    )

    print()
    print("Required data:")

    required_data = classification.get(
        "required_data",
        []
    )

    for item in required_data:
        print(f"  - {item}")


def print_questions(answers):

    print_header("USER ANSWERS")

    if not answers:
        print("Không có câu trả lời.")
        return

    for answer in answers:

        print()
        print(
            f"Question ID : "
            f"{answer.get('question_id')}"
        )

        print(
            f"Question    : "
            f"{answer.get('question')}"
        )

        print(
            f"Answer      : "
            f"{answer.get('answer')}"
        )


def print_collector_plan(plan):

    print_header("COLLECTOR PLAN")

    print(
        f"Fault ID : "
        f"{plan.get('fault_id')}"
    )

    print()
    print("Collectors:")

    collectors = plan.get(
        "collectors",
        []
    )

    for collector in collectors:
        print(f"  - {collector}")

    print()
    print("Reason:")

    reasons = plan.get(
        "reason",
        []
    )

    for reason in reasons:
        print(f"  - {reason}")


def print_collected_data(data):

    print_header("COLLECTED DATA")

    if not data:
        print("Không có dữ liệu.")
        return

    for name, value in data.items():

        print()
        print(
            f"[{name.upper()}]"
        )

        if isinstance(value, dict):

            for key, item in value.items():

                print(
                    f"  {key}: {item}"
                )

        else:

            print(
                f"  {value}"
            )


# =========================================================
# DIAGNOSIS DISPLAY
# =========================================================

def print_diagnosis(result):

    classification = result.get(
        "classification",
        {}
    )

    analysis = result.get(
        "analysis",
        {}
    )

    safety = result.get(
        "safety",
        {}
    )

    print_header("DIAGNOSIS RESULT")

    print(
        f"Fault ID : "
        f"{classification.get('fault_id')}"
    )

    print(
        f"Category : "
        f"{classification.get('category')}"
    )

    print(
        f"Title    : "
        f"{classification.get('title')}"
    )

    print()

    print(
        f"Status   : "
        f"{analysis.get('status')}"
    )

    print(
        f"Severity : "
        f"{analysis.get('severity')}"
    )

    # -----------------------------------------------------
    # FINDINGS
    # -----------------------------------------------------

    print()
    print("Possible causes:")

    findings = analysis.get(
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
                f"  [{index}] "
                f"{finding.get('cause')}"
            )

            print(
                f"      Evidence   : "
                f"{finding.get('evidence')}"
            )

            print(
                f"      Confidence : "
                f"{finding.get('confidence')}"
            )

    else:

        print(
            "  - Chưa xác định được "
            "nguyên nhân rõ ràng."
        )

    # -----------------------------------------------------
    # RECOMMENDATIONS
    # -----------------------------------------------------

    print()
    print("Recommendations:")

    recommendations = analysis.get(
        "recommendations",
        []
    )

    if recommendations:

        for recommendation in recommendations:

            print(
                f"  - {recommendation}"
            )

    else:

        print(
            "  - Không có khuyến nghị."
        )

    # -----------------------------------------------------
    # ADAPTIVE INFORMATION
    # -----------------------------------------------------

    if analysis.get(
        "adaptive",
        False
    ):

        print()
        print("Adaptive troubleshooting:")

        adaptive_status = analysis.get(
            "adaptive_status"
        )

        if adaptive_status:

            print(
                f"  Status : "
                f"{adaptive_status}"
            )

        adaptive_recommendations = (
            analysis.get(
                "adaptive_recommendations",
                []
            )
        )

        for recommendation in (
            adaptive_recommendations
        ):

            print(
                f"  - {recommendation}"
            )

    # -----------------------------------------------------
    # SAFETY
    # -----------------------------------------------------

    print()
    print("Safety:")

    print(
        f"  Automatic repair : "
        f"{safety.get('automatic_repair')}"
    )

    print(
        f"  Action level     : "
        f"{safety.get('action_level')}"
    )

    print(
        f"  Message          : "
        f"{safety.get('message')}"
    )


# =========================================================
# REPORT ADAPTER
# =========================================================

def build_partial_report(
    collected_data
):
    """
    Chuyển dữ liệu từ Collector Runner:

        {
            "cpu": {...},
            "memory": {...},
            "temperature": {...}
        }

    thành cấu trúc mà Diagnostic Engine sử dụng:

        {
            "hardware": {
                "cpu": {...},
                "memory": {...},
                "temperature": {...}
            }
        }
    """

    report = {

        "schema_version": "1.0",

        "timestamp":
            datetime.now().isoformat(),

        "system":
            collected_data.get(
                "system",
                {}
            ),

        "hardware": {

            "cpu":
                collected_data.get(
                    "cpu",
                    {}
                ),

            "memory":
                collected_data.get(
                    "memory",
                    {}
                ),

            "disk":
                collected_data.get(
                    "disk",
                    {}
                ),

            "gpu":
                collected_data.get(
                    "gpu",
                    {}
                ),

            "battery":
                collected_data.get(
                    "battery",
                    {}
                ),

            "temperature":
                collected_data.get(
                    "temperature",
                    {}
                )
        },

        "network":
            collected_data.get(
                "network",
                {}
            )
    }

    return report


# =========================================================
# ADAPTIVE TROUBLESHOOTING
# =========================================================

def run_adaptive_monitor(
    fault_id
):

    print_header(
        "ADAPTIVE TROUBLESHOOTING"
    )

    print()
    print(
        "Chưa đủ bằng chứng để "
        "xác định nguyên nhân."
    )

    print(
        "Hệ thống sẽ thu thập "
        "thêm dữ liệu hiệu năng."
    )

    # -----------------------------------------------------
    # PERFORMANCE
    # -----------------------------------------------------

    if fault_id == "R01":

        print()
        print(
            "[ADAPTIVE] "
            "Performance monitoring started."
        )

        samples = monitor_performance(
            duration_seconds=30,
            interval_seconds=5
        )

        print()
        print(
            "[ADAPTIVE] "
            "Analyzing performance data..."
        )

        result = analyze_performance_samples(
            samples
        )

        print(
            "[OK] Adaptive analysis completed."
        )

        return result

    # -----------------------------------------------------
    # OTHER FAULT TYPES
    # -----------------------------------------------------

    return {

        "status":
            "NOT_REQUIRED",

        "findings":
            [],

        "recommendations":
            []
    }


# =========================================================
# MAIN TROUBLESHOOTING FLOW
# =========================================================

def run_troubleshooting():

    # -----------------------------------------------------
    # HEADER
    # -----------------------------------------------------

    print_header(
        "AI LAPTOP DOCTOR"
    )

    print(
        "      END-TO-END TROUBLESHOOTING"
    )

    print(
        "=" * 70
    )

    # -----------------------------------------------------
    # STEP 1 - USER INPUT
    # -----------------------------------------------------

    print()
    print(
        "[1] Nhập vấn đề của máy tính"
    )

    print()

    user_input = input(
        "Mô tả lỗi: "
    ).strip()

    if not user_input:

        print()
        print(
            "[ERROR] "
            "Bạn chưa nhập vấn đề."
        )

        return

    print()

    print(
        f"Problem : "
        f"{user_input}"
    )

    # -----------------------------------------------------
    # STEP 2 - CLASSIFICATION
    # -----------------------------------------------------

    print()
    print(
        "[2] Phân loại lỗi..."
    )

    classification = classify_fault(
        user_input
    )

    print(
        "[OK] "
        "Fault classification completed."
    )

    print_classification(
        classification
    )

    fault_id = classification.get(
        "fault_id"
    )

    # -----------------------------------------------------
    # STEP 3 - QUESTIONS
    # -----------------------------------------------------

    print()
    print(
        "[3] Thu thập thông tin "
        "từ người dùng..."
    )

    answers = run_question_engine(
        fault_id
    )

    print(
        "[OK] "
        "Question collection completed."
    )

    print_questions(
        answers
    )

    # -----------------------------------------------------
    # STEP 4 - COLLECTOR PLAN
    # -----------------------------------------------------

    print()
    print(
        "[4] Tạo kế hoạch "
        "thu thập dữ liệu..."
    )

    collector_plan = create_collector_plan(
        fault_id,
        answers
    )

    print(
        "[OK] "
        "Collector plan created."
    )

    print_collector_plan(
        collector_plan
    )

    # -----------------------------------------------------
    # STEP 5 - COLLECT DATA
    # -----------------------------------------------------

    print()
    print(
        "[5] Thu thập dữ liệu "
        "từ laptop..."
    )

    collectors = collector_plan.get(
        "collectors",
        []
    )

    collected_data = run_collectors(
        collectors
    )

    print()
    print(
        "[OK] "
        "Data collection completed."
    )

    print_collected_data(
        collected_data
    )

    # -----------------------------------------------------
    # STEP 6 - FIRST DIAGNOSIS
    # -----------------------------------------------------

    print()
    print(
        "[6] Phân tích dữ liệu lần 1..."
    )

    report = build_partial_report(
        collected_data
    )

    diagnosis = diagnose_fault(
        user_input,
        report
    )

    print(
        "[OK] "
        "First diagnostic analysis completed."
    )

    # -----------------------------------------------------
    # ADAPTIVE DECISION
    # -----------------------------------------------------

    analysis = diagnosis.get(
        "analysis",
        {}
    )

    current_status = analysis.get(
        "status"
    )

    if current_status == "NO_CLEAR_CAUSE":

        adaptive_result = (
            run_adaptive_monitor(
                fault_id
            )
        )

        adaptive_findings = (
            adaptive_result.get(
                "findings",
                []
            )
        )

        adaptive_recommendations = (
            adaptive_result.get(
                "recommendations",
                []
            )
        )

        # -------------------------------------------------
        # FOUND EVIDENCE
        # -------------------------------------------------

        if adaptive_findings:

            diagnosis["analysis"][
                "status"
            ] = adaptive_result.get(
                "status",
                "WARNING"
            )

            diagnosis["analysis"][
                "severity"
            ] = "WARNING"

            diagnosis["analysis"][
                "findings"
            ] = adaptive_findings

            diagnosis["analysis"][
                "recommendations"
            ] = adaptive_recommendations

            diagnosis["analysis"][
                "adaptive"
            ] = True

            diagnosis["analysis"][
                "adaptive_status"
            ] = adaptive_result.get(
                "status"
            )

            diagnosis["analysis"][
                "adaptive_recommendations"
            ] = adaptive_recommendations

        # -------------------------------------------------
        # STILL NOT ENOUGH DATA
        # -------------------------------------------------

        else:

            diagnosis["analysis"][
                "adaptive"
            ] = True

            diagnosis["analysis"][
                "adaptive_status"
            ] = adaptive_result.get(
                "status",
                "NO_CLEAR_CAUSE"
            )

            diagnosis["analysis"][
                "adaptive_recommendations"
            ] = adaptive_recommendations

    # -----------------------------------------------------
    # STEP 7 - FINAL RESULT
    # -----------------------------------------------------

    print()
    print(
        "[7] Hoàn tất chẩn đoán."
    )

    print_diagnosis(
        diagnosis
    )

    # -----------------------------------------------------
    # END
    # -----------------------------------------------------

    print()
    print(
        "=" * 70
    )

    print(
        " TROUBLESHOOTING COMPLETED"
    )

    print(
        "=" * 70
    )


# =========================================================
# PROGRAM ENTRY
# =========================================================

if __name__ == "__main__":

    run_troubleshooting()