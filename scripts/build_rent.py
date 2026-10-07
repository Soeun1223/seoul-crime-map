"""서울시 부동산 전월세가 정보 CSV를 자치구별 월세 요약으로 만든다.

사용법:
    1. https://data.seoul.go.kr/dataList/OA-21276/S/1/datasetView.do 에서
       서울특별시_전월세가_2024.zip 을 내려받아 압축을 푼다.
    2. python3 scripts/build_rent.py <압축 푼 CSV 경로>

결과: data/seoul-rent-2024.json (crime-map 페이지가 읽는 파일)
"""

import csv
import json
import statistics
import sys
from collections import defaultdict
from pathlib import Path

YEAR = "2024"
TYPES = ["아파트", "오피스텔", "연립다세대", "단독다가구"]
SMALL = "10평 이하"
SMALL_MAX_M2 = 33.06  # 10평 = 33.0579㎡
SIZES = ["전체", SMALL]

OUTPUT_FILE = Path(__file__).resolve().parent.parent / "data" / f"seoul-rent-{YEAR}.json"


def read_rows(path):
    # 서울시 파일은 CP949로 저장돼 있다
    with open(path, encoding="cp949", newline="") as f:
        for r in csv.DictReader(f):
            if r["전월세구분"] != "월세" or not r["계약일"].startswith(YEAR):
                continue
            rent = float(r["임대료(만원)"] or 0)
            if rent > 0:
                yield r["자치구명"], r["건물용도"], float(r["임대면적"] or 0), rent, float(r["보증금(만원)"] or 0)


def summarize(items):
    rents = [rent for rent, _ in items]
    return {
        "avg": round(statistics.mean(rents), 1),
        "median": statistics.median(rents),
        "deposit": round(statistics.mean(dep for _, dep in items)),
        "n": len(items),
    }


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)

    # groups[구][면적][주택 유형] = [(월세, 보증금), ...]
    groups = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    for gu, kind, area, rent, deposit in read_rows(sys.argv[1]):
        sizes = ["전체"] + ([SMALL] if 0 < area <= SMALL_MAX_M2 else [])
        for size in sizes:
            for t in ("전체", kind):
                groups[gu][size][t].append((rent, deposit))

    out = {
        "source": f"서울시 부동산 전월세가 정보 {YEAR} (서울 열린데이터광장 OA-21276)",
        "note": f"{YEAR}년 계약 중 월세(임대료 0원 초과)만, 단위 만원. {SMALL}는 임대면적 {SMALL_MAX_M2}㎡ 이하",
        "sizes": SIZES,
        "types": ["전체"] + TYPES,
        "districts": {
            gu: {size: {t: summarize(v[size][t]) for t in ["전체"] + TYPES if v[size][t]} for size in SIZES}
            for gu, v in sorted(groups.items())
        },
    }
    OUTPUT_FILE.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"서울 {len(groups)}개 구 → {OUTPUT_FILE.name}")


if __name__ == "__main__":
    main()
