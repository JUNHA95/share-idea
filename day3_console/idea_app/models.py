"""Idea의 데이터 규칙. 모델은 입력창·화면 출력·파일 입출력을 담당하지 않습니다."""
DIFFICULTIES = ("기본필수", "응용", "심화") # 이게 튜플임. 수정불가하다.

def name_key(value):
    """비교용 문자열. 표시할 원문과 비교할 키를 분리합니다."""
    return value.strip().casefold() #.casefold()는 .lower()보다 더 강력하다. 어떤 문자든 비교가능하도록 표준화하는 것

def require_text(value, field):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field}: 비어 있지 않은 문자열이 필요합니다")
    return value.strip()

class Idea:
    def __init__(self, name, problem, roles, difficulty):
        self.name = require_text(name, "name")
        self.problem = require_text(problem, "problem")
        self.difficulty = require_text(difficulty, "difficulty")
        if self.difficulty not in DIFFICULTIES:
            raise ValueError("difficulty: 기본필수/응용/심화 중 하나여야 합니다")
        # roles가 리스트이기 때문에 조금 더 정교한 조건이 필요해서 아래에 쓰게 됨
        if not isinstance(roles, list) or not roles:
            raise ValueError("roles: 비어 있지 않은 List가 필요합니다")
        # 일단 리스트인지, 공백인지 판단하기
        cleaned, seen = [], set()
        for role in roles:
            value = require_text(role, "role")
            key = name_key(value)
            if key in seen:
                raise ValueError("roles: 같은 역할을 중복 등록할 수 없습니다")
            cleaned.append(value)
            seen.add(key)
        # 입력 List와 다른 새 List를 소유합니다. 문자열 원소는 불변입니다.
        self.roles = cleaned # 여기에 self.roles가 있음!!!!!!!! 위에 없다고 당황X

    def summary(self):
        return f"{self.name}: 역할 {len(self.roles)}개"

def to_record(idea):
    # Idea 객체를 받아서 to_record를 거치면 딕셔너리로 바꿔서 저장한다. JSON 그 자체저장은 힘들어서
    # 해설 TO-RECORD: Idea의 네 속성을 같은 키의 Dict로 반환하고 roles를 복사하세요.
    return {"name": idea.name, "problem": idea.problem,
            "roles": list(idea.roles), "difficulty": idea.difficulty}
            # list()하면 [[]]이렇게 되는게 아니고 리스트가 복사될 뿐이다.
            #[[]]하고 싶으면 그냥 [idea.roles]라고 하면 된다.
def from_record(record):
    """필수 키를 확인한 뒤 새 Idea를 만듭니다. 추가 키는 사용하지 않습니다."""
    # 해설 FROM-RECORD: Dict와 필수 키를 검사한 뒤 Idea 객체로 복원하세요.
    required = {"name", "problem", "roles", "difficulty"}
    if not isinstance(record, dict):
        raise ValueError("레코드는 Dict여야 합니다")
    if not required <= record.keys(): #필수 키 4개(이름 등등)이 제대로 있는지 검사하기
        # .key()는 딕셔너리에 있는 모든 키를 꺼내서 확인하는 것이다.
        # 숫자 비교를 의미하지 않고 부분집합 관계인지를 따지는 연산이다.
        missing = ", ".join(sorted(required - record.keys()))
        # 부족한 부분(required - record.keys())를 찾아서 알파벳순 정렬(sorted)해라
        # 그리고 그걸 ",".join() 쉼표로 연결해라. "\n".join()을 본적 있잖아.
        raise ValueError(f"필수 키 누락: {missing}")
    return Idea(record["name"], record["problem"],
                record["roles"], record["difficulty"])
        # 각 딕셔너리에서 값을 꺼낸다음에 다시 Idea 객체로 복원하라는 뜻이다.