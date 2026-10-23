"""상태를 바꾸지 않는 분석 함수. 기본필수에서는 외부 패키지를 불러오지 않습니다."""
from idea_app.models import DIFFICULTIES

def summarize_roles(ideas):
    # 해설 ROLE-STATS: 빈 목록은 count=0/mean=None/max=None, 나머지는 NumPy로 역할 수 평균·최댓값을 구하세요.
    if not ideas:
        return {"count": 0, "mean": None, "max": None}
    import numpy as np
    counts = np.array([len(idea.roles) for idea in ideas], dtype=int)
    return {"count": len(ideas), "mean": float(counts.mean()), "max": int(counts.max())}

def summarize_difficulty(ideas):
    # 해설 DIFFICULTY-STATS: Pandas groupby.size로 난이도별 개수를 구하고 기본필수/응용/심화 순서의 DataFrame을 반환하세요. 없는 난이도는 0입니다.
    import pandas as pd
    frame = pd.DataFrame({"difficulty": [idea.difficulty for idea in ideas]})
    counts = frame.groupby("difficulty").size().reindex(DIFFICULTIES, fill_value=0)
    return pd.DataFrame({"difficulty": list(DIFFICULTIES), "count": counts.to_numpy(dtype=int)})

def render_summary(ideas, extended=False):
    """제공 출력 형식. 통계가 없는 경우 0점/NaN 평균으로 오해하지 않게 표시합니다."""
    lines = [f"아이디어 수: {len(ideas)}"]
    lines.extend(idea.summary() for idea in ideas)
    if extended:
        role_stats = summarize_roles(ideas)
        if role_stats["mean"] is None:
            lines.append("역할 수 통계: 데이터 없음")
        else:
            lines.append(f"역할 수 평균: {role_stats['mean']:.2f}")
            lines.append(f"역할 수 최댓값: {role_stats['max']}")
        frame = summarize_difficulty(ideas)
        lines.append("난이도 | 개수")
        for row in frame.itertuples(index=False):
            lines.append(f"{row.difficulty} | {row.count}")
    return "\n".join(lines) + "\n"
