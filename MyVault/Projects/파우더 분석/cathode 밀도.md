# 배터리 Cathode 전극 파우더 밀도 측정 — 적용 가능 표준 및 방법

> 리튬이온 배터리 양극(cathode) 활물질은 금속 산화물 분말이므로,
> 기존 금속 분말 물성 ASTM 표준을 **직접 또는 응용하여** 적용할 수 있다.

---

## 1. Cathode 물질별 밀도 참고값

| 물질 | 화학식 | 이론밀도 (g/cm³) | 탭밀도 (g/cm³) | 압축밀도 (g/cm³) | D50 (μm) |
|------|--------|:----------------:|:--------------:|:----------------:|:--------:|
| **LCO** | LiCoO₂ | 5.06 | 2.8~3.0 | 4.0~4.2 | 8~15 |
| **NCM111** | LiNi₁/₃Co₁/₃Mn₁/₃O₂ | 4.70 | 2.0~2.4 | 3.3~3.6 | 8~12 |
| **NCM523** | LiNi₀.₅Co₀.₂Mn₀.₃O₂ | 4.65 | 2.2~2.6 | 3.4~3.7 | 8~13 |
| **NCM622** | LiNi₀.₆Co₀.₂Mn₀.₂O₂ | 4.63 | 2.3~2.7 | 3.5~3.8 | 10~15 |
| **NCM811** | LiNi₀.₈Co₀.₁Mn₀.₁O₂ | 4.78 | 2.5~2.9 (SC) | 3.6~3.9 | 3~5(SC), 10~15(PC) |
| **NCA** | LiNi₀.₈Co₀.₁₅Al₀.₀₅O₂ | 4.45 | ~2.5 | ~3.5 | 10~15 |
| **LFP** | LiFePO₄ | 3.57 | 0.9~1.3 | 2.3~2.5 | 1~5 |
| **LMO** | LiMn₂O₄ | 4.28 | 1.8~2.2 | 3.0~3.3 | 10~20 |
| **LMFP** | LiMn_xFe_(1-x)PO₄ | 3.4~3.6 | 1.0~1.4 | 2.2~2.5 | 1~5 |

> SC = Single Crystal(단결정), PC = Polycrystalline(다결정)
> 값은 제조사/합성 조건에 따라 변동. 참고용 대표값임.

---

## 2. 밀도 유형별 적용 표준

### 2.1 겉보기 밀도 (Apparent Density)

분말을 자유 낙하시켜 자연 충전 상태의 밀도를 측정.

| 표준 | 장비 | Cathode 적용성 | 비고 |
|------|------|:--------------:|------|
| **ASTM B212** | Hall Funnel (2.54mm) | **△ 제한적** | NCM/NCA 같은 구형 입자(10~15μm)는 가능. LFP(1~5μm)는 미세분말이라 유동 불가 가능성 높음 |
| **ASTM B417** | Carney Funnel (5.08mm) | **○ 양호** | Hall Funnel로 유동 불가 시 대안. LFP 등 미세분말에 적합 |
| **ASTM B329** | Scott Volumeter | **◎ 우수** | 배플 분산 방식이므로 유동성 불문. 모든 cathode 분말 적용 가능 |
| **ASTM B703** | Arnold Meter | **○ 양호** | 자동화 가능. 단, 타 표준 대비 ~0.2 g/cm³ 높게 산출 |

> **권장**: Cathode 분말은 유동성이 금속 분말보다 낮으므로 **B329(Scott)** 또는 **B417(Carney)** 우선 적용.

### 2.2 탭 밀도 (Tap Density) ⭐ 핵심 측정 항목

양극 활물질의 **체적 에너지 밀도**를 좌우하는 가장 중요한 분말 물성.

| 표준 | 장비 | Cathode 적용성 | 핵심 조건 |
|------|------|:--------------:|-----------|
| **ASTM B527** | 탭 밀도 시험기 | **◎ 직접 적용** | 시료 50~100 g, 100 mL(또는 25 mL) 실린더. 낙하 3 mm, 200 tap/min, 8분 |
| **ISO 3953** | 탭 밀도 시험기 | **◎ 직접 적용** | ASTM B527과 대응. 100 mL 또는 25 mL 실린더 |
| **ASTM D7481** | 메스실린더 | **○ 대안** | Loose + Tapped 동시 측정. 비금속 분말용이나 cathode 분말에도 활용 가능 |

> **업계 실무**: Cathode 활물질 QC에서 **ASTM B527 (탭밀도)**이 가장 널리 사용됨.
> 탭밀도가 높을수록 → 전극 로딩 밀도 ↑ → 체적 에너지 밀도 ↑

### 2.3 진밀도 / 골격밀도 (True / Skeletal Density)

기공을 제외한 분말 자체의 밀도. 전극 기공률 계산의 기준값.

| 표준 | 방법 | Cathode 적용성 | 비고 |
|------|------|:--------------:|------|
| **ASTM B923** | He/N₂ 가스 피크노미터 | **◎ 직접 적용** | 헬륨 가스가 미세 기공까지 침투하여 정확한 골격밀도 측정. Cathode 분말 분석에 최적 |
| **ISO 12154** | 가스 피크노미터 | **◎ 직접 적용** | ASTM B923과 대응 국제 표준 |

> **핵심 용도**: 진밀도 → 전극 코팅 후 **기공률(porosity)** 계산에 필수
> $$\text{Porosity} = 1 - \frac{\rho_{electrode}}{\rho_{true}} \times 100\%$$

### 2.4 압축밀도 (Compaction Density) ⭐ 배터리 특화

분말에 압력을 가한 후의 밀도. **캘린더링(calendering)** 공정 설계의 핵심 지표.

| 표준/방법 | 장비 | 적용 | 비고 |
|-----------|------|------|------|
| **GB/T 24533-2019** (부록 L) | 수동 정제기 + 하중 | **◎ 배터리 업계 표준** | 가압법/감압법. 10~200 MPa 범위, 10 MPa 간격 |
| **IEST 압축밀도 분석기** | 자동 분석 장비 | **◎ 자동화** | 가압 상태(Lc) 및 감압 후(Lr) 두께 측정 |

#### 압축밀도 측정 조건 (GB/T 24533 기준)

```
압력 범위: 10 ~ 200 MPa (10 MPa 간격)
가압 유지: 10초
감압 목표: 3 MPa
감압 유지: 10초
측정값: 가압 시 두께(Lc), 감압 후 두께(Lr)
```

#### 재료별 압축밀도 및 리바운드 특성

```
압축밀도 순서:  LCO > NCM > LFP
리바운드 크기:  NCM > LCO > LFP  (LFP가 리바운드 최소)
```

---

## 3. 유동성 평가 — Dry Electrode 공정과의 연관

### 3.1 기존 Slurry 공정 vs Dry Electrode 공정

| 항목 | Slurry 공정 | Dry Electrode 공정 |
|------|-------------|-------------------|
| 분말 유동성 중요도 | 낮음 (용매에 분산) | **매우 높음** (분말 직접 처리) |
| 관련 표준 | 슬러리 점도/레올로지 | **ASTM B213, B212, B417** |
| 핵심 지표 | 점도, 고형분 함량 | Hausner Ratio, Carr Index, 유동속도 |

### 3.2 적용 가능한 유동성 표준

| 표준 | 방법 | Dry Electrode 적용성 |
|------|------|:-------------------:|
| **ASTM B213** | Hall Funnel 유동속도 | △ (NCM 구형 입자만 가능) |
| **ASTM B964** | Carney Funnel 유동속도 | ○ (미세 분말 대응) |
| **Hausner Ratio** | B212(or B417) + B527 산출 | **◎ 핵심 지표** |
| **Carr Index** | B212(or B417) + B527 산출 | **◎ 핵심 지표** |

### 3.3 Cathode 분말의 유동성 특성

| 물질 | 형태 | D50 | 예상 유동성 | Hall Funnel 통과 |
|------|------|-----|-----------|:---------------:|
| NCM (다결정) | 구형 이차입자 | 10~15 μm | 양호~보통 | ○ 가능 |
| NCM (단결정) | 각형 단결정 | 3~5 μm | 보통~불량 | △ 어려움 |
| NCA | 구형 이차입자 | 10~15 μm | 양호~보통 | ○ 가능 |
| LFP | 불규칙/판상 | 1~5 μm | 불량 | ✕ 불가 |
| LMO | 다면체 | 10~20 μm | 양호 | ○ 가능 |

---

## 4. 추가 물성 측정 표준

| 측정 항목 | ASTM 표준 | 대응 ISO | Cathode 적용 |
|-----------|-----------|----------|:----------:|
| **비표면적 (BET)** | ASTM B922 | ISO 9277 | ◎ |
| **입도 분포 (PSD)** | ASTM B822 (레이저 회절) | ISO 13320 | ◎ |
| **수분 함량** | ASTM E1868 (Karl Fischer) | — | ◎ |
| **안식각 (Angle of Repose)** | ASTM C1444 | ISO 4324 | ○ |

---

## 5. 종합 — Cathode 분말 QC 측정 항목 및 표준 매핑

| 순위 | 측정 항목 | 적용 표준 | 중요도 | 목적 |
|:----:|-----------|-----------|:------:|------|
| 1 | **탭 밀도** | ASTM B527 / ISO 3953 | ★★★ | 체적 에너지 밀도 예측 |
| 2 | **진밀도** | ASTM B923 / ISO 12154 | ★★★ | 전극 기공률 계산 기준 |
| 3 | **압축밀도** | GB/T 24533 부록 L | ★★★ | 캘린더링 공정 설계 |
| 4 | **입도 분포** | ASTM B822 / ISO 13320 | ★★☆ | 충전 효율, 전극 균일성 |
| 5 | **비표면적** | ASTM B922 / ISO 9277 | ★★☆ | 전해액 반응성, 코팅량 |
| 6 | **겉보기 밀도** | ASTM B329(Scott) / B417(Carney) | ★★☆ | 분말 핸들링, 호퍼 설계 |
| 7 | **유동성** | Hausner Ratio (B212+B527) | ★☆☆→★★★* | Dry electrode 시 핵심 |
| 8 | **수분** | ASTM E1868 | ★★☆ | 전기화학 성능 보증 |

> *Dry electrode 공정 채택 시 유동성 중요도가 ★★★으로 상승

---

## 6. 밀도 간 관계 및 전극 설계 연결

```
┌──────────────────────────────────────────────────────────────┐
│                    Cathode 분말 밀도 체계                      │
│                                                              │
│   겉보기밀도 < 탭밀도 < 압축밀도 < 진밀도(이론밀도)              │
│   (자유충전)  (탭핑)   (가압)      (기공 0%)                    │
│                                                              │
│   예) NCM622:  ~1.5  <  ~2.5  <  ~3.6  <  4.63 g/cm³        │
│                                                              │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│   전극 설계 연결:                                              │
│                                                              │
│   탭밀도 → 전극 로딩량(mg/cm²) 예측                            │
│   압축밀도 → 캘린더링 목표 두께/밀도 설정                        │
│   진밀도 → 기공률 = 1 - (전극밀도/진밀도)                       │
│   기공률 목표: 18~35% (캘린더링 후)                              │
│                                                              │
│   Hausner Ratio = 탭밀도/겉보기밀도 → 유동성 판정                │
│   Carr Index = (탭밀도-겉보기밀도)/탭밀도 × 100% → 압축성 판정   │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## 7. 실험 설계와의 연관

현재 설계 중인 **관직경별 유동 특성 측정 실험**은 다음과 같이 cathode 분말에 응용 가능:

1. **다양한 오리피스 직경**에서의 유동 특성 → cathode 분말의 **임계 유동 직경** 도출
2. 로드셀 기반 연속 질량 측정 → **유동속도의 시간 변화** 관찰 (아칭/브리징 현상 감지)
3. 분말 마찰계수 → **DEM 시뮬레이션** 입력 파라미터로 활용
4. Dry electrode 공정의 **분말 공급(feeding) 설계**에 직접 반영 가능

---

## 8. 참고 자료

- [ASTM B527 - Tap Density](https://store.astm.org/b0527-22.html)
- [ASTM B923 - Skeletal Density (Pycnometer)](https://www.astm.org/b0923-21.html)
- [ASTM B212 - Apparent Density (Hall)](https://store.astm.org/standards/b212)
- [ASTM B417 - Apparent Density (Carney)](https://store.astm.org/b0417-22.html)
- [ASTM B329 - Apparent Density (Scott)](https://www.astm.org/DATABASE.CART/HISTORICAL/B329-06.htm)
- [ASTM B922 - Specific Surface Area (BET)](https://www.astm.org/Standards/B922.htm)
- [Bettersize - Improving Tapped Density of Cathode Material](https://www.bettersizeinstruments.com/learn/knowledge-center/improving-the-tapped-density-of-the-cathode-material-to-make-a-lithium-ion-battery-hold-more-energy/)
- [AZoM - Improving Li-Ion Batteries through Tapped Density](https://www.azom.com/article.aspx?ArticleID=21056)
- [IEST - Compaction Density Characterization](https://iestbattery.com/case/characterization-method-of-compaction-density/)
- [TA Instruments - NMC Dry Cathode Powder Flow Properties](https://www.tainstruments.com/applications-notes/shear-and-flow-properties-of-an-nmc-based-dry-cathode-powder-rh136/)
- [Battery Design - Calendering](https://www.batterydesign.net/manufacture/cell-manufacturing/battery-cell-manufacturing-process/electrode-manufacturing/calendaring/)

---

## 관련 문서

- [[powder 밀도]] — ASTM 분말 밀도 표준 전체 체계
- [[ASTM B213 비교]] — 유동속도 표준 버전별 비교
- [[파우더 물성 분석 실험 설계]] — 실험 설계 원본

---

> **작성일**: 2026-02-12
> **참고**: 밀도 참고값은 제조사/합성 조건에 따라 변동될 수 있으며, 정확한 값은 해당 물질의 CoA(Certificate of Analysis) 확인 필요.
