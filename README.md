# 서울 자치구별 범죄 · 월세 지도 (2024)

서울 25개 자치구의 범죄 발생 현황과 평균 월세를 지도와 산점도로 보여주는 페이지입니다.

## 데이터

| 데이터 | 출처 | 받는 방법 |
| --- | --- | --- |
| 범죄 발생 건수 | [경찰청_범죄 발생 지역별 통계 (2024)](https://www.data.go.kr/data/3074462/fileData.do) | 공공데이터포털 **API** (`scripts/fetch_crime.py`) |
| 자치구 인구 | [행정안전부 주민등록 인구통계](https://jumin.mois.go.kr/) 2024년 12월 말 | `data/seoul-population-2024.json`에 저장 |
| 평균 월세 | [서울시 부동산 전월세가 정보 (2024)](https://data.seoul.go.kr/dataList/OA-21276/S/1/datasetView.do) | 파일 다운로드 후 `scripts/build_rent.py`로 2024년 월세 계약 약 28만 건을 구별로 요약 (전체 / 10평=33.06㎡ 이하) |
| 자치구 경계 | [southkorea/seoul-maps](https://github.com/southkorea/seoul-maps) | GeoJSON |

범죄율은 `발생 건수 ÷ 주민등록 인구 × 100,000`(인구 10만 명당)입니다.

## API 인증키

인증키는 코드에 넣지 않고 GitHub Secret으로 관리합니다.

1. 저장소 **Settings → Secrets and variables → Actions → New repository secret**
2. Name `DATA_GO_KR_KEY`, 값은 공공데이터포털 일반 인증키 (Encoding/Decoding 둘 다 가능)
3. **Actions → Update crime data → Run workflow** 로 실행 (매달 1일에도 자동 실행)

자동 작업이 API를 불러 `data/seoul-crime-2024.json`을 갱신하고 커밋합니다.

내 컴퓨터에서 실행하기:

```bash
DATA_GO_KR_KEY=여기에_인증키 python3 scripts/fetch_crime.py
```

## 미리 보기

`index.html`이 `data/` 폴더의 JSON을 불러오기 때문에 로컬 서버로 열어야 합니다.

```bash
python3 -m http.server 8000
```

## 파일 구성

| 파일 | 역할 |
| --- | --- |
| `index.html` | 지도 페이지 (Leaflet) |
| `data/seoul-crime-2024.json` | 범죄 통계 (API로 갱신) |
| `data/seoul-population-2024.json` | 범죄율 계산용 인구 |
| `data/seoul-rent-2024.json` | 자치구·면적·주택 유형별 월세 요약 |
| `scripts/build_rent.py` | 전월세가 CSV로 월세 요약 JSON을 만드는 스크립트 |
| `data/seoul-gu.geojson` | 서울 자치구 경계 |
| `scripts/fetch_crime.py` | 공공데이터포털 API 호출 스크립트 |
| `.github/workflows/update-crime-data.yml` | 매달 API를 불러 데이터를 갱신하는 자동 작업 |
