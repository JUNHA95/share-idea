"""강사가 제공한 저장 보조 코드. 이번 시간의 구현 평가 대상이 아닙니다.
검증·직렬화가 끝난 내용을 같은 폴더의 임시 파일에 쓴 뒤 교체합니다.
데이터베이스 트랜잭션, 동시 쓰기 조정, 정전 내구성을 보장하는 예제는 아닙니다.
"""
import json
import os
import tempfile
from pathlib import Path

def write_json_atomic(path, records):
    # 직렬화가 실패하면 기존 파일을 열기도 전에 예외가 발생합니다.
    text = json.dumps(records, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=".ideas_", suffix=".tmp", dir=path.parent)
    temp_path = Path(temp_name)
    try:
        # fdopen이 닫힐 때 파일 핸들도 닫힙니다. Windows에서도 닫은 뒤 교체합니다.
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
        os.replace(temp_path, path)
    finally:
        # 교체 실패 시 남은 임시 파일만 삭제합니다. 원본은 삭제하지 않습니다.
        temp_path.unlink(missing_ok=True)
