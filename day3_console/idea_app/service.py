"""등록·검색·상태 교체 규칙. 파일 읽기나 화면 출력은 하지 않습니다."""
from idea_app.models import Idea, name_key
REJECT_DUPLICATES = False

class IdeaCatalog:
    def __init__(self):
        self.ideas = []

    def add(self, idea):
        # 해설 ADD: Idea인지 검사하고 단계의 이름 중복 정책을 적용한 뒤 목록에 추가하세요. 거부 시 기존 목록을 유지하세요.
        if not isinstance(idea, Idea):
            raise TypeError("Idea 객체가 필요합니다")
        if REJECT_DUPLICATES and any(name_key(item.name) == name_key(idea.name) for item in self.ideas):
            raise ValueError("이미 등록된 이름입니다")
        self.ideas.append(idea)

    def list_all(self):
        """List 컨테이너만 복사합니다. 안의 Idea 객체까지 깊게 복제하는 API는 아닙니다."""
        return list(self.ideas)

    def names(self):
        return [idea.name for idea in self.ideas]

    def search(self, keyword):
        # 해설 SEARCH: 빈 검색어를 거부하고 이름 또는 problem에 검색어가 포함된 Idea 목록을 반환하세요. 대소문자는 무시합니다.
        if not isinstance(keyword, str) or not keyword.strip():
            raise ValueError("검색어는 비어 있을 수 없습니다")
        key = name_key(keyword)
        return [idea for idea in self.ideas
                if key in name_key(idea.name) or key in name_key(idea.problem)]

    def replace_all(self, ideas):
        # 해설 REPLACE-ALL: 별도 후보 Catalog에서 모든 객체를 add로 검사한 뒤 한 번에 현재 ideas를 교체하세요.
        candidate = IdeaCatalog()
        for idea in ideas:
            candidate.add(idea)
        self.ideas = candidate.list_all()
