# =========================================================
# AI LAPTOP DOCTOR - SYMPTOM DIAGNOSIS
# Version: 1.2.0
# =========================================================

def classify_symptom(message: str):
    """
    Phân loại triệu chứng.
    Chỉ xác định nhóm lỗi, KHÔNG kết luận linh kiện hỏng.
    """

    text = message.lower().strip()

    # =====================================================
    # NORMALIZE CÁCH VIẾT THƯỜNG GẶP
    # =====================================================

    # Chỉ chuẩn hóa các viết tắt phổ biến.
    # Không thay toàn bộ chữ "k" để tránh làm hỏng từ khác.
    text = (
        text
        .replace("ko", "không")
        .replace("k0", "không")
        .replace("bth", "bình thường")
    )

    # =====================================================
    # POWER - KHÔNG LÊN NGUỒN
    # =====================================================

    power_keywords = [

        # -----------------------------
        # Không lên nguồn
        # -----------------------------

        "không lên nguồn",
        "không lên",

        "bật không lên",
        "bật lên không được",

        "bật máy không lên",
        "bật laptop không lên",

        "bật lại không lên",

        "bấm nguồn không lên",
        "bấm nút nguồn không lên",

        "nhấn nguồn không lên",
        "nhấn nút nguồn không lên",

        "không bật được",
        "không bật máy",

        "máy không bật",

        "máy không khởi động",
        "laptop không khởi động",

        # -----------------------------
        # Hôm qua dùng bình thường
        # -----------------------------

        "hôm nay không lên",
        "nay không lên",

        "hôm qua dùng bình thường",
        "hôm qua vẫn dùng bình thường",

        "hôm qua dùng bình thường nhưng",
        "hôm qua vẫn dùng bình thường nhưng",

        "đang dùng bình thường nhưng không lên",
        "dùng bình thường nhưng không lên",

        # -----------------------------
        # Bật lên rồi tắt
        # -----------------------------

        "bật lên rồi tắt",

        "bật lên được vài giây rồi tắt",

        "bật lên vài giây rồi tắt",

        "sáng lên rồi tắt",

        "đèn sáng rồi tắt",

        "sáng lên 2 giây rồi tắt",

        "sáng 2 giây rồi tắt",

        "sáng lên 2s rồi mất",

        "sáng 2s rồi mất",

        "sáng lên vài giây rồi mất",

        "sáng vài giây rồi mất",

        # -----------------------------
        # Máy có dấu hiệu nhưng không khởi động
        # -----------------------------

        "đèn nguồn sáng rồi tắt",

        "đèn nguồn sáng vài giây rồi tắt",

        "đèn bàn phím sáng rồi tắt",

        "bấm nút nguồn có sáng nhưng tắt",

        "bấm nguồn sáng rồi tắt"
    ]

    if any(
        keyword in text
        for keyword in power_keywords
    ):

        return {
            "code": "POWER_NO_START",

            "category": "Power & Battery",

            "title": "Máy không khởi động",

            "requires_agent": False
        }

    # =====================================================
    # DISPLAY - MÀN HÌNH ĐEN
    # =====================================================

    display_keywords = [

        "màn hình đen",

        "màn hình không lên",

        "bật máy nhưng màn hình đen",

        "máy lên nhưng màn hình không",

        "máy vẫn chạy nhưng màn hình đen",

        "máy vẫn chạy nhưng không có hình",

        "không có hình",

        "không hiển thị",

        "màn hình không hiển thị",

        "màn hình tối đen"
    ]

    if any(
        keyword in text
        for keyword in display_keywords
    ):

        return {
            "code": "DISPLAY_BLACK",

            "category": "Display",

            "title": "Màn hình không hiển thị",

            "requires_agent": False
        }

    # =====================================================
    # BEEP / POST
    # =====================================================

    beep_keywords = [

        "beep",

        "bíp",

        "bip",

        "tiếng bíp",

        "tiếng beep",

        "kêu beep",

        "kêu bíp",

        "máy kêu beep",

        "máy kêu bíp"
    ]

    if any(
        keyword in text
        for keyword in beep_keywords
    ):

        return {
            "code": "BEEP_POST",

            "category": "POST / Hardware",

            "title":
                "Phát hiện tiếng beep khi khởi động",

            "requires_agent": False
        }

    # =====================================================
    # BOOT WINDOWS
    # =====================================================

    boot_keywords = [

        "không vào windows",

        "không boot",

        "boot không được",

        "không vào được windows",

        "không vào win",

        "kẹt logo",

        "đứng ở logo",

        "boot loop",

        "khởi động lại liên tục",

        "restart liên tục",

        "tự khởi động lại liên tục",

        "bị vòng lặp khởi động"
    ]

    if any(
        keyword in text
        for keyword in boot_keywords
    ):

        return {
            "code": "BOOT_FAILURE",

            "category": "Storage & Boot",

            "title":
                "Lỗi khởi động hệ điều hành",

            "requires_agent": False
        }

    # =====================================================
    # TỰ TẮT
    # =====================================================

    shutdown_keywords = [

        "tự tắt",

        "đang dùng thì tắt",

        "tắt đột ngột",

        "shutdown đột ngột",

        "máy tự shutdown",

        "máy đang chạy tự tắt",

        "đang dùng tự nhiên tắt",

        "đang dùng thì máy tắt"
    ]

    if any(
        keyword in text
        for keyword in shutdown_keywords
    ):

        return {
            "code": "UNEXPECTED_SHUTDOWN",

            "category":
                "Power / Thermal / Software",

            "title":
                "Máy tự tắt đột ngột",

            "requires_agent": True
        }

    # =====================================================
    # UNKNOWN
    # =====================================================

    return {
        "code": "UNKNOWN",

        "category": "Unknown",

        "title":
            "Chưa xác định nhóm lỗi",

        "requires_agent": True
    }