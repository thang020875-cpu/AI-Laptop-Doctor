"""
AI Laptop Doctor
Knowledge Base - Power & No Power

Version: 1.0.0

Chứa kiến thức chẩn đoán cho nhóm:
- Laptop không lên nguồn
- Laptop không có dấu hiệu khởi động
"""

POWER_NO_START = {
    "code": "POWER_NO_START",
    "title": "Laptop không khởi động",
    "category": "Power & Battery",

    "causes": [
        {
            "id": "POWER_INPUT",
            "name": "Bộ sạc hoặc nguồn điện đầu vào",
            "description": (
                "Laptop có thể không nhận được nguồn điện cần thiết "
                "từ bộ sạc hoặc đầu vào nguồn."
            ),

            "supporting_evidence": [
                "charger_led_off",
                "no_power_led",
                "no_fan",
                "charger_unknown"
            ],

            "contradicting_evidence": [
                "charger_led_on"
            ],

            "priority": 5
        },

        {
            "id": "BATTERY_POWER",
            "name": "Pin hoặc mạch quản lý pin",
            "description": (
                "Pin hoặc mạch quản lý nguồn của pin có thể gặp vấn đề, "
                "khiến laptop không thể khởi động bình thường."
            ),

            "supporting_evidence": [
                "battery_problem",
                "no_power",
                "power_reset_failed"
            ],

            "contradicting_evidence": [],

            "priority": 3
        },

        {
            "id": "POWER_CIRCUIT",
            "name": "Mạch nguồn hoặc hệ thống cấp nguồn trên mainboard",
            "description": (
                "Laptop có thể nhận nguồn từ bộ sạc nhưng không thực hiện "
                "được quá trình khởi động do vấn đề ở hệ thống cấp nguồn "
                "bên trong."
            ),

            "supporting_evidence": [
                "charger_led_on",
                "no_power_led",
                "no_fan",
                "power_reset_failed"
            ],

            "contradicting_evidence": [],

            "priority": 4
        },

        {
            "id": "POWER_BUTTON",
            "name": "Nút nguồn hoặc mạch nút nguồn",
            "description": (
                "Tín hiệu từ nút nguồn có thể không được truyền đến "
                "hệ thống khởi động."
            ),

            "supporting_evidence": [
                "charger_led_on",
                "no_power_led",
                "no_fan",
                "power_button_unresponsive"
            ],

            "contradicting_evidence": [],

            "priority": 2
        },

        {
            "id": "MOTHERBOARD",
            "name": "Mainboard hoặc phần cứng khởi động",
            "description": (
                "Có thể có vấn đề phần cứng trên mainboard hoặc "
                "một thành phần liên quan đến quá trình POST."
            ),

            "supporting_evidence": [
                "charger_led_on",
                "no_power_led",
                "no_fan",
                "power_reset_failed"
            ],

            "contradicting_evidence": [],

            "priority": 2
        }
    ]
}