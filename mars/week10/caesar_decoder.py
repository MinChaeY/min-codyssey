def caesar_cipher_decode(target_text):
    decoded_texts = []

    for shift in range(1, 26):  # 1~25까지 이동
        decoded = ""

        for char in target_text:
            if char.isalpha():
                base = ord('A') if char.isupper() else ord('a')
                decoded += chr((ord(char) - base - shift) % 26 + base)
            else:
                decoded += char  # 공백, 숫자, 기호는 그대로

        print(f"Shift {shift}:\n{decoded}\n{'-'*50}")
        decoded_texts.append((shift, decoded))

    return decoded_texts


# ✅ 1. 암호문 읽기
with open("E:\min-codyssey\mars\week10\password.txt", "r", encoding="utf-8") as f:
    encrypted_text = f.read().strip()

# ✅ 2. 모든 shift에 대해 출력
decoded_candidates = caesar_cipher_decode(encrypted_text)

# ✅ 3. 사람이 직접 눈으로 확인 후 번호 입력
correct_shift = int(input("올바른 해독으로 보이는 Shift 번호를 입력하세요: "))

# ✅ 4. 해당 결과 저장
with open("E:/min-codyssey/mars/week10/result.txt", "w", encoding="utf-8") as f:
    for shift, result in decoded_candidates:
        if shift == correct_shift:
            f.write(result)
            print(f"Shift {shift} 결과가 result.txt에 저장되었습니다.")
            break
