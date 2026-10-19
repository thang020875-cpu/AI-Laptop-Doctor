# =========================================================
# AI LAPTOP DOCTOR - SYMPTOM QUESTION ENGINE
# Version: 1.1.0
# =========================================================

QUESTIONS = {

    # =====================================================
    # POWER - MÁY KHÔNG LÊN
    # =====================================================

    "POWER_NO_START": [
        {
            "id": "power_led",
            "question": "Khi bạn nhấn nút nguồn, máy có đèn nguồn hoặc đèn bàn phím sáng không?",
            "options": [
                "Không có đèn",
                "Có đèn",
                "Không chắc"
            ]
        },
        {
            "id": "fan",
            "question": "Khi nhấn nút nguồn, bạn có nghe thấy quạt quay không?",
            "options": [
                "Không",
                "Có",
                "Quay rồi tắt"
            ]
        },
        {
            "id": "charger",
            "question": "Khi cắm sạc, đèn báo sạc có sáng không?",
            "options": [
                "Có",
                "Không",
                "Không có đèn sạc",
                "Không chắc"
            ]
        },
        {
            "id": "charger_test",
            "question": "Bạn đã thử cắm sạc và nhấn giữ nút nguồn khoảng 10–15 giây chưa?",
            "options": [
                "Chưa thử",
                "Đã thử",
                "Không chắc"
            ]
        }
    ],

    # =====================================================
    # DISPLAY
    # =====================================================

    "DISPLAY_BLACK": [
        {
            "id": "power_led",
            "question": "Máy có đèn nguồn hoặc đèn bàn phím không?",
            "options": [
                "Có",
                "Không",
                "Không chắc"
            ]
        },
        {
            "id": "fan",
            "question": "Bạn có nghe thấy quạt hoạt động không?",
            "options": [
                "Có",
                "Không",
                "Không chắc"
            ]
        },
        {
            "id": "external_display",
            "question": "Nếu có màn hình ngoài, bạn đã thử kết nối HDMI/USB-C chưa?",
            "options": [
                "Chưa thử",
                "Đã thử và có hình",
                "Đã thử nhưng không có hình",
                "Không có màn hình ngoài"
            ]
        }
    ],

    # =====================================================
    # BEEP
    # =====================================================

    "BEEP_POST": [
        {
            "id": "brand",
            "question": "Laptop của bạn thuộc hãng nào?",
            "options": [
                "Lenovo",
                "ASUS",
                "Dell",
                "HP",
                "Acer",
                "MSI",
                "Khác"
            ]
        },
        {
            "id": "model",
            "question": "Bạn có biết model laptop không?",
            "options": [
                "Có",
                "Không"
            ]
        },
        {
            "id": "beep_count",
            "question": "Bạn nghe thấy bao nhiêu tiếng beep/bíp?",
            "options": [
                "1",
                "2",
                "3",
                "4",
                "Nhiều hơn 4",
                "Không chắc"
            ]
        },
        {
            "id": "beep_type",
            "question": "Các tiếng beep là tiếng ngắn hay tiếng dài?",
            "options": [
                "Ngắn",
                "Dài",
                "Kết hợp",
                "Không chắc"
            ]
        },
        {
            "id": "repeat",
            "question": "Chuỗi beep có lặp lại không?",
            "options": [
                "Có",
                "Không",
                "Không chắc"
            ]
        }
    ],

    # =====================================================
    # BOOT
    # =====================================================

    "BOOT_FAILURE": [
        {
            "id": "screen",
            "question": "Máy dừng ở đâu?",
            "options": [
                "Logo hãng",
                "Màn hình xanh",
                "Màn hình đen",
                "Thông báo lỗi",
                "Tự khởi động lại"
            ]
        },
        {
            "id": "storage",
            "question": "Bạn có thấy thông báo không nhận SSD hoặc không tìm thấy thiết bị boot không?",
            "options": [
                "Có",
                "Không",
                "Không chắc"
            ]
        }
    ]
}


def get_questions(symptom_code):
    return QUESTIONS.get(symptom_code, [])


def get_first_question(symptom_code):
    questions = get_questions(symptom_code)

    if not questions:
        return None

    return questions[0]


def get_question(symptom_code, question_index):
    questions = get_questions(symptom_code)

    if question_index < 0 or question_index >= len(questions):
        return None

    return questions[question_index]


def get_question_count(symptom_code):
    return len(get_questions(symptom_code))