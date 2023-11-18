import os


class G_F:

    def __init__(self, Polinomio_Irreducible = 0x11b):


        self.Polinomio_Irreducible = Polinomio_Irreducible
        self.Tabla_EXP = [0] * 256
        self.Tabla_LOG = [0] * 256
        self.generar_tablas()

    def generar_tablas(self):
        g = 0x02  # Generador del cuerpo finito
        elemento = 0x01
        for i in range(256):
            self.Tabla_EXP[i] = elemento
            self.Tabla_LOG[elemento] = i
            elemento = self.xTimes(elemento)


    def xTimes(self, n):
        result = n << 1
        if result > 255:
            result ^= self.Polinomio_Irreducible
        return result

    def producto(self, a, b):   
       p= 0
       while a and b:
              if b & 1:
                p ^= a
              b >>= 1
              a = self.xTimes(a)
       return p
    

    def inverso(self, n):
        if n == 0:
            return 0
        return self.Tabla_EXP[255 - self.Tabla_LOG[n]]
    

    def GMAC(self, mensaje, key):
        y = [0] * 128
        for i in range(1, 128):
            temp = y[i-1] ^ mensaje[i]
            temp = self.producto(temp, key)
            y[i] = temp
        return y

gf = G_F()
print(gf.GMAC(bytearray.fromhex(0x80000000000000000000000000000000), bytearray.fromhex(0x00000000000000000000000000000002)))