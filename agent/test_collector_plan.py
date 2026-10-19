from collector_plan import create_collector_plan


fault_id = input("Nhập Fault ID: ").strip()


answers = [
    {
        "question_id": "R01-Q01",
        "question": "Máy tính chạy chậm ngay sau khi bật máy hay sau một thời gian sử dụng?",
        "answer": "Không cố định"
    },
    {
        "question_id": "R01-Q02",
        "question": "Máy chạy chậm khi mở ứng dụng nào?",
        "answer": "photoshop"
    },
    {
        "question_id": "R01-Q03",
        "question": "Khi máy chậm, quạt có kêu to hoặc quay nhanh không?",
        "answer": "Có"
    },
    {
        "question_id": "R01-Q04",
        "question": "Hiện tượng máy chậm có xảy ra thường xuyên không?",
        "answer": "Thỉnh thoảng"
    }
]


plan = create_collector_plan(
    fault_id,
    answers
)


print()
print("=" * 65)
print("                 COLLECTOR PLAN")
print("=" * 65)

print()
print(f"Fault ID: {plan['fault_id']}")

print()
print("Collectors cần chạy:")

for collector in plan["collectors"]:

    print(f"  ✓ {collector}")


print()
print("Lý do:")

for reason in plan["reason"]:

    print(f"  - {reason}")


print()
print("=" * 65)