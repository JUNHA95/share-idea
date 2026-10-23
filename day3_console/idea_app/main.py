"""아이디어 콘솔 v2: 메뉴·실행 순서·오류 안내만 담당합니다.
LLM/API 키/네트워크를 사용하지 않습니다. 종료는 자동 저장이 아닙니다.
--workspace와 --demo는 강사가 제공한 시연/검수용 옵션입니다.
"""
import argparse
import json
from pathlib import Path
from idea_app.models import Idea, from_record, to_record
from idea_app.service import IdeaCatalog
from idea_app.storage import load_records, save_records
from idea_app.analytics import render_summary
ROOT = Path(__file__).resolve().parent.parent
# 현재 파일실행 경로Path(__file__)> 절대경로로 변환.resolve()> 위> 위 = day3_console
DATA_PATH = ROOT / "data" / "ideas.json"
EXTENDED = False

def reload_catalog(catalog, path):
    # 해설 RELOAD: 파일의 전체 읽기·검사와 새 객체 복원을 완료한 뒤에만 catalog.replace_all을 호출하세요.
    records = load_records(path)
    candidates = [from_record(record) for record in records]
    catalog.replace_all(candidates)

def write_report(workspace, ideas):
    """보고서 내용은 먼저 완성합니다. 본 함수는 제공되는 입출력 연결 코드입니다."""
    text = render_summary(ideas, extended=EXTENDED)
    path = workspace / "reports" / "summary.txt"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return text

def display_ideas(ideas):
    if not ideas:
        print("등록된 아이디어가 없습니다.")
    for index, idea in enumerate(ideas, start=1):
        print(f"{index}. {idea.summary()} / {idea.difficulty}")
        print("   문제:", idea.problem)
        print("   역할:", ", ".join(idea.roles))

def request_idea():
    name = input("프로젝트명> ")
    problem = input("문제> ")
    roles = input("역할(쉼표 구분)> ").split(",")
    difficulty = input("난이도(기본필수/응용/심화)> ")
    return Idea(name, problem, roles, difficulty)

def demo(workspace):
    """정해진 합성 아이디어 3건을 쓰는 시연. 이미 있는 파일은 덮어쓰지 않습니다."""
    path = workspace / "data" / "ideas.json"
    if path.exists():
        print("시연 중단: data/ideas.json이 이미 있습니다. 새 --workspace를 지정하세요.")
        return 2
    records = json.loads((ROOT / "fixtures" / "valid_ideas.json").read_text(encoding="utf-8"))
    catalog = IdeaCatalog()
    for record in records:
        catalog.add(from_record(record))
    save_records(path, [to_record(idea) for idea in catalog.list_all()])
    print("저장 완료: data/ideas.json")
    restored = IdeaCatalog()
    reload_catalog(restored, path)
    print(f"복원 확인: {len(restored.list_all())}개")
    print(write_report(workspace, restored.list_all()), end="")
    print("보고서 저장: reports/summary.txt")
    return 0

def main(argv=None):
    parser = argparse.ArgumentParser(description="Multi AI Agent 아이디어 관리 콘솔 v2")
    parser.add_argument("--workspace", type=Path, default=ROOT, help="data·reports가 만들어질 폴더")
    parser.add_argument("--demo", action="store_true", help="합성 3건 저장·복원·보고서 시연")
    parser.add_argument("--show", action="store_true", help="파일을 읽어 목록만 표시하고 종료")
    args = parser.parse_args(argv)
    workspace = args.workspace.expanduser().resolve()
    if args.demo:
        try:
            return demo(workspace)
        except (ValueError, OSError) as error:
            print(f"시연 실패: {error}")
            return 1
    path = workspace / "data" / "ideas.json"
    catalog = IdeaCatalog()
    blocked = False
    try:
        existed = path.exists()
        reload_catalog(catalog, path)
        if existed:
            print(f"아이디어 {len(catalog.list_all())}개를 불러왔습니다.")
        else:
            print("등록된 파일이 없습니다. 빈 목록으로 시작합니다.")
    except (ValueError, OSError) as error:
        # 손상된 파일을 읽지 못한 상태에서 빈 메모리를 덮어쓰는 일을 막습니다.
        blocked = True
        print(f"불러오기 실패: {error}")
        print("원본 보존: 다시 읽기에 성공하기 전에는 저장할 수 없습니다.")
    if args.show:
        display_ideas(catalog.list_all())
        return 1 if blocked else 0
    dirty = False
    while True:
        menu = "1=등록  2=목록  "
        if EXTENDED:
            menu += "3=검색  4=통계  "
        menu += "5=저장  6=다시읽기  0=종료"
        print(menu)
        try:
            choice = input("선택> ").strip()
            if choice == "0":
                if dirty:
                    print("주의: 저장하지 않은 변경은 파일에 반영되지 않습니다.")
                print("종료합니다.")
                return 0
            if choice == "1":
                try:
                    idea = request_idea()
                    catalog.add(idea)
                except (ValueError, TypeError) as error:
                    print(f"등록 거부: {error}")
                else:
                    dirty = True
                    print("아이디어 등록 완료")
            elif choice == "2":
                display_ideas(catalog.list_all())
            elif choice == "3" and EXTENDED:
                try:
                    display_ideas(catalog.search(input("검색어> ")))
                except ValueError as error:
                    print(f"검색 안내: {error}")
            elif choice == "4" and EXTENDED:
                try:
                    print(write_report(workspace, catalog.list_all()), end="")
                    print("보고서 저장: reports/summary.txt")
                except OSError as error:
                    print(f"보고서 저장 실패: {error}")
            elif choice == "5":
                if blocked:
                    print("저장 차단: 읽기 오류가 해결되지 않았습니다. 원본을 보존합니다.")
                    continue
                try:
                    save_records(path, [to_record(idea) for idea in catalog.list_all()])
                except (ValueError, OSError) as error:
                    print(f"저장 실패: {error}; 메모리는 유지합니다.")
                else:
                    dirty = False
                    print("저장 완료: data/ideas.json")
                    try:
                        write_report(workspace, catalog.list_all())
                        print("보고서 저장: reports/summary.txt")
                    except OSError as error:
                        print(f"JSON 저장은 완료했지만 보고서 저장은 실패했습니다: {error}")
            elif choice == "6":
                # 명시적 다시읽기에서는 파일 없음/저장하지 않은 변경도 따로 처리합니다.
                if dirty:
                    answer = input("저장하지 않은 메모리 변경을 버리고 다시 읽을까요? (y/n)> ").strip().casefold()
                    if answer != "y":
                        print("다시 읽기 취소: 메모리를 유지합니다.")
                        continue
                if not path.exists():
                    print("다시 읽기 취소: 파일이 없습니다. 현재 목록을 유지합니다.")
                    continue
                try:
                    reload_catalog(catalog, path)
                except (ValueError, OSError) as error:
                    blocked = True
                    print(f"다시 읽기 실패: {error}; 현재 목록과 원본을 보존합니다.")
                else:
                    blocked = False
                    dirty = False
                    print(f"복원 완료: {len(catalog.list_all())}개")
            else:
                print("메뉴에 있는 번호를 입력하세요.")
        except (EOFError, KeyboardInterrupt):
            print("\n입력이 종료되었습니다. 자동 저장하지 않습니다.")
            return 0

if __name__ == "__main__":
    raise SystemExit(main())
