import os

class G_F:

    def __init__(self, Polinomio_Irreducible = 0x15f):


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
       for i in range(8):
            if b & 1: p ^= a
            high_bit_set = a & 0x80
            a <<= 1
            a &= 0xFF
            if high_bit_set:
                a ^= self.Polinomio_Irreducible
            b >>= 1
       return p

    def inverso(self, n):
        if n == 0:
            return 0
        return self.Tabla_EXP[255 - self.Tabla_LOG[n]]

class AES:

    def __init__(self, Key, Polinomio_Irreducible=0x1f9):
        self.Polinomio_Irreducible = Polinomio_Irreducible
        self.gf = G_F(self.Polinomio_Irreducible)
        self.SBox = [0] * 256
        self.InvSBox = [0] * 256
        self.Rcon = (
                    0x00, 0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40,
                    0x80, 0x1B, 0x36, 0x6C, 0xD8, 0xAB, 0x4D, 0x9A,
                    0x2F, 0x5E, 0xBC, 0x63, 0xC6, 0x97, 0x35, 0x6A,
                    0xD4, 0xB3, 0x7D, 0xFA, 0xEF, 0xC5, 0x91, 0x39,
                    )
        self.InvMixMatrix = [
            [0x0E, 0x0B, 0x0D, 0x09],
            [0x09, 0x0E, 0x0B, 0x0D],
            [0x0D, 0x09, 0x0E, 0x0B],
            [0x0B, 0x0D, 0x09, 0x0E]
        ]  # Debes completar con la matriz inversa de MixColumns
        self.Nk = 4  # Número de palabras en la clave (4, 6 u 8)
        self.Nr = 10  # Número de rondas (depende de Nk)
        self.Key = bytes.fromhex(Key)
        self.Expanded_KEY = Key
        self.generate_Sbox_InvSbox()

    def generate_Sbox_InvSbox(self):
        p = self.Polinomio_Irreducible
        t = [0] * 256
        x = 1
        for i in range(256):
            t[i] = x
            x ^= (x << 1) ^ ((x >> 7) *p)

        Sbox = [0] * 256
        Sbox[0] = 0x63
        InvSbox = [0] * 256
        for i in range(255):
            x = t[255 - i]
            x |= x << 8
            x ^= (x >> 4) ^ (x >> 5) ^ (x >> 6) ^ (x >> 7)
            Sbox[t[i]] = (x ^ 0x63) & 0xFF
            InvSbox[Sbox[t[i]]] = t[i]
        self.SBox = Sbox
        self.InvSBox = InvSbox
        return 
    
    def sam_rcon(self, round):
        rcon = 0x8d

        for i in range(0, round):
            rcon = ((rcon << 1) ^ (self.Polinomio_Irreducible & - (rcon >> 7))) & 0xff
        return rcon
    
    # Definir los métodos restantes de acuerdo a las especificaciones del AES

    def SubBytes(self, State):
        for i in range(4):
            for j in range(4):
                State[i][j] = self.SBox[State[i][j]]

    def InvSubBytes(self, State):
        for i in range(4):
            for j in range(4):
                State[i][j] = self.InvSBox[State[i][j]]

    def ShiftRows(self, State):
        State[0][1], State[1][1], State[2][1], State[3][1] = State[1][1], State[2][1], State[3][1], State[0][1]
        State[0][2], State[1][2], State[2][2], State[3][2] = State[2][2], State[3][2], State[0][2], State[1][2]
        State[0][3], State[1][3], State[2][3], State[3][3] = State[3][3], State[0][3], State[1][3], State[2][3]

    


    def InvShiftRows(self, State):
        State[0][1], State[1][1], State[2][1], State[3][1] = State[3][1], State[0][1], State[1][1], State[2][1]
        State[0][2], State[1][2], State[2][2], State[3][2] = State[2][2], State[3][2], State[0][2], State[1][2]
        State[0][3], State[1][3], State[2][3], State[3][3] = State[1][3], State[2][3], State[3][3], State[0][3]
   

    def MixColumns(self, State):
        for i in range(4):
            self.mixColumn(State[i])
    
    def mixColumn(self, State):
        column_bytes = State[0] ^ State[1] ^ State[2] ^ State[3]
        column_first_byte = State[0]
        State[0] ^= column_bytes ^ self.gf.xTimes(State[0] ^ State[1])
        State[1] ^= column_bytes ^ self.gf.xTimes(State[1] ^ State[2])
        State[2] ^= column_bytes ^ self.gf.xTimes(State[2] ^ State[3])
        State[3] ^= column_bytes ^ self.gf.xTimes(State[3] ^ column_first_byte)

    def InvMixColumns(self, State):
        for i in range(4):
            self.InvMixColumn(State[i])
    
    def InvMixColumn(self, column):
        gf = self.gf
        u = gf.xTimes(gf.xTimes(column[0] ^ column[2]))
        v = gf.xTimes(gf.xTimes(column[1] ^ column[3]))
        column[0] ^= u
        column[1] ^= v
        column[2] ^= u
        column[3] ^= v
        self.mixColumn(column)

    
    def xor_bytes(self, a, b):
        return bytes([x ^ y for x, y in zip(a, b)])
    
    def AddRoundKey(self, State, roundKey):
        for i in range(4):
            for j in range(4):
                State[i][j] ^= roundKey[i][j]
                
    def KeyExpansion(self, key):
        key_columns = [list(key[i:i+4]) for i in range(0, len(key), 4)]
        iteration_size = len(key) // 4
        i = 1
        while len(key_columns) < (self.Nr + 1) * 4:
            word = list(key_columns[-1])
            if len(key_columns) % iteration_size == 0:
                word.append(word.pop(0))
                word = [self.SBox[b] for b in word]
                word[0] ^= self.sam_rcon(i)
                i += 1
            elif len(key) == 32 and len(key_columns) % iteration_size == 4:
                word = [self.SBox[b] for b in word]
            word = self.xor_bytes(word, key_columns[-iteration_size])
            key_columns.append(word)

        return [key_columns[4*i : 4*(i+1)] for i in range(len(key_columns) // 4)]

                        
    def append_pkcs7_padding(self, s):
        num_padding_bytes = 16 - (len(s) % 16)
        padding = bytes([num_padding_bytes] * num_padding_bytes)
        return s + padding

    def remove_pkcs7_padding(self, data):
        last_byte = data[-1]  # Obtiene el valor del último byte
        padding_length = last_byte

        # Comprueba que el valor del último byte sea válido
        if padding_length > 16:
            raise Exception('Padding incorrecto.')
        return data[:-padding_length]
    
    def bytes2matrix(self, text):
        return [list(text[i:i+4]) for i in range(0, len(text), 4)]

    def Cipher(self, plain_block):
        plain_state = self.bytes2matrix(plain_block)
        self.AddRoundKey(plain_state, self.Expanded_KEY[0])
        for round in range(1, self.Nr):
            self.SubBytes(plain_state)
            self.ShiftRows(plain_state)
            self.MixColumns(plain_state)
            self.AddRoundKey(plain_state, self.Expanded_KEY[round])
        self.SubBytes(plain_state)
        self.ShiftRows(plain_state)
        self.AddRoundKey(plain_state, self.Expanded_KEY[-1])
        return bytes(sum(plain_state, []))


    def InvCipher(self, ciphered_block):
        cipher_state = self.bytes2matrix(ciphered_block)
        self.AddRoundKey(cipher_state, self.Expanded_KEY[-1])
        self.InvShiftRows(cipher_state)
        self.InvSubBytes(cipher_state)
        for round in range(self.Nr-1, 0, -1):
            self.AddRoundKey(cipher_state, self.Expanded_KEY[round])
            self.InvMixColumns(cipher_state)
            self.InvShiftRows(cipher_state)
            self.InvSubBytes(cipher_state)
        self.AddRoundKey(cipher_state, self.Expanded_KEY[0])
        return bytes(sum(cipher_state, []))

       
    
    def split_blocks(self, data, block_size=16):
        assert len(data) % block_size == 0
        return [data[x:x+16] for x in range(0, len(data), block_size)]

    def encrypt_file(self, input_file):
        iv = os.urandom(16)  # Genera un IV aleatorio de 16 bytes
        with open(input_file, 'rb') as f_in:
            data = f_in.read()
            filename = input_file.split('/')[-1]
            filename = filename.split('.')[0]
            with open(filename + '.enc', 'wb') as f_out:
                self.Expanded_KEY = self.KeyExpansion(self.Key)
                f_out.truncate(0)
                f_out.write(iv)
                prev_chunk = iv
                blocks = []
                data = self.append_pkcs7_padding(data)
                for plaintext_block in self.split_blocks(data):
                    xored_block = self.xor_bytes(prev_chunk, plaintext_block)
                    encrypted_block = self.Cipher(xored_block)
                    blocks.append(encrypted_block)
                    prev_chunk = encrypted_block
                encrypted_data = b''.join(blocks)
                f_out.write(encrypted_data)


    
    
    def decrypt_file(self, input_file):
        with open(input_file, 'rb') as f_in:
            iv = f_in.read(16)  # Lee el IV del archivo cifrado
            data = f_in.read()
            filename = input_file.split('/')[-1]
            filename = filename.split('.')[0]
            with open(filename + '.dec', 'wb') as f_out:  
                self.Expanded_KEY = self.KeyExpansion(self.Key)
                prev_chunk = iv 
                f_in.seek(16) 
                blocks = []
                for cipher_block in self.split_blocks(data):
                    decrypted_block = self.InvCipher(cipher_block)
                    blocks.append(self.xor_bytes(prev_chunk, decrypted_block))
                    prev_chunk = cipher_block
                decrypted_data = b''.join(blocks)
                #decrypted_data = self.remove_pkcs7_padding(decrypted_data)
                f_out.write(decrypted_data)


  
def main():
    operation = input("0: Encriptar\n1: Desencriptar\n")
    key = input("Ingrese la llave: ")
    aes_class = AES(key)
    if operation == "0":
        infile = input("Ingrese el nombre del archivo a encriptar: ")
        aes_class.encrypt_file(infile)
        print("Archivo encriptado")
    elif operation == "1":
        infile = input("Ingrese el nombre del archivo a desencriptar: ")
        aes_class.decrypt_file(infile)
        print("Archivo desencriptado")
    

if __name__ == "__main__":
    main()