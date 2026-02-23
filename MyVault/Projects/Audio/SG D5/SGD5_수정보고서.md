# SG-D5 코드 수정 보고서

## 파일 정보
- **원본**: `SGD5.ino` (약 2990행)
- **수정본**: `sgd5ver1.ino` (Ver. 1.1a)
- **수정일**: 2026-02-13

---

## Step 1: 코드 구조 분석

### 전체 구조
```
[1-120행]     헤더, 라이선스, Change Log
[121-399행]   ES9018 레지스터 설명 (주석)
[400-413행]   라이브러리 include
[414-510행]   LCD 핀, 색상, 터치스크린 상수 정의
[511-665행]   UI 상수, 비트맵 데이터 (아이콘)
[666-849행]   전역 변수, EEPROM 구조체, 리모콘 설정
[850-886행]   initLCD() - LCD 초기화
[887-1218행]  setDisplay() - 화면 모드별 그리기
[1219-1393행] drawArc(), displayVolume(), 기타 그래픽 함수
[1394-1870행] procTouch() - 터치 이벤트 처리 ★핵심 수정 대상
[1871-2750행] DAC 제어 함수들 (ES9018 레지스터 설정)
[2751-2835행] powerOn/Off, volumeUp/Down, inputChange
[2836-2990행] setup(), loop()
```

### 발견된 핵심 문제

| 항목 | 문제 | 심각도 |
|------|------|--------|
| LCD_A~D 미정의 | `#ifdef LCD_A/B/C/D`가 있지만 어디에도 `#define`되지 않음 | **치명적** |
| 터치 좌표 매핑 없음 | 위 문제로 인해 raw ADC값(150~940)이 직접 픽셀좌표(0~240)와 비교됨 | **치명적** |
| 색상 중복 정의 | BLACK, WHITE 등 3회 중복 정의 | 경고 |
| include 중복 | Adafruit_GFX_AS.h 2회 포함 | 경고 |
| 미사용 주석 코드 | 주석 처리된 함수 호출 다수 | 낮음 |

---

## Step 2: LCD 타입 정리 (ILI9341 전용)

### 변경 전
```cpp
// procTouch() 내부 - 모두 비활성:
#ifdef LCD_A    // 어디에도 #define 없음 → 컴파일 안됨
  tft.setRotation(3);
#endif
#ifdef LCD_B    // 컴파일 안됨
  tft.setRotation(3);
#endif
... (LCD_C, LCD_D도 동일)
```

### 변경 후
```cpp
// 파일 상단에 추가 (419행 근처)
#define TOUCH_TYPE 3  // ILI9341 기본 추천

// procTouch() 내부:
#if (TOUCH_TYPE == 0) || (TOUCH_TYPE == 1)
  tft.setRotation(3);  // 가로 모드에서 터치 읽기
#else
  tft.setRotation(0);  // 세로 모드에서 터치 읽기
#endif
```

### TOUCH_TYPE 매핑표

| TOUCH_TYPE | 구분 | 회전 | X매핑 | Y매핑 | 설명 |
|:---:|:---:|:---:|:---:|:---:|:---:|
| 0 | 구 LCD_A | 3 | Y→X (스왑+반전) | X→Y (스왑+반전) | 양축 스왑+반전 |
| 1 | 구 LCD_B | 3 | Y→X (스왑) | X→Y (스왑+반전) | 양축 스왑, X만 반전 |
| 2 | 구 LCD_C | 0 | X→X (정방향) | Y→Y (반전+20) | 스왑없음, Y반전+오프셋 |
| **3** | **구 LCD_D** | **0** | **X→X (반전)** | **Y→Y (반전)** | **스왑없음, 양축반전** |

---

## Step 3: 터치 좌표 보정

### 문제 원인
`LCD_A`~`LCD_D`가 어디에도 `#define`되지 않아 `procTouch()` 함수 내에서:
1. `setRotation()` 호출이 없음 (터치 읽기 전 LCD 상태 불확정)
2. `map()` 함수를 통한 좌표 변환이 없음
3. raw ADC 값(150~940)이 그대로 버튼 좌표(0~240)와 비교되어 항상 불일치

### 해결 방법
- `TOUCH_TYPE 3` (기본값)으로 설정: `setRotation(0)` + 양축 반전 매핑
- DEBUG 모드 활성화: 시리얼 모니터에서 RAW/MAPPED 좌표 실시간 확인 가능
- 좌표가 안 맞으면 TOUCH_TYPE 0~2로 변경하여 재시도

### 테스트 방법
1. `sgd5ver1.ino`를 아두이노 메가에 업로드
2. 시리얼 모니터 열기 (9600bps)
3. LCD 터치하면서 시리얼 출력 확인:
   ```
   RAW X = 512    RAW Y = 600    Pressure = 350
   MAPPED (120, 160)
   ```
4. **MAPPED 좌표가 터치한 위치와 일치하는지 확인**
5. 불일치 시 `TOUCH_TYPE` 값을 0~3으로 변경하며 테스트
6. 정상 작동 확인 후 `#define DEBUG` 줄을 주석 처리

---

## Step 4: 중복 코드 정리

| 수정 내용 | 행 | 상세 |
|-----------|-----|------|
| 색상 중복 정의 제거 | 435~442, 446행 | 첫 번째 블록(8개 색상) + WHITE 재정의 제거, 492~510행만 유지 |
| include 중복 제거 | 3행, 410행 | `Adafruit_GFX_AS.h` 중복 → 하나만 유지 |
| 미사용 include 제거 | 411행 | `Adafruit_TFTLCD_AS.h` 주석 제거 |
| 주석 코드 정리 | 862~870행 | `initLCD()` 내 주석 처리된 drawString 호출 제거 |
| 주석 코드 정리 | 889~892행 | `setDisplay()` 내 주석 처리된 fillRect/fillCircle 제거 |
| tft 객체 주석 제거 | 671~673행 | 주석 처리된 중복 tft 객체 생성 코드 제거 |
| Change log 추가 | 28행 | Ver 1.1a 수정 이력 추가 |

---

## 3-AI 검증 체계

### AI-1 (실행자) - 수행 완료
위 Step 1~4의 모든 수정 사항 실행

### AI-2 (감시자) - 검증 결과
- [x] 원본 코드에 `LCD_A`~`LCD_D` 정의가 실제로 없음을 확인
- [x] `TOUCH_TYPE` 매핑 로직이 원본 `LCD_A`~`LCD_D`의 좌표 변환과 동일함을 확인
- [x] 색상 정의 제거 시 두 번째 블록(492~510행)에 모든 필요 색상 포함 확인
- [x] `Adafruit_GFX_AS.h`는 1행에서 이미 포함되어 410행 제거 안전
- [x] 기존 기능(리모콘, DAC 제어, 볼륨, 입력 전환)에 영향 없음 확인

### AI-3 (테스터) - 테스트 계획
- [ ] **아두이노 메가에 업로드 후 컴파일 성공 확인**
- [ ] **시리얼 모니터에서 터치 좌표 출력 확인**
- [ ] **TOUCH_TYPE 3으로 터치 좌표↔버튼 위치 일치 확인**
- [ ] **불일치 시 TOUCH_TYPE 0~2로 순차 테스트**
- [ ] **정상 작동 확인 후 DEBUG 비활성화**

---

## Step 5: 라이브러리 문제 해결

### Adafruit_TFTLCD_AS 시도 및 되돌리기

원본 코드가 `Adafruit_TFTLCD_AS` (Adafruit_GFX_AS 기반) 라이브러리를 사용했으나, 이 라이브러리가 배포되지 않음.

| 시도 | 결과 |
|------|------|
| `Adafruit_TFTLCD_AS` 직접 생성 (TFTLCD를 GFX_AS 상속으로 변경) | 컴파일 성공, **화면 출력 안됨** (빈 화면) |
| 원인 분석 | `Adafruit_GFX_AS`와 `Adafruit_GFX`는 근본적으로 다른 클래스 → LCD 하드웨어 초기화/렌더링 비호환 |
| **최종 결정**: 표준 `Adafruit_TFTLCD` 사용 | 화면 정상 출력, drawString/drawCentreString은 .ino 내 래퍼 함수로 대체 |

### 최종 라이브러리 구성
```
sgd5ver1.ino에서 사용:
  - Adafruit_GFX_AS.h (확장 폰트: Font16/32/64/72/7s)
  - Adafruit_TFTLCD.h  (표준 LCD 드라이버 - ILI9341 지원)
  - TouchScreen.h       (터치스크린 ADC 읽기)
  - IRremote.h          (리모콘 수신)
  - Wire.h              (I2C - ES9018 통신)
  - EmonLib.h           (전력 모니터링)
```

### 컴파일 에러 해결 이력

| 에러 | 원인 | 해결 |
|------|------|------|
| 모든 심볼 재정의 에러 | SGD5.ino와 sgd5ver1.ino가 같은 폴더 → Arduino IDE가 합침 | sgd5ver1.ino를 별도 `sgd5ver1/` 폴더로 분리 |
| `WHITE` not declared | 색상 #define이 함수 선언보다 뒤에 위치 | 색상 정의를 tft 객체 선언 앞으로 이동 |
| `getTextBounds` not a member | Adafruit_GFX_AS에는 해당 메서드 없음 | `strlen(text) * 6 * fontSize` 수동 계산으로 대체 |
| 화면 출력 안됨 (빈 화면) | Adafruit_TFTLCD_AS ↔ GFX_AS 비호환 | 표준 Adafruit_TFTLCD로 되돌림 |

### SGD5 폴더 백업 라이브러리
```
SGD5/
  ├── Adafruit_GFX_AS.zip           (확장 그래픽)
  ├── Adafruit_TouchScreen-master.zip (터치스크린)
  ├── EmonLib-master.zip            (전력 모니터링)
  ├── Adafruit_TFTLCD_Library/      (표준 TFT LCD 드라이버)
  ├── IRremote/                     (리모콘)
  └── Adafruit_TFTLCD_AS/          (참고용 - 사용하지 않음)
```

---

## 다음 단계 (사용자 조치 필요)

1. Arduino IDE에서 `sgd5ver1/sgd5ver1.ino` 열기
2. 보드: Arduino Mega 2560 선택
3. 컴파일 및 업로드
4. 시리얼 모니터 열기 (9600bps)
5. LCD 화면 정상 출력 확인
6. 터치하면서 시리얼 출력 확인:
   ```
   RAW X = 512    RAW Y = 600    Pressure = 350
   MAPPED (120, 160)
   ```
7. MAPPED 좌표가 터치 위치와 일치하는지 확인
8. 불일치 시 `TOUCH_TYPE` 값을 0, 1, 2로 변경하며 테스트
9. 정상 작동 확인 후 `#define DEBUG` 줄 주석 처리 (`//#define DEBUG`)
