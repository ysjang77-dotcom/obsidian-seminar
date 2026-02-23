# 파우더 밀도 측정 ASTM 표준 체계

> 파우더 밀도는 **겉보기 밀도(Apparent)**, **탭 밀도(Tap)**, **진밀도(True)** 3가지로 분류되며,
> 각각에 대응하는 ASTM 시험 표준이 존재한다.

---

## 1. 겉보기 밀도 (Apparent Density) — 자연 충전 상태

분말을 깔때기/장치를 통해 **자유 낙하**시켜 일정 부피의 컵에 채운 후, 질량/부피로 밀도를 산출한다.

| 표준 | 장비 | 적용 대상 | 핵심 사양 |
|------|------|-----------|-----------|
| **ASTM B212** | Hall Flowmeter Funnel | **자유 유동** 금속 분말 | 25 cm³ 밀도 컵, 60° 콘, 오리피스 2.54 mm. 분말이 자력으로 Hall Funnel을 통과해야 함 |
| **ASTM B417** | Carney Funnel | **비유동** 금속 분말 | 25 cm³ 밀도 컵, 오리피스 5.08 mm. Hall Funnel로 유동 불가 시 사용 |
| **ASTM B329** | Scott Volumeter | 금속 분말 및 화합물 | 25 cm³ 밀도 컵. 배플판(baffle)으로 분말을 분산시켜 균일하게 충전 |
| **ASTM B703** | Arnold Meter | 금속 분말 및 관련 화합물 | B212/B417/B329 대비 **약 0.2 g/cm³ 높은 값** 산출. 직접 비교 시 주의 |

### 겉보기 밀도 표준 선택 기준

```
분말이 Hall Funnel(2.54mm)을 자유 통과하는가?
├─ YES → ASTM B212 (Hall Funnel) ← 우선 적용
├─ NO  → ASTM B417 (Carney Funnel, 5.08mm)
└─ 미세 분말/특수 화합물 → ASTM B329 (Scott Volumeter)
```

> **주의**: ASTM B703(Arnold Meter)은 다른 3개 표준과 약 0.2 g/cm³ 차이가 나므로, 데이터 비교 시 동일 표준으로 측정한 값끼리만 비교해야 한다.

---

## 2. 탭 밀도 (Tap Density) — 진동/탭핑 후 충전 상태

분말을 메스실린더에 넣고 반복적으로 **탭핑(낙하 충격)**하여 최밀 충전 상태의 밀도를 측정한다.

| 표준 | 장비 | 적용 대상 | 핵심 사양 |
|------|------|-----------|-----------|
| **ASTM B527** | 탭 밀도 시험기 + 메스실린더 | **금속 분말/화합물** | 시료 100±0.5 g, 100 mL 실린더. 겉보기밀도 >4 g/cm³이면 25 mL 실린더 사용. 낙하 높이 3 mm, 100~300 tap/min |
| **ASTM D7481** | 메스실린더 | **일반 분말/과립** (≤3.5 mm) | Method A: Loose 밀도, Method B: Tapped 밀도. 비금속 분말/과립용 |

### B527 vs D7481 차이

| 항목 | ASTM B527 | ASTM D7481 |
|------|-----------|------------|
| 대상 | 금속 분말/화합물 | 일반 분말, 과립, 활성탄 등 |
| 관할 위원회 | B09 (Powder Metallurgy) | D18 (Soil and Rock) |
| 시료량 | 100 g (질량 기준) | 부피 기준 충전 |
| 실린더 | 100 mL 또는 25 mL | 메스실린더 |
| 탭핑 조건 | 낙하 3 mm, 100~300 tap/min | 규정된 탭핑 조건 |

---

## 3. 진밀도 (True/Absolute Density) — 기공 제외 순수 밀도

| 표준 | 방법 | 적용 대상 |
|------|------|-----------|
| **ASTM B311** | 수중 치환법 (Archimedes) | 기공률 <2% 분말야금(PM) 소결체, 초경합금 |

> 분말 상태의 진밀도 측정에는 **가스 피크노미터(Gas Pycnometer)**를 사용하며, 이는 ASTM B923 또는 ISO 12154에 해당한다.

---

## 4. 보조 표준

| 표준 | 용도 |
|------|------|
| **ASTM B873** | B212, B329, B417에 사용되는 **밀도 컵(25 cm³)의 부피 교정** 방법 |

---

## 5. 유동성 지표 — 밀도로부터 산출

겉보기 밀도와 탭 밀도를 조합하면 분말 유동성을 정량적으로 평가할 수 있다.

### Hausner Ratio

$$HR = \frac{\rho_{tap}}{\rho_{apparent}}$$

| Hausner Ratio | 유동성 평가 |
|---------------|-------------|
| < 1.11 | Excellent (매우 우수) |
| 1.12 ~ 1.18 | Good (양호) |
| 1.19 ~ 1.25 | Fair (보통) |
| 1.26 ~ 1.34 | Passable (통과 가능) |
| 1.35 ~ 1.45 | Poor (불량) |
| > 1.46 | Very Poor (매우 불량) |

### Carr Index (Compressibility Index)

$$CI = \frac{\rho_{tap} - \rho_{apparent}}{\rho_{tap}} \times 100\%$$

| Carr Index (%) | 유동성 평가 |
|----------------|-------------|
| < 10 | Excellent |
| 11 ~ 15 | Good |
| 16 ~ 20 | Fair |
| 21 ~ 25 | Passable |
| 26 ~ 31 | Poor |
| > 32 | Very Poor |

---

## 6. 대응 국제 표준 (ISO)

| ASTM | ISO | 측정 항목 |
|------|-----|-----------|
| B212 (Hall Funnel 겉보기밀도) | **ISO 3923-1** | Apparent Density (Hall) |
| B329 (Scott 겉보기밀도) | **ISO 3923-2** | Apparent Density (Scott) |
| B527 (탭 밀도) | **ISO 3953** | Tap Density |
| B213 (유동속도, Hall) | **ISO 4490** | Flow Rate |
| B964 (유동속도, Carney) | — | Flow Rate (Carney) |

---

## 7. 전체 표준 관계도

```
┌─────────────────────────────────────────────────────────┐
│                   금속 분말 물성 시험                      │
├─────────────┬──────────────┬────────────────────────────┤
│  유동 속도    │  겉보기 밀도   │  탭 밀도                   │
│             │              │                            │
│  B213(Hall) │  B212(Hall)  │  B527                      │
│  B964(Carney)│ B417(Carney) │  (ISO 3953)                │
│  (ISO 4490) │  B329(Scott) │                            │
│             │  B703(Arnold)│                            │
│             │  (ISO 3923)  │                            │
├─────────────┴──────────────┴────────────────────────────┤
│  보조: B873 (밀도 컵 부피 교정)                            │
│  유동성 지표: Hausner Ratio, Carr Index                    │
│  진밀도: B311 (소결체), B923 / ISO 12154 (가스 피크노미터)   │
└─────────────────────────────────────────────────────────┘
```

---

## 8. 실험 설계 권장 조합

현재 설계 중인 **관직경별 유동 특성 측정 실험**과 연계 시:

| 측정 항목 | 적용 표준 | 장비 | 목적 |
|-----------|-----------|------|------|
| 유동 속도 | **B213** | Hall Flowmeter | 기본 유동성 정량화 |
| 겉보기 밀도 | **B212** | Hall Funnel + 25 cm³ 컵 | 자연 충전 밀도 |
| 탭 밀도 | **B527** | 탭 밀도 시험기 | 최밀 충전 밀도 |
| → Hausner Ratio | B212 + B527 산출 | 계산 | 유동성 종합 지표 |
| → Carr Index | B212 + B527 산출 | 계산 | 압축성 지표 |

> **B213 (유동속도) + B212 (겉보기밀도) + B527 (탭 밀도)** 3종 세트가 분말 유동성 평가의 기본 조합이다.

---

## 9. 참고 자료

- [ASTM B212 - Apparent Density (Hall)](https://store.astm.org/standards/b212)
- [ASTM B417 - Apparent Density (Carney)](https://store.astm.org/b0417-22.html)
- [ASTM B329 - Apparent Density (Scott)](https://www.astm.org/DATABASE.CART/HISTORICAL/B329-06.htm)
- [ASTM B527 - Tap Density](https://store.astm.org/b0527-22.html)
- [ASTM B703 - Apparent Density (Arnold)](https://store.astm.org/b0703-21.html)
- [ASTM B873 - Density Cup Volume](https://store.astm.org/b0873-23.html)
- [ASTM B311 - PM Density (Archimedes)](https://www.astm.org/b0311-22.html)
- [ASTM D7481 - Loose/Tapped Bulk Density](https://store.astm.org/d7481-18.html)
- [Microtrac - Powder Characterization ASTM Standards](https://www.microtrac.com/applications/powder-characterization-astm-standards/)

---

## 관련 문서

- [[ASTM B213 비교]] — 유동속도 표준 버전별 비교
- [[파우더 물성 분석 실험 설계]] — 실험 설계 원본

---

> **작성일**: 2026-02-12
> **참고**: ASTM 표준 원문은 저작권 보호 대상이므로, 정확한 세부 수치는 ASTM International에서 구매한 원문을 확인할 것.
