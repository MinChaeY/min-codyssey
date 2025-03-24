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
    except (FileNotFoundError, PermissionError, OSError, UnicodeDecodeError) as e:
        print(f"File error: {e}")
        return []
    except ValueError as ve:
        print(f"Data error: {ve}")
        return []

def sort_by_flammability(inventory_list):
    try:
        return sorted(inventory_list, key=lambda x: x[4], reverse=True)
    except (IndexError, TypeError) as e:
        print(f"Data error when sorting by flammability: {e}")
        return []

def filter_high_flammability(inventory_list, threshold=0.7):
    try:
        return [item for item in inventory_list if item[4] >= threshold]
    except (IndexError, TypeError) as e:
        print(f"Data error when filtering by flammability: {e}")
        return []

def write_csv(filename, inventory_list):
    try:
        with open(filename, 'w', encoding='utf-8') as file:
            file.write('Substance,Weight (g),Specific Gravity,Strength,Flammability\n')
            for item in inventory_list:
                file.write(','.join(map(str, item)) + '\n')
    except OSError as e:
        print(f"File error when writing CSV: {e}")

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
        print(f"File error when writing binary: {e}")

def read_binary(filename):
    try:
        with open(filename, 'rb') as file:
            content = file.read()
            print(content.decode('utf-8'))
    except (FileNotFoundError, PermissionError, OSError, UnicodeDecodeError) as e:
        print(f"File error when reading binary: {e}")

# 메인 실행 코드
inventory_file = 'E:\min-codyssey\mars\week3\Mars_Base_Inventory_List.csv'
inventory_list = read_csv_to_list(inventory_file)

if inventory_list:
    # CSV 파일에서 읽은 내용 출력
    print("CSV 파일에서 읽은 내용:")
    for item in inventory_list:
        print(item)

    # 인화성 순으로 정렬
    sorted_inventory = sort_by_flammability(inventory_list)

    # 인화성 0.7 이상인 목록 필터링
    dangerous_inventory = filter_high_flammability(sorted_inventory)

    # 인화성 0.7 이상인 목록 CSV로 저장
    write_csv('Mars_Base_Inventory_danger.csv', dangerous_inventory)

    # 인화성 0.7 이상인 목록 출력
    print("인화성 지수가 0.7 이상인 물질 목록:")
    for item in dangerous_inventory:
        print(item)

    # 이진 파일로 저장 및 출력
    print('이진파일 출력')
    write_binary('Mars_Base_Inventory_List.bin', sorted_inventory)
    read_binary('Mars_Base_Inventory_List.bin')
