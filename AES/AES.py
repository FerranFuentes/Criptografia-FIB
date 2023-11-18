class G_F:
    def __init__(self, Polinomio_Irreductible = 0x11B):
        self.Polinomio_Irreductible = Polinomio_Irreductible
        self.Tabla_EXP = [0] * 256
        self.Tabla_LOG = [0] * 256

    def generarTablas(self):
        x = 0x01
        for log in range(0, 255):
            self.Tabla_EXP[log] = x
            self.Tabla_LOG[x] = log
            x = self.xTimes(x)

    def xTimes(self, n):
        x = n
        x = x << 1
        if x & 0x100:
            x = x ^ self.Polinomio_Irreductible
        return x
    

    def producto(self, a ,n):
        return self.Tabla_EXP[(self.Tabla_LOG[a] + self.Tabla_LOG[n]) % 255]

    
    def inverso(self, n):
        if n == 0:
            return 0
        else:
            for i in range(0, 255):
                if self.producto(n, i) == 1:
                    return i
                
class AES:
    def __init__(self, key, Polinomio_Irreductible = 0x11B):
        self.Polinomio_Irreductible = Polinomio_Irreductible
        self.SBox = [0] * 256
        self.InvSBox = [0] * 256
        #self.Rcon
        #self.InvMixMatrix
        self.GF = G_F(self.Polinomio_Irreductible)

    def generarTablas(self):
        self.SBox = [0] * 256
        self.InvSBox = [0] * 256
        self.SBox[0] = 0x63
        print("Test0")

        for i in range(1, 256):
            print("Test")
            inverso = self.GF.Tabla_EXP[255 - self.GF.Tabla_LOG[i]]
            self.SBox[i] = inverso ^ 0x63
            self.InvSBox[256-i] = self.SBox[i]

    
    def SubBytes(self, State):
        for i in range(0, 4):
            for j in range(0, 4):
                State[i][j] = self.SBox[State[i][j]]
    
    def InvSubBytes(self, State):
        for i in range(0, 4):
            for j in range(0, 4):
                State[i][j] = self.InvSBox[State[i][j]]
    
    def ShiftRows(self, State):
        for i in range(1, 4):
            State[i] = State[i][i:] + State[i][:i]
    
    def InvShiftRows(self, State):
        for i in range(1, 4):
            State[i] = State[i][-i:] + State[i][:-i]
    
    def GetSBox(self):
        return self.SBox
    
    #def MixColumns(self, State):

def main():
    polinomio = 0x11B
    #calculamos el inverso multiplicativo
    t = [0] * 256
    x = 0x01
    for i in range(1, 256):
        t[i] = x
    

if __name__ == "__main__":
    main()


        
        

    
