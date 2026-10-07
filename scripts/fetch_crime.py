"""공공데이터포털 API로 경찰청 범죄 통계를 받아 서울 25개 구 데이터만 저장한다.

사용법:
    DATA_GO_KR_KEY=<인증키> python3 scripts/fetch_crime.py

인증키는 공공데이터포털 마이페이지의 "일반 인증키"를 쓴다 (Encoding, Decoding 둘 다 가능).
결과: data/seoul-crime-2024.json (crime-map.html이 읽는 파일)
"""

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path

# 경찰청_범죄 발생 지역별 통계_20241231
API_URL = "https://api.odcloud.kr/api/3074462/v1/uddi:ae109087-8690-4cb5-bda9-a7876a92f3b8"
DATASET = "경찰청_범죄 발생 지역별 통계_20241231 (공공데이터포털 API)"

ROOT = Path(__file__).resolve().parent.parent
POPULATION_FILE = ROOT / "data" / "seoul-population-2024.json"
OUTPUT_FILE = ROOT / "data" / "seoul-crime-2024.json"


def fetch_rows(key):
    rows, page = [], 1
    while True:
        query = urllib.parse.urlencode({"page": page, "perPage": 100, "serviceKey": key})
        try:
            with urllib.request.urlopen(f"{API_URL}?{query}", timeout=30) as res:
                body = json.load(res)
        except urllib.error.HTTPError as e:
            sys.exit(f"API 요청 실패 ({e.code}): {e.read().decode('utf-8', 'replace')}")
        rows += body["data"]
        if len(rows) >= body["totalCount"] or not body["data"]:
            return rows
        page += 1


def main():
    key = os.environ.get("DATA_GO_KR_KEY", "").strip()
    if not key:
        sys.exit("DATA_GO_KR_KEY 환경 변수에 공공데이터포털 인증키를 넣어 주세요.")
    # Encoding 키를 넣어도 두 번 인코딩되지 않도록 원래 값으로 되돌린다
    key = urllib.parse.unquote(key)

    rows = fetch_rows(key)
    population = json.loads(POPULATION_FILE.read_text(encoding="utf-8"))

    # API 열 이름은 "서울 종로구"처럼 시도 + 구 형식
    districts = {}
    for gu, pop in population["population"].items():
        column = f"서울 {gu}"
        if column not in rows[0]:
            sys.exit(f"API 응답에 '{column}' 열이 없어요. 데이터 형식이 바뀌었는지 확인해 주세요.")
        districts[gu] = {"population": pop, "counts": [int(r[column]) for r in rows]}

    out = {
        "source": {"crime": DATASET, "population": population["source"]},
        "fetchedAt": datetime.now(timezone(timedelta(hours=9))).strftime("%Y-%m-%d %H:%M"),
        "categories": [[r["범죄대분류"], r["범죄중분류"]] for r in rows],
        "districts": districts,
    }
    OUTPUT_FILE.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"범죄 유형 {len(rows)}개 × 서울 {len(districts)}개 구 → {OUTPUT_FILE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
