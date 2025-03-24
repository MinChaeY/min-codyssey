def read_csv_to_list(filename):
    try:
        inventory_list = []
        with open(filename, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            if len(lines) < 2:  # 데이터가 없는 경우 예외 처리
                raise ValueError(f"File '{filename}' does not contain enough data (header and at least one row required).")
            for line in lines[1:]:  # 첫 번째 줄은 헤더로 제외
                parts = line.strip().split(',')
                if len(parts) != 5:  # 열 개수 불일치
                    print(f"Warning: Line has an incorrect number of columns: {line}")
                    continue  # 비정상적인 데이터는 건너뜀
                try:
                    parts[4] = float(parts[4])  # 인화성 변환
                except ValueError:
                    parts[4] = 0.0  # 인화성 값이 없을 경우 기본값
                inventory_list.append(parts)
        return inventory_list
    except FileNotFoundError:
        print(f"File '{filename}' not found. Please check the file path.")
        return []
    except PermissionError:
        print(f"Permission denied when trying to access '{filename}'.")
        return []
    except UnicodeDecodeError:
        print(f"File '{filename}' has encoding issues. Please ensure it is saved with UTF-8 encoding.")
        return []
    except OSError as e:
        print(f"An error occurred while accessing the file: {e}")
        return []
    except ValueError as ve:
        print(ve)
        return []

def sort_by_flammability(inventory_list):
    try:
        return sorted(inventory_list, key=lambda x: x[4], reverse=True)
    except IndexError as e:
        print(f"Index error when sorting by flammability: {e}")
        return []

def filter_high_flammability(inventory_list, threshold=0.7):
    try:
        return [item for item in inventory_list if item[4] >= threshold]
    except IndexError as e:
        print(f"Index error when filtering by flammability: {e}")
        return []

def write_csv(filename, inventory_list):
    try:
        with open(filename, 'w', encoding='utf-8') as file:
            file.write('Substance,Weight (g),Specific Gravity,Strength,Flammability\n')
            for item in inventory_list:
                file.write(','.join(map(str, item)) + '\n')
    except OSError as e:
        print(f"Error writing to file '{filename}': {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def write_binary(filename, inventory_list):
    try:
        with open(filename, 'wb') as file:
            for item in inventory_list:
                for elem in item:
                    try:
                        if isinstance(elem, str):
                            elem = elem.encode()  # 문자열을 바이트로 변환
                        file.write(bytes(str(elem), 'utf-8'))
                    except UnicodeEncodeError as ue:
                        print(f"Encoding error occurred: {ue}")
    except OSError as e:
        print(f"Error writing binary file: {e}")

def read_binary(filename):
    try:
        with open(filename, 'rb') as file:
            content = file.read()
            print(content.decode('utf-8'))
    except FileNotFoundError:
        print(f"Binary file '{filename}' not found.")
    except PermissionError:
        print(f"Permission denied when trying to access the binary file '{filename}'.")
    except OSError as e:
        print(f"Error reading binary file: {e}")
    except UnicodeDecodeError:
        print(f"Error decoding binary file '{filename}'. Please ensure the file is correctly encoded.")

# 메인 실행 코드
inventory_file = 'E:\min-codyssey\mars\week3\Mars_Base_Inventory_List.csv'
inventory_list = read_csv_to_list(inventory_file)

if inventory_list:
    # CSV 파일에서 읽은 내용 출력 (추가된 부분)
    print("CSV 파일에서 읽은 내용:")
    for item in inventory_list:
        print(item)

    # 인화성 순으로 정렬
    sorted_inventory = sort_by_flammability(inventory_list)

    # 인화성 0.7 이상인 목록 필터링
    dangerous_inventory = filter_high_flammability(sorted_inventory)

    # 인화성 0.7 이상인 목록 CSV로 저장
    write_csv('Mars_Base_Inventory_danger.csv', dangerous_inventory)

    # 인화성 0.7 이상인 목록 출력 (기존 부분)
    print("인화성 지수가 0.7 이상인 물질 목록:")
    for item in dangerous_inventory:
        print(item)

    # 이진 파일로 저장
    print('이진파일 출력부분')
    write_binary('Mars_Base_Inventory_List.bin', sorted_inventory)
    read_binary('Mars_Base_Inventory_List.bin')
