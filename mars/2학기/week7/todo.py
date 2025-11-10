from fastapi import FastAPI, APIRouter
from typing import Dict, List
import csv
import os

app = FastAPI()
router = APIRouter()

# CSV 파일 경로
CSV_FILE = 'todo_list.csv'

# CSV가 없으면 생성
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['id', 'task'])
        writer.writeheader()

# todo_list 리스트 객체
todo_list: List[Dict[str, str]] = []


def load_todos() -> None:
    """CSV 파일에서 todo_list로 데이터를 불러옴"""
    todo_list.clear()
    with open(CSV_FILE, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            todo_list.append({'id': row['id'], 'task': row['task']})


def save_todo(todo: Dict[str, str]) -> None:
    """CSV 파일에 새로운 todo를 추가 저장"""
    with open(CSV_FILE, 'a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['id', 'task'])
        writer.writerow(todo)


@router.post('/add_todo')
def add_todo(item: Dict[str, str]) -> Dict[str, str]:
    """새로운 할 일을 추가한다."""
    load_todos()
    todo_id = str(len(todo_list) + 1)
    task = item.get('task', '')
    new_todo = {'id': todo_id, 'task': task}
    save_todo(new_todo)
    return {'message': 'Todo added successfully', 'todo': new_todo}


@router.get('/retrieve_todo')
def retrieve_todo() -> Dict[str, List[Dict[str, str]]]:
    """할 일 목록을 반환한다."""
    load_todos()
    return {'todo_list': todo_list}


# 라우터 등록
app.include_router(router)
