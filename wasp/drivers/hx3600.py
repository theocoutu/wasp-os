# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson

# modified from hrs3300.py in 2023 by theocoutu

# DATASHEET w I2C INFO: http://www.synercontech.com/Public/uploads/file/2019_10/20191020152311_81180.pdf
# Other datasheet:      https://jenda.hrach.eu/f2/HX3603.pdf

"""HX3600 driver
~~~~~~~~~~~~~~~~~
"""

from micropython import const

_I2CADDR = const(0x44)

_ID = const(0x00)

_ENABLE = const(0x02)
_EN_OFF = const(0x33) # ADC OSR 1024; HRS+PS disabled
_ENA_ON = const(0x77) # ADC OSR 1024; HRS+PS  enabled

_SLEEP = const(0x09)
_SL_ACT = const(0x02)
_SL_SLP = const(0x03)

_LED_HS = const(0x04)
_LED_PS = const(0x05)

_LED_DRV = const(0xc0)
_LED_125 = const(0x84)

_H_1A_ = const(0xa0)
_H_1B_ = const(0xa1)
_H_1C_ = const(0xa2)

_H_2A_ = const(0xa3)
_H_2B_ = const(0xa4)
_H_2C_ = const(0xa5)

_P_1A_ = const(0xa6)
_P_1B_ = const(0xa7)
_P_1C_ = const(0xa8)

_P_2A_ = const(0xa9)
_P_2B_ = const(0xaa)
_P_2C_ = const(0xab)


class HX3600:
    def __init__(self, i2c):
        self._i2c = i2c

    def init(self):
        w = self.write_reg

        # HRS+PS disabled, 1024 ADC OSR
        w(_ENABLE, _EN_OFF)

        # 12.5 mA drive
        w(_LED_DRV, _LED_125)

        # Set LED on-time phase to recommended vals from datasheet
        w(_LED_HS, 0x10)
        #self.set_hwt(4)
        w(_LED_PS, 0x20)
        #self.set_pwt(5)

        # Go to sleep
        w(_SLEEP, _SL_SLP)

    def read_reg(self, addr):
        return self._i2c.readfrom_mem(_I2CADDR, addr, 1)[0]

    def write_reg(self, addr, val):
        self._i2c.writeto_mem(_I2CADDR, addr, bytes((val,)))

    def enable(self):
        self.init()
        
        # Wake from sleep
        self.write_reg(_SLEEP, _SL_ACT)
        
        # Enable HRS and PS
        self.write_reg(_ENABLE, _ENA_ON)

    def disable(self):
        # Disable HRS and PS
        self.write_reg(_ENABLE, _EN_OFF)
        
        # Go to sleep
        self.write_reg(_SLEEP, _SL_SLP)

    def read_hrs(self):
        # TODO: Try fusing the read of H & L
        h1a = self.read_reg(_H_1A_)
        h1b = self.read_reg(_H_1B_)
        h1c = self.read_reg(_H_1C_)

        h2a = self.read_reg(_H_2A_)
        h2b = self.read_reg(_H_2B_)
        h2c = self.read_reg(_H_2C_)
        
        return h1a << 24 (m << 8) | ((h & 0x0f) << 4) | (l & 0x0f) | ((l & 0x30) << 12)

    def read_ps(self):
        # TODO: Try fusing the read of H & L
        p1a = self.read_reg(_P_1A_)
        p1b = self.read_reg(_P_1B_)
        p1c = self.read_reg(_P_1C_)
        
        p2a = self.read_reg(_P_2A_)
        p2b = self.read_reg(_P_2B_)
        p2c = self.read_reg(_P_2C_)

        return (m << 3) | ((h & 0x3f) << 11) | (l & 0x07)

"""
    def set_drive(self, drive):
        #Set LED drive current
        #Parameters:
        #    drive (int) LED drive current
        #        0 = 12.5 mA
        #        1 = 25   mA
        #        2 = 50   mA
        #        3 = 100   mA
        #        
        #       00 = 12.5 mA
        #       01 = 25   mA
        #       10 = 50   mA
        #       11 = 100  mA
        
        en = self.read_reg(_ENABLE)
        pd = self.read_reg(_PDRIVER)
       
        en = (en & ~_ENABLE_PDRIVE1 ) | ((drive & 2) << 2)
        pd = (pd & ~_PDRIVER_PDRIVE0) | ((drive & 1) << 6)

        self.write_reg(_ENABLE, en)
        self.write_reg(_PDRIVER, pd)
"""

    def set_hwt(self, t):
        #Set wait time between each conversion cycle
        #Parameters:
        #    t (int) Wait time between each conversion cycle
        #        0 = 800   ms
        #        1 = 400   ms
        #        2 = 200   ms
        #        3 = 100   ms
        #        4 =  75   ms
        #        5 =  50   ms
        #        6 =  12.5 ms
        #        7 =   0   ms

        if t = 0:
            self.write_reg(_LED_HS, 0x01)
        elif t = 1:
            self.write_reg(_LED_HS, 0x02)
        elif t = 2:
            self.write_reg(_LED_HS, 0x04)
        elif t = 3:
            self.write_reg(_LED_HS, 0x08)
        elif t = 4:
            self.write_reg(_LED_HS, 0x10)
        elif t = 5:
            self.write_reg(_LED_HS, 0x20)
        elif t = 6:
            self.write_reg(_LED_HS, 0x40)
        elif t = 7:
            self.write_reg(_LED_HS, 0x80)
        else:
            print("error: invalid wait period (t)")
            pass


    def set_pwt(self, t):
        
        #Set wait time between each conversion cycle
        #Parameters:
        #    t (int) Wait time between each conversion cycle
        #        0 = 800   ms
        #        1 = 400   ms
        #        2 = 200   ms
        #        3 = 100   ms
        #        4 =  75   ms
        #        5 =  50   ms
        #        6 =  12.5 ms
        #        7 =   0   ms

        if t = 0:
            self.write_reg(_LED_PS, 0x01)
        elif t = 1:
            self.write_reg(_LED_PS, 0x02)
        elif t = 2:
            self.write_reg(_LED_PS, 0x04)
        elif t = 3:
            self.write_reg(_LED_PS, 0x08)
        elif t = 4:
            self.write_reg(_LED_PS, 0x10)
        elif t = 5:
            self.write_reg(_LED_PS, 0x20)
        elif t = 6:
            self.write_reg(_LED_PS, 0x40)
        elif t = 7:
            self.write_reg(_LED_PS, 0x80)
        else:
            print("error: invalid wait period (t)")
            pass
