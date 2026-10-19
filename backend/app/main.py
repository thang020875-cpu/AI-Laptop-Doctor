# =========================================================
# AI LAPTOP DOCTOR - BACKEND
# Version: 1.3.0
# =========================================================

import json
import subprocess
import uuid
import sys

from pathlib import Path
from datetime import datetime

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel


# =========================================================
# PATHS
# =========================================================

BACKEND_DIR = Path(__file__).resolve().parent

PROJECT_DIR = BACKEND_DIR.parent.parent

AGENT_DIR = PROJECT_DIR / "agent"

FRONTEND_DIR = PROJECT_DIR / "frontend"

REPORT_PATH = AGENT_DIR / "system_report.json"

PYTHON_PATH = (
    PROJECT_DIR
    / ".venv"
    / "Scripts"
    / "python.exe"
)

SCAN_SCRIPT = AGENT_DIR / "scan.py"


# =========================================================
# AGENT PATH
# =========================================================

if str(AGENT_DIR) not in sys.path:
    sys.path.insert(0, str(AGENT_DIR))


# =========================================================
# IMPORT SYMPTOM ENGINE
# =========================================================

from symptom_diagnosis import classify_symptom

from symptom_question_engine import get_questions, build_evidence


# =========================================================
# SYMPTOM SESSION
# =========================================================

from .symptom_session import (
    create_session,
    get_session,
    save_answer,
    finish_session,
    update_session,
    add_verification_result,
)


# =========================================================
# FASTAPI
# =========================================================

app = FastAPI(
    title="AI Laptop Doctor",
    description="AI-powered laptop diagnostic system",
    version="1.3.0"
)
# Lưu lịch sử chat AI theo từng phiên
CHAT_HISTORY: dict[str, list[dict[str, str]]] = {}
# =========================================================
# FRONTEND
# =========================================================

if FRONTEND_DIR.exists():

    app.mount(
        "/static",
        StaticFiles(
            directory=str(FRONTEND_DIR)
        ),
        name="static"
    )


# =========================================================
# MODELS
# =========================================================

class ChatRequest(BaseModel):

    message: str

    session_id: str | None = None


# =========================================================
# ROOT
# =========================================================

@app.get("/")
def root():

    index_file = FRONTEND_DIR / "index.html"

    if index_file.exists():

        return FileResponse(index_file)

    return {
        "name": "AI Laptop Doctor",
        "version": "1.2.0",
        "status": "online"
    }


# =========================================================
# HEALTH
# =========================================================

@app.get("/health")
def health():

    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


# =========================================================
# GET CURRENT REPORT
# =========================================================

@app.get("/api/report")
def get_report():

    if not REPORT_PATH.exists():

        return {
            "available": False,
            "message": "Chưa có dữ liệu kiểm tra."
        }

    try:

        with open(
            REPORT_PATH,
            "r",
            encoding="utf-8"
        ) as file:

            report = json.load(file)

        return {
            "available": True,
            "report": report
        }

    except Exception as error:

        return {
            "available": False,
            "error": str(error)
        }


# =========================================================
# RUN SCAN
# =========================================================

@app.post("/api/scan")
def scan_laptop():

    try:

        # -------------------------------------------------
        # CHECK PYTHON
        # -------------------------------------------------

        if not PYTHON_PATH.exists():

            return {
                "success": False,
                "message": "Không tìm thấy Python trong .venv.",
                "python": str(PYTHON_PATH)
            }


        # -------------------------------------------------
        # CHECK SCAN SCRIPT
        # -------------------------------------------------

        if not SCAN_SCRIPT.exists():

            return {
                "success": False,
                "message": "Không tìm thấy agent/scan.py.",
                "scan_script": str(SCAN_SCRIPT)
            }


        # -------------------------------------------------
        # RUN AGENT
        # -------------------------------------------------

        print("\n========== LAPTOP SCAN ==========")

        print(
            "Đang chạy AI Laptop Doctor Agent..."
        )

        result = subprocess.run(

            [
                str(PYTHON_PATH),
                str(SCAN_SCRIPT)
            ],

            cwd=str(AGENT_DIR),

            capture_output=True,

            text=True,

            timeout=120
        )


        # -------------------------------------------------
        # AGENT ERROR
        # -------------------------------------------------

        if result.returncode != 0:

            print("Agent scan FAILED.")

            print(result.stderr)

            return {

                "success": False,

                "message": "Agent scan thất bại.",

                "stdout": result.stdout[-5000:],

                "stderr": result.stderr[-5000:]
            }


        # -------------------------------------------------
        # CHECK REPORT
        # -------------------------------------------------

        if not REPORT_PATH.exists():

            return {

                "success": False,

                "message":
                    "Agent đã chạy nhưng "
                    "không tạo system_report.json."
            }


        # -------------------------------------------------
        # READ REPORT
        # -------------------------------------------------

        with open(

            REPORT_PATH,

            "r",

            encoding="utf-8"

        ) as file:

            report = json.load(file)


        print("Agent scan SUCCESS.")

        print(
            "================================\n"
        )


        return {

            "success": True,

            "message":
                "Kiểm tra laptop hoàn tất.",

            "report":
                report,

            "agent_output":
                result.stdout[-5000:]
        }


    except subprocess.TimeoutExpired:

        return {

            "success": False,

            "message":
                "Quá thời gian kiểm tra laptop."
        }


    except Exception as error:

        print(
            "\n========== SCAN ERROR =========="
        )

        print(
            "ERROR:",
            repr(error)
        )

        import traceback

        traceback.print_exc()


        return {

            "success": False,

            "message":
                "Đã xảy ra lỗi khi kiểm tra laptop.",

            "error":
                str(error)
        }


# =========================================================
# LOAD REPORT HELPER
# =========================================================

def load_system_report():

    if not REPORT_PATH.exists():

        return {}

    try:

        with open(

            REPORT_PATH,

            "r",

            encoding="utf-8"

        ) as file:

            return json.load(file)

    except Exception:

        return {}


# =========================================================
# SYMPTOM MODE
# =========================================================

def _append_step_to_history(session: dict, step: dict | None):
    """Ghi nhận bước Brain đang yêu cầu, tránh thêm trùng."""
    if not step:
        session["current_step"] = None
        return

    step_id = step.get("id")
    history = session.setdefault("step_history", [])

    if not history or history[-1].get("step_id") != step_id:
        history.append({
            "step_id": step_id,
            "title": step.get("title", "")
        })

    session["current_step"] = step


def _run_diagnostic_brain(session: dict):
    """Chạy Brain v2 trên toàn bộ evidence hiện có của session."""
    from diagnostic_brain import diagnose as brain_diagnose

    symptom_code = session["symptom"]["code"]

    # Luôn rebuild evidence từ toàn bộ câu trả lời đã lưu.
    # Tránh mất evidence cũ khi session/evidence bị lệch.
    question_evidence = build_evidence(
        symptom_code,
        session.get("answers", []),
    )

    stored_evidence = session.get("evidence", [])
    verification_evidence = []

    for item in stored_evidence:
        if item not in question_evidence:
            verification_evidence.append(item)

    evidence = []
    for item in question_evidence + verification_evidence:
        if item not in evidence:
            evidence.append(item)

    # Đồng bộ lại session để các lần phân tích sau dùng cùng evidence.
    session["evidence"] = evidence

    step_history = session.get("step_history", [])

    print("[BRAIN] Running Diagnostic Brain...")
    print("[BRAIN] Code:", symptom_code)
    print("[BRAIN] Answers:", session.get("answers", []))
    print("[BRAIN] Question evidence:", question_evidence)
    print("[BRAIN] Verification evidence:", verification_evidence)
    print("[BRAIN] Final evidence:", evidence)
    print("[BRAIN] Step history:", step_history)

    diagnosis = brain_diagnose(
        symptom_code,
        evidence,
        step_history,
    )

    # Nếu người dùng đã xác nhận máy khởi động được,
    # không tiếp tục ép sang bước kiểm tra phần cứng.
    if "system_started" in evidence:
        diagnosis["next_step"] = None
        diagnosis["status"] = "CONFIRMED"

    return diagnosis


# =========================================================
# FOLLOW-UP QUESTION DETECTION
# =========================================================

def is_followup_question(message: str) -> bool:
    """Nhận diện câu hỏi phụ trong lúc chẩn đoán."""

    text = message.strip().lower()

    patterns = (
        "mình sửa thế nào",
        "sửa thế nào",
        "khắc phục thế nào",
        "cách khắc phục",
        "làm thế nào",
        "tại sao",
        "nguyên nhân là gì",
        "giải thích giúp",
        "hướng dẫn mình",
        "nên làm gì",
        "có nguy hiểm không",
        "chi phí sửa",
        "hỏi thêm",
    )

    return any(
        pattern in text
        for pattern in patterns
    )


def handle_symptom_chat(
    message: str,
    session_id: str
):
    """
    Xử lý câu trả lời trong phiên chẩn đoán triệu chứng.

    Luồng:
    ACTIVE -> lưu câu trả lời -> câu hỏi tiếp theo
    READY_FOR_DIAGNOSIS -> Brain v2
    WAITING_FOR_VERIFICATION -> nhận kết quả bước kiểm tra
                              -> thêm evidence -> Brain phân tích lại
    DIAGNOSED -> giữ nguyên kết quả cuối cùng.
    """

    print("[SYMPTOM] Handling session:", session_id)

    session = get_session(session_id)

    if not session:
        print("[SYMPTOM] ERROR: Session không tồn tại.")
        return {
            "success": False,
            "mode": "symptom",
            "session_id": session_id,
            "status": "ERROR",
            "answer": (
                "Phiên chẩn đoán không tồn tại. "
                "Bạn hãy nhập lại triệu chứng."
            )
        }

    status = session.get("status", "ACTIVE")
    symptom_code = session["symptom"]["code"]

    print("[SYMPTOM] Code:", symptom_code)
    print("[SYMPTOM] Status:", status)

    # -----------------------------------------------------
    # 1. KẾT QUẢ ĐÃ HOÀN TẤT
    # -----------------------------------------------------
    if status == "DIAGNOSED":
        diagnosis = session.get("diagnosis")

        if diagnosis:
            return {
                "success": True,
                "mode": "symptom",
                "session_id": session_id,
                "status": "DIAGNOSED",
                "answer": format_brain_result(diagnosis)
            }

        status = "READY_FOR_DIAGNOSIS"

    # -----------------------------------------------------
    # 2. ĐANG CHỜ KẾT QUẢ BƯỚC KIỂM TRA
    # -----------------------------------------------------
    if status == "WAITING_FOR_VERIFICATION":
        print("[BRAIN] Verification answer:", message)

        try:
            from diagnostic_brain import (
                verification_to_evidence
            )

            verification_evidence = verification_to_evidence(message)

            print(
                "[BRAIN] Verification evidence:",
                verification_evidence
            )

            if not verification_evidence:
                current_step = session.get("current_step") or {}
                options = current_step.get("options", [])

                options_text = "\n".join(
                    f"- {option}"
                    for option in options
                )

                return {
                    "success": True,
                    "mode": "symptom",
                    "session_id": session_id,
                    "status": "WAITING_FOR_VERIFICATION",
                    "answer": (
                        "Mình chưa nhận ra kết quả kiểm tra từ câu trả lời này.\n\n"
                        "Bạn hãy chọn hoặc mô tả một trong các kết quả sau:\n"
                        f"{options_text}"
                    )
                }

            # Lưu evidence mới vào chính session hiện tại.
            add_verification_result(
                session_id,
                message,
                verification_evidence,
            )

            session = get_session(session_id)

            # Chạy lại Brain với evidence cũ + evidence mới.
            diagnosis = _run_diagnostic_brain(session)

            session["diagnosis"] = diagnosis

            next_step = diagnosis.get("next_step")

            if next_step:
                _append_step_to_history(
                    session,
                    next_step,
                )
                session["status"] = "WAITING_FOR_VERIFICATION"
                session["last_action"] = "BRAIN_NEXT_STEP"
            else:
                session["current_step"] = None
                session["status"] = "DIAGNOSED"
                session["last_action"] = "BRAIN_DIAGNOSIS_COMPLETE"

            update_session(session)

            print(
                "[BRAIN] Re-analysis status:",
                diagnosis.get("status")
            )

            print(
                "[BRAIN] Re-analysis top cause:",
                (
                    diagnosis.get("causes", [{}])[0].get("name")
                    if diagnosis.get("causes")
                    else "UNKNOWN"
                )
            )

            response_status = (
                "WAITING_FOR_VERIFICATION"
                if next_step
                else "DIAGNOSED"
            )

            return {
                "success": True,
                "mode": "symptom",
                "session_id": session_id,
                "status": response_status,
                "answer": format_brain_result(diagnosis)
            }

        except Exception as error:
            print("[BRAIN] VERIFICATION ERROR:", repr(error))

            return {
                "success": False,
                "mode": "symptom",
                "session_id": session_id,
                "status": "BRAIN_ERROR",
                "answer": (
                    "Mình đã nhận kết quả kiểm tra nhưng "
                    "Diagnostic Brain gặp lỗi khi phân tích lại.\n\n"
                    f"Chi tiết kỹ thuật: {error}"
                ),
                "error": str(error)
            }

    # -----------------------------------------------------
    # 3. ĐANG HỎI CÂU: LƯU CÂU TRẢ LỜI
    # -----------------------------------------------------
    if status == "ACTIVE":
        questions = get_questions(symptom_code)

        print("[SYMPTOM] Số câu hỏi:", len(questions))

        current_index = session.get("question_index", 0)

        if current_index < len(questions):
            current_question = questions[current_index]

            print(
                "[SYMPTOM] Lưu câu:",
                current_question["id"]
            )

            save_answer(
                session_id,
                current_question["id"],
                current_question["question"],
                message
            )

        # Reload session after save_answer().
        session = get_session(session_id)
        next_index = session.get("question_index", 0)

        # -------------------------------------------------
        # CÒN CÂU HỎI
        # -------------------------------------------------
        if next_index < len(questions):
            next_question = questions[next_index]

            options_text = "\n".join(
                f"- {option}"
                for option in next_question["options"]
            )

            print(
                "[SYMPTOM] Câu tiếp theo:",
                next_question["id"]
            )

            return {
                "success": True,
                "mode": "symptom",
                "session_id": session_id,
                "status": "ACTIVE",
                "answer": (
                    f"Đã ghi nhận: **{message}**\n\n"
                    f"**Câu hỏi tiếp theo:**\n"
                    f"{next_question['question']}\n\n"
                    "Bạn có thể chọn:\n"
                    f"{options_text}"
                )
            }

        # -------------------------------------------------
        # QUESTIONNAIRE COMPLETE
        # -------------------------------------------------
        print("[SYMPTOM] Đã hoàn thành tất cả câu hỏi.")

        session = get_session(session_id)
        status = session.get(
            "status",
            "READY_FOR_DIAGNOSIS"
        )

    # -----------------------------------------------------
    # 4. CHẠY DIAGNOSTIC BRAIN V2
    # -----------------------------------------------------
    if status == "READY_FOR_DIAGNOSIS":
        try:
            diagnosis = _run_diagnostic_brain(session)

            session["diagnosis"] = diagnosis

            next_step = diagnosis.get("next_step")

            if next_step:
                _append_step_to_history(
                    session,
                    next_step,
                )
                session["status"] = "WAITING_FOR_VERIFICATION"
                session["last_action"] = "BRAIN_NEXT_STEP"
            else:
                session["current_step"] = None
                session["status"] = "DIAGNOSED"
                session["last_action"] = "BRAIN_DIAGNOSIS_COMPLETE"

            update_session(session)

            print(
                "[BRAIN] Status:",
                diagnosis.get("status")
            )

            print(
                "[BRAIN] Top cause:",
                (
                    diagnosis.get("causes", [{}])[0].get("name")
                    if diagnosis.get("causes")
                    else "UNKNOWN"
                )
            )

            response_status = (
                "WAITING_FOR_VERIFICATION"
                if next_step
                else "DIAGNOSED"
            )

            return {
                "success": True,
                "mode": "symptom",
                "session_id": session_id,
                "status": response_status,
                "answer": format_brain_result(diagnosis)
            }

        except Exception as error:
            print("[BRAIN] ERROR:", repr(error))

            return {
                "success": False,
                "mode": "symptom",
                "session_id": session_id,
                "status": "BRAIN_ERROR",
                "answer": (
                    "Mình đã thu thập đủ thông tin nhưng "
                    "Diagnostic Brain đang gặp lỗi khi phân tích.\n\n"
                    f"Chi tiết kỹ thuật: {error}"
                ),
                "error": str(error)
            }

    # -----------------------------------------------------
    # 5. FALLBACK
    # -----------------------------------------------------
    return {
        "success": True,
        "mode": "symptom",
        "session_id": session_id,
        "status": status,
        "answer": (
            "Mình vẫn giữ nguyên phiên chẩn đoán hiện tại. "
            "Bạn có thể gửi kết quả kiểm tra tiếp theo."
        )
    }


def format_brain_result(diagnosis: dict) -> str:
    """
    Chuyển kết quả Diagnostic Brain thành câu trả lời dễ hiểu.
    Không tự khẳng định linh kiện cụ thể bị hỏng.
    """

    status = diagnosis.get("status", "UNKNOWN")
    evidence = diagnosis.get("evidence", [])
    causes = diagnosis.get("causes", [])
    next_step = diagnosis.get("next_step")

    status_text = {
        "CONFIRMED": "ĐÃ XÁC NHẬN",
        "LIKELY": "CÓ KHẢ NĂNG CAO",
        "POSSIBLE": "CÓ THỂ",
        "UNKNOWN": "CHƯA ĐỦ DỮ LIỆU",
    }.get(status, "CHƯA ĐỦ DỮ LIỆU")

    evidence_labels = {
        "no_power_led": "Không có đèn nguồn/đèn bàn phím.",
        "power_led_on": "Có đèn nguồn hoặc đèn bàn phím.",
        "fan_off": "Không nghe thấy quạt quay.",
        "no_fan": "Không nghe thấy quạt quay.",
        "fan_on": "Có nghe thấy quạt quay.",
        "fan_runs_then_stops": "Quạt quay rồi tắt.",
        "charger_led_on": "Đèn báo sạc có sáng.",
        "charger_led_off": "Đèn báo sạc không sáng.",
        "charger_led_unknown": "Chưa xác định được trạng thái đèn sạc.",
        "power_reset_failed": (
            "Đã thử giữ nút nguồn/reset nguồn nhưng máy vẫn không lên."
        ),
        "power_reset_not_tested": "Chưa thử reset nguồn.",
        "power_reset_unknown": (
            "Chưa xác định được kết quả reset nguồn."
        ),
        "no_power_after_reset": (
            "Sau khi reset nguồn, máy vẫn hoàn toàn không có phản hồi."
        ),
        "system_started": "Máy đã khởi động trở lại.",
        "partial_power_response": (
            "Máy bắt đầu có phản hồi nguồn như đèn hoặc quạt."
        ),
    }

    lines = [
        "## 🧠 Kết quả Diagnostic Brain",
        "",
        f"**Mức đánh giá:** {status_text}",
        "",
        "### Dấu hiệu đã ghi nhận",
    ]

    if evidence:
        for item in evidence:
            lines.append(
                f"- {evidence_labels.get(item, item)}"
            )
    else:
        lines.append("- Chưa có bằng chứng đủ rõ.")

    lines.extend([
        "",
        "### Các nguyên nhân được xếp hạng",
    ])

    if causes:
        for index, cause in enumerate(causes[:3], start=1):
            lines.append(
                f"{index}. **{cause['name']}** — điểm ưu tiên: "
                f"{cause['score']}"
            )
            lines.append(
                f"   {cause['description']}"
            )
    else:
        lines.append(
            "- Chưa xác định được nguyên nhân phù hợp."
        )

    lines.extend([
        "",
        "### ⚠️ Lưu ý",
        "- Điểm của Brain là **mức ưu tiên chẩn đoán**, không phải phần trăm xác suất.",
        "- Kết quả hiện tại chưa đủ để khẳng định một linh kiện cụ thể bị hỏng.",
    ])

    if next_step:
        lines.extend([
            "",
            f"### 🔧 Bước kiểm tra tiếp theo: {next_step.get('title', 'Kiểm tra tiếp theo')}",
            "",
            next_step.get(
                "instruction",
                "Thực hiện bước kiểm tra được yêu cầu."
            ),
            "",
            "**Kết quả bạn có thể gửi:**",
        ])

        for option in next_step.get("options", []):
            lines.append(f"- {option}")

        lines.extend([
            "",
            "Sau khi kiểm tra, hãy gửi lại đúng kết quả.",
            "Mình sẽ tiếp tục trên **chính phiên chẩn đoán này**, không hỏi lại từ đầu.",
        ])
    else:
        lines.extend([
            "",
            "### 🔧 Kết luận / bước tiếp theo",
            "Hiện chưa có bước kiểm tra tự thực hiện nào khác được Brain đề xuất.",
            "Nếu máy vẫn không hoạt động, nên mang máy đến kỹ thuật viên để kiểm tra phần cứng.",
        ])

    return "\n".join(lines)


# =========================================================
# START NEW SYMPTOM SESSION
# =========================================================

def start_symptom_session(
    message: str,
    session_id: str
):

    # -----------------------------------------------------
    # CLASSIFY
    # -----------------------------------------------------

    symptom = classify_symptom(
        message
    )


    print(
        "[CLASSIFIER] Message:",
        message
    )

    print(
        "[CLASSIFIER] Result:",
        symptom
    )


    # -----------------------------------------------------
    # SUPPORTED SYMPTOMS
    # -----------------------------------------------------

    symptom_codes = [

        "POWER_NO_START",

        "DISPLAY_BLACK",

        "BEEP_POST",

        "BOOT_FAILURE"
    ]


    # -----------------------------------------------------
    # UNKNOWN
    # -----------------------------------------------------

    if symptom["code"] not in symptom_codes:

        print(
            "[CLASSIFIER] -> UNKNOWN / SYSTEM MODE"
        )

        return None


    # -----------------------------------------------------
    # SYMPTOM DETECTED
    # -----------------------------------------------------

    print(
        "[CLASSIFIER] -> SYMPTOM MODE:",
        symptom["code"]
    )


    # -----------------------------------------------------
    # CREATE SESSION
    # -----------------------------------------------------

    session = create_session(

        session_id,

        symptom
    )


    # -----------------------------------------------------
    # QUESTION BANK
    # -----------------------------------------------------

    questions = get_questions(

        symptom["code"]
    )


    print(
        "[SESSION] Created:",
        session_id
    )

    print(
        "[SESSION] Question count:",
        len(questions)
    )


    # -----------------------------------------------------
    # NO QUESTIONS
    # -----------------------------------------------------

    if not questions:

        finish_session(
            session_id
        )

        return {

            "success": True,

            "mode": "symptom",

            "session_id": session_id,

            "status": "COMPLETED",

            "answer":
                (
                    "Mình đã nhận diện triệu chứng "
                    f"**{symptom['title']}**, "
                    "nhưng hiện chưa có bộ câu hỏi "
                    "chẩn đoán tương ứng."
                )
        }


    # -----------------------------------------------------
    # FIRST QUESTION
    # -----------------------------------------------------

    first_question = questions[0]


    options_text = "\n".join(

        f"- {option}"

        for option
        in first_question["options"]
    )


    print(
        "[SESSION] First question:",
        first_question["id"]
    )


    return {

        "success": True,

        "mode": "symptom",

        "session_id": session_id,

        "status": "ACTIVE",

        "answer":
            (
                "**Đã xác định nhóm triệu chứng:**\n"

                f"{symptom['title']}\n\n"

                "Mình sẽ không kết luận "
                "linh kiện hỏng ngay.\n\n"

                "Mình sẽ kiểm tra từng dấu hiệu "
                "một để thu hẹp nguyên nhân.\n\n"

                "**Câu hỏi 1:**\n"

                f"{first_question['question']}\n\n"

                "Bạn có thể chọn:\n"

                f"{options_text}"
            )
    }


# =========================================================
# AI CHAT
# =========================================================

@app.post("/api/chat")
def chat(request: ChatRequest):

    try:

        # =================================================
        # MESSAGE
        # =================================================

        message = request.message.strip()


        if not message:

            return {

                "success": False,

                "answer":
                    "Bạn hãy nhập câu hỏi hoặc triệu chứng."
            }


        # =================================================
        # SESSION ID
        # =================================================

        session_id = request.session_id


        if not session_id:

            session_id = str(
                uuid.uuid4()
            )


        # =================================================
        # DEBUG LOG
        # =================================================

        print("\n")
        print("=" * 70)
        print("[CHAT] NEW MESSAGE")
        print("[CHAT] Message:", message)
        print("[CHAT] Session ID:", session_id)
        print("=" * 70)


        # =================================================
        # CHECK EXISTING SESSION
        # =================================================

        existing_session = get_session(
            session_id
        )


        if existing_session:

            print(
                "[CHAT] Existing session:",
                existing_session["status"]
            )

            print(
                "[CHAT] Existing symptom:",
                existing_session["symptom"]["code"]
            )


        # =================================================
        # ACTIVE SYMPTOM SESSION
        # =================================================

        if (
            existing_session
            and existing_session.get("status") in {
                "ACTIVE",
                "READY_FOR_DIAGNOSIS",
                "DIAGNOSED",
                "WAITING_FOR_VERIFICATION",
            }
        ):

            status = existing_session.get("status")

            # -------------------------------------------------
            # FOLLOW-UP QUESTION
            # Không lưu câu hỏi phụ thành câu trả lời chẩn đoán
            # -------------------------------------------------

            if is_followup_question(message):

                print(
                    "[CHAT] -> FOLLOW-UP QUESTION"
                )

                report = load_system_report()

                from .ai_engine import generate_answer

                answer = generate_answer(
                    message,
                    report
                )

                return {
                    "success": True,
                    "mode": "system",
                    "session_id": session_id,
                    "status": status,
                    "answer": (
                        answer
                        + "\n\n"
                        + "Mình vẫn giữ nguyên phiên chẩn đoán "
                        "trước đó. Bạn có thể tiếp tục trả lời "
                        "câu hỏi kiểm tra đang chờ."
                    )
                }

            # -------------------------------------------------
            # CONTINUE EXISTING SYMPTOM SESSION
            # -------------------------------------------------

            print(
                "[CHAT] -> EXISTING SYMPTOM SESSION"
            )

            return handle_symptom_chat(
                message,
                session_id
            )


               # =================================================
        # GEMINI FREE-FORM SYMPTOM CHAT
        # =================================================

        print("[CHAT] -> GEMINI FREE-FORM MODE")

        report = load_system_report()

        from .symptom_ai import generate_symptom_turn

        history = CHAT_HISTORY.setdefault(
            session_id,
            []
        )

        turn = generate_symptom_turn(
            message,
            history,
            report
        )

        answer = turn.get(
            "answer",
            "Mình chưa tạo được câu trả lời."
        )

        stage = turn.get("stage", "answer")

        history.extend([
            {
                "role": "user",
                "content": message
            },
            {
                "role": "assistant",
                "content": answer
            }
        ])

        CHAT_HISTORY[session_id] = history[-24:]

        status_map = {
            "question": "NEEDS_INFO",
            "diagnosis": "DIAGNOSED",
            "answer": "NORMAL"
        }

        return {
            "success": True,
            "mode": "system",
            "session_id": session_id,
            "status": status_map.get(
                stage,
                "NORMAL"
            ),
            "answer": answer
        }

        # =================================================
        # SYSTEM MODE
        # =================================================

        print(
            "[CHAT] -> SYSTEM MODE"
        )


        report = load_system_report()

        from .symptom_ai import generate_symptom_turn

        # Lấy lịch sử hội thoại theo phiên
        history = CHAT_HISTORY.setdefault(session_id, [])

        # Gửi câu hỏi đến Gemini
        turn = generate_symptom_turn(
            message,
            history,
            report
        )

        answer = turn["answer"]
        stage = turn.get("stage", "answer")

        # Lưu câu hỏi và câu trả lời
        history.extend([
            {"role": "user", "content": message},
            {"role": "assistant", "content": answer}
        ])

        # Giữ tối đa 24 tin nhắn gần nhất
        CHAT_HISTORY[session_id] = history[-24:]

        status_map = {
            "question": "NEEDS_INFO",
            "diagnosis": "DIAGNOSED",
            "answer": "NORMAL"
        }

        return {
            "success": True,
            "mode": "system",
            "session_id": session_id,
            "status": status_map.get(stage, "NORMAL"),
            "answer": answer
        }

        from .symptom_ai import generate_symptom_turn

        # Lấy lịch sử hội thoại theo phiên
        history = CHAT_HISTORY.setdefault(session_id, [])

        # Gửi câu hỏi đến Gemini
        turn = generate_symptom_turn(
            message,
            history,
            report
        )

        answer = turn["answer"]
        stage = turn.get("stage", "answer")

        # Lưu câu hỏi và câu trả lời
        history.extend([
            {"role": "user", "content": message},
            {"role": "assistant", "content": answer}
        ])

        # Giữ tối đa 24 tin nhắn gần nhất
        CHAT_HISTORY[session_id] = history[-24:]

        status_map = {
            "question": "NEEDS_INFO",
            "diagnosis": "DIAGNOSED",
            "answer": "NORMAL"
        }

        return {
            "success": True,
            "mode": "system",
            "session_id": session_id,
            "status": status_map.get(stage, "NORMAL"),
            "answer": answer
        }


    except Exception as error:

        print(
            "\n========== CHAT ERROR =========="
        )

        print(
            "ERROR:",
            repr(error)
        )


        import traceback

        traceback.print_exc()


        print(
            "================================\n"
        )


        return {

            "success": False,

            "answer":
                "AI đang gặp lỗi.",

            "error":
                str(error)
        }


# =========================================================
# EXISTING AGENT REPORT
# =========================================================

@app.post("/agent/report")
def receive_agent_report(
    report: dict
):

    try:

        with open(

            REPORT_PATH,

            "w",

            encoding="utf-8"

        ) as file:

            json.dump(

                report,

                file,

                ensure_ascii=False,

                indent=4
            )


        return {

            "status":
                "received",

            "message":
                "Laptop report received successfully",

            "received_at":
                datetime.now().isoformat()
        }


    except Exception as error:

        print(
            "\n========== AGENT REPORT ERROR =========="
        )

        print(
            "ERROR:",
            repr(error)
        )


        return {

            "status":
                "error",

            "message":
                "Không thể lưu laptop report.",

            "error":
                str(error)
        }