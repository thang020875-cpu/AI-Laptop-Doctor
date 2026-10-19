"""
AI Laptop Doctor
Symptom Question Engine v2

Nhiệm vụ:
- Đặt câu hỏi chẩn đoán theo triệu chứng
- Chuyển câu trả lời thành Evidence ID
- Không chỉ lưu câu trả lời dạng chữ
- Chuẩn bị dữ liệu cho Diagnostic Brain
"""

QUESTION_BANK = {

    "POWER_NO_START": [

        {
            "id": "power_led",
            "question": "Khi bạn nhấn nút nguồn, máy có đèn nguồn hoặc đèn bàn phím sáng không?",
            "options": {
                "Không có đèn": ["no_power_led"],
                "Có đèn": ["power_led_on"],
                "Không chắc": ["power_led_unknown"]
            }
        },

        {
            "id": "fan",
            "question": "Khi nhấn nút nguồn, bạn có nghe thấy quạt quay không?",
            "options": {
                "Không": ["fan_off"],
                "Có": ["fan_on"],
                "Quay rồi tắt": ["fan_runs_then_stops"]
            }
        },

        {
            "id": "charger",
            "question": "Khi cắm sạc, đèn báo sạc có sáng không?",
            "options": {
                "Có": ["charger_led_on"],
                "Không": ["charger_led_off"],
                "Không có đèn sạc": ["charger_led_unknown"],
                "Không chắc": ["charger_led_unknown"]
            }
        },

        {
            "id": "charger_test",
            "question": "Bạn đã thử cắm sạc và nhấn giữ nút nguồn khoảng 10–15 giây chưa?",
            "options": {
                "Chưa thử": ["power_reset_not_tested"],
                "Đã thử": ["power_reset_failed"],
                "Không chắc": ["power_reset_unknown"]
            }
        }
    ]
}


def get_questions(symptom_code):
    """
    Lấy bộ câu hỏi theo mã triệu chứng.
    """

    return QUESTION_BANK.get(
        symptom_code,
        []
    )


def get_question(symptom_code, question_index):
    """
    Lấy một câu hỏi cụ thể.
    """

    questions = get_questions(symptom_code)

    if question_index < 0:
        return None

    if question_index >= len(questions):
        return None

    return questions[question_index]


def answer_to_evidence(symptom_code, question_id, answer):
    """
    Chuyển câu trả lời của người dùng
    thành Evidence ID chuẩn hóa.
    """

    questions = get_questions(symptom_code)

    for question in questions:

        if question["id"] != question_id:
            continue

        options = question["options"]

        # Tìm chính xác
        if answer in options:
            return options[answer]

        # Chuẩn hóa một số cách trả lời phổ biến
        normalized = answer.strip().lower()

        for option_text, evidence in options.items():

            if normalized == option_text.lower():
                return evidence

        return []

    return []


def get_next_question(
    symptom_code,
    answered_question_ids
):
    """
    Tìm câu hỏi tiếp theo chưa được trả lời.
    """

    questions = get_questions(symptom_code)

    for question in questions:

        if question["id"] not in answered_question_ids:
            return question

    return None


def is_questionnaire_complete(
    symptom_code,
    answered_question_ids
):
    """
    Kiểm tra đã trả lời hết câu hỏi chưa.
    """

    questions = get_questions(symptom_code)

    if not questions:
        return False

    question_ids = {
        question["id"]
        for question in questions
    }

    return question_ids.issubset(
        set(answered_question_ids)
    )


def build_evidence(
    symptom_code,
    answers
):
    """
    Chuyển toàn bộ câu trả lời trong session
    thành danh sách Evidence ID.

    answers có dạng:

    [
        {
            "question_id": "power_led",
            "answer": "Không có đèn"
        }
    ]
    """

    evidence = []

    for item in answers:

        question_id = item.get(
            "question_id"
        )

        answer = item.get(
            "answer",
            ""
        )

        result = answer_to_evidence(
            symptom_code,
            question_id,
            answer
        )

        for evidence_id in result:

            if evidence_id not in evidence:
                evidence.append(
                    evidence_id
                )

    return evidence


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("AI LAPTOP DOCTOR - SYMPTOM QUESTION ENGINE V2")
    print("=" * 60)

    symptom_code = "POWER_NO_START"

    answers = [
        {
            "question_id": "power_led",
            "answer": "Không có đèn"
        },
        {
            "question_id": "fan",
            "answer": "Không"
        },
        {
            "question_id": "charger",
            "answer": "Có"
        },
        {
            "question_id": "charger_test",
            "answer": "Đã thử"
        }
    ]

    print("\nAnswers:")

    for item in answers:
        print(
            f"  {item['question_id']}: "
            f"{item['answer']}"
        )

    evidence = build_evidence(
        symptom_code,
        answers
    )

    print("\nEvidence:")

    for item in evidence:
        print(
            f"  - {item}"
        )

    print("\nQuestionnaire complete:")

    answered_ids = [
        item["question_id"]
        for item in answers
    ]

    print(
        is_questionnaire_complete(
            symptom_code,
            answered_ids
        )
    )

    print("\nNext question:")

    next_question = get_next_question(
        symptom_code,
        answered_ids
    )

    print(next_question)

    print("\n" + "=" * 60)