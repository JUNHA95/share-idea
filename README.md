# 실습 08 · 일일 프로젝트 · 아이디어 콘솔 v2 · 기본필수

**PPT 실습 74쪽 · 설명 62~78쪽 · 전체 단계 선택 실습 40분**

## 목표
모듈형 콘솔의 등록·목록·저장·복원을 연결합니다. 비어 있는 필수 입력은 거부하고 첫 실행의 파일 없음은 빈 목록으로 시작합니다.

## 진행 순서
먼저 동작을 예측하고, 아래 TODO를 구현합니다. 직접 실행 → 공개 검사 → 페어 설명/기록 순서로 마칩니다.
TODO가 아닌 입출력 틀·검사 도구·이전 단계 구현은 제공 코드입니다. 파일 간 책임을 바꾸지 않고 핵심 처리부터 완성합니다.

| 수정할 파일 | TODO/해설 번호 | 구현할 내용 |
|---|---|---|
| `day3_console/idea_app/models.py` | `TO-RECORD` | Idea의 네 속성을 같은 키의 Dict로 반환하고 roles를 복사하세요. |
| `day3_console/idea_app/service.py` | `ADD` | Idea인지 검사하고 단계의 이름 중복 정책을 적용한 뒤 목록에 추가하세요. 거부 시 기존 목록을 유지하세요. |
| `day3_console/idea_app/storage.py` | `LOAD` | UTF-8 JSON을 읽으세요. 파일 없음만 []로 처리하고 손상은 ValueError로 전달한 뒤 전체 검사하세요. |
| `day3_console/idea_app/storage.py` | `SAVE` | 전체 검사를 먼저 수행하고 제공된 write_json_atomic(path, records)로 저장하세요. 실패를 숨기지 마세요. |
| `day3_console/idea_app/main.py` | `RELOAD` | 파일의 전체 읽기·검사와 새 객체 복원을 완료한 뒤에만 catalog.replace_all을 호출하세요. |

## 실행
가상환경의 Python으로 실행합니다. 현재 난이도 폴더에서:

```text
cd day3_console
python -m idea_app.main
# 합성 3건을 이용한 시연(데이터 파일이 없는 새 폴더에서)
python -m idea_app.main --demo
```

역할 폴더(강사용 또는 수강생용)에서 제공 런처를 사용할 때:

```text
python tools/run.py --exercise 08 --level basic --demo
python tools/check.py --exercise 08 --level basic
```

`checks.py`는 기능 확인용 제공 테스트입니다. 검사 도구는 임시 복사본에서 실행하여 원본 소스와 결과물을 변경하지 않습니다.
출력 기대값은 `expected_output.txt`, 생성 파일 예시는 `expected_outputs/`를 확인합니다. 구현을 하드코딩해 예시 한 건만 맞추지 마세요.

## 생성할 결과
- `day3_console/data/ideas.json`
- `day3_console/reports/summary.txt`

### 프로젝트 범위
실제 Multi AI Agent를 실행하는 것이 아니라 아이디어의 이름·문제·역할·난이도를 관리합니다. LLM API·API 키·GPU를 사용하지 않습니다.
모든 단계는 네 필드의 빈 값/역할 중복을 검사합니다. 아이디어 이름의 중복 거부와 검색·통계는 응용부터 확장됩니다.
기본필수는 공통 기준만으로 100점 가능하며 확장 기능을 하지 않았다는 이유로 감점하지 않습니다.

### 구조와 실행
정식 실행: day3_console에서 `python -m idea_app.main`.
메뉴: 1 등록, 2 목록, 5 저장, 6 다시읽기, 0 종료. 응용/심화에는 3 검색, 4 통계를 추가합니다.
이름·역할 비교는 앞뒤 공백과 대소문자를 무시합니다. 표시 문자열은 공백만 정리합니다.
0으로 종료해도 자동 저장되지 않습니다. 저장하려면 5를 선택합니다. 메모리에 저장하지 않은 변경이 있을 때 6은 확인을 요청합니다.
`--demo`는 합성 3건을 저장·복원해 보고서를 생성하며 기존 data/ideas.json을 덮어쓰지 않습니다.
새 시연: `python -m idea_app.main --demo --workspace ./trial_02`.
재실행 확인: 같은 경로에 `python -m idea_app.main --show --workspace ./trial_02`.

### 데이터 안전성
파일 없음은 첫 실행에서 빈 목록 정책입니다. 명시적 다시읽기의 파일 없음은 현재 메모리를 유지합니다.
손상·권한·레코드 오류로 시작하면 저장을 차단합니다. 같은 경로의 파일을 수정한 뒤 다시읽기에 성공해야 차단이 해제됩니다.
전체 읽기·검증 후에만 객체 목록을 바꾸며, 저장 실패 시 메모리와 기존 파일을 보존합니다.
io_support.py의 임시 파일 교체는 제공 보조 코드입니다. 데이터베이스 수준 동시성·정전 복구를 보장하는 프로젝트는 아닙니다.

### 제출
idea_app 소스, 합성 아이디어 3건의 data/ideas.json, reports/summary.txt, README, 테스트 기록, 리뷰 기록, 개인 기여를 제출합니다.
심화는 직접 완성한 test_cases.py도 제출합니다. score/role_count는 별도 분석 실습용 열이며 JSON 필수 저장 키가 아닙니다.


## 완료 확인
구현한 범위의 자동 테스트가 통과하고, 테스트_기록.md에 실제 명령/결과를 기록했는지 확인합니다.
코드를 설명하지 못한 채 출력만 맞춘 경우에는 페어에게 입력 → 처리 → 반환/저장의 순서를 설명해 봅니다.

강사용: 각 `해설` 번호는 수강생 TODO와 대응합니다. `예상 출력`은 실제 정답 실행 결과이며 학생 기록의 대필용으로 배포하지 않습니다.
