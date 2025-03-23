
# CSV 파일을 읽어 리스트로 변환하는 함수

def read_csv_to_list(filename):
    try:
        #파일을 with 구문을 사용하여 열었기 때문에 file.close()를 쓰지 않아도 자동으로 닫아준다.
        with open(filename, 'r') as file:
            lines = file.readlines()
        inventory_list = []

        for line in lines[1:]: #csv파일의 첫번째 줄은 헤더이므로 제외함
            parts = line.strip().split(',')
            #인화성은 마지막열이므로 마지막열만 float 형식으로 변환
            try:
                parts[4] = float(parts[4])
            except ValueError:
                #인화성에 대한 정보가 없을 경우의 기본값 지정
                parts[4] = 0.0
            inventory_list.append(parts)
        return inventory_list
    except Exception as e:
        print(f"Error reading file: {e}")
        return []
    
def sort_by_flammability(inventory_list):
    return sorted(inventory_list, key = lambda x: x[4], reverse = True)

def filter_high_flammability(inventory_list, threshold=0.7):
    return [item for item in inventory_list if item[4] >= threshold]

def write_csv(filename, inventory_list):
    try:
        with open(filename, 'w') as file:
            file.write('Substance,Weight (g),Specific Gravity,Strength,Flammability\n')
            for item in inventory_list:
                file.write(','.join(map(str, item)) + '\n')
    except Exception as e:
        print(f"Error writing to file: {e}")

# 이진 파일에 데이터를 저장하는 함수
def write_binary(filename, inventory_list):
    try:
        with open(filename, 'wb') as file:
            for item in inventory_list:
                for elem in item:
                    if isinstance(elem, str):
                        elem = elem.encode()  # 문자열을 바이트로 변환
                    file.write(bytes(str(elem), 'utf-8'))
    except Exception as e:
        print(f"Error writing binary file: {e}")


def read_binary(filename):
    try:
        with open(filename, 'rb') as file:
            content = file.read()
            print(content.decode('utf-8'))
    except Exception as e:
        print(f"Error reading binary file: {e}")


# 메인 실행 코드
inventory_file = 'Mars_Base_Inventory_List.csv'
inventory_list = read_csv_to_list(inventory_file)

# 인화성 순으로 정렬
sorted_inventory = sort_by_flammability(inventory_list)

# 인화성 0.7 이상인 목록 필터링
dangerous_inventory = filter_high_flammability(sorted_inventory)

# 인화성 0.7 이상인 목록 CSV로 저장
write_csv('Mars_Base_Inventory_danger.csv', dangerous_inventory)

# 이진 파일로 저장
write_binary('Mars_Base_Inventory_List.bin', sorted_inventory)
read_binary('Mars_Base_Inventory_List.bin')


