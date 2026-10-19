from question_engine import run_question_engine


fault_id = input("Nhập Fault ID cần kiểm tra: ").strip()

answers = run_question_engine(fault_id)


print()
print("=" * 65)
print("                 KẾT QUẢ TRẢ LỜI")
print("=" * 65)

if not answers:

    print()
    print("Không tìm thấy câu hỏi cho Fault ID này.")

else:

    for answer in answers:

        print()
        print(f"Question ID : {answer['question_id']}")
        print(f"Question    : {answer['question']}")
        print(f"Answer      : {answer['answer']}")

print()
print("=" * 65)