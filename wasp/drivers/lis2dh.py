# 

"""LIS2DH driver
~~~~~~~~~~~~~~~~~
"""

from micropython import const

_I2CADDR = const(0x19)

_CTLREG1 = const(0x20)
_10HZ_ON = const(0x27)

_CTLREG4 = const(0x23)
_CONT_2G = const(0x00) #continuous update, full-scale ±2g

_X_LSB_R = const(0x28)
_X_MSB_R = const(0x29)

_Y_LSB_R = const(0x2a)
_Y_MSB_R = const(0x2b)

_Z_LSB_R = const(0x2c)
_Z_MSB_R = const(0x2d)

class LIS2DH:
    def __init__(self, i2c):
        self._i2c = i2c

    def init(self):
        w = self.write_reg

        # Power ON mode; Data rate selection = 10 Hz; X+Y+Z-Axis enabled
        w(_CTLREG1, _10HZ_ON)

        # Continuous update, Full-scale selection = ±2G
        w(_CTLREG4, _CONT_2G)

    def read_reg(self, addr):
        return self._i2c.readfrom_mem(_I2CADDR, addr, 1)[0]

    def write_reg(self, addr, val):
        self._i2c.writeto_mem(_I2CADDR, addr, bytes((val,)))

    def read_x(self):
        # TODO: Try fusing the read of LSB & MSB
        xl = self.read_reg(_X_LSB_R)
        xm = self.read_reg(_X_MSB_R)

        x_accel = xm * 256 + xl
        if x_accel > 32767 :
            x = x_accel - 65536
        else:
            x = x_accel

        return x

    def read_y(self):
        # TODO: Try fusing the read of LSB & MSB
        yl = self.read_reg(_Y_LSB_R)
        ym = self.read_reg(_Y_MSB_R)

        y_accel = ym * 256 + yl
        if y_accel > 32767 :
            y = y_accel - 65536
        else:
            y = y_accel

        return y

    def read_z(self):
        zl = self.read_reg(_Z_LSB_R)
        zm = self.read_reg(_Z_MSB_R)

        z_accel = zm * 256 + zl
        if z_accel > 32767 :
            z = z_accel - 65536
        else:
            z = z_accel

        return z



"""LIS2HH Driver - i2c Accelerometer
https://docs.firialabs.com/_modules/lis2dh.html
"""

"""
import time

# Device registers
LIS_TEMP_L = 0x0c   # Temperature sensor
LIS_TEMP_H = 0x0d
LIS_DEV_ID = 0x0f  # hardcoded WHO_AM_I ID
LIS_CTRL_REG0 = 0x1e
LIS_TMP_CFG = 0x1f
LIS_CTRL_REG1 = 0x20
LIS_CTRL_REG2 = 0x21
LIS_CTRL_REG3 = 0x22
LIS_CTRL_REG4 = 0x23
LIS_CTRL_REG5 = 0x24
LIS_CTRL_REG6 = 0x25
LIS_REFERENCE = 0x26
LIS_STATUS_REG = 0x27
LIS_OUT_REG_MULTI = 0x28  # 3 axes XYZ, each 16bit 2's complement
LIS_FIFO_CTRL = 0x2e
LIS_FIFO_SRC = 0x2f
LIS_IG1_CFG = 0x30  # Interrupt Generator 1
LIS_IG1_SRC = 0x31
LIS_IG1_THRESH = 0x32
LIS_IG1_DURATION = 0x33
LIS_IG2_CFG = 0x34  # Interrupt Generator 2
LIS_IG2_SRC = 0x35
LIS_IG2_THRESH = 0x36
LIS_IG2_DURATION = 0x37

LIS_VFY_DEV_ID = 0x33

# Default values
LIS_DEF_CTRL0 = 0b10010000  # Disable SA0 pullup
LIS_DEF_CTRL1 = 0b0111_0_111  # ODR=400Hz, High-Rez mode, XYZ axes enabled
LIS_DEF_CTRL2 = 0b10000111  # High pass filter bypassed to FIFO, configured 8Hz cutoff for IRQ
LIS_DEF_CTRL3 = 0b00000000  # No IRQ pin
LIS_DEF_CTRL4 = 0b1_0_00_1_00_0  # Block data update, Little-endian, 2g full-scale, 12-bit
LIS_DEF_CTRL5 = 0b00000000  # FIFO disabled, non-latching IRQ
LIS_DEF_CTRL6 = 0b00000010  # INT2 disabled, Interrupt polarity active low
LIS_DEF_FIFO_CTRL = 0b10000000  # Stream mode, Watermark = 0


class LIS2DH:
    ### Device driver for LIS2DH accelerometer, controlled via i2c bus.

    # Note: default addr assumes SA0 tied high or floating
    def __init__(self, i2c, addr=0x19):
        self.i2c = i2c
        self.i2c.unlock()
        self.addr = addr
        self.orientation = (0, 0, 0)
        self.buf1 = bytearray(1)  # Pre-allocate command/resp buffer usable from IRQ
        self.buf2 = bytearray(2)

        self.reset()

    def reset(self):
        ### Init registers to default config
        self.set_byte(LIS_CTRL_REG1, LIS_DEF_CTRL1)
        self.set_byte(LIS_CTRL_REG2, LIS_DEF_CTRL2)
        self.set_byte(LIS_CTRL_REG3, LIS_DEF_CTRL3)
        self.set_byte(LIS_CTRL_REG4, LIS_DEF_CTRL4)
        self.set_byte(LIS_CTRL_REG5, LIS_DEF_CTRL5)
        self.set_byte(LIS_CTRL_REG6, LIS_DEF_CTRL6)


    def set_byte(self, reg, val):
        ### Set byte register
        self.buf2[0] = reg
        self.buf2[1] = val
        self.i2c.try_lock()
        self.i2c.writeto(self.addr, self.buf2)
        self.i2c.unlock()


    def get_byte(self, reg):
        self.buf1[0] = reg
        self.i2c.try_lock()
        self.i2c.writeto(self.addr, self.buf1)
        self.i2c.readfrom_into(self.addr, self.buf1)
        self.i2c.unlock()
        return self.buf1[0]

    def verify_id(self):
        ### Verify device ID - return True if correct
        return self.get_byte(LIS_DEV_ID) == LIS_VFY_DEV_ID


    def poll_x(self):
        stat = 0
        count = 10000
        while (stat & 0b00001000) == 0 and count:
            stat = self.get_byte(LIS_STATUS_REG)
            count -= 1

        if count:
            xl = self.get_byte(0x28)
            xh = self.get_byte(0x29)
            print(hex(xl), hex(xh), 'x=', self.signed12((xl, xh)), 'count=', count)
        else:
            print("timeout")

    def wait_xyz_ready(self):
        ### Poll status register and return True when READY, False if timeout
        stat = 0
        count = 1000
        while (stat & 0b00001000) == 0 and count:
            stat = self.get_byte(LIS_STATUS_REG)
            count -= 1

        return bool(count)


    @staticmethod
    def test_exceeds(a, b, delta):
        ### Test each iterable value: a[0..n] - b[0..n] > delta
        for i, j in zip(a, b):
            if abs(i - j) < delta:
                return False
        return True


    def self_test(self):
        ### Run self-test and return device to default state. Return True if passed
        result = False
        normal = self.read()
        # print("normal=", normal)
        self.set_byte(LIS_CTRL_REG4, 0b1_0_00_1_10_0)  # Induce positive force
        time.sleep(0.200)
        pos_test = self.read()
        # print("pos=", pos_test)
        if self.test_exceeds(normal, pos_test, 1000):
            self.set_byte(LIS_CTRL_REG4, 0b1_0_00_1_01_0)  # Induce negative force
            time.sleep(0.200)
            neg_test = self.read()
            # print("neg=", neg_test)
            if self.test_exceeds(neg_test, normal, 1000):
                result = True

        self.set_byte(LIS_CTRL_REG4, LIS_DEF_CTRL4)   # Back to normal
        return result


    @staticmethod
    def signed12(buf):
        val = ((buf[1] << 4) | (buf[0] >> 4)) & 0x0fff   # Little endian 12-bit left-justified
        return (val & 0xf800) - (val & 0x07ff)  # Convert to 2's complement signed integer

    @staticmethod
    def signed16(buf):
        val = (buf[1] << 8) | buf[0]   # Little endian 16-bit 2's complement value
        return (val & 0x8000) - (val & 0x7fff)  # Convert to signed integer

    def read(self):
        ### Read current XYZ axis values and update orientation
        # Auto address increment isn't working on lis2dh12 as it did on lis2hh12. For now, do byte-at-a-time.
        if self.wait_xyz_ready():
            xl = self.get_byte(0x28)
            xh = self.get_byte(0x29)
            x = self.signed16((xl, xh))
            yl = self.get_byte(0x2a)
            yh = self.get_byte(0x2b)
            y = self.signed16((yl, yh))
            zl = self.get_byte(0x2c)
            zh = self.get_byte(0x2d)
            z = self.signed16((zl, zh))

            # Change accelerometer coords to match (x,y,z) on PCB silkscreen
            self.orientation = (y, x, z)
        else:
            print("timeout")

        return self.orientation


    def dump_axes(self):
        ### Debug - send axis values to stdout
        print("X={}, Y={}, Z={}".format(*self.read()))
"""



# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson

"""Bosch BMA421 accelerometer driver
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

"""
import bma42x
import time

# Sensor orientation definition.
# The 6 most significant bits define the indexes of the x, y, and z values
# in the acceleration tuple returned by the sensor, while the 3 least
# significant bits define their sign (1 = keep original sign, 0 = negate).
#
#         Z index ─────────────────┐
#         Y index ───────────────┐ │
#         X index ─────────────┐ │ │
#                              ├┐├┐├┐
_DEFAULT_ORIENTATION = const(0b010010101)
#          1 = keep, 0 = negate      │││
#          X sign ───────────────────┘││
#          Y sign ────────────────────┘│
#          Z sign ─────────────────────┘

class BMA421:
    ### BMA421 driver
    # .. automethod:: __init__
    
    def __init__(self, i2c, orientation=_DEFAULT_ORIENTATION):
        ### Configure the driver.
        # :param machine.I2C i2c: I2C bus used to access the sensor.
        
        self._dev = bma42x.BMA42X(i2c)
        self._orientation = orientation

    def reset(self):
        ### Reset and reinitialize the sensor.
        dev = self._dev

        # Init, reset, wait for reset, enable I2C watchdog
        dev.init()
        dev.set_command_register(0xb6)
        time.sleep(0.05)
        dev.set_reg(bma42x.NV_CONFIG_ADDR, 6);

        # Configure the sensor for basic step counting
        dev.write_config_file()
        dev.set_accel_enable(True)
        dev.set_accel_config(odr=bma42x.OUTPUT_DATA_RATE_100HZ,
                               range=bma42x.ACCEL_RANGE_2G,
                               bandwidth=bma42x.ACCEL_NORMAL_AVG4,
                               perf_mode=bma42x.CIC_AVG_MODE)
        dev.feature_enable(bma42x.STEP_CNTR, True)

    @property
    def steps(self):
        ### Report the number of steps counted.
        return self._dev.step_counter_output()

    @steps.setter
    def steps(self, value):
        if value != 0:
            raise ValueError()
        self._dev.reset_step_counter()

    def accel_xyz(self):
        ### Return a triple with acceleration values
        raw = self._dev.read_accel_xyz()
        x = raw[self._orientation >> 7 & 0b11] * ((self._orientation >> 1 & 0b10) - 1)
        y = raw[self._orientation >> 5 & 0b11] * ((self._orientation      & 0b10) - 1)
        z = raw[self._orientation >> 3 & 0b11] * ((self._orientation << 1 & 0b10) - 1)
        return (x, y, z)
"""
