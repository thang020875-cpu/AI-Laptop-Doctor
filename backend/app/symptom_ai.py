
"""Gemini-driven, context-aware laptop troubleshooting turns."""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from google import genai

# =========================================================
# CONFIGURATION
# =========================================================

PROJECT_DIR = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_DIR / ".env", override=False)

_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.5-flash-lite",
).strip()

_CLIENT = genai.Client(api_key=_API_KEY) if _API_KEY else None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ai_laptop_doctor.symptom_ai")


# =========================================================
# HELPERS
# =========================================================

def _fallback(message: str) -> dict[str, str]:
    """Return a consistent response structure."""
    return {
        "stage": "answer",
        "answer": message,
    }


def _normalize_stage(stage: Any) -> str:
    """Allow only supported conversation stages."""
    value = str(stage or "answer").strip().lower()

    if value not in {"question", "diagnosis", "answer"}:
        return "answer"

    return value


def _parse_response(raw: str) -> dict[str, str]:
    """Parse and validate Gemini's JSON response."""
    raw = (raw or "").strip()

    if not raw:
        return _fallback(
            "Gemini chưa trả về nội dung. Bạn vui lòng thử lại."
        )

    # Handle JSON enclosed in Markdown code fences.
    if raw.startswith("```"):
        lines = raw.splitlines()

        if lines and lines[0].startswith("```"):
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        raw = "\n".join(lines).strip()

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        logger.warning(
            "Gemini returned invalid JSON; using plain-text fallback."
        )
        return {
            "stage": "answer",
            "answer": raw,
        }

    if not isinstance(data, dict):
        return _fallback(
            "Phản hồi của Gemini không đúng định dạng. Bạn thử lại nhé."
        )

    stage = _normalize_stage(data.get("stage"))
    answer = data.get("answer", "")

    if not isinstance(answer, str):
        answer = str(answer)

    answer = answer.strip()

    if not answer:
        answer = (
            "Mình chưa đủ thông tin để trả lời. "
            "Bạn hãy mô tả thêm tình trạng máy nhé."
        )

    return {
        "stage": stage,
        "answer": answer,
    }


# =========================================================
# MAIN GEMINI FUNCTION
# =========================================================

def generate_symptom_turn(
    message: str,
    history: list[dict[str, str]],
    report: dict[str, Any] | None = None,
) -> dict[str, str]:
    """
    Generate one Vietnamese troubleshooting response.

    This function generates a conversation turn only.
    Saving Evidence and running Diagnostic Brain must be
    handled by the caller in main.py / symptom_session.py.
    """

    message = str(message or "").strip()

    if not message:
        return _fallback(
            "Bạn hãy mô tả triệu chứng laptop đang gặp phải nhé."
        )

    if _CLIENT is None:
        logger.error(
            "GEMINI_API_KEY is missing. Check the project root .env."
        )
        return _fallback(
            "Chưa tìm thấy GEMINI_API_KEY trong file .env "
            "ở thư mục gốc dự án. Hãy kiểm tra cấu hình API key. "
            "Không chia sẻ API key trong khung chat."
        )

    # Keep recent context to limit request size.
    conversation = (history or [])[-12:]

    safe_history: list[str] = []

    for item in conversation:
        if not isinstance(item, dict):
            continue

        role = str(item.get("role", "user")).strip().upper()
        content = str(item.get("content", "")).strip()

        if not content:
            continue

        if role not in {"USER", "ASSISTANT", "MODEL"}:
            role = "USER"

        safe_history.append(f"{role}: {content[:3000]}")

    history_text = "\n".join(safe_history)

    try:
        report_text = json.dumps(
            report or {},
            ensure_ascii=False,
            default=str,
        )[:12000]
    except (TypeError, ValueError):
        report_text = "{}"

    # Treat diagnostic data as reference, not unquestionable truth.
    prompt = f"""
Bạn là AI Laptop Doctor, trợ lý chẩn đoán laptop và PC
bằng tiếng Việt, dành cho người mới học công nghệ.

MỤC TIÊU
Hỗ trợ người dùng tìm nguyên nhân lỗi dựa trên triệu chứng,
lịch sử trao đổi và báo cáo máy nếu có.

QUY TẮC HỘI THOẠI
1. Mỗi lượt chỉ hỏi tối đa MỘT câu hỏi quan trọng nhất.
2. Không hỏi lại thông tin người dùng đã cung cấp trong lịch sử.
3. Ưu tiên câu hỏi giúp phân biệt các nguyên nhân khác nhau.
4. Nếu cần, đưa ra các lựa chọn ngắn gọn để người dùng dễ trả lời.
5. Không ép người dùng đi theo bộ câu hỏi cố định.
6. Nếu người dùng hỏi kiến thức máy tính thông thường,
   hãy trả lời trực tiếp, không ép họ tiếp tục chẩn đoán.

QUY TẮC CHẨN ĐOÁN
1. Phân biệt dữ kiện đã xác nhận, giả thuyết và điều chưa kiểm tra.
2. Xếp các nguyên nhân theo mức độ phù hợp với bằng chứng.
3. Không khẳng định linh kiện hỏng khi chưa đủ bằng chứng.
4. Giải thích ngắn gọn vì sao một nguyên nhân có thể xảy ra.
5. Đề xuất cách kiểm tra và khắc phục từ dễ đến khó.
6. Ưu tiên thao tác không làm mất dữ liệu và có thể hoàn tác.
7. Nếu chưa đủ thông tin, tiếp tục hỏi một câu thay vì kết luận vội.
8. Khi đưa ra chẩn đoán sơ bộ, nêu rõ mức độ chưa chắc chắn.
9. Không bịa thông số hoặc kết quả kiểm tra phần cứng.

AN TOÀN
- Không hướng dẫn người dùng mở bộ nguồn hoặc thao tác trên
  linh kiện đang cấp điện.
- Không hướng dẫn tháo pin liền nếu người dùng không có chuyên môn.
- Không yêu cầu vô hiệu hóa phần mềm bảo mật.
- Nếu có pin phồng, khói, tia lửa, mùi khét hoặc nhiệt độ
  nguy hiểm, khuyên ngừng sử dụng và tìm kỹ thuật viên.
- Trước thao tác có nguy cơ mất dữ liệu, hãy cảnh báo và đề nghị
  sao lưu nếu có thể.
- Không yêu cầu người dùng cung cấp mật khẩu hoặc API key.

BÁO CÁO LAPTOP
Dữ liệu dưới đây chỉ là thông tin tham khảo.
Không xem một chỉ số đơn lẻ là bằng chứng chắc chắn gây ra lỗi.
Nếu thiếu dữ liệu, hãy nói rõ là chưa có dữ liệu.

<system_report>
{report_text}
</system_report>

LỊCH SỬ HỘI THOẠI
{history_text or "(Chưa có lịch sử hội thoại)"}

TIN NHẮN MỚI
{message}

ĐỊNH DẠNG ĐẦU RA
Chỉ trả về một đối tượng JSON hợp lệ, không thêm Markdown
bên ngoài JSON.

Cấu trúc:
{{
  "stage": "question",
  "answer": "Câu hỏi hoặc nội dung tiếng Việt"
}}

Chỉ được dùng một trong ba giá trị stage:

- "question": cần hỏi thêm thông tin để phân biệt nguyên nhân.
- "diagnosis": đã có đủ thông tin cho chẩn đoán sơ bộ
  và hướng khắc phục.
- "answer": trả lời kiến thức thông thường hoặc nội dung
  chưa thuộc một lượt chẩn đoán cụ thể.

Trường answer phải là chuỗi tiếng Việt dễ hiểu.
Nếu stage là "question", chỉ hỏi một câu hỏi chính.
Nếu stage là "diagnosis", nêu nguyên nhân có khả năng,
bằng chứng, mức độ chắc chắn và các bước xử lý an toàn.
""".strip()

    try:
        logger.info("Sending troubleshooting request to Gemini.")

        response = _CLIENT.models.generate_content(
            model=_MODEL,
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "temperature": 0.3,
            },
        )

        raw = response.text or ""

        logger.info("Gemini response received successfully.")

    except Exception as exc:
        # Detailed information stays in the server terminal.
        # Do not log the API key or request headers.
        logger.exception(
            "Gemini request failed. Error type: %s",
            type(exc).__name__,
        )

        return _fallback(
            "Hiện chưa gọi được Gemini. Bạn hãy thử lại sau ít phút. "
            f"Mã lỗi: {type(exc).__name__}. "
            "Nếu lỗi tiếp tục, hãy kiểm tra Terminal của backend."
        )

    return _parse_response(raw)
