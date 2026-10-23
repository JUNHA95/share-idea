"""JSON 읽기·전체 검사·저장. 실패를 빈 목록 또는 성공으로 위장하지 않습니다."""
import json
from pathlib import Path
from idea_app.models import from_record, to_record, name_key
from idea_app.io_support import write_json_atomic
REJECT_DUPLICATES = False

def validate_records(records):
    # 입력 데이터 리스트인지 확인> 맞다면 하나씩 검사 후 Idea 객체로 변환> 이름 중복검사> 통과값 validated에 모으기
    if not isinstance(records, list):
        # isinstance(a,b)는 a가 b라는 자료형에 해당하는지 확인하는 함수로, 맞으면 True, 아니면 False
        raise ValueError("최상위 데이터는 List여야 합니다")
    validated, seen = [], set() # 반복문 하기 전, 검사 통과 데이터와 확인한 데이터 모을 변수설정함
    for index, record in enumerate(records, start=1): # 하나씩 검사하며, 문제가 있으면 순서를 함께 기억가능하므로
        try: 
            idea = from_record(record) #검사 후 사용가능한 Idea 객체로 변환하는 함수임
        except ValueError as error:
            raise ValueError(f"레코드 {index}: {error}") from error
        # 앞 try에서 from_record가 검사 했는데 문제가 생기면 except로 넘기는 것
        # ValueError 발생하면 error로 받고, 개발자가 참조하기 쉽게 메세지를 남겼다.
        # 그런데 그 메세지가 enumerate를 사용한 덕택에 index도 함께 출력됨
        key = name_key(idea.name) # name_key()는 models.py에 있음
        # 클래스 정의로 Idea를 정했으면 그 요소로 idea = Idea(~~~~)식으로 값을 저장하는 것이다.
        # 그래서 저장된 Idea에 name, role, difficulty도 있으면 idea = Idea("준하", "학생", "어려움")이 있다.
        # 그걸 idea.name으로 불러오는 것
        if REJECT_DUPLICATES and key in seen:
            # REJECT_DUPLICATES는 항상 False로 설정되어 있는데, key in seen이 똑같이 False면 if 이하 조건문 실행됨
            # key값이 seen에 있는 값이 아니면 False 겠지. 이 뜻은 값을 살핀적이 없다는 뜻이다.
            raise ValueError(f"레코드 {index}: 이름 중복: {idea.name}")
        seen.add(key)
        validated.append(to_record(idea))
    return validated

def load_records(path):  # 함수를 정의하는데, path를 매개변수로 설정한 이유는 경로를 전달받는 다는 의미의 표현
# 이 함수는 지정된 경로의 JSON 파일 읽어서 파이썬 데이터로 변환하고 그 다음으로 다음을 처리한다.
# 1. 파일 자체가 없으면 빈 목록 반환 
# 2. 파일은 있는데 JSON 형식이 잘못되었으면 오류 일으키기
# 3. 파일 있고, JSON 형식도 정상이면 데이터 전체가 현재 프로그램에 정의된 정해진 규칙에 맞는지 검사
    try: # try except는 오류 가능성 and 오류 구분가능 and 대응법 존재일 때 사용할 것
         # try: 일단 해봐 > except: 그런데 except 다음에 적힌 일이 발생하면 수행할 일이 있어
        with Path(path).open("r", encoding="utf-8") as f:
            records = json.load(f)
        # 경로 객체 만들기 Path(path) > 열되(utf-8)로 읽기 > 연 파일을 f 로 설정
        # json.load(f): json파일을 읽고, 파이썬 자료형으로 변환하는 함수
           # (f)인 이유는 앞에서 오픈한 파일을 f로 하기로 정했으니까
    except FileNotFoundError:
        # json 파일 자체각 존재하지 않으면 뜨는 오류이다. 그 경우 빈목록 반환
        return []
    except json.JSONDecodeError as error: # JSON을 읽다가 발생한 오류인데, 이를 error로 부르기로 한다. as의 경우 꼭 except 뒤에 오는 것은 아니다.
        raise ValueError("JSON 손상: 원본 보존") from error # raise는 오류를 강제로 일으키는 것인데, ValueError의 경우 JASONDecodeError를 포함하는 상위 오류명이다.
        # JASONDecodeError가 발생 > error로 할당> from error: JSONDecodeError 떄문에 ValueError 발생한 것으로 인과관계 설정(그냥 보여주기 위한 것임)
        # 왜 ValueError를 썼는가: raise뒤에 실제 오류명이 와야하는데, 상위 오류를 쓰면 될 것이지 굳이 다른 것을 쓸 필요는 없다.
        # ValueError 뒤에 문구는 써도 되고 안 써도 된다. 당장 출력되는 것은 아니다. 개발자 보라고 있는 것
    return validate_records(records)
        # 멀쩡하면 validate_records(records)수행하여 프로젝트가 요구하는 규격에 맞는지 검사하기

def save_records(path, records):
    # 해설 SAVE: 전체 검사를 먼저 수행하고 제공된 write_json_atomic(path, records)로 저장하세요. 실패를 숨기지 마세요.
    validated = validate_records(records)
    write_json_atomic(Path(path), validated)
    # 일단 JSON 문자열 생성 > 임시파일 기록> 최종파일 교체> 남은 임시파일 정리만 알아둬
    # 성공 메시지는 함수가 정상 반환된 뒤 main에서만 출력합니다.
