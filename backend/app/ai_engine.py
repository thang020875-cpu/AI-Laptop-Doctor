# =========================================================
# AI LAPTOP DOCTOR - AI ENGINE
# Version: 1.0.0
# =========================================================

import os
import json
import sys
from pathlib import Path

from dotenv import load_dotenv
from google import genai


# =========================================================
# LOAD ENVIRONMENT
# =========================================================

PROJECT_DIR = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_DIR / ".env")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.6-flash"
)


# =========================================================
# GEMINI CLIENT
# =========================================================

client = None

if GEMINI_API_KEY:
    client = genai.Client(
        api_key=GEMINI_API_KEY
    )


# =========================================================
# IMPORT SYMPTOM DIAGNOSIS
# =========================================================

PROJECT_DIR = Path(__file__).resolve().parents[2]

AGENT_DIR = PROJECT_DIR / "agent"

if str(AGENT_DIR) not in sys.path:
    sys.path.append(str(AGENT_DIR))


try:

    from symptom_diagnosis import classify_symptom
    from symptom_question_engine import get_questions

except ImportError:

    classify_symptom = None
    get_questions = None


# =========================================================
# SYSTEM PROMPT
# =========================================================

SYSTEM_PROMPT = """
Bạn là AI Laptop Doctor.

Bạn là trợ lý kỹ thuật chuyên hỗ trợ chẩn đoán
laptop và máy tính Windows.

==================================================
NGUYÊN TẮC CHUNG
==================================================

1. Không được bịa dữ liệu phần cứng.

2. Nếu có system report, ưu tiên sử dụng dữ liệu
   thực tế do Agent thu thập.

3. Phân biệt:
   - Dữ liệu đã xác minh
   - Nguyên nhân có khả năng
   - Cần kiểm tra thêm

4. Không được khẳng định linh kiện chắc chắn hỏng
   nếu chưa đủ bằng chứng.

5. Khi chưa đủ thông tin, hãy hỏi người dùng
   câu hỏi tiếp theo phù hợp.

6. Không tự ý thực hiện thao tác sửa chữa.

7. Không hướng dẫn người dùng thực hiện thao tác
   nguy hiểm nếu chưa cần thiết.

8. Không yêu cầu Local Agent khi máy không thể
   khởi động Windows.

==================================================
CHẾ ĐỘ 1 - SYSTEM DIAGNOSTICS
==================================================

Nếu laptop vẫn hoạt động:

Có thể sử dụng dữ liệu:

- CPU
- RAM
- GPU
- SSD
- Battery
- Temperature
- Network
- Process
- Windows
- Driver

Agent là nguồn dữ liệu hệ thống.

AI có nhiệm vụ phân tích dữ liệu đó.

==================================================
CHẾ ĐỘ 2 - SYMPTOM DIAGNOSTICS
==================================================

Nếu người dùng nói:

- Không lên nguồn
- Không bật được
- Màn hình đen
- Beep / bíp
- Không POST
- Không boot
- Kẹt logo
- Tự restart
- Tự tắt

thì chuyển sang chẩn đoán theo TRIỆU CHỨNG.

Không phụ thuộc vào system report.

AI phải hỏi từng câu hỏi cần thiết.

==================================================
BEEP / BÍP
==================================================

Không được kết luận:

"3 beep = RAM hỏng"

chỉ dựa vào số tiếng beep.

Cần xem xét:

- Hãng
- Model
- Số beep
- Beep ngắn hay dài
- Chuỗi beep có lặp lại không
- Màn hình có hiển thị không
- Quạt có quay không
- Đèn nguồn có sáng không

Ý nghĩa beep code có thể khác nhau
giữa hãng, model và BIOS.

==================================================
MỨC ĐỘ KẾT LUẬN
==================================================

🟢 Đã xác minh:

Có dữ liệu trực tiếp chứng minh.

🟡 Có khả năng:

Triệu chứng phù hợp nhưng chưa đủ bằng chứng.

🔴 Cần kiểm tra vật lý:

Không thể xác minh bằng phần mềm.

==================================================
CẤU TRÚC TRẢ LỜI
==================================================

Khi phù hợp, trả lời theo:

🔍 Đánh giá

📊 Dữ liệu liên quan

🧠 Nguyên nhân có khả năng

⚠️ Mức độ

🔧 Hướng xử lý

❓ Cần kiểm tra thêm

Nếu chưa đủ dữ liệu để chẩn đoán,
hãy hỏi câu hỏi tiếp theo thay vì đoán.
"""


# =========================================================
# HARDWARE
# =========================================================

def get_hardware(report):

    if not isinstance(report, dict):
        return {}

    return report.get(
        "hardware",
        {}
    )


# =========================================================
# BATTERY SAFE HELPER
# =========================================================

def get_first_battery(battery):

    batteries = battery.get(
        "batteries",
        []
    )

    if isinstance(batteries, list) and batteries:

        if isinstance(
            batteries[0],
            dict
        ):
            return batteries[0]

    return {}


# =========================================================
# LOCAL RULE-BASED ANALYSIS
# =========================================================

def answer_health_question(
    message,
    report
):

    hardware = get_hardware(
        report
    )

    cpu = hardware.get(
        "cpu",
        {}
    )

    memory = hardware.get(
        "memory",
        {}
    )

    disk = hardware.get(
        "disk",
        {}
    )

    gpu = hardware.get(
        "gpu",
        {}
    )

    battery = hardware.get(
        "battery",
        {}
    )

    temperature = hardware.get(
        "temperature",
        {}
    )

    cpu_temp = (
        temperature
        .get("cpu", {})
        .get("package_c")
    )

    gpu_temp = (
        temperature
        .get("gpu", {})
        .get("core_c")
    )

    cpu_usage = cpu.get(
        "usage_percent"
    )

    memory_usage = memory.get(
        "usage_percent"
    )

    disk_usage = disk.get(
        "usage_percent"
    )

    gpu_name = None

    gpus = gpu.get(
        "gpus",
        []
    )

    if isinstance(gpus, list) and gpus:

        if isinstance(
            gpus[0],
            dict
        ):
            gpu_name = gpus[0].get(
                "name"
            )

    text = message.lower()

    # =====================================================
    # TEMPERATURE
    # =====================================================

    if any(
        keyword in text
        for keyword in [
            "nóng",
            "nhiệt độ",
            "temperature",
            "overheat"
        ]
    ):

        return (
            "Dựa trên lần kiểm tra gần nhất:\n\n"
            f"- CPU: {cpu_temp}°C\n"
            f"- GPU: {gpu_temp}°C\n\n"
            "Đây là nhiệt độ tại thời điểm kiểm tra, "
            "không phải nhiệt độ tối đa trong toàn bộ "
            "quá trình sử dụng.\n\n"
            "Nếu laptop nóng khi chạy ứng dụng nặng, "
            "nên theo dõi thêm trong thời gian tải cao "
            "để xác định nguyên nhân."
        )

    # =====================================================
    # RAM
    # =====================================================

    if any(
        keyword in text
        for keyword in [
            "ram",
            "memory",
            "bộ nhớ"
        ]
    ):

        return (
            "Thông tin RAM hiện tại:\n\n"
            f"- Tổng RAM: "
            f"{memory.get('total_gb', 'N/A')} GB\n"
            f"- Đang sử dụng: "
            f"{memory_usage}%\n"
            f"- Còn trống: "
            f"{memory.get('available_gb', 'N/A')} GB\n\n"
            "Nếu RAM thường xuyên ở mức rất cao khi "
            "sử dụng ứng dụng nặng, hệ thống có thể "
            "bắt đầu sử dụng bộ nhớ ảo trên ổ đĩa."
        )

    # =====================================================
    # CPU
    # =====================================================

    if any(
        keyword in text
        for keyword in [
            "cpu",
            "processor",
            "bộ xử lý"
        ]
    ):

        return (
            "Thông tin CPU hiện tại:\n\n"
            f"- CPU: "
            f"{cpu.get('name', 'N/A')}\n"
            f"- Physical cores: "
            f"{cpu.get('physical_cores', 'N/A')}\n"
            f"- Logical cores: "
            f"{cpu.get('logical_cores', 'N/A')}\n"
            f"- Usage: "
            f"{cpu_usage}%\n\n"
            "CPU usage là mức sử dụng tại thời điểm "
            "scan. Muốn tìm nguyên nhân máy chậm, "
            "cần theo dõi CPU trong thời gian xảy ra lỗi."
        )

    # =====================================================
    # GPU
    # =====================================================

    if any(
        keyword in text
        for keyword in [
            "gpu",
            "card màn hình",
            "card đồ họa",
            "rtx",
            "nvidia"
        ]
    ):

        if gpu_name:

            return (
                "GPU được phát hiện trên laptop:\n\n"
                f"- GPU: {gpu_name}\n"
                f"- Temperature: {gpu_temp}°C\n\n"
                "GPU có thể được kiểm tra sâu hơn bằng "
                "cách theo dõi tải GPU khi chạy game hoặc "
                "ứng dụng đồ họa."
            )

        return (
            "Hiện tại Agent chưa lấy được thông tin GPU."
        )

    # =====================================================
    # DISK
    # =====================================================

    if any(
        keyword in text
        for keyword in [
            "ssd",
            "ổ cứng",
            "ổ đĩa",
            "disk",
            "dung lượng"
        ]
    ):

        return (
            "Thông tin ổ đĩa:\n\n"
            f"- Tổng dung lượng: "
            f"{disk.get('total_gb', 'N/A')} GB\n"
            f"- Đã sử dụng: "
            f"{disk_usage}%\n"
            f"- Còn trống: "
            f"{disk.get('free_gb', 'N/A')} GB\n\n"
            "Ổ đĩa hiện chưa được đánh giá là gần đầy "
            "nếu mức sử dụng vẫn còn dưới ngưỡng cảnh báo."
        )

    # =====================================================
    # BATTERY
    # =====================================================

    if any(
        keyword in text
        for keyword in [
            "pin",
            "battery",
            "sạc"
        ]
    ):

        capacity = battery.get(
            "capacity",
            {}
        )

        first_battery = get_first_battery(
            battery
        )

        return (
            "Thông tin pin:\n\n"
            f"- Mức pin hiện tại: "
            f"{first_battery.get('charge_percent', 'N/A')}%\n"
            f"- Design capacity: "
            f"{capacity.get('design_mwh', 'N/A')} mWh\n"
            f"- Full charge capacity: "
            f"{capacity.get('full_charge_mwh', 'N/A')} mWh\n\n"
            "Capacity ratio không phải là phần trăm "
            "pin còn lại. Nó là tỷ lệ giữa dung lượng "
            "sạc đầy hiện tại và dung lượng thiết kế."
        )

    # =====================================================
    # SLOW COMPUTER
    # =====================================================

    if any(
        keyword in text
        for keyword in [
            "chậm",
            "lag",
            "đơ",
            "treo",
            "giật"
        ]
    ):

        diagnosis = report.get(
            "diagnosis",
            {}
        )

        status = diagnosis.get(
            "status",
            "UNKNOWN"
        )

        if status == "NORMAL":

            return (
                "Từ lần kiểm tra gần nhất, hệ thống "
                "chưa phát hiện vấn đề rõ ràng.\n\n"
                f"- CPU: {cpu_usage}%\n"
                f"- RAM: {memory_usage}%\n"
                f"- Disk: {disk_usage}%\n"
                f"- CPU Temp: {cpu_temp}°C\n\n"
                "Nếu máy chỉ chậm trong một ứng dụng cụ thể, "
                "nên kiểm tra tiếp process CPU/RAM/Disk I/O "
                "đúng tại thời điểm ứng dụng đó đang chạy."
            )

        return (
            "Hệ thống đã phát hiện một số dấu hiệu "
            "cần kiểm tra thêm.\n\n"
            "Bạn có thể nhấn 'Kiểm tra laptop' để cập nhật "
            "dữ liệu mới nhất trước khi chẩn đoán."
        )

    # =====================================================
    # GENERAL
    # =====================================================

    return (
        "Tôi có thể phân tích laptop dựa trên dữ liệu "
        "đã được Agent thu thập.\n\n"
        "Bạn có thể hỏi tôi về:\n"
        "- CPU\n"
        "- RAM\n"
        "- GPU\n"
        "- SSD\n"
        "- Pin\n"
        "- Nhiệt độ\n"
        "- Máy chạy chậm\n"
        "- Kết nối mạng\n\n"
        "Ngoài ra, bạn có thể mô tả lỗi ngay cả khi "
        "máy không bật được.\n\n"
        "Ví dụ:\n"
        "'Laptop của tôi không lên nguồn.'\n"
        "'Máy bật nhưng màn hình đen.'\n"
        "'Laptop kêu beep 3 lần.'"
    )


# =========================================================
# GEMINI ANALYSIS (gi? t?n h?m c? ?? t??ng th?ch)
# =========================================================

def openai_diagnosis(
    message,
    report,
    symptom
):

    if not client:
        return None

    safe_report = (
        report
        if isinstance(report, dict)
        else {}
    )

    prompt = f"""
THÔNG TIN SYSTEM REPORT:

{json.dumps(
    safe_report,
    ensure_ascii=False,
    indent=2
)}

==================================================

PHÂN LOẠI TRIỆU CHỨNG:

{json.dumps(
    symptom,
    ensure_ascii=False,
    indent=2
)}

==================================================

TIN NHẮN NGƯỜI DÙNG:

{message}

==================================================

YÊU CẦU:

Hãy đóng vai kỹ thuật viên máy tính.

Nếu đây là lỗi mà laptop vẫn hoạt động:
hãy sử dụng system report để phân tích.

Nếu đây là lỗi máy không khởi động:
hãy sử dụng triệu chứng người dùng cung cấp.

Nếu thiếu thông tin:
chỉ hỏi câu hỏi cần thiết tiếp theo.

Không được bịa số liệu.

Không khẳng định linh kiện hỏng nếu chưa đủ bằng chứng.

Với beep code:
hãy yêu cầu hãng/model và đặc điểm beep nếu chưa có.

Trả lời bằng tiếng Việt, dễ hiểu.

Nếu phù hợp, dùng cấu trúc:

🔍 Đánh giá

📊 Dữ liệu liên quan

🧠 Nguyên nhân có khả năng

⚠️ Mức độ

🔧 Hướng xử lý

❓ Cần kiểm tra thêm
"""

    try:

        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=f"{SYSTEM_PROMPT}\n\n{prompt}"
        )

        if response.text:
            return response.text.strip()

        return None

    except Exception as error:

        print(
            "\\n========== GEMINI ERROR =========="
        )

        print(
            "ERROR:",
            repr(error)
        )

        return None


# =========================================================
# MAIN AI FUNCTION
# =========================================================

def generate_answer(
    message,
    report
):

    if not message or not message.strip():

        return (
            "Bạn hãy nhập câu hỏi về laptop."
        )

    message = message.strip()

    # -----------------------------------------------------
    # CLASSIFY SYMPTOM
    # -----------------------------------------------------

    if classify_symptom:

        try:

            symptom = classify_symptom(
                message
            )

        except Exception as error:

            print(
                "Symptom classifier error:",
                repr(error)
            )

            symptom = {
                "code": "UNKNOWN",
                "category": "Unknown",
                "requires_agent": True
            }

    else:

        symptom = {
            "code": "UNKNOWN",
            "category": "Unknown",
            "requires_agent": True
        }

    # -----------------------------------------------------
    # SYMPTOM MODE
    # -----------------------------------------------------

    symptom_codes = [
        "POWER_NO_START",
        "DISPLAY_BLACK",
        "BEEP_POST",
        "BOOT_FAILURE"
    ]

    if (
        symptom.get("code")
        in symptom_codes
    ):

        if client:

            answer = openai_diagnosis(
                message,
                report,
                symptom
            )

            if answer:
                return answer

        # Fallback nếu OpenAI không hoạt động

        return (
            f"🔍 Tôi đã xác định nhóm triệu chứng: "
            f"{symptom.get('title', 'Chưa xác định')}.\n\n"
            "Tôi cần hỏi thêm một số thông tin để "
            "khoanh vùng nguyên nhân.\n\n"
            "Bạn hãy mô tả rõ hơn hiện tượng xảy ra "
            "khi nhấn nút nguồn."
        )

    # -----------------------------------------------------
    # SYSTEM REPORT + GEMINI
    # -----------------------------------------------------

    if client:

        answer = openai_diagnosis(
            message,
            report,
            symptom
        )

        if answer:

            return answer

    # -----------------------------------------------------
    # LOCAL FALLBACK
    # -----------------------------------------------------

    return answer_health_question(
        message,
        report
    )