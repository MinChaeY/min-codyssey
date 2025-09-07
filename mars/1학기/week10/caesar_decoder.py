def caesar_cipher_decode(target_text):
    decoded_texts = []

    for shift in range(1, 26):  # 1~25까지 이동
        decoded = ""

        for char in target_text:
            if char.isalpha():  # 알파벳만 변환
                base = ord('A') if char.isupper() else ord('a')
                decoded += chr((ord(char) - base - shift) % 26 + base)
            else:
                decoded += char  # 공백, 숫자, 기호는 그대로 유지

        print(f"Shift {shift}:\n{decoded}\n{'-'*50}")
        decoded_texts.append((shift, decoded))

    return decoded_texts


# 1. 암호문 읽기
try:
    with open("E:/min-codyssey/mars/week10/password.txt", "r", encoding="utf-8") as f:
        encrypted_text = f.read().strip()
except FileNotFoundError:
    print("오류: password.txt 파일을 찾을 수 없습니다.")
    exit(1)
except UnicodeDecodeError:
    print("오류: 파일 인코딩 문제로 password.txt를 읽을 수 없습니다.")
    exit(1)

# 2. 해독 시도
decoded_candidates = caesar_cipher_decode(encrypted_text)

# 3. 사용자 입력 처리
try:
    correct_shift = int(input("올바른 해독으로 보이는 Shift 번호를 입력하세요: "))
    if not 1 <= correct_shift <= 25:
        raise ValueError
except ValueError:
    print("오류: 1에서 25 사이의 숫자를 입력해주세요.")
    exit(1)

# 4. 결과 저장 (예외 처리 포함)
try:
    with open("E:/min-codyssey/mars/week10/result.txt", "w", encoding="utf-8") as f:
        for shift, result in decoded_candidates:
            if shift == correct_shift:
                f.write(result)
                print(f"✅ Shift {shift} 결과가 result.txt에 저장되었습니다.")
                break
except IOError:
    print("오류: result.txt 파일을 쓸 수 없습니다.")
    exit(1)
