#include <Arduino.h>

#include <Wire.h>
// #include <SoftTimer.h>
// #include <DelayRun.h>
#include <stdint.h>

#ifndef __SCHAR_MAX__
# define __SCHAR_MAX__ 0x7f
#endif

#ifndef __SHRT_MAX__
# define __SHRT_MAX__ 0x7fff
#endif

#define I2C_ADDR  0x45
#define MAX_RECEIVED_BYTES  16

