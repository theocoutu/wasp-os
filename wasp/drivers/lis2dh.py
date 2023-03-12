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
            x = x_accel -= 65536
        else:
            x = x_accel

        return x

    def read_y(self):
        # TODO: Try fusing the read of LSB & MSB
        yl = self.read_reg(_Y_LSB_R)
        ym = self.read_reg(_Y_MSB_R)

        y_accel = ym * 256 + yl
        if y_accel > 32767 :
            y = y_accel -= 65536
        else:
            y = y_accel

        return y

    def read_z(self):
        zl = self.read_reg(_Z_LSB_R)
        zm = self.read_reg(_Z_MSB_R)

        z_accel = zm * 256 + zl
        if z_accel > 32767 :
            z = z_accel -= 65536
        else:
            z = z_accel

        return z
