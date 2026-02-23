# Cathode 전극 분말 유동속도 측정 — ASTM B213 기반 적용 방법

> ASTM B213(Hall Flowmeter)은 **금속 분말** 대상 표준이나,
> 양극 활물질(NCM, NCA, LFP 등)은 금속 산화물 분말이므로 **동일 장비 및 절차를 응용**할 수 있다.
> 본 문서는 [[ASTM B213 비교]]를 기반으로 cathode 전극 분말에의 적용 가능성을 정리한다.

---

## 1. ASTM B213 핵심 사양 요약 (→ [[ASTM B213 비교]] 참조)

| 항목 | Hall Flowmeter (B213) | Carney Funnel (B964) |
|------|:---------------------:|:--------------------:|
| 오리피스 직경 | 2.54 mm (0.1 inch) | 5.08 mm (0.2 inch) |
| 콘 각도 | 60° | 60° |
| 시료 질량 | 50 g | 50 g |
| 측정값 | 통과 시간 (s) | 통과 시간 (s) |
| 적용 대상 | 자유 유동 분말 | 비유동 분말 (Hall 통과 불가 시) |
| 교정 | 에머리 분말 40±0.5 s | 별도 교정 |
| 최신 버전 | B213-25 (2025) | B964-25 (2025) |
| 대응 ISO | ISO 4490 | — |

> **B213-11 이후**: Hall Funnel과 Carney Funnel이 별도 표준으로 분리됨
> **단위 체계**: B213-20 기준 inch-pound 기본 (SI 참고)

---

## 2. Cathode 분말별 Hall Funnel 적용성 평가

### 2.1 물질별 유동 특성

| 물질 | 형태 | D50 (μm) | 겉보기밀도 (g/cm³) | Hall Funnel (2.54mm) | Carney Funnel (5.08mm) |
|------|------|:--------:|:-----------------:|:--------------------:|:---------------------:|
| **NCM (다결정)** | 구형 이차입자 | 10~15 | 1.3~1.8 | **○ 유동 가능** | ○ |
| **NCM (단결정)** | 각형 단결정 | 3~5 | 1.0~1.5 | **△ 유동 어려움** | ○ |
| **NCA** | 구형 이차입자 | 10~15 | 1.3~1.8 | **○ 유동 가능** | ○ |
| **LCO** | 판상/구형 | 8~15 | 1.5~2.0 | **○ 유동 가능** | ○ |
| **LFP** | 불규칙/판상 | 1~5 | 0.5~0.8 | **✕ 유동 불가** | △~○ |
| **LMO** | 다면체 | 10~20 | 1.2~1.6 | **○ 유동 가능** | ○ |
| **LMFP** | 불규칙 | 1~5 | 0.5~0.9 | **✕ 유동 불가** | △ |

### 2.2 유동 가능/불가 판정 기준

```
Hall Funnel(2.54mm) 유동 가능 조건:
├─ D50 > ~8 μm (대략적 하한)
├─ 구형 또는 준구형 입자 형태
├─ 겉보기밀도 > ~1.0 g/cm³
└─ 응집(cohesion)이 낮은 분말

Hall Funnel 유동 불가 시:
├─ ASTM B964 (Carney Funnel, 5.08mm) 사용
├─ 그래도 유동 불가 시 → 동적 유동성 시험법(FT4 등) 전환
└─ "유동 불가(No Flow)" 자체가 의미있는 결과로 보고
```

---

## 3. 표준 시험법 선택 가이드

### 3.1 깔때기식 유동속도 (ASTM B213 / B964 계열)

| 단계 | 방법 | 표준 | Cathode 적용 |
|:----:|------|------|:----------:|
| 1차 | Hall Funnel (2.54mm) | **ASTM B213-20** / ISO 4490 | NCM(다결정), NCA, LCO, LMO |
| 2차 | Carney Funnel (5.08mm) | **ASTM B964-16** | NCM(단결정), LFP(조건부) |
| 보고 | "No Flow" 기록 | B213/B964 | LFP, LMFP 등 미세분말 |

#### Hall Funnel 시험 절차 (B213 기반, cathode 적용)

```
1. 깔때기 교정: 에머리 분말로 40±0.5 s 확인
2. 시료 준비: 50.0±0.1 g 칭량
3. 오리피스를 손가락으로 막고 시료 투입
4. 손가락 제거와 동시에 타이머 시작
5. 마지막 분말이 떨어질 때 타이머 정지
6. 3회 반복, 평균값 보고
7. 유동 불가 시 "No Flow" 기록 → B964로 전환
```

> **주의**: ASTM B213은 "metal powders"를 대상으로 명시하므로,
> cathode 분말(금속 산화물)에 적용 시 보고서에 **"B213 절차 준용"** 또는
> **"ISO 4490 참조"**로 명기하는 것이 적절함.

### 3.2 동적 유동성 시험 (FT4 Powder Rheometer 계열) ⭐ Dry Electrode 핵심

깔때기식 시험이 불가능하거나 더 정밀한 유동 특성이 필요할 때 사용.

| 표준                | 시험 항목  | 측정 파라미터                                               |    Cathode 적용    |
| ----------------- | ------ | ----------------------------------------------------- | :--------------: |
| **ASTM D8328-24** | 동적 유동성 | BFE(기본유동에너지), SE(비에너지), SI(안정성), FRI(유동속도지수), CI(압축성) | **◎ 모든 cathode** |
| **ASTM D7891-15** | 전단 시험  | 응집력(Cohesion), 비폐쇄항복강도(UYS), 유동함수(ff), 내부마찰각          | **◎ 모든 cathode** |
| **ASTM D8327-24** | 투과성    | 압력강하, 가스투과율                                           | **◎ 모든 cathode** |

#### FT4 주요 측정 파라미터 해설

| 파라미터 | 약어 | 의미 | Cathode 해석 |
|----------|------|------|-------------|
| Basic Flowability Energy | **BFE** | 기본 유동 에너지 (mJ) | 낮을수록 유동 용이. 분말 공급/이송 설계 기준 |
| Specific Energy | **SE** | 비에너지 (mJ/g) | 입자 간 마찰/응집 지표. 건식 전극 균일성 예측 |
| Stability Index | **SI** | 안정성 (무차원) | 1.0에 가까울수록 안정. 반복 이송 시 유동 변화 예측 |
| Flow Rate Index | **FRI** | 유동속도 의존성 | 속도에 따른 유동 변화. 라인 스피드 설계 |
| Compressibility | **CI** | 압축성 (%) | 높을수록 응집성. 호퍼/피더 설계 기준 |
| Cohesion | **C** | 응집력 (kPa) | 건식 전극 코팅 균일성의 핵심 지표 |
| Flow Function | **ff** | 유동함수 | ff>10: 자유유동, 4~10: 쉬운유동, 2~4: 응집, <2: 매우 응집 |

### 3.3 간이 유동성 지표 (Hausner Ratio / Carr Index)

밀도 측정만으로 유동성을 간접 평가. → [[powder 밀도]] 참조

| 지표 | 산출 | 필요 표준 | 장점 | 한계 |
|------|------|-----------|------|------|
| **Hausner Ratio** | 탭밀도/겉보기밀도 | B527 + B212(or B417) | 빠르고 저렴 | 동적 거동 반영 불가 |
| **Carr Index** | (탭-겉보기)/탭 × 100% | B527 + B212(or B417) | QC 스크리닝 | 벽면 마찰, 아칭 미반영 |

### 3.4 안식각 (Angle of Repose)

| 표준                       | 방법              |      Cathode 적용      |
| ------------------------ | --------------- | :------------------: |
| **ASTM C1444**           | 고정 깔때기 안식각      |          ○           |
| **ISO 4324**             | 안식각 측정          |          ○           |
| 회전 드럼 (Avalanche Tester) | 동적 안식각, 눈사태 에너지 | **◎** (연속 공정 모사에 적합) |

---

## 4. 시험법 비교 종합표

| 시험법 | 표준 | NCM(PC) | NCM(SC) | NCA | LFP | 장비 비용 | 정보량 |
|--------|------|:-------:|:-------:|:---:|:---:|:---------:|:------:|
| Hall Funnel | **B213** | ○ | △ | ○ | ✕ | 低 | 低 |
| Carney Funnel | **B964** | ○ | ○ | ○ | △ | 低 | 低 |
| Hausner/Carr | B527+B212 | ○ | ○ | ○ | ○ | 低 | 中 |
| 안식각 | C1444 | ○ | ○ | ○ | ○ | 低 | 低 |
| FT4 동적 | **D8328** | ◎ | ◎ | ◎ | ◎ | **高** | **高** |
| FT4 전단 | **D7891** | ◎ | ◎ | ◎ | ◎ | **高** | **高** |
| FT4 투과성 | **D8327** | ◎ | ◎ | ◎ | ◎ | **高** | **高** |

> PC = Polycrystalline(다결정), SC = Single Crystal(단결정)

---

## 5. 공정별 필요 유동성 시험

### 5.1 기존 Slurry 공정 (습식)

```
분말 → 용매 + 바인더 혼합 → 슬러리 → 코팅 → 건조 → 캘린더링
         ↑
    분말 유동성 중요도: ★☆☆ (슬러리 점도가 더 중요)
```

**필요 시험**: Hall/Carney 유동속도(B213/B964) + Hausner Ratio → QC 수준 충분

### 5.2 Dry Electrode 공정 (건식) ⭐

```
분말 + 바인더(PTFE) → 건식 혼합 → 피브릴화 → 캘린더링 → 전극
     ↑                    ↑              ↑
  유동성 ★★★        균일성 ★★★      압축성 ★★★
```

**필요 시험**:
| 단계 | 핵심 물성 | 권장 시험 |
|------|-----------|----------|
| 분말 공급(Feeding) | 유동속도, 안정성 | B213/B964 + D8328(BFE, SI) |
| 건식 혼합(Mixing) | 응집력, 분산성 | D7891(Cohesion, ff) |
| 피브릴화/캘린더링 | 압축성, 투과성 | D8328(CI) + D8327(투과율) |
| 최종 QC | 종합 유동성 | Hausner Ratio + Hall/Carney |

---

## 6. NMC Cathode 분말 유동성 연구 사례

### TA Instruments 연구 (NMC + Carbon Black + PVDF 건식 혼합)

| 조성 | 응집력 (kPa) | 유동함수 (ff) | 유동에너지 (mJ) | 유동성 등급 |
|------|:----------:|:----------:|:-------------:|:---------:|
| NMC + CB 3% + PVDF 3% | 높음 | <4 | 높음 | 응집 |
| NMC + CB 3% + PVDF 5% | 중간 | 4~10 | 중간 | 쉬운 유동 |
| NMC + CB 3% + PVDF 8% | 낮음 | >10 | 낮음 | 자유 유동 |

> **발견**: PVDF 바인더 함량 증가 → 유동함수(ff) 증가, 응집력 감소
> → 건식 전극 코팅 균일성 향상. 단, 바인더 과량 시 전기화학 성능 저하.

---

## 7. 현재 실험 설계와의 연결

현재 설계 중인 **관직경별 유동 특성 측정 실험**(→ [[파우더 물성 분석 실험 설계]])의 cathode 응용:

### 7.1 ASTM B213 기반 확장 실험 설계

| 요소 | B213 표준 | 확장 실험 (cathode 응용) |
|------|-----------|------------------------|
| 오리피스 | 2.54mm 고정 | **다중 직경** (2, 3, 4, 5, 8, 10mm) |
| 측정 | 50g 통과 시간 (이산적) | **로드셀 연속 질량 측정** (연속적) |
| 분석 | 유동속도 (g/s) 1개 값 | **시간-질량 곡선 기울기 변화** |
| 목표 | 유동/비유동 판정 | **임계 유동 직경** + 마찰계수 추정 |

### 7.2 실험 매트릭스 제안

```
                    오리피스 직경 (mm)
                 2.0  3.0  4.0  5.0  8.0  10.0
NCM811(PC)       △    ○    ○    ○    ○    ○
NCM811(SC)       ✕    △    ○    ○    ○    ○
NCA              △    ○    ○    ○    ○    ○
LFP              ✕    ✕    ✕    △    ○    ○
LFP+PVDF 5%     ✕    ✕    △    ○    ○    ○
LMO              ○    ○    ○    ○    ○    ○

○: 유동 예상  △: 경계  ✕: 유동 불가 예상
→ "임계 유동 직경" = △에서 ○로 전환되는 직경
```

### 7.3 DEM 시뮬레이션 연계

```
실험 결과 (임계 유동 직경, 유동속도)
    ↓
마찰계수 역산 (입자간 마찰, 입자-벽면 마찰)
    ↓
DEM 시뮬레이션 입력 파라미터
    ↓
Dry electrode 공정 최적화 (피더 설계, 호퍼 각도, 라인 속도)
```

---

## 8. 참고 자료

### ASTM 표준
- [ASTM B213-20 - Hall Flowmeter](https://store.astm.org/b0213-20.html)
- [ASTM B964-16 - Carney Funnel](https://store.astm.org/b0964-16.html)
- [ASTM D8328-24 - FT4 Dynamic Testing](https://store.astm.org/d8328-24.html)
- [ASTM D7891-15 - FT4 Shear Testing](https://store.astm.org/d7891-15.html)
- [ASTM D8327-24 - FT4 Permeability](https://store.astm.org/d8327-24.html)
- [ISO 4490:2018 - Hall Flowmeter (국제표준)](https://www.iso.org/standard/69218.html)

### 연구 자료
- [TA Instruments - NMC Dry Cathode Powder Shear & Flow](https://www.tainstruments.com/applications-notes/shear-and-flow-properties-of-an-nmc-based-dry-cathode-powder-rh136/)
- [ACS - Dry Electrode Manufacturing: Role of Powder Premixing](https://pubs.acs.org/doi/10.1021/acsaem.2c03755)
- [Micromeritics - ASTM FT4 Standards (2024)](https://micromeritics.com/press-release/astm-international-publishes-new-standards-d8328-d8327-and-d7891for-ft4-powder-rheometer-procedures/)
- [Battery Design - Calendering Process](https://www.batterydesign.net/manufacture/cell-manufacturing/battery-cell-manufacturing-process/electrode-manufacturing/calendaring/)

---

## 관련 문서

- [[ASTM B213 비교]] — B213 버전별(97/03/11/17/20) 상세 비교
- [[powder 밀도]] — 분말 밀도 측정 ASTM 표준 체계
- [[cathode 밀도]] — cathode 전극 밀도 측정 방법
- [[파우더 물성 분석 실험 설계]] — 관직경별 유동 특성 실험 설계 원본

---

> **작성일**: 2026-02-12
> **참고**: ASTM B213/B964는 "metal powders" 대상이므로, cathode 분말(금속 산화물)에 적용 시 "B213 절차 준용" 또는 "ISO 4490 참조"로 보고서에 명기할 것.
