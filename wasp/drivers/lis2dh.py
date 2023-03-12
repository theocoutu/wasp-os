# Distributed with a free-will license.
# Use it any way you want, profit or free, provided it fits in the licenses of its associated works.
# LIS2DHTR
# This code is designed to work with the LIS2DHTR_I2CS I2C Mini Module available from ControlEverything.com.
# https://www.controleverything.com/content/Accelorometer?sku=LIS2DHTR_I2CS#tabs-0-product_tabset-2

import I2C

import time

# Get I2C bus
bus = smbus.SMBus(1)

# LIS2DHTR address, 0x19(24)
# Select control register1, 0x20(32)
# 0x27(39) Power ON mode, Data rate selection = 10 Hz
# X, Y, Z-Axis enabled
bus.write_byte_data(0x19, 0x20, 0x27)

# LIS2DHTR address, 0x19(24)
# Select control register4, 0x23(35)
# 0x00(00) Continuous update, Full-scale selection = +/-2G
bus.write_byte_data(0x19, 0x23, 0x00)

time.sleep(0.5)

# LIS2DHTR address, 0x19(24)
# Read data back from 0x28(40), 2 bytes
# X-Axis LSB, X-Axis MSB
data0 = bus.read_byte_data(0x19, 0x28)
data1 = bus.read_byte_data(0x19, 0x29)

# Convert the data
xAccl = data1 * 256 + data0
if xAccl > 32767 :
xAccl -= 65536

# LIS2DHTR address, 0x19(24)
# Read data back from 0x2A(42), 2 bytes
# Y-Axis LSB, Y-Axis MSB
data0 = bus.read_byte_data(0x19, 0x2A)
data1 = bus.read_byte_data(0x19, 0x2B)

# Convert the data
yAccl = data1 * 256 + data0
if yAccl > 32767 :
yAccl -= 65536

# LIS2DHTR address, 0x19(24)
# Read data back from 0x2C(44), 2 bytes
# Z-Axis LSB, Z-Axis MSB
data0 = bus.read_byte_data(0x19, 0x2C)
data1 = bus.read_byte_data(0x19, 0x2D)

# Convert the data
zAccl = data1 * 256 + data0
if zAccl > 32767 :
zAccl -= 65536









# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson

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

    def read_hrs(self):
        # TODO: Try fusing the read of H & L
        xl = self.read_reg(_X_LSB_R)
        xm = self.read_reg(_X_LSB_R)

        yl = self.read_reg(_C0DATAL)
        yh = self.read_reg(_C0DATAL)

        zl = self.read_reg(_C0DATAL)
        zh = self.read_reg(_C0DATAL)

        return (m << 8) | ((h & 0x0f) << 4) | (l & 0x0f) | ((l & 0x30) << 12)

    def read_als(self):
        # TODO: Try fusing the read of H & L
        m = self.read_reg(_C1DATAM)
        h = self.read_reg(_C1DATAH)
        l = self.read_reg(_C1DATAL)

        return (m << 3) | ((h & 0x3f) << 11) | (l & 0x07)

    def set_gain(self, gain):
        if gain > 64:
            gain = 64
        hgain = 0
        while (1 << hgain) < gain:
            hgain += 1
        self.write_reg(_HGAIN, hgain << 2)

    def set_drive(self, drive):
        """
        Set LED drive current
        Parameters:
            drive (int) LED drive current
                0 = 12.5 mA
                1 = 20   mA
                2 = 30   mA
                3 = 40   mA
        """
        en = self.read_reg(_ENABLE)
        pd = self.read_reg(_PDRIVER)
       
        en = (en & ~_ENABLE_PDRIVE1 ) | ((drive & 2) << 2)
        pd = (pd & ~_PDRIVER_PDRIVE0) | ((drive & 1) << 6)

        self.write_reg(_ENABLE, en)
        self.write_reg(_PDRIVER, pd)

    def set_hwt(self, t):
        """
        Set wait time between each conversion cycle
        Parameters:
            t (int) Wait time between each conversion cycle
                0 = 800   ms
                1 = 400   ms
                2 = 200   ms
                3 = 100   ms
                4 =  75   ms
                5 =  50   ms
                6 =  12.5 ms
                7 =   0   ms
        """
        en = self.read_reg(_ENABLE)
        en = (en & ~_ENABLE_HWT) | (t << 4)
        self.write_reg(_ENABLE, en)
