
# SG-D5 터치 수정 작업 중간 저장

## 작업 날짜: 2026-02-20
## 상태: **PIN 7 = LCD 제어 핀 발견 (★★ 핵심 돌파구)** / procTouch() 임시 비활성화 상태 / 터치 시 화면 흰색 문제 미해결

---

## 1. 프로젝트 개요

- **목적**: SG-D5 듀얼 ES9018 DAC 컨트롤러의 LCD 모듈 교체 후 터치 기능 복원
- **하드웨어**: Arduino Mega 2560 + 2.8" TFT LCD Shield (ILI9341) + 듀얼 ES9018 DAC
- **원본 파일**: `SGD5\SGD5.ino` (~2990행)
- **수정 파일**: `sgd5ver1\sgd5ver1.ino` (Ver. 1.1a)
- **작업 지시서**: `SG D5 코딩.md`

---

## 2. 핀맵 (확정)

### LCD 제어 핀 (아날로그 핀)
```
A0 → LCD_RD
A1 → LCD_WR  ← 터치 YP (Y+ 전극) 공유
A2 → LCD_RS  ← 터치 XM (X- 전극) 공유
A3 → LCD_CS  ← 74HC245 OE 공유 (LOW=활성화)
A4 → LCD_RESET
```

### LCD 데이터 버스 (74HC245 경유)
```
22 → LCD_D0
23 → LCD_D1
24 → LCD_D2
25 → LCD_D3
26 → LCD_D4
27 → LCD_D5
28 → LCD_D6  ← 터치 XP (X+ 전극) 공유
29 → LCD_D7  ← 터치 YM (Y- 전극) 공유
```

### ★★ 핵심 발견: PIN 7 (2026-02-20)
```
pin 7 → 74HC245 DIR 핀 (추정) 또는 LCD 관련 제어 핀
         HIGH 필수! LOW이면 LCD 통신 불가 → 흰 화면
```
- **YM=7 코드 업로드 시** ts.getPoint()가 pin 7을 LOW로 구동 → LCD 망가짐
- **YM=29 원복 후에도** pin 7이 INPUT(플로팅)으로 남아 LCD 계속 불량
- **setup() 맨 앞에 pin 7=OUTPUT HIGH 추가** → 검정 화면 복원 성공 ✓
- 74HC245: U2 (레벨시프터), U3 (전압 레귤레이터) - 쉴드에 탑재

### 터치 4선식 핀 (최종)
```
YP = A1  (물리적 Y 전극 / LCD_WR 공유)
XM = A2  (물리적 X 전극 / LCD_RS 공유)
XP = 28  (물리적 X 전극 / 74HC245 경유)
YM = 29  (물리적 Y 전극 / 74HC245 경유)
```

### 기타 핀
```
_RESET_9018 = 10  (ES9018 DAC 리셋)
_POWER      = ?   (DAC 전원 제어)
RECV_PIN    = 11  (IR 수신기)
_DSD_PLAY   = ?   (DSD 재생 신호)
```

---

## 3. 이전 작업 완료 내역 (2026-02-19까지)

### 완료된 수정
- **#ifdef LCD_A/B/C/D 버그 수정**: TOUCH_TYPE 0~3 방식으로 교체
- **라이브러리**: Adafruit_TFTLCD_AS → Adafruit_TFTLCD (표준) 사용
- **readTouchOnce()**: LCD_CS HIGH + DDRA=0x00 + 아날로그 핀 INPUT 설정
- **dualCheckMillis**: ES9018 dual chip 확인을 10초 주기 별도 타이머로 분리
- **핀 스왑 원복**: YP=A1, XM=A2, YM=29, XP=28 (원래값 복원)
- **inputChange() 버그**: Serial.begin(9600) 제거
- **임계값**: p.x >= 935 (비터치 시 935~1009)
- **touchCount >= 5**: 연속 5회 확인 (손 뗄 때 노이즈 제거)
- **3초 가드**: millis() < 3000이면 procTouch() 조기 리턴 (부팅 직후 가짜 터치 방지)

---

## 4. 오늘(2026-02-20) 발견 및 작업

### 4-1. 흰 화면의 근본 원인 규명

**증상 흐름**:
1. YM=7 코드 업로드 → 흰 화면 발생
2. YM=29 원복 후에도 흰 화면 지속 → 하드웨어/핀 상태 문제

**Serial DBG 출력 확인**:
```
DBG: tft.begin done    ← LCD 초기화 완료
DBG: fillScreen BLACK  ← BLACK 픽셀 전송 완료
DBG: fillScreen done
DBG: setup COMPLETE
```
→ `fillScreen(BLACK)`은 실행됐지만 화면은 흰색 → **LCD 통신 자체가 안 되는 것**

**원인 분석**:
- IRremote 경고: "using old version 2.0 code" (IRremote 3.x 라이브러리와 구 API 불일치)
- 부팅 직후 `px=11~12` (가짜 터치) → `powerOn()` 트리거 → 재시작 루프
- 이것과 별개로 **pin 7 문제**가 핵심

### 4-2. ★★ PIN 7 = LCD 핵심 제어 핀 발견

**테스트**: setup() 맨 앞에 `pinMode(7, OUTPUT); digitalWrite(7, HIGH);` 추가

**결과**: 검정 화면 복원 성공!

**결론**: pin 7이 74HC245의 DIR 핀으로 추정됨
- DIR=HIGH: 데이터 흐름 A→B (Arduino → LCD) ← 올바른 방향
- DIR=LOW: 데이터 흐름 B→A (LCD → Arduino) ← LCD에 쓰기 불가
- YM=7 코드가 pin 7을 LOW로 만들어 방향이 반전됨
- 이후 pin 7이 INPUT(플로팅)으로 남아 계속 불량

### 4-3. 남은 문제: 터치 시 흰 화면 전환

- `procTouch()` 비활성화 상태에서도 화면에 **두 번 접촉하면** 흰 화면으로 변함
- 원인 추정 두 가지:
  1. IRremote 3.x 라이브러리 호환성 문제 → irrecv.decode()가 잘못된 값 반환 → powerOn() 트리거 → initLCD() 내 tft.reset() 후 실패
  2. 물리적 터치가 A1(LCD_WR)/A2(LCD_RS) 핀 전압에 영향 → LCD 신호 오염
- **아직 해결 전**

---

## 5. 현재 코드 상태 (sgd5ver1.ino 기준)

### 핵심 설정
```cpp
#define TOUCH_TYPE 0            // p.y→화면X, p.x→화면Y
#define CONTROLLER_ID 0x9341    // ILI9341

// 터치 핀
#define YP A1
#define XM A2
#define YM 29
#define XP 28

// 캘리브레이션
#define TS_MINX 0
#define TS_MINY 0
#define TS_MAXX 1023
#define TS_MAXY 1023

#define MINPRESSURE 180
#define MAXPRESSURE 2000
#define DEBUG
```

### setup() 맨 앞 (★ 새로 추가됨)
```cpp
void setup() {
  // ★ 진단: pin7이 74HC245 DIR 또는 LCD 관련 핀 → HIGH로 고정
  pinMode(7, OUTPUT);
  digitalWrite(7, HIGH);
  ...
}
```

### procTouch() 상태 (★ 현재 비활성화 - 재활성화 필요!)
```cpp
void loop() {
  //procTouch();  // ← 진단용 임시 비활성화 ← ★ 주석 제거해야 함!
  refreshSampleRate();
  ...
}
```

### readTouchOnce() (현재)
```cpp
static TSPoint readTouchOnce() {
  digitalWrite(LCD_CS, LOW);   // 74HC245 활성화
  DDRA = 0x00;
  PORTA = 0x00;
  pinMode(YP, INPUT);  digitalWrite(YP, LOW);
  pinMode(XM, INPUT);  digitalWrite(XM, LOW);
  delay(20);
  TSPoint p = ts.getPoint();
  digitalWrite(LCD_CS, HIGH);
  pinMode(XM, OUTPUT);
  pinMode(YP, OUTPUT);
  DDRA = 0xFF;
  return p;
}
```

### procTouch() 터치 감지 로직
```cpp
void procTouch() {
  if (millis() < 3000) return;  // 부팅 직후 3초 가드

  TSPoint p = readTouchOnce();

  static int touchCount = 0;
  if (p.x >= 935) { touchCount = 0; return; }
  touchCount++;
  if (touchCount < 5) return;

  if (millis() - debounceMillis < 1000) return;
  debounceMillis = millis();
  touchCount = 0;
  ...
}
```

### TOUCH_TYPE=0 좌표 매핑
```cpp
// p.x → 화면 Y (버튼 상하 위치)
// p.y → 화면 X (항상 ~970 → 매핑 후 x≈228, 버튼 영역 182-240에 해당)
p.x = 240 - map(p.y, TS_MINX, TS_MAXX, 240, 0);   // ~228 (버튼 영역)
p.y = 320 - map(tmp_x, TS_MINY, TS_MAXY, 320, 0);  // 버튼별 다름
```

---

## 6. 실측 터치 데이터

### 비터치 상태
```
px = 935~1009,  py = 945~970
```

### 터치 상태 (오른쪽 버튼들)
```
px = 109~124 (Vol+),   py ≈ 970 (항상 고정)
px = 약 다름 (다른 버튼들), py ≈ 970
```

### TOUCH_TYPE=0 매핑 결과 (p.x=116, p.y=970)
```
화면 x ≈ 228 (버튼 영역 182~240 ✓)
화면 y ≈ 36  (Vol+ 영역 10~58 ✓)
```

### 버튼 좌표 범위 (메인화면)
```
Vol+:   x=182~240, y=10~58
Vol-:   x=182~240, y=73~121
Input:  x=182~240, y=136~184
Menu:   x=182~240, y=199~247
Power:  x=182~240, y=262~310
```

---

## 7. 다음 작업 절차 (★ 여기서 시작)

### Step 1: procTouch() 재활성화
```cpp
// loop() 안에서 주석 제거:
procTouch();  // 주석 제거 (현재 //procTouch(); 상태)
```

### Step 2: 터치 시 흰 화면 문제 해결

**접근 A: readTouchOnce() 안에서 pin 7 명시적 유지**
```cpp
static TSPoint readTouchOnce() {
  pinMode(7, OUTPUT);
  digitalWrite(7, HIGH);  // ← 추가: 74HC245 DIR 유지
  digitalWrite(LCD_CS, LOW);
  DDRA = 0x00;
  PORTA = 0x00;
  pinMode(YP, INPUT);  digitalWrite(YP, LOW);
  pinMode(XM, INPUT);  digitalWrite(XM, LOW);
  delay(20);
  TSPoint p = ts.getPoint();
  digitalWrite(LCD_CS, HIGH);
  pinMode(XM, OUTPUT);
  pinMode(YP, OUTPUT);
  DDRA = 0xFF;
  digitalWrite(7, HIGH);  // ← 추가: ts.getPoint() 이후 복원
  return p;
}
```

**접근 B: IRremote 라이브러리 다운그레이드**
- Arduino IDE → 라이브러리 매니저 → IRremote 검색 → **2.6.0으로 다운그레이드**
- Serial 경고 메시지가 사라지면 라이브러리가 올바르게 작동

**접근 C (만약 A,B 안 되면): LCD 재초기화 후 touch read**
- ts.getPoint() 후 `tft.setRotation(3)` 호출로 LCD 상태 복원

### Step 3: DBG 프린트 제거 (작업 완료 후)
- setup(), powerOff(), powerOn() 안의 `Serial.println(F("DBG: ..."))` 모두 제거

### Step 4: 최종 검증
- 5개 버튼 모두 정상 인식 확인
- `#define DEBUG` 제거

---

## 8. IRremote 라이브러리 현황

```
설치 버전: IRremote 3.x 이상 (구 2.x API와 호환 안 됨)
경고 메시지 출력 중:
  "Thank you for using the IRremote library!
   It seems, that you are using an old version 2.0 code"
해결: 2.6.0으로 다운그레이드 권장
경로: Arduino IDE → 스케치 → 라이브러리 포함 → 라이브러리 관리
     → IRremote 검색 → 버전 선택 → 2.6.0 설치
```

---

## 9. Arduino libraries 폴더 상태
```
C:\Users\jys\Documents\Arduino\libraries\
├── Adafruit_TFTLCD_Library\        ← 사용 중
├── Adafruit_TFTLCD_AS_DISABLED\    ← 비활성화됨
├── Adafruit_GFX_AS\                ← 사용 중
├── Adafruit_TouchScreen\           ← 사용 중
├── IRremote\                       ← 버전 문제! → 2.6.0 다운그레이드 권장
└── EmonLib\                        ← 사용 중
```

---

## 10. 파일 위치
```
D:\AI\MyVault\Projects\Audio\SG D5\
├── SG D5 코딩.md              ← 작업 지시서
├── SGD5_수정보고서.md          ← 수정 내역 보고서
├── sgd5-작업중간.md            ← ★ 이 파일
├── 터치결과.txt                ← 이전 RAW 데이터
├── 핀맵.txt                    ← 핀맵 메모
├── 20260213_143135.jpg         ← LCD 모듈 사진 (2.8" TFT LCD Shield)
├── SGD5\                       ← 원본 코드 (수정 안 함)
└── sgd5ver1\                   ← ★ 현재 작업 파일
    └── sgd5ver1.ino
```

---

## 11. 다른 컴퓨터에서 이어서 할 때 Claude에게 전달할 메시지

```
`D:\AI\MyVault\Projects\Audio\SG D5\sgd5-작업중간.md` 파일을 읽고
SG-D5 터치 작업을 이어서 해줘.

오늘 할 작업:
1. procTouch() 재활성화 (loop()에서 주석 제거)
2. readTouchOnce() 안에서 pin7=HIGH 명시 추가
3. 터치 시 흰 화면 문제 해결
4. IRremote 2.6.0으로 다운그레이드 고려

업로드 후 시리얼 결과:
[여기에 시리얼 출력 붙여넣기]
```

---

*마지막 업데이트: 2026-02-20 (pin 7=74HC245 DIR 발견, LCD 검정 복원, 터치 흰화면 문제 미해결)*
