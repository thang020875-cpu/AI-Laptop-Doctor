# =========================================================
# AI LAPTOP DOCTOR - COLLECTOR PLAN
# Version: 0.3.0
# =========================================================


def create_collector_plan(fault_id, answers):

    plan = {
        "fault_id": fault_id,
        "collectors": [],
        "reason": []
    }

    # =====================================================
    # PERFORMANCE
    # =====================================================

    if fault_id == "R01":

        plan["collectors"] = [
            "cpu",
            "memory",
            "disk",
            "temperature",
            "gpu"
        ]

        plan["reason"].append(
            "Kiểm tra CPU, RAM và nhiệt độ vì người dùng báo máy chậm."
        )

        # Kiểm tra câu trả lời của người dùng

        for answer in answers:

            question_id = answer.get("question_id")
            value = answer.get("answer", "").lower()

            # Quạt kêu to
            if question_id == "R01-Q03" and value == "có":

                if "temperature" not in plan["collectors"]:
                    plan["collectors"].append("temperature")

                plan["reason"].append(
                    "Người dùng báo quạt kêu to → cần kiểm tra nhiệt độ."
                )

            # Photoshop
            if question_id == "R01-Q02":

                plan["reason"].append(
                    "Người dùng báo lỗi xảy ra khi sử dụng ứng dụng nặng "
                    "→ cần kiểm tra CPU, RAM và GPU."
                )

    # =====================================================
    # THERMAL
    # =====================================================

    elif fault_id == "T01":

        plan["collectors"] = [
            "cpu",
            "gpu",
            "temperature"
        ]

        plan["reason"].append(
            "Kiểm tra nhiệt độ CPU và GPU."
        )

    # =====================================================
    # BATTERY
    # =====================================================

    elif fault_id == "B01":

        plan["collectors"] = [
            "battery"
        ]

        plan["reason"].append(
            "Kiểm tra tình trạng pin và dung lượng pin."
        )

    # =====================================================
    # NETWORK
    # =====================================================

    elif fault_id == "N01":

        plan["collectors"] = [
            "network"
        ]

        plan["reason"].append(
            "Kiểm tra adapter mạng, IP, DNS và kết nối Internet."
        )

    # =====================================================
    # STORAGE
    # =====================================================

    elif fault_id == "D01":

        plan["collectors"] = [
            "disk"
        ]

        plan["reason"].append(
            "Kiểm tra tình trạng dung lượng ổ đĩa."
        )

    # =====================================================
    # DISPLAY
    # =====================================================

    elif fault_id == "D02":

        plan["collectors"] = [
            "gpu",
            "system"
        ]

        plan["reason"].append(
            "Kiểm tra GPU và thông tin hệ thống hiển thị."
        )

    # =====================================================
    # UNKNOWN
    # =====================================================

    else:

        plan["collectors"] = [
            "system"
        ]

        plan["reason"].append(
            "Chưa xác định được nhóm lỗi → chỉ thu thập thông tin hệ thống cơ bản."
        )

    # Loại bỏ collector trùng nhau
    plan["collectors"] = list(
        dict.fromkeys(plan["collectors"])
    )

    return plan