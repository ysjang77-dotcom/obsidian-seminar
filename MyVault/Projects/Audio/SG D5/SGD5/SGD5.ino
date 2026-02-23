#include <EmonLib.h>

#include <Adafruit_GFX_AS.h>
#include <Font16.h>
#include <Font32.h>
#include <Font64.h>
#include <Font72.h>
#include <Font7s.h>
#include <Load_fonts.h>


/***************************************************************************************************
  HIFIDUINO Code: Supports Buffalo II 80Mhz and 100Mhz, stereo and dual mono.
                  Others have used it with Buffalo III and Acko DAC with great success
                  Also tested with QuangHao's DAC-END with multiple live inputs
  SG-D5 : 스피커 공작 듀얼 ES9018 DAC용 펌웨어
          터치패널로 모든 기능 제어
          리모트콘트롤 사용 가능
          Adaruit_gfx_as 를 이용한 확장 그래픽
          아두이노 메가 + ILI9325/9341 컨트롤러의 LCD 터치패널
************************************** LICENSE *****************************************************
                         http://creativecommons.org/licenses/by/3.0/
                         Attribution
                         CC BY

****************************************************************************************************
  Change log:
  Modified 06/09/16:- 스공 9018 듀얼 DAC에 맞도록 11차수정 (DSD 재생시 핀 high)
  Modified 01/21/16:- 스공 9018 듀얼 DAC에 맞도록 10차수정 (전원오프시 9018 뮤트, 딜레이 추가)
  Modified 01/18/16:- 스공 9018 듀얼 DAC에 맞도록 9차수정 (LCD TYPE 정의, 전원오프 시 샘플레이트표시 수정)
  Modified 01/18/16:- 스공 9018 듀얼 DAC에 맞도록 8차수정 (행복문님 2차 버그리포트 수정)
  Modified 01/14/16:- 스공 9018 듀얼 DAC에 맞도록 7차수정 (행복문님 버그리포트 수정)
  Modified 12/26/15:- 스공 9018 듀얼 DAC에 맞도록 6차수정 (리모콘 처리 추가 - 직접 입력 키)
  Modified 12/16/15:- 스공 9018 듀얼 DAC에 맞도록 5차수정 (리모콘 처리)
  Modified 11/29/15:- 스공 9018 듀얼 DAC에 맞도록 4차수정 (터치 패널 정식 그래픽 소스 통합)
  Modified 11/12/15:- 스공 9018 듀얼 DAC에 맞도록 3차수정 (터치 패널 추가)
  Modified 11/04/15:- 스공 9018 듀얼 DAC에 맞도록 2차수정 (듀얼모두 설정 수정)
  Modified 10/18/15:- 스공 9018 듀얼 DAC에 맞도록 수정

  V. B1.1f 03/23/13:- Fixed a bug in selecting SPDIF inputs (had the wrong register value for
                      spdif#3
                    - Tested the input switching with a simultanous live spdif and live I2S signal
                      This required moving the spdif mux away from a live spdif signal when using
                      I2S in order for the status register to report serial input. If the spdif mux
                      is set to a live spdif input, then the status register will report spdif
                      regardless of whether the input is switched to I2S or not.
                    - Cleaner code for DUAL MONO recognizing that for the most part changes in
                      register value for one chip are the same as for the other chip, so after
                      changing the register values for both chips, we just change the channel bit
                      for the right channel chip.
  V. B1.1d 11/28/12:- Removed the "optimized" volume routine which proved unreliable
  V. B1.1c 11/27/12:- Code has grown to over 15K, so it can no longer fit in the AT168 based Arduino
                    - Changed the EEPROM writing routine to only write if there is a change
                      This will improve somewhat the longevity of the EEPROM
                    - Choice of sample rate display format: nominal value or exact value
                    - Input selection now includes SPDIF #1, 3, 7 and 8 to support "smart wiring on
                      Buffalo III boards
                    - Sample rate reading is more accurate to compensate for integer operation
                    - Removed the "primeDpll" function. Doesn't seem to do anything...
                    - Optimized volume routine (use sequential write without releasing the bus)
                    - Fixed a bug in the remote code that prevented repeat keys
                    - Minor code clean up here and there
                    - Ensure accuracy of comments
  v. B1.1a 11/11/12:- Changed UI to support DSD better: status format is now DSD, PCM or SpD
                    - Serial mode setting (32 bit, RJ...) only displayed during setting change
                    - Changed SR display to give the nominal value rather than exact value
                    - Correctly displays frequency for DSD streams
                    - Apple remote code supports all Apple remotes by fixing detection of control
                      byte from 8-bits to 7-bits
  v. B1.0e 02/10/12:- Fixed some minor bug wih Jitter eliminator bypass
                    - Added more serial mode settings: LJ, RJ, 32 bit, 24 bit, 16 bit
                    - Displays serial bit-depth setting when locked to signal
                    - When no signal, displays "SER" for serial rather than "I/D" for I2S/DSD
                    - Additional code cleaning/optimizing
                    - Tested with "New LCD library" for improved code efficiency
  v. B1.0b 01/07/12:- Compatible with Arduino 1.0 (but not backwards compatible)
                    - Fixed Minor (potential) bugs
                    - Two additional settings: Oversampling bypass and jitter eliminator bypass
  v. B09f 08/24/11: - Dual MONO: Flipped polarity on one side of each dacs to make it the same as
                      TPA's dual mono code (outputs on each side of each DAC have opposite polarity)
  v. B09e 08/23/11: - Added control for DPLL multiplier
                    - Turned on automute loopback to mitigate 382.8KHz audio with 80MHz part
                    - Dual MONO compability (outputs on each side of each DAC have same polarity)
  v. B09c 07/01/11: - Tweaked DIM/Ramp-up to be more gradual (longer at higher volumes)
                    - Increased name of input from 3 to 6 characters
                    - Customizable features: crystal frequency (80 or 100 MHz)
                    - Customizable number of inputs (up to 6) each with its own settings
  v. B09b 06/21/11: - DIM/Ramp-up control (Soft mute) -set at -70db
                    - Remote keys are non-repeating by default
                    - All settings configurable for each (labeled) input (no need for defaults)
                    - Save settings in EEPROM. Remembers all settings/last setting
  v. B08a 06/11/11: - Rearranged and simplified the UI to reclaim some real state and improve looks
                    - Added adjustment of notch delay and IIR filter selection
                    - Optimized and simplified the code some more
  v. B07d 06/04/11: - Separate tracking of DPLL setting for I2S and SPDIF
                    - Fixed dpll setting not updated when switching between SPDIF and I2S
                    - Two versions: B07d80 and B07d100 for different frequency crystal
  v. B07c 06/02/11: - Requires Arduino 0022 version in order to support pulseIn function for remote
                    - Moved muting DACs to the beginning of program to minimize the time for full
                      vol during power on of the DAC/Arduino when there is an SPDIF signal present
                    - Jitter is now always ON (Did not see the need to turn it off). No selection
                    - Supports different quantization bit depth: 6,7,8,9 in pseudo and true diff
                    - Implemented "DPLL Priming" which goes through all the settings when the DAC
                      first locks unto a signal (done once during a power cycle)
  v. B06e 01/08/11: Supports 32-bit I2S input in accordance to Buffalo II input wiring of SabreDAC
                    Rearranged code for default conditions, correct reading of sample rate in I2S
                    Allows manual "best DPLL bandwidth" setting. Allows manual selection of I2S or
                    SPDIF. Can set default startup to I2S or SPDIF (in the code)
                    This version compatible with Arduino 0021. Fixes a deficiency in pulseIn()
                    by redefining the function with the fix.
  v. B05  11/25/10: Added remote control capability using the Apple Aluminum Remote Control. This
                    version enables remote volume control only.
  v. B04  11/06/10: Added large numbers, tidy-up the UI, "pulse" indicator -every time the Status
                    information is read. Also status indicator for PCM/DSD and Signal Lock
  v. B03  11/02/10: Supports s/w debounce, added setting of FIR filter, DPLL bandwidth, jitter
                    reduction and adjustment of LCD brightness.
  v. B021 10/18/10: No new functionality, but cleaned up the code and comments.
  v. B02  10/15/10: Added reading of sample rate.
  v. B01  10/11/10: Volume control, LCD, Rotary Encoder.
***************************************************************************************************/
/***************************************************************************************************
  look for "code customization section" to customize code to your setup

***************************************************************************************************/
/***************************************************************************************************
  The following is a description of some of the registers of Sabre32. Based on datasheet and other
  sources and also my own experimentation
***************************************************************************************************/
/*
  1-Set up for I2S/DSD support according to BuffII input wiring

  Register 14 (0x0E) DAC source, IIR Bandwidth and FIR roll off
  |0| | | | | | | | Source of DAC8 is DAC8 (D)
  |1| | | | | | | | Source of DAC8 is DAC6 (To Buffalo II wiring)
  | |0| | | | | | | Source of DAC7 is DAC7 (D)
  | |1| | | | | | | Source of DAC7 is DAC5 (To Buffalo II wiring)
  | | |0| | | | | | Source of DAC4 is DAC4 (D)
  | | |1| | | | | | Source of DAC4 is DAC2 (To Buffalo II wiring)
  | | | |0| | | | | Source of DAC3 is DAC3 (D)
  | | | |1| | | | | Source of DAC3 is DAC1 (To Buffalo II wiring)
  | | | | |0| | | | Pseudo differential
  | | | | |1| | | | True differential (D)
  | | | | | |0|0| | IIR Bandwidth: Normal (for PCM, 47k)
  | | | | | |0|1| | IIR Bandwidth: 50k (for DSD) (D)
  | | | | | |1|0| | IIR Bandwidth: 60k (for DSD)
  | | | | | |1|1| | IIR Bandwidth: 70k (for DSD)
  | | | | | | | |0| FIR Rolloff: Slow
  | | | | | | | |1| FIR Rolloff: Fast (D)

  Buffalo II input pins are wired as such: 1111xxxx for example

  11111001 or 0xF9 Default for BII wiring, true differential, IIR normal, FIR fast
  Pseudo diff: clear bit 3
  true diff:   set   bit 3
  Slow FIR:    clear bit 0
  Fast FIr:    set   bit 0
  ------------------

  2- Set up I2S bit depth. In theory I2S can be set to 32 bit and it
   will automatically handle all bit depths.

  Register 10 (0x0A) (MC1)
  |0|0| | | | | | |  24bit data
  |0|1| | | | | | |  20bit data
  |1|0| | | | | | |  16bit data
  |1|1| | | | | | |  32bit data (D)
  | | |0|0| | | | |  I2S (D)
  | | |0|1| | | | |  LJ
  | | |1|0| | | | |  RJ
  | | |1|1| | | | |  I2S (Not sure why two values for I2S)
  | | | | |1| | | |  Reserved for engineering; must be 1 (D)
  | | | | | |0| | |  Jitter Reduction Bypass
  | | | | | |1| | |  Jitter Reduction ON (D)
  | | | | | | |0| |  Deemph ON
  | | | | | | |1| |  Deemph Bypass (D) (can set auto deemph in Reg17)
  | | | | | | | |0|  Unmute DACs (D)
  | | | | | | | |1|  Mute DACs

  32 bit I2S, Other defaults such as Jitter ON, Deemphasis Bypass...
  11001111 or 0xCF (Jitter on, etc, MUTE DACs)  (0xFF is also valid)
  11001110 or 0xCE (Unmute DACs)
  ------------------

  3- Set up to allow all DPLL settings

  Register 25 (0x19): DPLL Mode control
  |0|0|0|0|0|0| | | Reserved, must be zeros (D)
  | | | | | | |0| | DPLL Bandwidht: allow all Settings
  | | | | | | |1| | DPLL Bandwidht: Use best DPLL Settings (D)
  | | | | | | | |0| DPLL128x: Use DPLL setting (D)
  | | | | | | | |1| DPLL128x: Multiply DPLL by 128

  Allow all DPLL settings at 1x:
  00000000 or 0x00
  Use best DPLL settings:
  00000010 or 0x02
  Allow all DPLL settings at 128x:
  00000000 or 0x01
  ------------------

  4- Set up for DPLL bandwidth

  Register 11 (0x0B) (MC2)
  |1|0|0| | | | | |  Reserved for engineering, Must be 100 (D)
  | | | |0|0|0| | |  DPLL BW: No Bandwidth
  | | | |0|0|1| | |  DPLL BW: Lowest (D)
  | | | |0|1|0| | |  DPLL BW: Low
  | | | |0|1|1| | |  DPLL BW: Medium-Low
  | | | |1|0|0| | |  DPLL BW: Medium
  | | | |1|0|1| | |  DPLL BW: Medium-High
  | | | |1|1|0| | |  DPLL BW: High
  | | | |1|1|1| | |  DPLL BW: Highest
  | | | | | | |0|0|  DeEmph: 32k
  | | | | | | |0|1|  DeEmph: 44.1k (D)
  | | | | | | |1|0|  DeEmph: 48k
  | | | | | | |1|1|  Reserved, do not use

  Lowest Bandwidth 44.1K De-emphasis select (these are chip default):
  10000101 or 0x85 (or decimal 133)
  ---
  10000001 or 0x81 (No Bandwidth)
  10000101 or 0x85 (lowest)
  10001001 or 0x89 (low)
  10001101 or 0x8D (med-low)
  10010001 or 0x91 (med)
  10010101 or 0x95 (med-hi)
  10011001 or 0x99 (high)
  10011101 or 0x9D (highest)
  ------------------

  5- Set up reg 17 for manual or auto  SPDIF selection

  Register 17 (0x11) (MC5)
  |1| | | | | | | |  Mono Right (if set for MONO)
  |0| | | | | | | |  Mono Left (if set for MONO) (D)
  | |1| | | | | | |  OSF (Oversample filter) Bypass
  | |0| | | | | | |  Use OSF (D)
  | | |1| | | | | |  Relock Jitter Reduction
  | | |0| | | | | |  Normal Operation Jitter Reduction (D)
  | | | |1| | | | |  SPDIF: Auto deemph ON (D)
  | | | |0| | | | |  SPDIF: Auto deemph OFF
  | | | | |1| | | |  SPDIF Auto (Only if no I2S on pins) (D)
  | | | | |0| | | |  SPDIF Manual (Manually select SPDIF input format)
  | | | | | |1| | |  FIR: 28 coefficients (D)
  | | | | | |0| | |  FIR: 27 coefficients
  | | | | | | |1| |  DPLL: Phase invert
  | | | | | | |0| |  DPLL: Phase NO invert (D)
  | | | | | | | |1|  All MONO (Then select Mono L or R)
  | | | | | | | |0|  Eight channel (D)

  Auto SPDIF, others at defaults:
  00001100 (0x1C)
  Manual SPDIF, others at default:
  00000100 (0x14)
  ------------------

  6- Enable I2S/DSD

  Register 8 (0x08) Auto-mute level, manual spdif/i2s
  |0| | | | | | | |  Use I2S or DSD (D)
  |1| | | | | | | |  Use SPDIF
  | |1|1|0|1|0|0|0|  Automute trigger point (D)

  I2S/DSD input format:
  01101000 (0x68)
  SPDIF input format:
  11101000 (0xE8) // (Actually just disables I2S input format)

  If we use a different automute trigger point, say -60 db then
  (This is for experimenting the automute feature)
  I2S/DSD input format:
  00111100 (0x3C)
  SPDIF input format:
  10111100 (0xBC) // (Actually just disables I2S input format)


  NOTE on auto/manual SPDIF selection
  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  Apparentely, auto detection of spdif and I2S (with I2S/DSD enabled in reg 8), only works when the
  DAC powers up. Once you turn off auto-SPDIF and then turn on auto-SPDIF, it will not work with SPDIF
  input format while reg 8 is still set for I2S/DSD. In order for SDPIF to work, reg 8 must be set for
  SPDIF and reg 17 for auto-SDPIF. In summary:

  reg 17 auto-SPDIF | reg 8 source | Result
  ~~~~~~~~~~~~~~~~~~|~~~~~~~~~~~~~~|~~~~~~~
   ON              | I2S/DSD      | SPDIF works: Only works with default startup.
   ON              | SPDIF        | SPDIF works: Works when auto-SPDIF is set to OFF, then to ON (1)
   OFF             | SPDIF        | SPDIF does not work, I2S does not work (3)
   OFF             | I2S/DSD      | I2S works (2)

  Thus for manual operation:
  - use (1) to select SDPIF input
  - use (2) to select I2S input
  - I don't know what is the purpose of (3)

  Writing to register 18 (selecting the spdif input line) alone will not work if auto-SPDIF is off.
  You need to turn on auto-SPDIF and if using SPDIF input line other than #1, you need to select the
  input line with register 18 (tested may 29, 2011 - with Buffalo II which only has spdif#1 connected)
  Also tested March 23, 2013 with QuangHao's DAC-END which also uses spdif 3, 7 and 8 in addition to
  I2S/DSD
  ------------------

  7- Re- route SPDIF input line to pin Data5 which is also connected to D1 (Experimental info)

  Register 18 (0x12): Spdif Input line
  |0|0|0|0|0|0|0|1|  SDPIF Input: Data1 (D) (In BuffII, spdif is connected to this pin)
  |0|0|0|0|0|0|1|0|  SDPIF Input: Data2
  |0|0|0|0|0|1|0|0|  SDPIF Input: Data3
  |0|0|0|0|1|0|0|0|  SDPIF Input: Data4
  |0|0|0|1|0|0|0|0|  SDPIF Input: Data5 (In BuffII, spdif is also  connected to this pin)
  |0|0|1|0|0|0|0|0|  SDPIF Input: Data6
  |0|1|0|0|0|0|0|0|  SDPIF Input: Data7
  |1|0|0|0|0|0|0|0|  SDPIF Input: Data8

  Re-route spdif input line to Data5 (Maybe it will help the I2S lock issue):
  00010000 or 0x10
  Re-route spdif input line to Data8 (which is not a valid spdif input, but it is grounded)
  10000000 or 0x80
  ------------------

  Register 37 (0x25)
  |0|0| | | | | | |  Reserved (D)
  | | |1| | | | | |  Use downloaded coefficients for stage 1 FIR filter
  | | |0| | | | | |  Use built-in coefficients for stage 1 FIR filter (D)
  | | | |1| | | | |  Enable writing of coefficients for stage 1 -Use when starting to write coeffs
  | | | |0| | | | |  Not enabled to write coefficients for stage 1 (D) -Also use when done writing
  | | | | |0|0| | |  Reserved (D)
  | | | | | | |1| |  Use downloaded coefficients for stage 2 FIR filter
  | | | | | | |0| |  Use built-in coefficients for stage 2 FIR filter (D)
  | | | | | | | |1|  Enable writing of coefficients for stage 2 -Use when starting to write coeffs
  | | | | | | | |0|  Not enabled to write coefficients for stage 2 (D) -Also use when done writing

  Start writing coefficients into stage 1:
  00010000 or 0x10; 00110000 or 0x30 might work too
  Done writing coefficients into stage 1:
  00000000 or 0x00

  Use built-in coefficients for stage 1 and stage 2:
  00000000 or 0x00
  Use downloaded coefficients for stage 1 and built-in for stage 2:
  00100000 or 0x20
  Use downloaded coefficients for stage 1 and stage 2:
  00100010 or 0x22
  Use built-in coefficients for stage 1 and downloaded for stage 2:
  00000010 or 0x02
  ------------------

  Reg 38 (0x26)
  Reg 39 (0x27)
  Reg 40 (0x28)
  Reg 41 (0x29)
  ------------------

  Register 15 (0x0F) Quantizer bit depth
  6-bit: 0x00 (D)
  7-bit: 0x55
  8-bit: 0xAA
  9-bit: 0xFF
  ------------------

  Register 13 (0x0D) DAC polarity
  In-phase: 0x00 (all 8 channels) (D)
  Anti-phase: 0xFF (all 8 channels)

  ------------------

  Register 19 (0x13) DACB polarity
  In-phase: 0xFF (all 8 channels)
  Anti-phase: 0x00 (all 8 channels) (D)
  1256 In-Phase; 3478 Anti-Phase: 0x33
  1256 Anti-Phase; 3478 In-Phase: 0xCC
  ------------------

  Register 12 (0x0C)
  |0| | | | | | | | Dither Control: Apply
  |1| | | | | | | | Dither Control: Use fixed rotation pattern
  | |0| | | | | | | Rotator Input: NS-mod input
  | |1| | | | | | | Rotator Input: External input
  | | |0| | | | | | Remapping: No remap
  | | |1| | | | | | Remapping: Remap diigital outputs for max phase separation in analog cell

  | | | |0|0|0|0|0| No Notch
  | | | |0|0|0|0|1| Notch at MCLK/4
  | | | |0|0|0|1|1| Notch at MCLK/8
  | | | |0|0|1|1|1| Notch at MCLK/16
  | | | |0|1|1|1|1| Notch at MCLK/32
  | | | |1|1|1|1|1| Notch at MCLK/64

  |0|0|1|0|0|0|0|0| Power-on Default

  Values to use in register 12:
  00100000 or 0x20 NtNO
  00100001 or 0x21 Nt04
  00100011 or 0x23 Nt08
  00100111 or 0x27 Nt16
  00101111 or 0x2F Nt32
  00111111 or 0x3F Nt64

*/

/***************************************************************************************************
  Code starts here
***************************************************************************************************/

// LIBRARIES
#include <Wire.h> // For I2C
//#include <EEPROM.h>
#include <avr/eeprom.h>
#include <IRremote.h>
#include <Adafruit_GFX_AS.h>    // Core graphics library
//#include <Adafruit_TFTLCD_AS.h> // Hardware-specific library
#include <Adafruit_TFTLCD.h> // Hardware-specific library
#include <TouchScreen.h>


// 버전정보
#define VER_INFO "Ver. 1.0c"

#define CONTROLLER_ID 0x9341 //ILI9341 LCD driver


///////////////////////// SG-D5 그래픽 관련///////////////////////////////////////
//TFT LCD

// 핀 정의 및 TFT 객체 생성 (예시 핀 번호)

#define LCD_CS A3
#define LCD_CD A2
#define LCD_WR A1
#define LCD_RD A0
// optional
//#define LCD_RESET 0  //IOREF에 연결
#define LCD_RESET A4

#define	BLACK   0x0000
#define	BLUE    0x001F
#define	RED     0xF800
#define	GREEN   0x07E0
#define CYAN    0x07FF
#define MAGENTA 0xF81F
#define YELLOW  0xFFE0
#define WHITE   0xFFFF

Adafruit_TFTLCD tft(LCD_CS, LCD_CD, LCD_WR, LCD_RD, LCD_RESET);

#define WHITE 0xFFFF  // 색상 정의 없을 시 추가

void drawString(const char* text, int x, int y, int fontSize, uint16_t color = WHITE) {
  tft.setTextColor(color);
  tft.setTextSize(fontSize);
  tft.setCursor(x, y);
  tft.print(text);
}

void drawCentreString(const char* text, int x, int y, int fontSize, uint16_t color = WHITE) {
  tft.setTextColor(color);
  tft.setTextSize(fontSize);
  int16_t x1, y1;
  uint16_t w, h;
  tft.getTextBounds(text, x, y, &x1, &y1, &w, &h);
  tft.setCursor(x - w / 2, y);
  tft.print(text);
}


// 수정 종료

// When using the BREAKOUT BOARD only, use these 8 data lines to the LCD:
// For the Arduino Uno, Duemilanove, Diecimila, etc.:
//   D0 connects to digital pin 8  22 (Notice these are
//   D1 connects to digital pin 9  23  NOT in order!)
//   D2 connects to digital pin 2  24
//   D3 connects to digital pin 3  25
//   D4 connects to digital pin 4  26
//   D5 connects to digital pin 5  27
//   D6 connects to digital pin 6  28
//   D7 connects to digital pin 7  29
// For the Arduino Mega, use digital pins 22 through 29
// (on the 2-row header at the end of the board).

#define YP A1  // must be an analog pin, use "An" notation!
#define XM A2  // must be an analog pin, use "An" notation!
#define YM 29   // can be a digital pin //uno 7, mega 29
#define XP 28   // can be a digital pin //uno 6, mega 28 

#define TS_MINX 150
#define TS_MINY 120
#define TS_MAXX 920
#define TS_MAXY 940

// Assign human-readable names to some common 16-bit color values:
#define BLACK       0x0000      /*   0,   0,   0 */
#define NAVY        0x000F      /*   0,   0, 128 */
#define DARKGREEN   0x03E0      /*   0, 128,   0 */
#define DARKCYAN    0x03EF      /*   0, 128, 128 */
#define MAROON      0x7800      /* 128,   0,   0 */
#define PURPLE      0x780F      /* 128,   0, 128 */
#define OLIVE       0x7BE0      /* 128, 128,   0 */
#define LIGHTGREY   0xC618      /* 192, 192, 192 */
#define DARKGREY    0x7BEF      /* 128, 128, 128 */
#define BLUE        0x001F      /*   0,   0, 255 */
#define GREEN       0x07E0      /*   0, 255,   0 */
#define CYAN        0x07FF      /*   0, 255, 255 */
#define RED         0xF800      /* 255,   0,   0 */
#define MAGENTA     0xF81F      /* 255,   0, 255 */
#define YELLOW      0xFFE0      /* 255, 255,   0 */
#define WHITE       0xFFFF      /* 255, 255, 255 */
#define ORANGE      0xFD20      /* 255, 165,   0 */
#define GREENYELLOW 0xAFE5      /* 173, 255,  47 */
#define PINK        0xF81F

uint16_t getColor(uint8_t red, uint8_t green, uint8_t blue)
{
  red   >>= 3;
  green >>= 2;
  blue  >>= 3;
  return (red << 11) | (green << 5) | blue;
}

//////// 메인화면 버튼 좌표 관련
#define BUTTON_R 24
#define BUTTON_D 15 //메인화면 버튼 간격
#define BUTTON_MARGIN_X 10
#define BUTTON_MARGIN_Y 10

/////// 메인화면 볼륨 표시 숫자 ( 7 세그먼트 넘버)
#define VOL_POSX 200
#define VOL_POSY 60
#define SEG_WIDTH 7
#define SEG_LENGTH 24
#define SEG_COL WHITE

/////// 메뉴화면 아이템 좌표
#define mnu_marginx   12
#define mnu_marginy   12
#define mnu_height    22
#define mnu_offsety   12
#define mnu_offsetx   170

/////// 전원 상태
#define _POWER_OFF 0
#define _POWER_ON 1

/////// LCD 화면 모드
#define _MAIN_SCREEN 0
#define _MENU_SCREEN_1 1
#define _MENU_SCREEN_2 2
#define _MENU_SCREEN_3 3
#define _MENU_SCREEN_4 4

/////// 리모콘 핀
#define RECV_PIN 11

/////// 전원 릴레이 핀
#define _POWER 12

/////// DSD 신호 핀
#define _DSD_PLAY 13

/////// 9018 RESET  핀
#define _RESET_9018 10

/////// 메인화면 하단 버튼 이미지
static const unsigned char PROGMEM setupmenu [] = {
  0x00, 0x00, 0x1F, 0xF8, 0x00, 0x00, 0x00, 0x00, 0xFF, 0xFF, 0x00, 0x00, 0x00, 0x07, 0xFF, 0xFF,
  0xE0, 0x00, 0x00, 0x0F, 0xFF, 0xFF, 0xF0, 0x00, 0x00, 0x3F, 0xFF, 0xFF, 0xFC, 0x00, 0x00, 0x7F,
  0xFF, 0xFF, 0xFE, 0x00, 0x00, 0xFF, 0xFF, 0xFF, 0xFF, 0x00, 0x01, 0xFF, 0xFF, 0xFF, 0xFF, 0x80,
  0x03, 0xFF, 0xFF, 0xFF, 0xFF, 0xC0, 0x07, 0xFF, 0xFF, 0xFF, 0xFF, 0xE0, 0x0F, 0xFF, 0xFF, 0xFF,
  0xFF, 0xF0, 0x0F, 0xFF, 0xFF, 0xFF, 0xFF, 0xF0, 0x1F, 0xFE, 0x1C, 0x38, 0x7F, 0xF8, 0x3F, 0xFE,
  0x1C, 0x38, 0x7F, 0xFC, 0x3F, 0xFE, 0x1C, 0x38, 0x7F, 0xFC, 0x3F, 0xFE, 0x1C, 0x38, 0x7F, 0xFC,
  0x7F, 0xFE, 0x1C, 0x38, 0x7F, 0xFE, 0x7F, 0xFE, 0x1C, 0x38, 0x7F, 0xFE, 0x7F, 0xFE, 0x1C, 0x38,
  0x7F, 0xFE, 0xFF, 0xFE, 0x1C, 0x38, 0x7F, 0xFF, 0xFF, 0xFE, 0x1C, 0x38, 0x7F, 0xFF, 0xFF, 0xFE,
  0x1C, 0x38, 0x7F, 0xFF, 0xFF, 0xFE, 0x1C, 0x38, 0x7F, 0xFF, 0xFF, 0xFE, 0x1C, 0x38, 0x7F, 0xFF,
  0xFF, 0xFE, 0x1C, 0x38, 0x7F, 0xFF, 0xFF, 0xFE, 0x1C, 0x38, 0x7F, 0xFF, 0xFF, 0xFE, 0x1C, 0x38,
  0x7F, 0xFF, 0xFF, 0xFE, 0x1C, 0x38, 0x7F, 0xFF, 0xFF, 0xFE, 0x1C, 0x38, 0x7F, 0xFF, 0x7F, 0xFE,
  0x1C, 0x38, 0x7F, 0xFE, 0x7F, 0xFF, 0xFF, 0xFF, 0xFF, 0xFE, 0x7F, 0xFF, 0xFF, 0xFF, 0xFF, 0xFE,
  0x3F, 0xFE, 0x1C, 0x38, 0x7F, 0xFC, 0x3F, 0xFE, 0x1C, 0x38, 0x7F, 0xFC, 0x3F, 0xFE, 0x1C, 0x38,
  0x7F, 0xFC, 0x1F, 0xFE, 0x1C, 0x38, 0x7F, 0xF8, 0x0F, 0xFF, 0xFF, 0xFF, 0xFF, 0xF0, 0x0F, 0xFF,
  0xFF, 0xFF, 0xFF, 0xF0, 0x07, 0xFF, 0xFF, 0xFF, 0xFF, 0xE0, 0x03, 0xFF, 0xFF, 0xFF, 0xFF, 0xC0,
  0x01, 0xFF, 0xFF, 0xFF, 0xFF, 0x80, 0x00, 0xFF, 0xFF, 0xFF, 0xFF, 0x00, 0x00, 0x7F, 0xFF, 0xFF,
  0xFE, 0x00, 0x00, 0x3F, 0xFF, 0xFF, 0xFC, 0x00, 0x00, 0x0F, 0xFF, 0xFF, 0xF0, 0x00, 0x00, 0x07,
  0xFF, 0xFF, 0xE0, 0x00, 0x00, 0x00, 0xFF, 0xFF, 0x00, 0x00, 0x00, 0x00, 0x1F, 0xF8, 0x00, 0x00
};

static const unsigned char PROGMEM inputselect [] = {
  0x00, 0x00, 0x1F, 0xF8, 0x00, 0x00, 0x00, 0x00, 0xFF, 0xFF, 0x00, 0x00, 0x00, 0x07, 0xFF, 0xFF,
  0xE0, 0x00, 0x00, 0x0F, 0xFF, 0xFF, 0xF0, 0x00, 0x00, 0x3F, 0xFF, 0xFF, 0xFC, 0x00, 0x00, 0x7F,
  0xFF, 0xFF, 0xFE, 0x00, 0x00, 0xFF, 0xFF, 0xFF, 0xFF, 0x00, 0x01, 0xFF, 0xFF, 0xFF, 0xFF, 0x80,
  0x03, 0xFF, 0xFF, 0xFF, 0xFF, 0xC0, 0x07, 0xFF, 0xFF, 0xFF, 0xFF, 0xE0, 0x0F, 0xFF, 0xFF, 0xFF,
  0xFF, 0xF0, 0x0F, 0xFF, 0xFF, 0xFF, 0xFF, 0xF0, 0x1F, 0xFF, 0xFF, 0xFF, 0xFF, 0xF8, 0x3F, 0xFF,
  0xFF, 0xFF, 0xFF, 0xFC, 0x3F, 0xE0, 0x00, 0x00, 0x07, 0xFC, 0x3F, 0xE0, 0x00, 0x00, 0x07, 0xFC,
  0x7F, 0xE0, 0x00, 0x00, 0x07, 0xFE, 0x7F, 0xE0, 0x00, 0x00, 0x07, 0xFE, 0x7F, 0xE0, 0x00, 0x00,
  0x07, 0xFE, 0xFF, 0xE0, 0x01, 0x80, 0x07, 0xFF, 0xFF, 0xE0, 0x03, 0xC0, 0x07, 0xFF, 0xFF, 0xE0,
  0x07, 0xE0, 0x07, 0xFF, 0xFF, 0xE0, 0x0F, 0xF0, 0x07, 0xFF, 0xFF, 0xE0, 0x1F, 0xF8, 0x07, 0xFF,
  0xFF, 0xE0, 0x3F, 0xFC, 0x07, 0xFF, 0xFF, 0xE0, 0x7F, 0xFE, 0x07, 0xFF, 0xFF, 0xE0, 0xFF, 0xFF,
  0x07, 0xFF, 0xFF, 0xE0, 0x0F, 0xF0, 0x07, 0xFF, 0xFF, 0xE0, 0x0F, 0xF0, 0x07, 0xFF, 0x7F, 0xE0,
  0x0F, 0xF0, 0x07, 0xFE, 0x7F, 0xE0, 0x0F, 0xF0, 0x07, 0xFE, 0x7F, 0xE0, 0x0F, 0xF0, 0x07, 0xFE,
  0x3F, 0xE0, 0x0F, 0xF0, 0x07, 0xFC, 0x3F, 0xE0, 0x0F, 0xF0, 0x07, 0xFC, 0x3F, 0xFF, 0xF0, 0x0F,
  0xFF, 0xFC, 0x1F, 0xFF, 0xF0, 0x0F, 0xFF, 0xF8, 0x0F, 0xFF, 0xF0, 0x0F, 0xFF, 0xF0, 0x0F, 0xFF,
  0xF0, 0x0F, 0xFF, 0xF0, 0x07, 0xFF, 0xF0, 0x0F, 0xFF, 0xE0, 0x03, 0xFF, 0xFF, 0xFF, 0xFF, 0xC0,
  0x01, 0xFF, 0xFF, 0xFF, 0xFF, 0x80, 0x00, 0xFF, 0xFF, 0xFF, 0xFF, 0x00, 0x00, 0x7F, 0xFF, 0xFF,
  0xFE, 0x00, 0x00, 0x3F, 0xFF, 0xFF, 0xFC, 0x00, 0x00, 0x0F, 0xFF, 0xFF, 0xF0, 0x00, 0x00, 0x07,
  0xFF, 0xFF, 0xE0, 0x00, 0x00, 0x00, 0xFF, 0xFF, 0x00, 0x00, 0x00, 0x00, 0x1F, 0xF8, 0x00, 0x00
};
static const unsigned char PROGMEM volup [] = {
  0x00, 0x00, 0x1F, 0xF8, 0x00, 0x00, 0x00, 0x00, 0xFF, 0xFF, 0x00, 0x00, 0x00, 0x07, 0xFF, 0xFF,
  0xE0, 0x00, 0x00, 0x0F, 0xFF, 0xFF, 0xF0, 0x00, 0x00, 0x3F, 0xFF, 0xFF, 0xFC, 0x00, 0x00, 0x7F,
  0xFF, 0xFF, 0xFE, 0x00, 0x00, 0xFF, 0xFF, 0xFF, 0xFF, 0x00, 0x01, 0xFF, 0xFF, 0xFF, 0xFF, 0x80,
  0x03, 0xFF, 0xFF, 0xFF, 0xFF, 0xC0, 0x07, 0xFF, 0xFF, 0xFF, 0xFF, 0xE0, 0x0F, 0xFF, 0xFF, 0xFF,
  0xFF, 0xF0, 0x0F, 0xFF, 0xFF, 0xFF, 0xFF, 0xF0, 0x1F, 0xFF, 0xC7, 0xFF, 0xFF, 0xF8, 0x3F, 0xFF,
  0xC3, 0xFF, 0xFF, 0xFC, 0x3F, 0xFF, 0xC1, 0xFF, 0xFF, 0xFC, 0x3F, 0xFF, 0xC0, 0xFF, 0xFF, 0xFC,
  0x7F, 0xFF, 0xC0, 0x7F, 0xFF, 0xFE, 0x7F, 0xFF, 0xC0, 0x3F, 0xFF, 0xFE, 0x7F, 0xFF, 0xC0, 0x1F,
  0xFF, 0xFE, 0xFF, 0xFF, 0xC0, 0x0F, 0xFF, 0xFF, 0xFF, 0xFF, 0xC0, 0x07, 0xFF, 0xFF, 0xFF, 0xFF,
  0xC0, 0x03, 0xFF, 0xFF, 0xFF, 0xFF, 0xC0, 0x01, 0xFF, 0xFF, 0xFF, 0xFF, 0xC0, 0x00, 0xFF, 0xFF,
  0xFF, 0xFF, 0xC0, 0x00, 0xFF, 0xFF, 0xFF, 0xFF, 0xC0, 0x01, 0xFF, 0xFF, 0xFF, 0xFF, 0xC0, 0x03,
  0xFF, 0xFF, 0xFF, 0xFF, 0xC0, 0x07, 0xFF, 0xFF, 0xFF, 0xFF, 0xC0, 0x0F, 0xFF, 0xFF, 0x7F, 0xFF,
  0xC0, 0x1F, 0xFF, 0xFE, 0x7F, 0xFF, 0xC0, 0x3F, 0xFF, 0xFE, 0x7F, 0xFF, 0xC0, 0x7F, 0xFF, 0xFE,
  0x3F, 0xFF, 0xC0, 0xFF, 0xFF, 0xFC, 0x3F, 0xFF, 0xC1, 0xFF, 0xFF, 0xFC, 0x3F, 0xFF, 0xC3, 0xFF,
  0xFF, 0xFC, 0x1F, 0xFF, 0xC7, 0xFF, 0xFF, 0xF8, 0x0F, 0xFF, 0xFF, 0xFF, 0xFF, 0xF0, 0x0F, 0xFF,
  0xFF, 0xFF, 0xFF, 0xF0, 0x07, 0xFF, 0xFF, 0xFF, 0xFF, 0xE0, 0x03, 0xFF, 0xFF, 0xFF, 0xFF, 0xC0,
  0x01, 0xFF, 0xFF, 0xFF, 0xFF, 0x80, 0x00, 0xFF, 0xFF, 0xFF, 0xFF, 0x00, 0x00, 0x7F, 0xFF, 0xFF,
  0xFE, 0x00, 0x00, 0x3F, 0xFF, 0xFF, 0xFC, 0x00, 0x00, 0x0F, 0xFF, 0xFF, 0xF0, 0x00, 0x00, 0x07,
  0xFF, 0xFF, 0xE0, 0x00, 0x00, 0x00, 0xFF, 0xFF, 0x00, 0x00, 0x00, 0x00, 0x1F, 0xF8, 0x00, 0x00
};

static const unsigned char PROGMEM voldown [] = {
  0x00, 0x00, 0x1F, 0xF8, 0x00, 0x00, 0x00, 0x00, 0xFF, 0xFF, 0x00, 0x00, 0x00, 0x07, 0xFF, 0xFF,
  0xE0, 0x00, 0x00, 0x0F, 0xFF, 0xFF, 0xF0, 0x00, 0x00, 0x3F, 0xFF, 0xFF, 0xFC, 0x00, 0x00, 0x7F,
  0xFF, 0xFF, 0xFE, 0x00, 0x00, 0xFF, 0xFF, 0xFF, 0xFF, 0x00, 0x01, 0xFF, 0xFF, 0xFF, 0xFF, 0x80,
  0x03, 0xFF, 0xFF, 0xFF, 0xFF, 0xC0, 0x07, 0xFF, 0xFF, 0xFF, 0xFF, 0xE0, 0x0F, 0xFF, 0xFF, 0xFF,
  0xFF, 0xF0, 0x0F, 0xFF, 0xFF, 0xFF, 0xFF, 0xF0, 0x1F, 0xFF, 0xFF, 0x8F, 0xFF, 0xF8, 0x3F, 0xFF,
  0xFF, 0x0F, 0xFF, 0xFC, 0x3F, 0xFF, 0xFE, 0x0F, 0xFF, 0xFC, 0x3F, 0xFF, 0xFC, 0x0F, 0xFF, 0xFC,
  0x7F, 0xFF, 0xF8, 0x0F, 0xFF, 0xFE, 0x7F, 0xFF, 0xF0, 0x0F, 0xFF, 0xFE, 0x7F, 0xFF, 0xE0, 0x0F,
  0xFF, 0xFE, 0xFF, 0xFF, 0xC0, 0x0F, 0xFF, 0xFF, 0xFF, 0xFF, 0x80, 0x0F, 0xFF, 0xFF, 0xFF, 0xFF,
  0x00, 0x0F, 0xFF, 0xFF, 0xFF, 0xFE, 0x00, 0x0F, 0xFF, 0xFF, 0xFF, 0xFC, 0x00, 0x0F, 0xFF, 0xFF,
  0xFF, 0xFC, 0x00, 0x0F, 0xFF, 0xFF, 0xFF, 0xFE, 0x00, 0x0F, 0xFF, 0xFF, 0xFF, 0xFF, 0x00, 0x0F,
  0xFF, 0xFF, 0xFF, 0xFF, 0x80, 0x0F, 0xFF, 0xFF, 0xFF, 0xFF, 0xC0, 0x0F, 0xFF, 0xFF, 0x7F, 0xFF,
  0xE0, 0x0F, 0xFF, 0xFE, 0x7F, 0xFF, 0xF0, 0x0F, 0xFF, 0xFE, 0x7F, 0xFF, 0xF8, 0x0F, 0xFF, 0xFE,
  0x3F, 0xFF, 0xFC, 0x0F, 0xFF, 0xFC, 0x3F, 0xFF, 0xFE, 0x0F, 0xFF, 0xFC, 0x3F, 0xFF, 0xFF, 0x0F,
  0xFF, 0xFC, 0x1F, 0xFF, 0xFF, 0x8F, 0xFF, 0xF8, 0x0F, 0xFF, 0xFF, 0xFF, 0xFF, 0xF0, 0x0F, 0xFF,
  0xFF, 0xFF, 0xFF, 0xF0, 0x07, 0xFF, 0xFF, 0xFF, 0xFF, 0xE0, 0x03, 0xFF, 0xFF, 0xFF, 0xFF, 0xC0,
  0x01, 0xFF, 0xFF, 0xFF, 0xFF, 0x80, 0x00, 0xFF, 0xFF, 0xFF, 0xFF, 0x00, 0x00, 0x7F, 0xFF, 0xFF,
  0xFE, 0x00, 0x00, 0x3F, 0xFF, 0xFF, 0xFC, 0x00, 0x00, 0x0F, 0xFF, 0xFF, 0xF0, 0x00, 0x00, 0x07,
  0xFF, 0xFF, 0xE0, 0x00, 0x00, 0x00, 0xFF, 0xFF, 0x00, 0x00, 0x00, 0x00, 0x1F, 0xF8, 0x00, 0x00
};
static const unsigned char PROGMEM power [] = {
  0x00, 0x00, 0x1F, 0xF8, 0x00, 0x00, 0x00, 0x00, 0xFF, 0xFF, 0x00, 0x00, 0x00, 0x07, 0xFF, 0xFF,
  0xE0, 0x00, 0x00, 0x0F, 0xFF, 0xFF, 0xF0, 0x00, 0x00, 0x3F, 0xFF, 0xFF, 0xFC, 0x00, 0x00, 0x7F,
  0xFF, 0xFF, 0xFE, 0x00, 0x00, 0xFF, 0xFF, 0xFF, 0xFF, 0x00, 0x01, 0xFF, 0xFF, 0xFF, 0xFF, 0x80,
  0x03, 0xFF, 0xF0, 0x1F, 0xFF, 0xC0, 0x07, 0xFF, 0x80, 0x03, 0xFF, 0xE0, 0x0F, 0xFE, 0x00, 0x00,
  0xFF, 0xF0, 0x0F, 0xFC, 0x00, 0x00, 0x7F, 0xF0, 0x1F, 0xF8, 0x00, 0x00, 0x3F, 0xF8, 0x3F, 0xF8,
  0x03, 0x80, 0x1F, 0xFC, 0x3F, 0xF8, 0x1F, 0xF0, 0x0F, 0xFC, 0x3F, 0xFC, 0x7F, 0xFC, 0x07, 0xFC,
  0x7F, 0xFF, 0xFF, 0xFE, 0x07, 0xFE, 0x7F, 0xFF, 0xFF, 0xFF, 0x03, 0xFE, 0x7F, 0xFF, 0xFF, 0xFF,
  0x03, 0xFE, 0xFF, 0xFF, 0xFF, 0xFF, 0x83, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0x81, 0xFF, 0xFF, 0x00,
  0x00, 0xFF, 0x81, 0xFF, 0xFF, 0x00, 0x00, 0xFF, 0xC1, 0xFF, 0xFF, 0x00, 0x00, 0xFF, 0xC1, 0xFF,
  0xFF, 0x00, 0x00, 0xFF, 0xC1, 0xFF, 0xFF, 0x00, 0x00, 0xFF, 0x81, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
  0x81, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0x83, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0x03, 0xFF, 0x7F, 0xFF,
  0xFF, 0xFF, 0x03, 0xFE, 0x7F, 0xFF, 0xFF, 0xFE, 0x07, 0xFE, 0x7F, 0xFC, 0x7F, 0xFC, 0x07, 0xFE,
  0x3F, 0xF8, 0x1F, 0xF0, 0x0F, 0xFC, 0x3F, 0xF8, 0x03, 0x80, 0x1F, 0xFC, 0x3F, 0xF8, 0x00, 0x00,
  0x3F, 0xFC, 0x1F, 0xFC, 0x00, 0x00, 0x7F, 0xF8, 0x0F, 0xFE, 0x00, 0x00, 0xFF, 0xF0, 0x0F, 0xFF,
  0x80, 0x03, 0xFF, 0xF0, 0x07, 0xFF, 0xF0, 0x1F, 0xFF, 0xE0, 0x03, 0xFF, 0xFF, 0xFF, 0xFF, 0xC0,
  0x01, 0xFF, 0xFF, 0xFF, 0xFF, 0x80, 0x00, 0xFF, 0xFF, 0xFF, 0xFF, 0x00, 0x00, 0x7F, 0xFF, 0xFF,
  0xFE, 0x00, 0x00, 0x3F, 0xFF, 0xFF, 0xFC, 0x00, 0x00, 0x0F, 0xFF, 0xFF, 0xF0, 0x00, 0x00, 0x07,
  0xFF, 0xFF, 0xE0, 0x00, 0x00, 0x00, 0xFF, 0xFF, 0x00, 0x00, 0x00, 0x00, 0x1F, 0xF8, 0x00, 0x00
};

// For better pressure precision, we need to know the resistance
// between X+ and X- Use any multimeter to read it
// For the one we're using, its 300 ohms across the X plate
TouchScreen ts = TouchScreen(XP, YP, XM, YM, 100);

//TFT 객체 생성
//Adafruit_TFTLCD_AS tft(LCD_CS, LCD_CD, LCD_WR, LCD_RD, LCD_RESET);
//Adafruit_TFTLCD tft(LCD_CS, LCD_CD, LCD_WR, LCD_RD, LCD_RESET);

//리모콘 수신 객체 생성
IRrecv irrecv(RECV_PIN);
decode_results results;

/////// 각종 전역 설정값////////////////////////////////////////
uint16_t volColor = getColor(30, 135, 255); // 볼륨 테두리 미터 색상 - 속도때문에 전역으로 한번 설정 - 나중에 #define으로 변경할 것
int screenMode = _MAIN_SCREEN ;
bool playDSD = false;
bool prevPlayDSD = false;
int powerStatus = _POWER_OFF;
bool bLearningMode = false;
bool bMuteStatus = false;
bool bDisplayUnlock = true;

// 셋업메뉴 설정값
int firRollOff[4] = {0, 0, 0, 0};   // fast
int iirBandwidth[4] = {1, 1, 1, 1}; // 50k
int dpllBandwidth[4] = {0, 0, 0, 0}; // Best DPLL
int dpllMode[4] = {1, 1, 1, 1};     // x1(Normal)
int quantizer[4] = {0, 0, 0, 0};    // 6bit True Differential
int jitterReduction[4] = {1, 1, 1, 1}; // On
int notchDelay[4] = {0, 0, 0, 0};   // No Notch
byte saveStamp;

//셋업메뉴 화면에서 취소 시 설정값을 복원하기 위한 임시 변수
int _firRollOff;
int _iirBandwidth;
int _dpllBandwidth;
int _dpllMode;
int _quantizer;
int _jitterReduction;
int _notchDelay;
boolean _bypassOSF;

//리모콘 설정값
unsigned long rmtPowerOnOff = 0;
unsigned long rmtVolUp = 0;
unsigned long rmtVolDown = 0;
unsigned long rmtInputSelect = 0;
unsigned long rmtInputUSB = 0;
unsigned long rmtInputOpt = 0;
unsigned long rmtInputCoax = 0;
unsigned long rmtInputAES = 0;
unsigned long rmtMute = 0;

#define _POWER_BUTTON 0
#define _VOLUP_BUTTON 1
#define _VOLDOWN_BUTTON 2
#define _INPUT_BUTTON 3
#define _INPUT_DRIECT_BUTTON_USB 4
#define _INPUT_DRIECT_BUTTON_OPT 5
#define _INPUT_DRIECT_BUTTON_COAX 6
#define _INPUT_DRIECT_BUTTON_AES 7
#define _MUTE_BUTTON 8
int currButton = -1 ;

// EEPROM에 환경설정을 저장할 때 사용하는 구조체
struct dacSettings_t
{
  int firRollOff[4];
  int iirBandwidth[4];
  int dpllBandwidth[4];
  int dpllMode[4];
  int quantizer[4];
  int jitterReduction[4];
  int notchDelay[4];
  boolean bypassOSF;

  unsigned long rmtPowerOnOff;
  unsigned long rmtVolUp;
  unsigned long rmtVolDown;
  unsigned long rmtInputSelect;
  unsigned long rmtInputUSB;
  unsigned long rmtInputOpt;
  unsigned long rmtInputCoax;
  unsigned long rmtInputAES;
  unsigned long rmtMute;

  byte saveStamp;
} dacSettings;

// CONSTANT DEFINITION
/******************* Code Customization Section *********************/

/* First: Choose the clock frequency you have and comment the other */

//#define USE80MHZ
#define USE100MHZ

//#define DEBUG
//#define USE_ADAFRUIT_SHIELD_PINOUT
/* Second: Choose your configuration

   | CONFIGURATION       | #define DUALMONO | #define TPAPHASE |
   |---------------------|------------------|------------------|
   | Dual mono in-phase  | un-comment       | comment          |
   | Dual mono TPA phase | un-comment       | un-comment       |
   | Stereo              | comment          | comment          |
   |---------------------|------------------|------------------|    */

#define DUALMONO
//#define TPAPHASE  //TPA는  Twisted Pear Audio사의 9018 DAC. 두 모듈의 극성이 반대임.

/* Optionally choose the number of inputs. 6 is the max without
   modifying the code. You could lower the number of input choices
   here. for example if you only want to see 2 choices, modify the
   code lke this: #define ICHO 2                                    */

// #define ICHO 4

/* Make sure you use the correct chip address for each board

   for stereo ES9018: use address 0x90
   for dual mono: Use address 0x90 for mono left ES9018
                  Use address 0x92 for mono right ES9018

   Since Arduino uses 7-bit address, I converted the addresses
   to 7-bit by removing the least significant bit thus

   Address 0x48 for Stereo or mono left
   Address 0x49 for mono right                                       */

/***************** END Code Customization Section *******************/

#define DEFAULTATTNU 0x5A //-50 dB this is 50x2=100 or 0x64. Sabre32 is 0 to -127dB in .5dB steps //최초 볼륨은 최대로 설정함. (프리앰프에서 볼륨 조정하는 것으로 가정)
#define MAXATTNU 0x7F     //-99dB this is 99X2=198 or 0xC6 -Can go higher but LCD shows 2 digits
#define MINATTNU 0x00     //-0 dB -Maximum volume is -0 dB
#define DIM 0x8C          //-70 dB this is 70x2=140 or 0x8C. Dim volume
#define RAMP 10           // Additional msec delay per 1 db for ramping up to volume after dim

#define INTERVAL_SAMPLE 1          // Time interval in SECONDS for refreshing the sample rate
#define INTERVAL_BOUNCE 2          // Time in milliseconds to debounce the rotary encoder
#define INTERVAL_SWITCHBOUNCE 250  // Time in milliseconds to debounce switch
#define INTERVAL_SELECT 5          // Time in sec to exit select mode when no activity

// VARIABLE DECLARATION

// Register variables: used for registers that have lots of options. They are initialized here
// with valid values, but will eventually be overwritten by the values in EEPROM
byte reg14 = 0xF9;  // Default value for register 14. We use a variable for reg 14 because it controls
// several parameters: IIR, FIR, differential whereas the other registers typically
// controls a single parameter.
byte reg25 = 0;     // 0= allow all settings
byte reg17 = 0x1D;  // Auto SPDIF, 8-channel mode, other defaults
// reg17 is used for stereo and for MONO. It is used for both chips
#ifdef DUALMONO
byte reg17R = 0x9D; // Auto SPDIF, MONO RIGHT CHANNEL, other defaults. Used for reg 17 right only
#endif DUALMONO

byte reg10 = 0xCE; // jitter ON, dacs unmute, other defaults (0xFE also I2S)

unsigned long displayMillis = 0;   // Stores last recorded time for display interval
unsigned long debounceMillis = 0;  // Stores last recorded time for switch debounce interval
unsigned long selectMillis = 0;    // Stores last recorded time for being in select mode
unsigned long sr = 1;              // Holds the value for the incoming sample rate
unsigned long prev_sr = 1;        // 샘플링 레이트의 리프레시는 변경되었을 때만 수행(화면 깜빡거림 방지)

int input = 0;               // The current input to the DAC //0: USB, 1: OPT, 2:COAX, 3: AES/EBU
float currAttnu = DEFAULTATTNU; // Variable to hold the current attenuation value

byte select;             // To record current select position (FIL, VOL, DPLL, etc)

boolean selectMode;      // To indicate whether in select mode or not
boolean SPDIFValid;      // To indicate whether SPDIF valid data
boolean spdifIn;         // To indicate whether in I2S/DSD or SPDIF input format mode
boolean bypassOSF = false; // false=no bypass; This is the condition at startup
boolean SRExact = false;  // Display exact sample rate value; false = display nominal value
boolean dimmed = false;  // To indicate dim (mute) or not
byte pulse = 0;          // Used by the "heartbeat" display
byte Status;             // To hold value of Sabre32 status register

unsigned long pushedRemoconButton;

#define MINPRESSURE 50
#define MAXPRESSURE 1000

/////////////////////////////////////////// TFT 그래픽 및 터치 처리 관련 ////////////////////////////////////////////////////////////////

// LCD 화면 초기화
void initLCD()
{
  tft.reset();
  tft.begin(CONTROLLER_ID);
  tft.setRotation(3);
  if (powerStatus == _POWER_OFF)
  {
    tft.fillScreen(BLACK);
  }
  else if (powerStatus == _POWER_ON)
  {
    //SG-D5 기동 화면
    tft.fillScreen(BLACK);
    tft.setTextColor(WHITE);
    tft.setTextSize(1);
    //tft.drdrawCentreString("Starting SG-D5.. ", 160, 80, 4);
    //drdrawCentreString("Starting SG-D5.. ", 160, 80, 4);
    drawCentreString("Starting SG-D5.. ", 160, 80, 4);


    //tft.drawCentreString(VER_INFO, 160, 110, 4);
    drawCentreString(VER_INFO, 160, 110, 4);
    tft.setTextColor(GREEN);
    //tft.drawCentreString("http://cafe.naver.com/myspeaker", 160, 140, 2);
    drawCentreString("http://cafe.naver.com/myspeaker", 160, 140, 2);
    delay(1500);

    //처음 가동시에는 무조건 메인화면 (0)
    screenMode = _MAIN_SCREEN;
    setDisplay ();
  }
}
//화면 모드(메인, 메뉴1, 메뉴2... )에 따라 화면을 그려줌
void setDisplay()
{
  tft.setRotation(3);
  tft.fillScreen(BLACK);
  tft.setTextSize(1);
  if (screenMode == _MAIN_SCREEN)
  {
    bLearningMode = false;
    // 화면 바탕 색상 및 배경설정
    //tft.fillRect(0, 0, 320, 240, getColor(50, 78, 150));
    //tft.fillRect(0, 17, 225, 140, BLACK);
    //tft.fillCircle(230, 87, 68, WHITE);
    //tft.fillCircle(230, 87, 60, BLACK);

    // 하단 버튼 영역 그리기
    uint16_t barCol = BLACK;
    for (int i = 240; i >= 170; i -= 4)
    {
      tft.fillRect(0, i, 320, 4, barCol++);
    }
    tft.drawLine (0, 173, 340, 173, getColor(110, 110, 140));

    // 버튼 그리기
    tft.setRotation(0);
    uint16_t btnColor = getColor(160, 165, 200);
    tft.drawBitmap(240 - BUTTON_MARGIN_X - BUTTON_R * 2, BUTTON_R * 8 + BUTTON_D * 4 + BUTTON_MARGIN_Y, power,  BUTTON_R * 2, BUTTON_R * 2, btnColor);
    tft.drawBitmap(240 - BUTTON_MARGIN_X - BUTTON_R * 2, BUTTON_R * 6 + BUTTON_D * 3 + BUTTON_MARGIN_Y, setupmenu,  BUTTON_R * 2, BUTTON_R * 2, btnColor);
    tft.drawBitmap(240 - BUTTON_MARGIN_X - BUTTON_R * 2, BUTTON_R * 4 + BUTTON_D * 2 + BUTTON_MARGIN_Y, inputselect,  BUTTON_R * 2, BUTTON_R * 2, btnColor);
    tft.drawBitmap(240 - BUTTON_MARGIN_X - BUTTON_R * 2, BUTTON_R * 2 + BUTTON_D * 1 + BUTTON_MARGIN_Y, volup,  BUTTON_R * 2, BUTTON_R * 2, btnColor);
    tft.drawBitmap(240 - BUTTON_MARGIN_X - BUTTON_R * 2, BUTTON_R * 0 + BUTTON_D * 0 + BUTTON_MARGIN_Y, voldown,  BUTTON_R * 2, BUTTON_R * 2, btnColor);


    printMute(); //평소엔 "DB"를 , 뮤트된 상태면 "mute" 표시

    //tft.fillRect(181, 85, 12, 6, WHITE);
    //현재 인풋 표시
    printInput();

    // 현재 볼륨 표시
    tft.fillRect(VOL_POSX - 20, VOL_POSY + SEG_LENGTH, 13, 4, WHITE); //(-)표시
    displayVolume();
  }
  else if (screenMode == _MENU_SCREEN_1) //설정메뉴 첫페이지
  {
    bLearningMode = false;
    // 화면 바탕 색상 및 배경설정
    tft.setRotation(3);
    tft.fillRect(0, 0, 320, 190, BLACK);
    tft.fillRect(0, 190, 320, 50, WHITE);

    //메뉴 레이블 LCD에 표시
    printSetup(0, "FIR Roll-Off", 1);
    printSetup(0, "IIR BW", 2);
    printSetup(0, "DPLL BW", 3);
    printSetup(0, "DPLL Mode", 4);
    printSetup(0, "OSF Bypass", 5);

    //메뉴(1) 설정값을 LCD에 표시
    //FIR Roll-Off
    setAndPrintFirFilter(true);

    //IIR Bandwith
    setAndPrintIirFilter(true);

    //DPLL Bandwidth
    setAndPrintDPLLBandwidth(true);

    //DPLL Mode
    setAndPrintDPLLMode(true);

    //Oversampling
    setAndPrintBypassOSF(true);

    printMenuButton();
    printFirmwareVer();
  }
  else if (screenMode == _MENU_SCREEN_2) //설정메뉴 두번째 페이지
  {
    bLearningMode = false;
    tft.setRotation(3);
    tft.fillRect(0, 0, 320, 190, BLACK);
    tft.fillRect(0, 190, 320, 50, WHITE);

    printSetup(0, "Quantizer", 1);
    printSetup(0, "Jit.Reduction", 2);
    printSetup(0, "Notch Delay", 3);
    printSetup(0, "Reset Default", 5);

    //메뉴(2) 설정값을 LCD에 표시
    //Quantizer
    setAndPrintQuantizer(true);

    //Jitter Reduction
    setAndPrintJitterReduction(true);

    //Notch Delay
    setAndPrintNotch(true);

    //Reset Message
    printSetup (1, "", 4);

    printMenuButton();
    printFirmwareVer();
  }
  else if (screenMode == _MENU_SCREEN_3) //설정메뉴 세번째 페이지 - 리모콘 학습 1
  {
    bLearningMode = true;
    tft.setRotation(3);
    tft.fillRect(0, 0, 320, 190, BLACK);
    tft.fillRect(0, 190, 320, 50, WHITE);

    printSetup(0, "PowerOn/Off", 1);
    printSetup(0, "Volume Up", 2);
    printSetup(0, "Volume Down", 3);
    printSetup(0, "Input Select", 4);
    printSetup(0, "Mute", 5);

    //메뉴(3) 설정값을 LCD에 표시
    char buf[11];
    sprintf(buf, "%lx", rmtPowerOnOff);
    printSetup (1, buf, 1);
    sprintf(buf, "%lx", rmtVolUp );
    printSetup (1, buf, 2);
    sprintf(buf, "%lx", rmtVolDown );
    printSetup (1, buf, 3);
    sprintf(buf, "%lx", rmtInputSelect );
    printSetup (1, buf, 4);
    sprintf(buf, "%lx", rmtMute );
    printSetup (1, buf, 5);

    printMenuButton();
    printFirmwareVer();
  } else if (screenMode == _MENU_SCREEN_4) //설정메뉴 네번째 페이지 - 리모콘 학습 2
  {
    bLearningMode = true;
    tft.setRotation(3);
    tft.fillRect(0, 0, 320, 190, BLACK);
    tft.fillRect(0, 190, 320, 50, WHITE);

    printSetup(0, "USB In", 1);
    printSetup(0, "Opt In", 2);
    printSetup(0, "Coax In", 3);
    printSetup(0, "AES/EBU In", 4);

    //메뉴(4) 설정값을 LCD에 표시
    char buf[11];
    sprintf(buf, "%lx", rmtInputUSB );
    printSetup (1, buf, 1);
    sprintf(buf, "%lx", rmtInputOpt  );
    printSetup (1, buf, 2);
    sprintf(buf, "%lx", rmtInputCoax  );
    printSetup (1, buf, 3);
    sprintf(buf, "%lx", rmtInputAES  );
    printSetup (1, buf, 4);

    printMenuButton();
    printFirmwareVer();
  }
}

void printFirmwareVer()
{
  tft.setTextColor(BLACK);
  //tft.drawString(VER_INFO, 20, 210, 2);
  drawString(VER_INFO, 20, 210, 2);
}

//메뉴 설정시 하단 버튼을 그려줌
void printMenuButton()
{
  tft.fillCircle ( 155, 214, 18, BLACK);
  tft.fillCircle ( 205, 214, 18, BLACK);
  tft.fillCircle ( 285, 214, 18, BLACK);
  tft.setTextColor(WHITE);
  if (screenMode == _MENU_SCREEN_1 )
    // tft.drawString ( "1", 150, 202, 4);
    drawString ( "1", 150, 202, 4);
  else if (screenMode == _MENU_SCREEN_2)
    //tft.drawString ( "2", 150, 202, 4);
    drawString ( "2", 150, 202, 4);
  else if (screenMode == _MENU_SCREEN_3)
    //tft.drawString ( "3", 150, 202, 4);
    drawString ( "3", 150, 202, 4);
  else if (screenMode == _MENU_SCREEN_4)
    //tft.drawString ( "4", 150, 202, 4);
  //tft.drawString ( "OK", 198, 205, 2);
  //tft.drawString ( "x", 278, 202, 4);
  drawString ( "4", 150, 202, 4);
  drawString ( "OK", 198, 205, 2);
  drawString ( "x", 278, 202, 4);
}

void printMute()
{
  // 정상인 경우는 볼륨 하단에 "dB"를, 뮤트일 때는 "Mute" 표시
  tft.setRotation(3);
  tft.setTextSize(1);
  if (!bMuteStatus) {
    tft.fillRoundRect(210, 139, 42, 15, 5, BLUE);
    tft.setTextColor(WHITE);
    tft.setCursor(225, 143);
    tft.println("dB");
  } else {
    tft.fillRoundRect(210, 139, 42, 15, 5, WHITE);
    tft.setTextColor(BLACK);
    tft.setCursor(220, 143);
    tft.println("Mute");
  }
}

/// 현재 입력선택을 LCD 에 표시
void printInput()
{
  tft.setRotation(3);
  tft.fillRect(20, 40, 110, 32, BLACK);
  tft.setTextColor(WHITE);
  tft.setTextSize(1);
  prev_sr = 0;
  bDisplayUnlock = true;
  if (input == 0)
  {
///tft.drawString("USB", 20, 40, 4);
    drawString("USB", 20, 40, 4);

    printInputFormat("Unlocked");
    printSamplingRate("");
  }
  else if (input == 1)
  {
    //tft.drawString("Optical", 20, 40, 4);
    drawString("Optical", 20, 40, 4);
    drawString("Optical", 20, 40, 4);
    printInputFormat("Unlocked");
    printSamplingRate("");
  }
  else if (input == 2)
  {
    //tft.drawString("Coaxial", 20, 40, 4);
    drawString("Coaxial", 20, 40, 4);
    printInputFormat("Unlocked");
    printSamplingRate("");
  }
  else if (input == 3)
  {
    //tft.drawString("AES/EBU", 20, 40, 4);
    drawString("AES/EBU", 20, 40, 4);
    printInputFormat("Unlocked");
    printSamplingRate("");
  }
  delay(300);
}

void print7Seg(byte n, int rotation)
{
  tft.setRotation(rotation);
  int i = n / 10;

  int r = SEG_WIDTH / 2;
  int x1 = VOL_POSX;
  int x2 = x1 + SEG_LENGTH;
  int y1 = VOL_POSY;
  int y2 = y1 + SEG_LENGTH;
  int y3 = y1 + SEG_LENGTH * 2;


  if (i == 0 || i == 2 || i == 3 || i == 5 || i == 6 || i == 7 || i == 8 || i == 9 || i == 0 )
    tft.fillRoundRect(x1, y1, SEG_LENGTH, SEG_WIDTH, r, SEG_COL);
  else
    tft.fillRoundRect(x1, y1, SEG_LENGTH, SEG_WIDTH, r, BLACK);
  if ( i == 2 || i == 3 || i == 4 || i == 5 || i == 6 || i == 8 || i == 9 )
    tft.fillRoundRect(x1, y2, SEG_LENGTH, SEG_WIDTH, r, SEG_COL);
  else
    tft.fillRoundRect(x1, y2, SEG_LENGTH, SEG_WIDTH, r, BLACK);
  if ( i == 2 || i == 3 || i == 5 || i == 6 || i == 8 || i == 9 || i == 0 )
    tft.fillRoundRect(x1, y3, SEG_LENGTH, SEG_WIDTH, r, SEG_COL);
  else
    tft.fillRoundRect(x1, y3, SEG_LENGTH, SEG_WIDTH, r, BLACK);

  if ( i == 4 || i == 5 || i == 6 || i == 8 || i == 9 || i == 0 )
    tft.fillRoundRect(x1 - r, y1 + r, SEG_WIDTH, SEG_LENGTH, r, SEG_COL);
  else
    tft.fillRoundRect(x1 - r, y1 + r, SEG_WIDTH, SEG_LENGTH, r, BLACK);
  if ( i == 2 || i == 6 || i == 8 || i == 0 )
    tft.fillRoundRect(x1 - r, y2 + r, SEG_WIDTH, SEG_LENGTH, r, SEG_COL);
  else
    tft.fillRoundRect(x1 - r, y2 + r, SEG_WIDTH, SEG_LENGTH, r, BLACK);
  if ( i == 1 || i == 2 || i == 3 || i == 4 || i == 7 || i == 8 || i == 9 || i == 0 )
    tft.fillRoundRect(x2 - r, y1 + r, SEG_WIDTH, SEG_LENGTH, r, SEG_COL);
  else
    tft.fillRoundRect(x2 - r, y1 + r, SEG_WIDTH, SEG_LENGTH, r, BLACK);
  if ( i == 1 || i == 3 || i == 4 || i == 5 || i == 6 || i == 7 || i == 8 || i == 9 || i == 0 )
    tft.fillRoundRect(x2 - r, y2 + r, SEG_WIDTH, SEG_LENGTH, r, SEG_COL);
  else
    tft.fillRoundRect(x2 - r, y2 + r, SEG_WIDTH, SEG_LENGTH, r, BLACK);


  i = n % 10;
  x1 = x1 + SEG_LENGTH + 2 * r + 0.4 * SEG_LENGTH;
  x2 = x1 + SEG_LENGTH ;
  if (i == 0 || i == 2 || i == 3 || i == 5 || i == 6 || i == 7 || i == 8 || i == 9 || i == 0 )
    tft.fillRoundRect(x1, y1, SEG_LENGTH, SEG_WIDTH, r, SEG_COL);
  else
    tft.fillRoundRect(x1, y1, SEG_LENGTH, SEG_WIDTH, r, BLACK);
  if ( i == 2 || i == 3 || i == 4 || i == 5 || i == 6 || i == 8 || i == 9 )
    tft.fillRoundRect(x1, y2, SEG_LENGTH, SEG_WIDTH, r, SEG_COL);
  else
    tft.fillRoundRect(x1, y2, SEG_LENGTH, SEG_WIDTH, r, BLACK);
  if ( i == 2 || i == 3 || i == 5 || i == 6 || i == 8 || i == 9 || i == 0 )
    tft.fillRoundRect(x1, y3, SEG_LENGTH, SEG_WIDTH, r, SEG_COL);
  else
    tft.fillRoundRect(x1, y3, SEG_LENGTH, SEG_WIDTH, r, BLACK);

  if ( i == 4 || i == 5 || i == 6 || i == 8 || i == 9 || i == 0 )
    tft.fillRoundRect(x1 - r, y1 + r, SEG_WIDTH, SEG_LENGTH, r, SEG_COL);
  else
    tft.fillRoundRect(x1 - r, y1 + r, SEG_WIDTH, SEG_LENGTH, r, BLACK);
  if ( i == 2 || i == 6 || i == 8 || i == 0 )
    tft.fillRoundRect(x1 - r, y2 + r, SEG_WIDTH, SEG_LENGTH, r, SEG_COL);
  else
    tft.fillRoundRect(x1 - r, y2 + r, SEG_WIDTH, SEG_LENGTH, r, BLACK);
  if ( i == 1 || i == 2 || i == 3 || i == 4 || i == 7 || i == 8 || i == 9 || i == 0 )
    tft.fillRoundRect(x2 - r, y1 + r, SEG_WIDTH, SEG_LENGTH, r, SEG_COL);
  else
    tft.fillRoundRect(x2 - r, y1 + r, SEG_WIDTH, SEG_LENGTH, r, BLACK);
  if ( i == 1 || i == 3 || i == 4 || i == 5 || i == 6 || i == 7 || i == 8 || i == 9 || i == 0 )
    tft.fillRoundRect(x2 - r, y2 + r, SEG_WIDTH, SEG_LENGTH, r, SEG_COL);
  else
    tft.fillRoundRect(x2 - r, y2 + r, SEG_WIDTH, SEG_LENGTH, r, BLACK);
}

// 볼륨표시 숫자 바깥의 속도계 그리기
void drawArc(int vol)
{
  tft.setRotation(3);

  int radius = 65;
  int arcX, arcY;
  int posX = 230;
  int posY = 87;
  // 속도 증가를 위해 삼각함수 호출하지 않고 미리 계산값을 테이블로 만들어서 처리
  float sinRad[] = {
    0.644217687, 0.764328937, 0.867423226, 0.939099356, 0.98544973, 0.999999683, 0.983985947, 0.939645474, 0.868214583, 0.765354953,
    0.645434998, 0.498261642, 0.344393467, 0.170751829, 0.001592653, -0.177462425, -0.341401278, -0.504158548, -0.642998742, -0.763300983,
    -0.866629667, -0.938550857, -0.985177782, -0.999997146, -0.984268583, -0.940189208, -0.864012316, -0.766379027, -0.638990604
  };
  float cosRad[] = {
    0.7660 , 0.6428 , 0.5000 , 0.3420 , 0.1736 , 0.0000 , -0.1736 , -0.3420 , -0.5000 , -0.6428 ,
    -0.7660 , -0.8660 , -0.9397 , -0.9848 , -1.0000 , -0.9848 , -0.9397 , -0.8660 , -0.7660 , -0.6428 ,
    -0.5000 , -0.3420 , -0.1736 , 0.0000 , 0.1736 , 0.3420 , 0.5000 , 0.6428 , 0.7660
  };

  for (int i = 0 ; i < 29 ; i ++)
  {
    arcX = radius * sinRad[i];
    arcY = radius * cosRad[i];

    if (i < (vol / 3)) //
      tft.fillCircle(arcX + posX, arcY + posY, 3, WHITE);
    else
      tft.fillCircle(arcX + posX, arcY + posY, 3, volColor);
  }
}

void displayVolume()
{
  print7Seg(currAttnu / 2, 3);
  drawArc(currAttnu / 2);
}

// 현재 샘플링 레이트와 신호 포맷(PCM/DSD)를 매 INTERVAL_SAMPLE 마다 화면에 표시
void refreshSampleRate()
{
  if (screenMode == _MAIN_SCREEN && powerStatus == _POWER_ON) {
    tft.setRotation(3);
    tft.setCursor(10, 50);
    tft.setTextSize(2);
    tft.setTextColor(WHITE);

    // Print the sample rate, input and lock (once every "INTERVAL_SAMPLE" time)
    if ((millis() - displayMillis > INTERVAL_SAMPLE * 1000)) {
      displayMillis = millis(); // Saving last time we display sample rate

      Status = readRegister(27); // Read status register
      //Serial.println(Status, BIN);
      if (Status & B00000100)
        SPDIFValid = true; // Determine if valid spdif data
      else
        SPDIFValid = false;              // SR calculation depends on I2S or SPDIf

      // Update the sample rate display if there is a lock (otherwise, SR=0)

      if (Status & B00000001) {    // There is a lock in a signal
        bDisplayUnlock = false;
        sr = 0;
        sr = sampleRate();         // Get the sample rate from register

        if (Status & B00001000) {  // Determines if DSD and print DSD sample rate
          Serial.println ("_DSD");
          if (!playDSD || abs(sr * 64 - prev_sr) > 10)
          {
            sr *= 64;                // It is DSD, the sample rate is 64x
            prev_sr = sr;
            printInputFormat("DSD");

            if (SRExact == true)
              Serial.print(sr, DEC);    // Print DSD sample rate in exact format
            else                     // Print DSD sample rate in nominal format
              if (sr > 6143000)
                printSamplingRate("6.1 MHz");
              else if (sr > 5644000)
                printSamplingRate("5.6 MHz");
              else if (sr > 3071000)
                printSamplingRate("3.0 MHz");
              else if (sr > 2822000)
                printSamplingRate("2.8 MHz");
              else
                printSamplingRate("UNKNOWN");
          }
          playDSD = true;
          pinMode(_DSD_PLAY, OUTPUT);
          digitalWrite(_DSD_PLAY, HIGH);
        }
        else {                     // If not DSD then it is I2S or SPDIF
          pinMode(_DSD_PLAY, OUTPUT);
          digitalWrite(_DSD_PLAY, LOW);
          playDSD = false;
          Serial.println ("_PCM");
          Serial.print ("sr:");
          Serial.println(sr, DEC);
          Serial.print ("prev_sr:");
          Serial.println(prev_sr, DEC);

          if (abs(sr - prev_sr) > 10)
          {
            prev_sr = sr;
            if (SPDIFValid && spdifIn)          // If valid spdif data, then it is spdif
              printInputFormat("SPDIF");
            else                     // Otherwise it is PCM
              printInputFormat("PCM");

            if (SRExact == true) {    // Print PCM sample rate in exact format
              Serial.print(F(" "));
              Serial.print(sr, DEC);
            }
            else                     // Print PCM sample rate in nominal format
              if (sr > 383900)
                printSamplingRate("384 kHz");
              else if (sr > 352700)
                printSamplingRate("352 kHz");
              else if (sr > 191900)
                printSamplingRate("192 kHz");
              else if (sr > 176300)
                printSamplingRate("176 kHz");
              else if (sr > 95900)
                printSamplingRate("96 kHz");
              else if (sr > 88100)
                printSamplingRate("88 kHz");
              else if (sr > 47900)
                printSamplingRate("48 kHz");
              else
                printSamplingRate("44 kHz");
          }
        }
      }
      else {                       // There is no lock we print input selection
        if (bDisplayUnlock == false && screenMode == _MAIN_SCREEN && powerStatus == _POWER_ON)
        {
          bDisplayUnlock = true;
          printInput();
        }
        /*
          if (spdifIn)               // spdifIn=true means we selected SDPIF input
          Serial.print(F("SDPIF input"));
          else                       // Otherwise, we selected Serial Interface as input
          Serial.print(F("Serial Interface"));
        */
      }
      // 샘플링레이트 표시할 때 듀얼모드가 유지되고 있는지도 체크함
      if (checkDualMode() == false)
      {
        Serial.println("Not Dual mode");
        setDualMode();
      } else {
        Serial.println("Dual working");
      }
    }
  }
}

void printSamplingRate(char *sValue)
{
  tft.setTextSize(1);
  tft.fillRect(20, 110, 100, 30, BLACK);
  //tft.drawString(sValue, 20, 110, 4);
  drawString(sValue, 20, 110, 4);
  Serial.println(sValue);
}

void printInputFormat(char *sValue)
{
  tft.setTextSize(1);
  tft.fillRect(20, 75, 110, 30, BLACK);
  //tft.drawString(sValue, 20, 75, 4);
  drawString(sValue, 20, 75, 4);
  Serial.println(sValue);
}

// 터치 이벤트 발생했을 때 처리
void procTouch()
{
#ifdef LCD_A
  tft.setRotation(3);
#endif

#ifdef LCD_B
  tft.setRotation(3);
#endif

#ifdef LCD_C
  tft.setRotation(0);
#endif

#ifdef LCD_D
  tft.setRotation(0);
#endif

  TSPoint p = ts.getPoint();

  pinMode(XM, OUTPUT);
  pinMode(YP, OUTPUT);

  if (p.z > MINPRESSURE && p.z < MAXPRESSURE) {
#ifdef DEBUG
    Serial.print("X = "); Serial.print(p.x);
    Serial.print("\tY = "); Serial.print(p.y);
    Serial.print("\tPressure = "); Serial.println(p.z);
#endif // DEBUG

#ifdef LCD_A
    int tmp_x = p.x;
    p.x = tft.height() - (map(p.y, TS_MINX, TS_MAXX, tft.height(), 0));
    p.y = tft.width() - (map(tmp_x, TS_MINY, TS_MAXY, tft.width(), 0));
#endif

#ifdef LCD_B
    int tmp_x = p.x;
    p.x = (map(p.y, TS_MINX, TS_MAXX, tft.height(), 0));
    p.y = tft.width() - (map(tmp_x, TS_MINY, TS_MAXY, tft.width(), 0));
#endif

#ifdef LCD_C
    p.x = (map(p.x, TS_MINX, TS_MAXX, tft.width(), 0));
    p.y = tft.height() - (map(p.y, TS_MINY, TS_MAXY, tft.height(), 0)) + 20;
#endif

#ifdef LCD_D
    p.x = tft.width() - (map(p.x, TS_MINX, TS_MAXX, tft.width(), 0));
    p.y = tft.height() - (map(p.y, TS_MINY, TS_MAXY, tft.height(), 0));
#endif

#ifdef DEBUG
    Serial.print("("); Serial.print(p.x);
    Serial.print(", "); Serial.print(p.y);
    Serial.println(")");
#endif // DEBUG        
    if (powerStatus == _POWER_OFF) //전원이 꺼진 상태에서는 아무곳이나 터치해도 전원 온하고 리턴
    {
      powerOn();
      return;
    }
    if (screenMode == _MAIN_SCREEN) //메인화면에서 터치 이벤트 처리 (하단 버튼)
    {
      if ((p.x > 240 - BUTTON_MARGIN_X - 2 * BUTTON_R) && (p.x < 240)) {
        if (p.y > BUTTON_MARGIN_Y  && p.y < BUTTON_MARGIN_Y + 2 * BUTTON_R) { //오른쪽에서 첫번재 버튼

          volumeUp();
        } else if ((p.y > BUTTON_MARGIN_Y + 2 * BUTTON_R + BUTTON_D) && (p.y < BUTTON_MARGIN_Y + 4 * BUTTON_R + BUTTON_D)) { //오른쪽에서 두번재 버튼
          volumeDown();
        } else if ((p.y > BUTTON_MARGIN_Y + 4 * BUTTON_R + BUTTON_D * 2) && (p.y < BUTTON_MARGIN_Y + 6 * BUTTON_R + BUTTON_D * 2)) { //오른쪽에서 3번재 버튼
          /*
            input++;
            if (input > 3  ) input = 0;
            setAndPrintInput();
            delay(100);
          */
          inputChange();
          delay(100);

        } else if ((p.y > BUTTON_MARGIN_Y + 6 * BUTTON_R + BUTTON_D * 3) && (p.y < BUTTON_MARGIN_Y + 8 * BUTTON_R + BUTTON_D * 3)) { //오른쪽에서 4번재 버튼
          delay(50);
          //메뉴 화면 띄우기 전에 취소하고 나가는 것을 대비해서 현재 설정값을 임시로 저장해 놓는다.
          // DAC 설정값
          _firRollOff = firRollOff[input];
          _iirBandwidth = iirBandwidth[input];
          _dpllBandwidth = dpllBandwidth[input];
          _dpllMode = dpllMode[input];
          _bypassOSF = bypassOSF;
          _quantizer = quantizer[input];
          _jitterReduction = jitterReduction[input];
          _notchDelay = notchDelay[input];
          //리모콘 설정값
          //....

          screenMode = _MENU_SCREEN_1;
          setDisplay() ;

        } else if ((p.y > BUTTON_MARGIN_Y + 8 * BUTTON_R + BUTTON_D * 4) && (p.y < BUTTON_MARGIN_Y + 10 * BUTTON_R + BUTTON_D * 4)) { //오른쪽에서 5번재 버튼
          delay(50);
          powerOff();
        }
      }
    }
    else if (screenMode == _MENU_SCREEN_1) //메뉴설정화면 1 에서 터치 이벤트 처리
    {
      tft.setTextSize(1);
      Serial.println(p.x);
      // 하단 버튼 (메뉴페이지1,2,3,4, OK, 취소)
      if ((p.y > 140) && (p.y < 177) && (p.x > 180)) {
        screenMode = _MENU_SCREEN_2;
        setDisplay();
      }
      if ((p.y > 104) && (p.y < 140) && (p.x > 180)) {
        saveAndexitMenu();
      }
      if ((p.y > 25) && (p.y < 55) && (p.x > 180)) {
        cancelAndexitMenu();
      }

      // 메뉴 항목 (최대 5줄)
      if (p.y > 150) {
        tft.setRotation(3);
        if (p.x > mnu_marginy  && p.x < mnu_marginy + mnu_height)
        {
          //firRollOff
          //0 : Fast
          //1 : Slow
          if (firRollOff[input] == 0)
          {
            firRollOff[input] = 1; // 현재값이 0이면 1로 바꾸고
            // 설정값 배열에 저장 (추후 작업)
            printSetup(1, "Slow", 1); //화면에는 1(Slow)
          } else if (firRollOff[input] == 1)
          {
            firRollOff[input] = 0; // 현재값이 1이면 0로 바꾸고
            // 설정값 배열에 저장 (추후 작업)
            printSetup(1, "Fast", 1); //화면에는 0(Fast)
          }
        }
        if (p.x > mnu_marginy + mnu_height + mnu_offsety && p.x < mnu_marginy + mnu_height * 2 + mnu_offsety )
        {
          //iif bandwidth
          //0 : Normal
          //1 : 50k
          //2 : 60k
          //3 : 70k
          if (iirBandwidth[input] == 0) //현재 0인상태에서 터치했으므로 1 증가시킨 값이 현재값이 됨
          {
            iirBandwidth[input]++ ;
            printSetup(1, "50k", 2);
          }
          else if (iirBandwidth[input] == 1)
          {
            iirBandwidth[input]++ ;
            printSetup(1, "60k", 2);
          }
          else if (iirBandwidth[input] == 2)
          {
            iirBandwidth[input]++;
            printSetup(1, "70k", 2);
          }
          else if (iirBandwidth[input] == 3)
          {
            iirBandwidth[input] = 0;
            printSetup(1, "Normal", 2);
          }
        }
        if (p.x > mnu_marginy + mnu_height * 2 + mnu_offsety && p.x < mnu_marginy + mnu_height * 3 + mnu_offsety * 2 )
        {
          //DPLL bandwidth
          //0 : Best DPLL
          //1 : Lowest
          //2 : Low
          //3 : Med-Low
          //4 : Medium
          //5 : Med-High
          //6 : High
          //7 : Highest

          if (dpllBandwidth[input] == 0)
          {
            dpllBandwidth[input]++ ;
            printSetup(1, "Lowest", 3);
          }
          else if (dpllBandwidth[input] == 1)
          {
            dpllBandwidth[input]++;
            printSetup(1, "Low", 3);
          }
          else if (dpllBandwidth[input] == 2)
          {
            dpllBandwidth[input]++;
            printSetup(1, "Med-Low", 3);
          }
          else if (dpllBandwidth[input] == 3)
          {
            dpllBandwidth[input]++;
            printSetup(1, "Medium", 3);
          }
          else if (dpllBandwidth[input] == 4)
          {
            dpllBandwidth[input]++;
            printSetup(1, "Med-High", 3);
          }
          else if (dpllBandwidth[input] == 5)
          {
            dpllBandwidth[input]++;
            printSetup(1, "High", 3);
          }
          else if (dpllBandwidth[input] == 6)
          {
            dpllBandwidth[input]++;
            printSetup(1, "Highest", 3);
          }
          else if (dpllBandwidth[input] == 7)
          {
            dpllBandwidth[input] = 0 ;
            printSetup(1, "Best DPLL", 3);
          }
        }
        if (p.x > mnu_marginy + mnu_height * 3 + mnu_offsety * 2 && p.x < mnu_marginy + mnu_height * 4 + mnu_offsety * 3 )
        {
          //DPLL Mode
          //0 : x128
          //1 : Normal(x1)
          //2 : Inverted Phase
          if (dpllMode[input] == 0)
          {
            dpllMode[input]++;
            printSetup(1, "Normal(x1)", 4);
          }
          else if (dpllMode[input] == 1)
          {
            dpllMode[input]++;
            printSetup(1, "Inv.Phase", 4);
          }
          else if (dpllMode[input] == 2)
          {
            dpllMode[input] = 0;
            printSetup(1, "x128", 4);
          }
        }
        if (p.x > mnu_marginy + mnu_height * 4 + mnu_offsety * 3 && p.x < mnu_marginy + mnu_height * 5 + mnu_offsety * 4 )
        {
          //Oversampling
          if (bypassOSF == true)
          {
            bypassOSF = false;
            printSetup(1, "OSF On", 5);
          }
          else
          {
            bypassOSF = true;
            printSetup(1, "Bypass", 5);
          }
        }
        delay(200);
      }
    }
    else if (screenMode == _MENU_SCREEN_2) //메뉴설정화면 2 에서 터치 이벤트 처리
    {
      tft.setTextSize(1);
      Serial.println(p.x);
      // 하단 버튼 (이전/다음, OK, 취소)
      if ((p.y > 140) && (p.y < 177) && (p.x > 180)) {
        screenMode = _MENU_SCREEN_3;
        setDisplay();
      }
      if ((p.y > 104) && (p.y < 140) && (p.x > 180)) {
        saveAndexitMenu();
      }
      if ((p.y > 20) && (p.y < 55) && (p.x > 180)) {
        cancelAndexitMenu();
      }

      // 메뉴 항목 (최대 5줄)
      if (p.y > 150) {
        tft.setRotation(3);
        if (p.x > mnu_marginy  && p.x < mnu_marginy + mnu_height)
        {
          //Quantizer
          //0 : in phase
          //1 : anti phase
          if (quantizer[input] == 0)
          {
            quantizer[input]++;
            printSetup(1, "7bit Pseu", 1);
          }
          else if (quantizer[input] == 1)
          {
            quantizer[input]++;
            printSetup(1, "7bit True", 1);
          }
          else if (quantizer[input] == 2)
          {
            quantizer[input]++;
            printSetup(1, "8bit Pseu", 1);
          }
          else if (quantizer[input] == 3)
          {
            quantizer[input]++;
            printSetup(1, "8bit True", 1);
          }
          else if (quantizer[input] == 4)
          {
            quantizer[input]++;
            printSetup(1, "9bit Pseu", 1);
          }
          else if (quantizer[input] == 5)
          {
            quantizer[input] = 0;
            printSetup(1, "6bit True", 1);
          }
        }
        if (p.x > mnu_marginy + mnu_height + mnu_offsety && p.x < mnu_marginy + mnu_height * 2 + mnu_offsety )
        {
          //Jitter Reduction
          //0 : Bypass
          //1 : On

          if (jitterReduction[input] == 0)
          {
            jitterReduction[input] = 1 ;
            printSetup(1, "On", 2);
          }
          else if (jitterReduction[input] == 1)
          {
            jitterReduction[input] = 0 ;
            printSetup(1, "Bypass", 2);
          }
        }
        if (p.x > mnu_marginy + mnu_height * 2 + mnu_offsety && p.x < mnu_marginy + mnu_height * 3 + mnu_offsety * 2 )
        {
          //Notch Delay
          //0 : No Notch
          //1 : MCLK/4
          //2 : MCLK/8
          //3 : MCLK/16
          //4 : MCLK/32
          //5 : MCLK/64

          if (notchDelay[input] == 0)
          {
            notchDelay[input]++ ;
            printSetup(1, "MCLK/4", 3);
          }
          else if (notchDelay[input] == 1)
          {
            notchDelay[input]++ ;
            printSetup(1, "MCLK/8", 3);
          }
          else if (notchDelay[input] == 2)
          {
            notchDelay[input]++ ;
            printSetup(1, "MCLK/16", 3);
          }
          else if (notchDelay[input] == 3)
          {
            notchDelay[input]++ ;
            printSetup(1, "MCLK/32", 3);
          }
          else if (notchDelay[input] == 4)
          {
            notchDelay[input]++ ;
            printSetup(1, "MCLK/64", 3);
          }
          else if (notchDelay[input] == 5)
          {
            notchDelay[input] = 0 ;
            printSetup(1, "No Notch", 3);
          }
        }
        if (p.x > mnu_marginy + mnu_height * 4 + mnu_offsety * 3 && p.x < mnu_marginy + mnu_height * 5 + mnu_offsety * 4 )
        {
          setDefaultSetting();
          printSetup(1, "OK to reset", 5);
        }
        delay(200);
      }
    }
    else if (screenMode == _MENU_SCREEN_3) //메뉴설정화면 3(리모콘 학습) 에서 터치 이벤트 처리
    {
      tft.setTextSize(1);
      Serial.println(p.x);
      // 하단 버튼 (이전/다음, OK, 취소)
      if ((p.y > 140) && (p.y < 177) && (p.x > 180)) {
        screenMode = _MENU_SCREEN_4;
        setDisplay();
      }
      if ((p.y > 104) && (p.y < 140) && (p.x > 180)) {
        saveAndexitMenu();
      }
      if ((p.y > 20) && (p.y < 55) && (p.x > 180)) {
        cancelAndexitMenu();
      }

      // 메뉴 항목 (최대 5줄)
      if (p.y > 150) {
        tft.setRotation(3);
        if (p.x > mnu_marginy  && p.x < mnu_marginy + mnu_height)
        {
          currButton = _POWER_BUTTON ;
          printSetup(1, "Wait..", 1);
        }
        if (p.x > mnu_marginy + mnu_height + mnu_offsety && p.x < mnu_marginy + mnu_height * 2 + mnu_offsety )
        {
          currButton = _VOLUP_BUTTON;
          printSetup(1, "Wait..", 2);
        }
        if (p.x > mnu_marginy + mnu_height * 2 + mnu_offsety && p.x < mnu_marginy + mnu_height * 3 + mnu_offsety * 2 )
        {
          currButton = _VOLDOWN_BUTTON ;
          printSetup(1, "Wait..", 3);
        }
        if (p.x > mnu_marginy + mnu_height * 3 + mnu_offsety * 2 && p.x < mnu_marginy + mnu_height * 4 + mnu_offsety * 3 )
        {
          currButton = _INPUT_BUTTON ;
          printSetup(1, "Wait..", 4);
        }
        if (p.x > mnu_marginy + mnu_height * 4 + mnu_offsety * 3 && p.x < mnu_marginy + mnu_height * 5 + mnu_offsety * 4 )
        {
          currButton = _MUTE_BUTTON ;
          printSetup(1, "Wait..", 5);
        }
        delay(200);
      }
    } else if (screenMode == _MENU_SCREEN_4) //메뉴설정화면 4(리모콘 학습) 에서 터치 이벤트 처리
    {
      tft.setTextSize(1);
      Serial.println(p.x);
      // 하단 버튼 (이전/다음, OK, 취소)
      if ((p.y > 140) && (p.y < 177) && (p.x > 180)) {
        screenMode = _MENU_SCREEN_1;
        setDisplay();
      }
      if ((p.y > 104) && (p.y < 140) && (p.x > 180)) {
        saveAndexitMenu();
      }
      if ((p.y > 20) && (p.y < 55) && (p.x > 180)) {
        cancelAndexitMenu();
      }

      // 메뉴 항목 (최대 5줄)
      if (p.y > 150) {
        tft.setRotation(3);
        if (p.x > mnu_marginy  && p.x < mnu_marginy + mnu_height)
        {
          currButton = _INPUT_DRIECT_BUTTON_USB  ;
          printSetup(1, "Wait..", 1);
        }
        if (p.x > mnu_marginy + mnu_height + mnu_offsety && p.x < mnu_marginy + mnu_height * 2 + mnu_offsety )
        {
          currButton = _INPUT_DRIECT_BUTTON_OPT ;
          printSetup(1, "Wait..", 2);
        }
        if (p.x > mnu_marginy + mnu_height * 2 + mnu_offsety && p.x < mnu_marginy + mnu_height * 3 + mnu_offsety * 2 )
        {
          currButton = _INPUT_DRIECT_BUTTON_COAX  ;
          printSetup(1, "Wait..", 3);
        }
        if (p.x > mnu_marginy + mnu_height * 3 + mnu_offsety * 2 && p.x < mnu_marginy + mnu_height * 4 + mnu_offsety * 3 )
        {
          currButton = _INPUT_DRIECT_BUTTON_AES  ;
          printSetup(1, "Wait..", 4);
        }
        delay(200);
      }
    }
  }
}

void saveAndexitMenu()
{
  muteDAC(true);
  writeSettings();
  applySettings();
  delay(500);
  muteDAC(false);
  screenMode = _MAIN_SCREEN;
  setDisplay();
}

void cancelAndexitMenu()
{
  //취소 시에는 처음 메뉴 화면에 들어왔을 당시의 설정값으로 복원한다.
  restoreSettings();
  screenMode = _MAIN_SCREEN;
  setDisplay();
}


//메뉴 설정 값을 9018의 기본 설정값으로 설정한다.
void setDefaultSetting()
{
  //메뉴 설정값을 메이커 기본 설정값으로 변경
  //현재 선택된 입력에만 해당 (bypassOSF는 모든 입력에 적용)
  firRollOff[input] = 0 ;     // 0 : fast
  iirBandwidth[input] = 1 ;   // 1 : 50k
  dpllBandwidth[input] = 0 ;  // 0 : BEST DPLL
  dpllMode[input] = 1 ;       // 1 : x1 (normal)
  quantizer[input] = 0 ;      // 0 : 6bit True Differential
  jitterReduction[input] = 1; // 1 : On
  notchDelay[input] = 0 ;     // 0 : No Notch Delay
  bypassOSF = false;          // false : OSF On
}

void restoreSettings()
{
  // DAC 설정값
  firRollOff[input] = _firRollOff;
  iirBandwidth[input] = _iirBandwidth;
  dpllBandwidth[input] = _dpllBandwidth;
  dpllMode[input] = _dpllMode;
  quantizer[input] = _quantizer;
  jitterReduction[input] = _jitterReduction;
  notchDelay[input] = _notchDelay;
  bypassOSF = _bypassOSF;
  //리모콘 설정값은 restore 하지 않음;
}

// 메뉴화면에서 메뉴항목과 설정값 LCD에 표시
void printSetup(int kind, char *sValue, int line )
{
  if (kind == 0) //메뉴 항목
  {
    tft.setTextColor(BLACK);
    tft.fillRoundRect(mnu_marginx - 4, mnu_marginy - 3 + (mnu_height + mnu_offsety) * (line - 1), mnu_offsetx, mnu_height + 7 , 8, WHITE);
    //tft.drawString(sValue, mnu_marginx, mnu_marginy + (mnu_height + mnu_offsety) * (line - 1), 4) ;
    drawString(sValue, mnu_marginx, mnu_marginy + (mnu_height + mnu_offsety) * (line - 1), 4) ;

  }
  else if (kind == 1) //메뉴 설정값
  {
    tft.setTextColor(WHITE);
    tft.fillRect(mnu_marginx * 2  + mnu_offsetx , mnu_marginy + (mnu_height + mnu_offsety) * (line - 1), 320 - mnu_offsetx, mnu_height + 5, BLACK);
    //tft.drawString(sValue, mnu_marginx * 2  + mnu_offsetx, mnu_marginy + (mnu_height + mnu_offsety) * (line - 1), 4) ;
    drawString(sValue, mnu_marginx * 2  + mnu_offsetx, mnu_marginy + (mnu_height + mnu_offsety) * (line - 1), 4) ;
  }

}

/// 셋업메뉴에서 설정된 값을 9018 레지스터에 기록 -  설정메뉴 OK 하거나 처음 DAC 기동시 호출됨
void applySettings()
{
  // 9018 레지스터에 반영
  tft.setRotation(3);
  setAndPrintFirFilter(false);
  setAndPrintIirFilter(false);
  setAndPrintDPLLBandwidth(false);
  setAndPrintDPLLMode(false);
  setAndPrintBypassOSF(false);
  setAndPrintJitterReduction(false);
  setAndPrintQuantizer(false);
  setAndPrintNotch(false);
}


/////////////////////////////////////////// 리모콘 관련 ////////////////////////////////////////////////////////////////////


/////////////////////////////////////////// 시스템 제어 관련 ///////////////////////////////////////////////////////////////


// EEPROM에 설정값 저장하기
// EEPROM은 쓰기에 수명이 있는 저장소이므로 입력선택, 볼륨값등은 저장하지 않는다
// DAC 자체의 전원은 꺼도 아두이노는 전원 플러그를 뽑지 않는 한 전원이 공급되므로 입력 선택, 볼륨은 DAC을 껐다 켜도 유지됨
// 전원플러그를 완전히 뺐다 껴면 설정값은 유지되나 입력선택과 볼륨은 디폴트값으로 변함
void writeSettings() {
  //9018 레지스터 관련 값 구조체 설정
  for (int j = 0 ; j < 4 ; j++) { //input 값 별로 저장해야 함
    dacSettings.firRollOff[j] = firRollOff[j];
    dacSettings.iirBandwidth[j] = iirBandwidth[j];
    dacSettings.dpllBandwidth[j] = dpllBandwidth[j];
    dacSettings.dpllMode[j] = dpllMode[j];
    dacSettings.quantizer[j] = quantizer[j];
    dacSettings.jitterReduction[j] = jitterReduction[j];
    dacSettings.notchDelay[j] = notchDelay[j];
  }
  Serial.print("bypassOSF:");
  Serial.println(bypassOSF);
  dacSettings.bypassOSF = bypassOSF;

  //리모콘 설정값 구조체값 저장
  dacSettings.rmtPowerOnOff = rmtPowerOnOff;
  dacSettings.rmtVolUp = rmtVolUp;
  dacSettings.rmtVolDown = rmtVolDown;
  dacSettings.rmtInputSelect = rmtInputSelect;
  dacSettings.rmtInputUSB  = rmtInputUSB ;
  dacSettings.rmtInputOpt  = rmtInputOpt ;
  dacSettings.rmtInputCoax  = rmtInputCoax ;
  dacSettings.rmtInputAES  = rmtInputAES ;
  dacSettings.rmtMute = rmtMute;

  //한번도 저장된 적이 없는지 구분하기 위한 Stamp
  dacSettings.saveStamp = 99;

  //dacSettings 구조체 값을 eeprom에 저장함.
  eeprom_write_block((const void*)&dacSettings, (void*)0, sizeof(dacSettings) + 1);
}

// EEPROM에서 설정값 불러오기
void readSettings() {
  //eeprom에서 값을 읽어서 dacSettings 구조체에 저장함.
  eeprom_read_block((void*)&dacSettings, (void*)0, sizeof(dacSettings) + 1);

  //9018 레지스터값 부분을 전역변수에 설정 - 값만 읽어오고 실제 9018에 레지스터 기록되는 것은 setAndPrintInput이나 applySettings에서 이뤄짐
  for (int n = 0 ; n < 4 ; n++) { //input 값 별로 가져와야 함
    firRollOff[n] = dacSettings.firRollOff[n];
    iirBandwidth[n] = dacSettings.iirBandwidth[n];
    dpllBandwidth[n] = dacSettings.dpllBandwidth[n];
    dpllMode[n] = dacSettings.dpllMode[n];
    quantizer[n] = dacSettings.quantizer[n];
    jitterReduction[n] = dacSettings.jitterReduction[n];
    notchDelay[n] = dacSettings.notchDelay[n];
  }
  bypassOSF = dacSettings.bypassOSF;
  //Serial.print("readsetting : osf : ");
  //if(bypassOSF) Serial.println("true");
  //else Serial.println("false");

  //리모콘 설정값 읽어서 전역변수에 설정
  rmtPowerOnOff = dacSettings.rmtPowerOnOff;
  rmtVolUp = dacSettings.rmtVolUp;
  rmtVolDown = dacSettings.rmtVolDown;
  rmtInputSelect = dacSettings.rmtInputSelect;
  rmtMute = dacSettings.rmtMute;
  rmtInputUSB  = dacSettings.rmtInputUSB ;
  rmtInputOpt  = dacSettings.rmtInputOpt ;
  rmtInputCoax  = dacSettings.rmtInputCoax ;
  rmtInputAES  = dacSettings.rmtInputAES ;

  saveStamp = dacSettings.saveStamp;
}

/*
  READING THE SAMPLE RATE

  The sample rate can be calculated by reading the DPLL 32-bit register. For SPDIF DPLL value
  is divided by (2^32/Crystal-Frequency). In Buffalo II (original), the Crystal frequency is
  80,000,000 Hz. In Arduino (and other small microprocessors) it is NOT advisable to do floating point
  math because "it is very slow"; therefore integer math will be used to calculate the sample rate.

  The value of 2^32/80,000,000 is 53.687091 (which is a floating point number). If we use the
  integer part (53 or 54) we get the following results for a 44.1K sample rate signal:  divided by 53
  the result is 44.677K; divided by 54, the result is 43.849K. Clearly there are large errors from
  being confined to integer math. The actual result, if we use floating point math and use all the
  significant digits is 44,105 Hz (the 5 Hz deviation from ideal 44100 Hz is within the specification
  of SPDIF and the tolerances of the crystals and clocks involved)

  In order to increase the accuracy of the integer calculation, we can use more of the significant
  digits of the divisor. I did some evaluation of the DPLL register values for sample rates ranging
  from 44.1K to 192K and noticed that I could multiply the value of the DPLL number by up to
  400 without overflowing the 32-bits. Therefore, since we have 32 bit number to work with, we
  can multiply the DPLL number by  up to 400 and then divide by 400X53.687091=21475. If we do this,
  we obtain 44.105K which is the same as the exact value.

  I used a spreadsheet to calculate the multipliers for SPDIF and I2S and for both 80Mhz and 100Mhz

  SPDIF 80Mhz:  x80, %4295
  SPDIF 100Mhz: x20, %859
  I2S 80Mhz:     x1, %3436
  I2S 100Mhz:    x4, %10995 (higher multiplier will overflow the 32bit value for 384KHz SR)
                x5, %13744 (More accurate but only works up to 192KHz SR)

  For I2S input format the dpll number is divided by (2^32*64/Crystal-Frequency) Note the 64 factor.
  The value of this is 3435.97 which rounds off nicely to 3436 (which is only 0.0008% error). The
  resultant value for the sample rate is the same wheter in spdif or I2S mode.
*/

// Sample rate reading routines

volatile unsigned long DPLLNum; // Variable to hold DPLL value

byte readRegister(byte regAddr) {
  Wire.beginTransmission(0x48); // Hard coded the Sabre/Buffalo device  address
  Wire.write(regAddr);          // Queues the address of the register
  Wire.endTransmission();       // Sends the address of the register
  Wire.requestFrom(0x48, 1);    // Hard coded to Buffalo, request one byte from address
  // specified with Wire.write()/wire.endTransmission()
  if (Wire.available())         // Wire.available indicates if data is available
    return Wire.read();         // Wire.read() reads the data on the wire
  else
    return 0;                   // In no data in the wire, then return 0 to indicate error
}

byte readRegisterR(byte regAddr) {
  Wire.beginTransmission(0x49); // Hard coded the Sabre/Buffalo device  address
  Wire.write(regAddr);          // Queues the address of the register
  Wire.endTransmission();       // Sends the address of the register
  Wire.requestFrom(0x49, 1);    // Hard coded to Buffalo, request one byte from address
  // specified with Wire.write()/wire.endTransmission()
  if (Wire.available())         // Wire.available indicates if data is available
    return Wire.read();         // Wire.read() reads the data on the wire
  else
    return 0;                   // In no data in the wire, then return 0 to indicate error
}

unsigned long sampleRate() {
  DPLLNum = 0;
  // Reading the 4 registers of DPLL one byte at a time and stuffing into a single 32-bit number
  DPLLNum |= readRegister(31);
  DPLLNum <<= 8;
  DPLLNum |= readRegister(30);
  DPLLNum <<= 8;
  DPLLNum |= readRegister(29);
  DPLLNum <<= 8;
  DPLLNum |= readRegister(28);
  // The following calculation supports 80 MHz oscillator
  if (SPDIFValid) {
#ifdef USE80MHZ
    DPLLNum *= 80;    // Calculate SR for SPDIF -80MHz part
    DPLLNum /= 4295;  // Calculate SR for SDPIF -80MHz part
#endif
#ifdef USE100MHZ
    DPLLNum *= 20;    // Calculate SR for SPDIF -100MHz part
    DPLLNum /= 859;   // Calculate SR for SDPIF -100MHz part
#endif
  }
  else {              // Different calculation for SPDIF and I2S
#ifdef USE80MHZ
    DPLLNum /= 3436;  // Calculate SR for I2S -80MHz part
#endif
#ifdef USE100MHZ
    DPLLNum *= 4;    // Calculate SR for I2S -100MHz part
    DPLLNum /= 10995; // Calculate SR for I2S -100MHz part
#endif
  }
  if (DPLLNum < 90000) // Adjusting because in integer operation, the residual is truncated
    DPLLNum += 1;
  else if (DPLLNum < 190000)
    DPLLNum += 2;
  else if (DPLLNum < 350000)
    DPLLNum += 3;
  else
    DPLLNum += 4;

  if (bypassOSF)     // When OSF is bypassed, the magnitude of DPLL is reduced by a factor of 64
    DPLLNum *= 64;

  return DPLLNum;
}

/*
  CONTROLLING THE DIGITAL ATTENUATION (VOLUME) -and other registers IN THE DAC

  The device address of Sabre DAC Datasheet specifies the address as 0x90 which is an 8-bit value.
  The wire library in Arduino uses 7-bit device addresses and the 8th R/W bit is added automatically
  depending on whether you use the write call [beginTransmission()] or the read call [requestFrom()].
  Therefore, you will use the 7 most significant bits of the 8-bit address.
  In our example, 0x90 becomes 0x48 as follows:
  0x90: 10010000 (we eliminate the rightmost bit to get I2C address)
  0x48: 1001000
  When using dual-mono configuration, the other device can be set to addres 0x92
  0x92: 10010010 (we eliminate the rightmost bit to get I2C address)
  0x49: 1001001
*/

// The default mode is for the address 0x48 to be the left chip
void writeSabreLeftReg(byte regAddr, byte regVal)
{
  Wire.beginTransmission(0x48);
  Wire.write(regAddr);
  Wire.write(regVal);
  Wire.endTransmission();
}

// In dual mono, sometimes different values are written to L and R chips
void writeSabreRightReg(byte regAddr, byte regVal)
{
  Wire.beginTransmission(0x49);
  Wire.write(regAddr);
  Wire.write(regVal);
  Wire.endTransmission();
}

// The following routine writes to both chips in dual mono mode. With some exceptions, one only needs
// to set one of the chips to be the right channel

void writeSabreReg(byte regAddr, byte regVal)
{
  writeSabreLeftReg(regAddr, regVal);
  writeSabreRightReg(regAddr, regVal);
}

void setDualMode()
{
  bitClear(reg17, 7); //0XXXXXXX : 좌측채널로 설정
  bitSet(reg17, 0);   //XXXXXXX1 : 듀얼모노로 설정
  writeSabreLeftReg(0x11, reg17 );

  reg17R = reg17;
  bitSet(reg17R, 7); //1XXXXXXX : 우측채널로 설정
  bitSet(reg17R, 0); //XXXXXXX1 : 듀얼모노로 설정
  writeSabreRightReg(0x11, reg17R );
}

bool checkDualMode()
{
  bool ret = false;
  byte dualStatus = readRegister(17);
  Serial.print  ("dual status L (0x48 Reg17) :");
  Serial.println  (dualStatus, BIN);
  byte dualStatusR = readRegisterR(17);
  Serial.print  ("dual status R (0x49 Reg17) :");
  Serial.println  (dualStatusR, BIN);

  if (dualStatus & B00000001 && dualStatusR & B00000001)
    ret = true;
  else
    ret = false;
  return ret;
}

void setSabreVolume(byte regVal)
{
  writeSabreReg(0, regVal); // set up volume in DAC1
  writeSabreReg(1, regVal); // set up volume in DAC2
  writeSabreReg(2, regVal); // set up volume in DAC3
  writeSabreReg(3, regVal); // set up volume in DAC4
  writeSabreReg(4, regVal); // set up volume in DAC5
  writeSabreReg(5, regVal); // set up volume in DAC6
  writeSabreReg(6, regVal); // set up volume in DAC7
  writeSabreReg(7, regVal); // set up volume in DAC8
}

void rampUp()
{
  byte i = (DIM - currAttnu);
  for (byte dimval = DIM; dimval > currAttnu; dimval--) {
    setSabreVolume(dimval);
    delay((RAMP) * (1 + (10 / i * i)));
    i--;
  }
}

void setAndPrintDPLLBandwidth(bool bDisplay) {

  Serial.print(F("- DPLL :"));

  switch (dpllBandwidth[input]) {
    case 0:
      if (bDisplay)
        printSetup(1, "Best DPLL", 3);
      else {
        bitSet(reg25, 1);           // Reg 25: set bit 1 for "use best dpll"
        writeSabreReg(0x19, reg25); // Write value into reg 25 for best dpll
        Serial.println(F("Best DPLL"));
      }
      break;
    case 1:
      if (bDisplay)
        printSetup(1, "Lowest", 3);
      else {
        bitClear(reg25, 1);         // Reg 25: Clear bit 1 for "use all settings"
        writeSabreReg(0x19, reg25); // Write value into reg 25 for all settings
        writeSabreReg(0x0B, 0x85);  // Reg 11: Set corresponding DPLL bandwidth
        Serial.println(F("Lowest Bandwidth"));
      }
      break;
    case 2:
      if (bDisplay)
        printSetup(1, "Low", 3);
      else {
        bitClear(reg25, 1);         // Reg 25: Clear bit 1 for "use all settings"
        writeSabreReg(0x19, reg25); // Write value into reg 25 for all settings
        writeSabreReg(0x0B, 0x89);  // Reg 11: Set corresponding DPLL bandwidth
        Serial.println(F("Low Bandwidth"));
      }
      break;
    case 3:
      if (bDisplay)
        printSetup (1, "Med-Low", 3);
      else {
        bitClear(reg25, 1);         // Reg 25: Clear bit 1 for "use all settings"
        writeSabreReg(0x19, reg25); // Write value into reg 25 for all settings
        writeSabreReg(0x0B, 0x8D);  // Reg 11: Set corresponding DPLL bandwidth
        Serial.println(F("Med-Low Bandwidth"));
      }
      break;
    case 4:
      if (bDisplay)
        printSetup (1, "Medium", 3);
      else {
        bitClear(reg25, 1);         // Reg 25: Clear bit 1 for "use all settings"
        writeSabreReg(0x19, reg25); // Write value into reg 25 for all settings
        writeSabreReg(0x0B, 0x91);  // Reg 11: Set corresponding DPLL bandwidth
        Serial.println(F("Medium Bandwidth"));
      }
      break;
    case 5:
      if (bDisplay)
        printSetup (1, "Med-High", 3);
      else {
        bitClear(reg25, 1);         // Reg 25: Clear bit 1 for "use all settings"
        writeSabreReg(0x19, reg25); // Write value into reg 25 for all settings
        writeSabreReg(0x0B, 0x95);  // Reg 11: Set corresponding DPLL bandwidth
        Serial.println(F("Med-High Bandwidth"));
      }
      break;
    case 6:
      if (bDisplay)
        printSetup (1, "High", 3);
      else {
        bitClear(reg25, 1);         // Reg 25: Clear bit 1 for "use all settings"
        writeSabreReg(0x19, reg25); // Write value into reg 25 for all settings
        writeSabreReg(0x0B, 0x99);  // Reg 11: Set corresponding DPLL bandwidth
        //Serial.println(F("High Bandwidth"));
      }
      break;
    case 7:
      if (bDisplay)
        printSetup (1, "Highest", 3);
      else {
        bitClear(reg25, 1);         // Reg 25: Clear bit 1 for "use all settings"
        writeSabreReg(0x19, reg25); // Write value into reg 25 for all settings
        writeSabreReg(0x0B, 0x9D);  // Reg 11: Set corresponding DPLL bandwidth
        //Serial.println(F("Highest Bandwidth"));
      }
      break;
  }
}

void setAndPrintDPLLMode(bool bDisplay) { // Set the DPLL Mode
  Serial.print(F("- DPLL Mode:"));
  switch (dpllMode[input]) {
    case 0:
      if (bDisplay)
        printSetup(1, "x128", 4);
      else {
        bitSet(reg25, 0);          // Set bit 0 of reg 25 for x128 DPLL bandwidth
        writeSabreReg(0x19, reg25);
        bitClear(reg17, 1);        // Reg 17: Clear bit 1 to NOT invert DPLL phase
        writeSabreReg(0x11, reg17);
        Serial.println(F("Multiply x128"));
      }
      break;

    case 1:
      if (bDisplay)
        printSetup(1, "Normal(x1)", 4);
      else {
        bitClear(reg25, 0);        // Clear bit 0 of reg 25 for x1 DPLL bandwidth
        writeSabreReg(0x19, reg25);
        bitClear(reg17, 1);        // Reg 17: Clear bit 1 to NOT invert DPLL phase
        writeSabreReg(0x11, reg17);
        Serial.println(F("Normal"));
      }
      break;
    case 2:
      if (bDisplay)
        printSetup(1, "Inv.Phase", 4);
      else {
        bitClear(reg25, 0);        // Clear bit 0 of reg 25 for x1 DPLL bandwidth
        writeSabreReg(0x19, reg25);
        bitSet(reg17, 1);          // Reg 17: Set bit 1 to invert DPLL phase
        writeSabreReg(0x11, reg17);
        Serial.println(F("Inverted phase"));
      }
      break;
  }
}

void setAndPrintJitterReduction(bool bDisplay) {
  Serial.print(F("- Jitter Reduction:"));
  switch (jitterReduction[input]) {
    case 0: //bypass
      if (bDisplay)
        printSetup(1, "Bypass", 2);
      else
      {
        bitClear(reg10, 2);          // Set bit 2 of reg 10: jitter reduction ON
        writeSabreReg(0x0A, reg10);
        Serial.println(F("Bypass"));
      }
      break;
    case 1:
      if (bDisplay)
        printSetup(1, "On", 2);
      else {
        bitSet(reg10, 2);          // Set bit 2 of reg 10: jitter reduction ON
        writeSabreReg(0x0A, reg10);
        Serial.println(F("On"));
      }
      break;
  }
}

void setAndPrintBypassOSF(bool bDisplay) {
  Serial.print(F("- Oversampling FIR Bypass:"));
  if (!bypassOSF) {
    if (bDisplay)
      printSetup(1, "OSF On", 5);
    else {
      bitClear(reg17, 6);              // Reg 17: clear bypass oversampling bit in register
      writeSabreReg(0x11, reg17);      // Reg 17: bypass OSF off
      Serial.println(F("OSF On"));        // Indicate oversampling is ON (^)
    }
  }
  else {
    if (bDisplay)
      printSetup(1, "Bypass", 5);
    else {
      bitSet(reg17, 6);                // Reg 17: set bypass oversampling bit in register
      bitSet (reg17, 5);               // Reg 17: set Jitter lock bit, normal operation
      writeSabreReg(0x11, reg17);      // Reg 17: bypass OSF on, force relock
      delay(100);
      bitClear(reg17, 5);              // Reg 17: clear relock jitter for normal operation
      writeSabreReg(0x11, reg17);      // Reg 17: Jitter eliminator Normal operation
      Serial.println(F("Bypass"));                 // Indicate no oversampling (.)
    }
  }
}

void setAndPrintFirFilter(bool bDisplay) {

  Serial.print(F("- Fir Filter : "));

  switch (firRollOff[input]) {
    case 0:
      if (bDisplay)
        printSetup(1, "Fast", 1);
      else {
        bitSet(reg14, 0);          // Set bit 0 of reg 14 for sharp fir
        writeSabreReg(0x0E, reg14);
        Serial.println(F("Sharp fir"));
      }
      break;
    case 1:
      if (bDisplay)
        printSetup(1, "Slow", 1);
      else {
        bitClear(reg14, 0);        // Clear bit 0 of reg 14 for slow fir
        writeSabreReg(0x0E, reg14);
        Serial.println(F("Slow fir"));
      }
      break;
  }
}

void setAndPrintIirFilter(bool bDisplay) {
  Serial.print(F("- IIR Bandwidth : "));
  switch (iirBandwidth[input]) {
    case 0:                        // | | | | | |0|0| | IIR Bandwidth: Normal (for PCM)
      if (bDisplay)
        printSetup(1, "Normal", 2);
      else {
        bitClear(reg14, 1);          // Clear bit 1
        bitClear(reg14, 2);          // Clear bit 2
        writeSabreReg(0x0E, reg14);
        Serial.println(F("Normal (for PCM)"));
      }
      break;
    case 1:                        // | | | | | |0|1| | IIR Bandwidth: 50k (for DSD) (D)
      if (bDisplay)
        printSetup(1, "50k", 2);
      else {
        bitSet(reg14, 1);            // Set bit 1
        bitClear(reg14, 2);          // Clear bit 2
        writeSabreReg(0x0E, reg14);
        Serial.println(F("50k (for DSD)"));
      }
      break;
    case 2:                        // | | | | | |1|0| | IIR Bandwidth: 60k (for DSD)
      if (bDisplay)
        printSetup(1, "60k", 2);
      else {
        bitSet(reg14, 2);            // Set bit 2
        bitClear(reg14, 1);          // Clear bit 1
        writeSabreReg(0x0E, reg14);
        Serial.println(F("60k (for DSD)"));
      }
      break;
    case 3:                        // | | | | | |1|1| | IIR Bandwidth: 70k (for DSD)
      if (bDisplay)
        printSetup(1, "70k", 2);
      else {
        bitSet(reg14, 1);            // Set bit 1
        bitSet(reg14, 2);            // Set bit 2
        writeSabreReg(0x0E, reg14);
        Serial.println(F("Bandwidth: 70k (for DSD)"));
      }
      break;
  }
}

void setAndPrintQuantizer(bool bDisplay) {
  Serial.print(F("- Quantizer : "));
  switch (quantizer[input]) {
    case 0:                        // 6-bit true diff
      if (bDisplay)
        printSetup(1, "6bit True", 1);
      else {
        bitSet(reg14, 3);            // True differential
        writeSabreReg(0x0E, reg14);
        writeSabreReg(0x0F, 0x00);   // 6-bit quantizer
        Serial.println(F("6 bit True differential"));
      }
      break;
    case 1:                        // 7-bit pseudo diff
      if (bDisplay)
        printSetup(1, "7bit Pseu", 1);
      else {
        bitClear(reg14, 3);          // Pseudo diff
        writeSabreReg(0x0E, reg14);
        writeSabreReg(0x0F, 0x55);   // 7-bit quantizer
        Serial.println(F("7 bit pseudo differential"));
      }
      break;
    case 2:                        // 7-it true diff
      if (bDisplay)
        printSetup(1, "7bit True", 1);
      else {
        bitSet(reg14, 3);            // True differential
        writeSabreReg(0x0E, reg14);
        writeSabreReg(0x0F, 0x55);   // 7-bit quantizer
        Serial.println(F("7 bit True differential"));
      }
      break;
    case 3:                        // 8-bit pseudo diff
      if (bDisplay)
        printSetup(1, "8bit Pseu", 1);
      else {
        bitClear(reg14, 3);          // Pseudo diff
        writeSabreReg(0x0E, reg14);
        writeSabreReg(0x0F, 0xAA);   // 8-bit quantizer
        Serial.println(F("8 bit pseudo differential"));
      }
      break;
    case 4:                        // 8-bit true diff
      if (bDisplay)
        printSetup(1, "8bit True", 1);
      else {
        bitSet(reg14, 3);            // True differential
        writeSabreReg(0x0E, reg14);
        writeSabreReg(0x0F, 0xAA);   // 8-bit quantizer
        Serial.println(F("8 bit True differential"));
      }
      break;
    case 5:                        // 9-bit pseudo diff
      if (bDisplay)
        printSetup(1, "9bit Pseu", 1);
      else {
        bitClear(reg14, 3);          // Pseudo diff
        writeSabreReg(0x0E, reg14);
        writeSabreReg(0x0F, 0xFF);   // 9-bit quantizer
        Serial.println(F("9 bit pseudo differential"));
      }
      break;
  }
}

void setAndPrintNotch(bool bDisplay) {
  Serial.print(F("- Notch Delay : "));
  switch (notchDelay[input]) {
    case 0:
      if (bDisplay)
        printSetup(1, "No Notch", 3);
      else {
        writeSabreReg(0x0C, 0x20);   // No notch delay
        Serial.println(F("No notch delay"));
      }
      break;
    case 1:
      if (bDisplay)
        printSetup(1, "MCLK/4", 3);
      else {
        writeSabreReg(0x0C, 0x21);   // notch delay=mclk/4
        Serial.println(F("mclk/4"));
      }
      break;
    case 2:
      if (bDisplay)
        printSetup(1, "MCLK/8", 3);
      else {
        writeSabreReg(0x0C, 0x23);   // notch delay=mclk/8
        Serial.println(F("mclk/8"));
      }
      break;
    case 3:
      if (bDisplay)
        printSetup(1, "MCLK/16", 3);
      else {
        writeSabreReg(0x0C, 0x27);   // notch delay=mclk/16
        Serial.println(F("mclk/16"));
      }
      break;
    case 4:
      if (bDisplay)
        printSetup(1, "MCLK/32", 3);
      else {
        writeSabreReg(0x0C, 0x2F);   // notch delay=mclk/32
        Serial.println(F("mclk/32"));
      }
      break;
    case 5:
      if (bDisplay)
        printSetup(1, "MCLK/64", 3);
      else {
        writeSabreReg(0x0C, 0x3F);   // notch delay=mclk/64
        Serial.println(F("mclk/64"));
      }
      break;
  }
}
void setAndPrintInputFormat() {
  // This register also controls mono-8channel operation, thus more code...
  Serial.print(F("- Input Format : "));
  Serial.println(input);

  switch (input) {
    case 0 :                           // I2S 32 bit - USB 입력과 연결
      writeSabreReg(0x12, 0x01);       // Set SPDIF to input #1
      // Move the spdif mux away from a live spdif signal
      bitSet(reg17, 3);                // Reg 17: auto spdif detection ON -Set bit 3
      writeSabreReg(0x11, reg17);      //  SPDIF detection required
      writeSabreReg(0x08, 0x68);       // Reg 8: Enable I2S/DSD input format
      spdifIn = false;                 // Set variable to indicate input format is I2S/DSD mode
      bitClear(reg10, 4);              // Setting to I2S (2 bits required)
      bitClear(reg10, 5);
      bitSet(reg10, 6);                // Setting to 32 bit (2 bits required)
      bitSet(reg10, 7);
      writeSabreReg(0x0A, reg10);
      Serial.println(F("usb"));
      break;

    case 1 :                           // optical
      writeSabreReg(0x08, 0xE8);       // Reg 8: Enable SPDIF input format
      bitSet(reg17, 3);                // Reg 17: auto spdif detection ON -Set bit 3
      // Auto SPDIF detection required
      writeSabreReg(0x11, reg17);      // Reg 17: write value into register
      writeSabreReg(0x12, 0x80);       // Set SPDIF to input #8
      spdifIn = true;                  // Indicates input format is spdif.
      Serial.println(F("opt"));
      break;

    case 2 :                           // Coax
      writeSabreReg(0x08, 0xE8);       // Reg 8: Enable SPDIF input format
      bitSet(reg17, 3);                // Reg 17: auto spdif detection ON -Set bit 3
      // Auto SPDIF detection required
      writeSabreReg(0x11, reg17);      // Reg 17: write value into register
      writeSabreReg(0x12, 0x40);       // Set SPDIF to input #7
      spdifIn = true;                  // Indicates input format is spdif.
      Serial.println(F("Coax"));
      break;

    case 3 :                           // AES/EBU
      writeSabreReg(0x08, 0xE8);       // Reg 8: Enable SPDIF input format
      bitSet(reg17, 3);                // Reg 17:auto spdif detection ON -Set bit 3
      // Auto SPDIF detection required
      writeSabreReg(0x11, reg17);      // Reg 17: write value into register
      writeSabreReg(0x12, 0x04);       // Set SPDIF to input #3
      spdifIn = true;                  // Indicates input format is spdif.
      Serial.println(F("AES/EBU"));
      break;
  }
}

void procMute() //사용자 조작에 의해 뮤트 콘트롤 (리모콘 또는 터치)
{
  bMuteStatus = !bMuteStatus;
  muteDAC(bMuteStatus);
  printMute();
}

void muteDAC(bool bMute) //사용자 조작이 아닌 시스템 내부에서 사용하는 함수
{
  if (bMute)
    bitSet(reg10, 0);
  else
    bitClear(reg10, 0);
  writeSabreReg(0x0A, reg10);
}

void setAndPrintInput() {
  Serial.println(input);
  muteDAC(true);

  printInput() ;
  setAndPrintInputFormat();  // Setup input format value
  setAndPrintFirFilter(false);
  setAndPrintIirFilter(false);
  setAndPrintDPLLBandwidth(false);
  setAndPrintJitterReduction(false);
  setAndPrintBypassOSF(false);
  setAndPrintDPLLMode(false);
  setAndPrintQuantizer(false);
  setAndPrintNotch(false);

  setDualMode();
  delay(100);
  muteDAC(false);

}

// The following 2 routine sets up the registers in the DAC at startup

void startDac1() {

  setSabreVolume(currAttnu);    // Reg 0 to Reg 7 Set volume registers with startup volume level
  displayVolume();              // LCD volume display update
  //writeSabreReg(0x0D, 0x00);    // DAC in-phase
  //writeSabreReg(0x13, 0x00);    // DACB anti-phase
  //writeSabreReg(0x25, 0x00);    // Use built in filter for stage 1 and stage 2
  //writeSabreReg(0x0E, reg14);   // Reg 14: BuffII input map, trueDiff, normal IIR and Fast rolloff
  // Reg 14: except BuffII input map setting, the others will be
  // redefined.
  /*
    The code below may provide some mitigation to the white noise during silence
    #ifdef USE80MHZ
    writeSabreReg(0x10,0x08);     // Reg 16: Turn automute loopback -only to mitigate 352.8KHz noise
    writeSabreReg(0x09,0x10);     // Reg 9: Set automute time 4x less than default (value is in denom.)
    #endif USE80MHZ
  */

  /*
    #ifdef DUALMONO                // DAC registers default to stereo. Set to MONO L/R for dual MONO
    bitSet(reg17,0);               // Set for MONO
    writeSabreReg(0x11,reg17);     // Sets both chips to MONO
    #endif DUALMONO
  */


#ifdef TPAPHASE
  /* The outputs on each side of each MONO board will be in opposite phase. In order to do this
     the phase of the odd dacs are out of phase with the even dacs. Further, buffalo is configured
     such that (In dual mono mode) the channel on the DAC which is opposite of the selected channel
     carries the same analog signal but in anti-phase (odd dacs are the left channel;
     even dacs are the right channel)
     See http://hifiduino.wordpress.com/sabre32/ for further explaination
  */
  writeSabreLeftReg(0x0D, 0x22); // MONO LEFT DACx: odd dacs=in-phase; even dacs=anti-phase
  // writeSabreLeftReg(0x13,0x00);  // MONO LEFT DACBx: all dacs anti-phase with respect to DACx
  writeSabreRightReg(0x0D, 0x11); // MONO RIGHT DACx: odd dacs=anti-phase; even dacs=in-phase
  // writeSabreRightReg(0x13,0x00); // MONO RIGHT DACBx: all dacs anti-phase with respect to DACx
#endif TPAPHASE
}

void startDac2() {
  setAndPrintInput();
  muteDAC(false);
}

void reset9018() {
  //ES9018 초기화
  //10번 디지털 핀에 2초간 High, 이후 low
  Serial.println("Reset ES9018 : Start. Wait for 2 sec.");

  pinMode(_RESET_9018, OUTPUT);
  digitalWrite(_RESET_9018, HIGH);
  delay(1000);
  digitalWrite(_RESET_9018, LOW);
  muteDAC(true);
}

void powerOn()
{
  readSettings();
  if (saveStamp != 99) setDefaultSetting(); //한번도 설정이 저장된 적이 없으므로 9018 디폴트 셋팅으로 설정
  bMuteStatus = false;
  pinMode(_POWER, OUTPUT);
  digitalWrite(_POWER, HIGH);
  reset9018();
  powerStatus = _POWER_ON;
  bitSet(reg10, 0);             // Set bit zero for reg 10: Mute DACs
  writeSabreReg(0x0A, reg10);   // Mute DACs. Earliest we can mute the DACs to avoid full volume
  setSabreVolume(currAttnu);

  //LCD 초기화 - 메인화면
  initLCD();

  // First part of starting the DAC
  startDac1();

  // Print the welcome message and other labels to the Serial Monitor
  Serial.println(F(VER_INFO));
  Serial.println(F("2015-10-18"));
  startDac2();  // prints all the values in the screen
  //듀얼 모노 셋팅
  setDualMode();
}

void powerOff()
{
  //파워 오프 클릭후 9018 뮤트
  bMuteStatus = true;
  muteDAC(true);
  delay(100);

  //LCD 초기화 - Blank
  tft.reset();
  tft.begin(CONTROLLER_ID);
  tft.setRotation(3);
  tft.fillScreen(BLACK);

  prev_sr = 0;

  delay(1200);

  // 파워오프 신호 전송
  pinMode( _POWER, OUTPUT);
  digitalWrite(_POWER, LOW);
  powerStatus = _POWER_OFF;

  //tft.lcdoff();

  pinMode(_DSD_PLAY, OUTPUT);
  digitalWrite(_DSD_PLAY, LOW);
}

void volumeUp()
{
  if (bMuteStatus) procMute();
  if (currAttnu > 0)
  {
    currAttnu -= 2;
    displayVolume();
    setSabreVolume(currAttnu);
  } else {
  }
}

void volumeDown()
{
  if (bMuteStatus) procMute();
  if (currAttnu < 180)
  {
    currAttnu += 2;
    displayVolume();
    setSabreVolume(currAttnu);
  } else {
  }
}

void inputChange()
{
  input++;
  if (input > 3  ) input = 0;
  setAndPrintInput();Serial.begin(9600);
}
/////////////////////////////////////////// 메인프로그램 시작 - Setup  /////////////////////////////////////////////////////
void setup() {
  //디버깅용 시리얼 모니터 시작
  Serial.begin(9600);

  //IR 수신 활성화
  irrecv.enableIRIn(); // Start the receiver

  //I2C 통신 시작
  //I2C 버스에 마스터로 합류
  Wire.begin();        // Join the I2C bus as a master
  //Wire.setClock(400000L);  //I2C 통신속도 설정 : 디폴트값은 100kHz, 고속통신 400kHz

  //전원 Off - 아두이노가 리셋될 때는 9018 전원 오프
  powerStatus = _POWER_OFF;
  powerOff();

  //EEPROM 셋팅값 불러오기 - 리모콘 ON을 위해서 가져올 필요 있음
  readSettings();

}  // End setup()

/////////////////////////////////////////// 메인프로그램  - loop  /////////////////////////////////////////////////////
void loop() {
  //LCD 터치 이벤트 처리
  procTouch();

  refreshSampleRate();

  if (irrecv.decode(&results)) {
    Serial.println(results.value, HEX);
    if (results.value != 0xFFFFFFFF) pushedRemoconButton = results.value;

    if (powerStatus == _POWER_OFF && results.value == rmtPowerOnOff)
    {
      powerOn();
    } else if (powerStatus == _POWER_ON )
    {
      if (!bLearningMode)
      {
        if (screenMode == _MAIN_SCREEN)
        {
          if (results.value == rmtVolUp) {
            volumeUp();
          } else if (results.value == rmtVolDown) {
            volumeDown();
          } else if (results.value == rmtInputSelect) {
            inputChange();
          } else if (results.value == rmtInputUSB ) {
            input = 0;
            setAndPrintInput();
          } else if (results.value == rmtInputOpt ) {
            input = 1;
            setAndPrintInput();
          } else if (results.value == rmtInputCoax ) {
            input = 2;
            setAndPrintInput();
          } else if (results.value == rmtInputAES ) {
            input = 3;
            setAndPrintInput();
          } else if (results.value == rmtMute ) {
            procMute();
          } else if (results.value == rmtPowerOnOff) {
            if (powerStatus == _POWER_OFF)
              powerOn();
            else if (powerStatus == _POWER_ON)
              powerOff();
          } else if (results.value == 0xFFFFFFFF) {
            Serial.println(pushedRemoconButton, HEX);
            if (pushedRemoconButton == rmtVolUp ) {
              currAttnu -= 6;
              if (currAttnu < 0) currAttnu = 2;
              Serial.println (currAttnu, DEC);
              volumeUp();
            } else if (pushedRemoconButton == rmtVolDown) {
              currAttnu += 6;
              if (currAttnu > 180) currAttnu = 178;
              volumeDown();
            }
          }
        }
      }
      else //리모콘 학습 모드
      {
        if (results.value != 0xFFFFFFFF)
        {
          tft.setRotation(3);
          char buf[11];
          switch (currButton)
          {
            case _POWER_BUTTON :
              rmtPowerOnOff = results.value;
              sprintf(buf, "%lx", rmtPowerOnOff);
              printSetup (1, buf, 1);
              break;

            case _VOLUP_BUTTON  :
              rmtVolUp  = results.value;
              sprintf(buf, "%lx", rmtVolUp);
              printSetup (1, buf, 2);
              break;

            case _VOLDOWN_BUTTON :
              rmtVolDown  = results.value;
              sprintf(buf, "%lx", rmtVolDown);
              printSetup (1, buf, 3);
              break;

            case _INPUT_BUTTON :
              rmtInputSelect  = results.value;
              sprintf(buf, "%lx", rmtInputSelect);
              printSetup (1, buf, 4);
              break;

            case _INPUT_DRIECT_BUTTON_USB :
              rmtInputUSB  = results.value;
              sprintf(buf, "%lx", rmtInputUSB );
              printSetup (1, buf, 1);
              break;

            case _INPUT_DRIECT_BUTTON_OPT  :
              rmtInputOpt  = results.value;
              sprintf(buf, "%lx", rmtInputOpt );
              printSetup (1, buf, 2);
              break;

            case _INPUT_DRIECT_BUTTON_COAX  :
              rmtInputCoax   = results.value;
              sprintf(buf, "%lx", rmtInputCoax );
              printSetup (1, buf, 3);
              break;

            case _INPUT_DRIECT_BUTTON_AES  :
              rmtInputAES   = results.value;
              sprintf(buf, "%lx", rmtInputAES );
              printSetup (1, buf, 4);
              break;

            case _MUTE_BUTTON :
              rmtMute  = results.value;
              sprintf(buf, "%lx", rmtMute);
              printSetup (1, buf, 5);
              break;
          }
        }
      }
    }
    irrecv.resume(); // Receive the next value
  }

}




