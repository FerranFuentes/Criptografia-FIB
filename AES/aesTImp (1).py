import os
import argparse
import random


class G_F:

    def __init__(self, Polinomio_Irreducible):
        self.Tabla_EXP = [0] * 256
        self.Tabla_LOG = [0] * 256
        self.Polinomio_Irreducible = Polinomio_Irreducible

        # Inicializa la tabla Tabla_EXP y Tabla_LOG
        
        '''NO SABEMOS POR QUE RAZON NOS DA EROROR, POR ESO USAMOS XTIMES EN MIXCOLUMNS
        (x = 1
        for i in range(256):
            self.Tabla_EXP[i] = x
            self.Tabla_LOG[x] = i
            x = self.xTimes(x))
        '''
            


    def xTimes(self, n):
        result = n << 1
        # Si el resultado nos da mayor que 255 hacemos XOR con el polinomio irreducible.
        if result > 255:
            result ^= self.Polinomio_Irreducible
        return result


    def producto(self, a, b):
        if a == 0 or b == 0:
            return 0
        else:
            log_a = self.Tabla_LOG[a]
            log_b = self.Tabla_LOG[b]
            log_result = (log_a + log_b) % 255
            result = self.Tabla_EXP[log_result]
            return result


    def inverso(self, n):
        if n == 0:
            return 0
        else:
            log_n = self.Tabla_LOG[n]
            log_result = 255 - log_n
            result = self.Tabla_EXP[log_result]
            return result



class AES:
    
    def generate_s_boxes(self):
        # Para generar las Sbox hemos usado https://github.com/Merricx/aes-sbox/blob/master/sbox.js
        # Calculamos el multiplicativo inverso
        t = [0] * 256
        x = 1
        for i in range(256):
            t[i] = x
            x ^= (x << 1) ^ ((x >> 7) * self.Polinomio_Irreducible)

        # Generate Sbox with Affine transformation
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
    
    


    def generate_rcon(self):
        self.Rcon = [1]
        for i in range(1, 10):
            self.Rcon.append(self.gf.xTimes(self.Rcon[i-1]))



    def __init__(self, key, Polinomio_Irreducible):
        self.Polinomio_Irreducible = Polinomio_Irreducible
        self.gf = G_F(self.Polinomio_Irreducible)
        self.SBox = [0]*256
        self.InvSBox = [0]*256
        self.generate_s_boxes()

        self.Rcon = (
                    0x00, 0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40,
                    0x80, 0x1B, 0x36, 0x6C, 0xD8, 0xAB, 0x4D, 0x9A,
                    0x2F, 0x5E, 0xBC, 0x63, 0xC6, 0x97, 0x35, 0x6A,
                    0xD4, 0xB3, 0x7D, 0xFA, 0xEF, 0xC5, 0x91, 0x39,
                    )


        self.InvMixMatrix=(
            [0x0E, 0x0B, 0x0D, 0x09],
            [0x09, 0x0E, 0x0B, 0x0D],
            [0x0D, 0x09, 0x0E, 0x0B],
            [0x0B, 0x0D, 0x09, 0x0E]
        )
        self.Nk = 4  
        self.Nr = 10
        self.Expanded_KEY = self.KeyExpansion(key)


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


    def mix_single_column(self, State):
        column_bytes = State[0] ^ State[1] ^ State[2] ^ State[3]
        column_first_byte = State[0]
        State[0] ^= column_bytes ^ self.gf.xTimes(State[0] ^ State[1])
        State[1] ^= column_bytes ^ self.gf.xTimes(State[1] ^ State[2])
        State[2] ^= column_bytes ^ self.gf.xTimes(State[2] ^ State[3])
        State[3] ^= column_bytes ^ self.gf.xTimes(State[3] ^ column_first_byte)

    def MixColumns(self, State):
        print("MASTER STATE: ", State)
        for i in range(4):
            self.mix_single_column(State[i])

    def InvMixColumns(self, State):
        print("SLAVE STATE: ", State)
        for i in range(4):
            a = self.gf.xTimes(self.gf.xTimes(State[i][0] ^ State[i][2]))
            b = self.gf.xTimes(self.gf.xTimes(State[i][1] ^ State[i][3]))
            State[i][0] ^= a
            State[i][1] ^= b
            State[i][2] ^= a
            State[i][3] ^= b

        self.MixColumns(State)
    

    def AddRoundKey(self, State, roundKey):
        for i in range(4):
            for j in range(4):
                State[i][j] ^= roundKey[i][j]
    

    def bytes2matrix(self, text):
        return [list(text[i:i+4]) for i in range(0, len(text), 4)]

    def matrix2bytes(self, matrix):
        return bytes(sum(matrix, []))

    def xor_bytes(self, a, b):
        """ Returns a new byte array with the elements xor'ed. """
        return bytes(i^j for i, j in zip(a, b))

    def KeyExpansion(self, key):
        # Initialize round keys with raw key material.
        key_columns = self.bytes2matrix(key)
        iteration_size = len(key) // 4

        i = 1
        while len(key_columns) < (self.Nr + 1) * 4:
            # Copy previous word.
            word = list(key_columns[-1])

            # Perform schedule_core once every "row".
            if len(key_columns) % iteration_size == 0:
                # Circular shift.
                word.append(word.pop(0))
                # Map to S-BOX.
                word = [self.SBox[b] for b in word]
                # XOR with first byte of R-CON, since the others bytes of R-CON are 0.
                word[0] ^= self.Rcon[i]
                i += 1
            elif len(key) == 32 and len(key_columns) % iteration_size == 4:
                # Run word through S-box in the fourth iteration when using a
                # 256-bit key.
                word = [self.SBox[b] for b in word]

            # XOR with equivalent word from previous iteration.
            word = self.xor_bytes(word, key_columns[-iteration_size])
            key_columns.append(word)

        # Group key words in 4x4 byte matrices.
        return [key_columns[4*i : 4*(i+1)] for i in range(len(key_columns) // 4)]


    def Cipher(self, State, Nr, Expanded_KEY):
        pt_state = self.bytes2matrix(State)
        self.AddRoundKey(pt_state, self.Expanded_KEY[0])
        for i in range(1, self.Nr):
            self.SubBytes(pt_state)
            self.ShiftRows(pt_state)
            self.MixColumns(pt_state)
            roundKey = self.Expanded_KEY[i]  
            self.AddRoundKey(pt_state, roundKey)
        self.SubBytes(pt_state)
        self.ShiftRows(pt_state)
        self.AddRoundKey(pt_state, self.Expanded_KEY[-1])

        State = self.matrix2bytes(pt_state)
        return State


    def InvCipher(self, State, Nr, Expanded_KEY):
        cipher_state = self.bytes2matrix(State)
        self.AddRoundKey(cipher_state, self.Expanded_KEY[-1])   
        self.InvShiftRows(cipher_state)
        self.InvSubBytes(cipher_state)

        for i in range(self.Nr - 1, 0, -1):             
            roundKey = self.Expanded_KEY[i]  
            self.AddRoundKey(cipher_state, roundKey)
            self.InvMixColumns(cipher_state)
            self.InvShiftRows(cipher_state)
            self.InvSubBytes(cipher_state)
            
            

        roundkey = self.Expanded_KEY[0]
        self.AddRoundKey(cipher_state, roundkey)

        State = self.matrix2bytes(cipher_state)
        return State


    def pad(self, plaintext):
        """
        Pads the given plaintext with PKCS#7 padding to a multiple of 16 bytes.
        Note that if the plaintext size is a multiple of 16,
        a whole block will be added.
        """
        padding_len = 16 - (len(plaintext) % 16)
        padding = bytes([padding_len] * padding_len)
        return plaintext + padding


    def unpad(self, plaintext):
        """
        Removes a PKCS#7 padding, returning the unpadded text and ensuring the
        padding was correct.
        """
        padding_len = plaintext[-1]
        assert padding_len > 0
        message, padding = plaintext[:-padding_len], plaintext[-padding_len:]
        assert all(p == padding_len for p in padding)
        return message

    def split_blocks(self, message, block_size=16, require_padding=True):
        assert len(message) % block_size == 0 or not require_padding
        return [message[i:i+16] for i in range(0, len(message), block_size)]

    def encrypt_file(self, fichero):
        # Generar un IV aleatorio de 16 bytes
        iv = os.urandom(16)

        # Obtener el nombre del archivo cifrado
        output_filename = fichero + ".enc"

        # Abrir el archivo de entrada y lectura
        with open(fichero, 'rb') as input_file:
            plaintext = input_file.read()
        # Aplicar el padding PKCS7
        plaintext = self.pad(plaintext)

        # Dividir el texto en bloques de 16 bytes
        block_size = 16
        encrypted_blocks = []
        previous = iv
        for i in self.split_blocks(plaintext):
            # Debes implementar el cifrado AES para cada bloque y almacenar el resultado en encrypted_block
            encrypted_block = self.Cipher(self.xor_bytes(i, previous), self.Nr, self.Expanded_KEY)
            # Agrega el bloque cifrado a la lista
            encrypted_blocks.append(encrypted_block)
            # Iguala previous al bloque actual
            previous = encrypted_block
            

        # Escribir el IV en el archivo cifrado
        with open(output_filename, 'wb') as output_file:
            output_file.write(iv)
            # Escribir los bloques cifrados en el archivo
            for encrypted_block in encrypted_blocks:
                output_file.write(encrypted_block)

        print(f"Archivo cifrado y guardado como {output_filename}")

    def decrypt_file(self, fichero):
        # Obtener el nombre del archivo original sin la extensión ".enc"
        output_filename = "decrypted_" + fichero[:-4] 

        iv = 0

        # Leer el IV del archivo cifrado
        with open(fichero, 'rb') as input_file:
            iv = input_file.read(16)
            input_file.seek(16)
            ciphertext = input_file.read()

        # Inicializar la lista para almacenar los bloques descifrados
        decrypted_blocks = []
        

        previous = iv
        # Abrir el archivo cifrado y leer los bloques cifrados
        with open(fichero, 'rb') as input_file:
            for i in self.split_blocks(ciphertext):
                decrypted_block = self.InvCipher(i, self.Nr, self.Expanded_KEY)
                decrypted_blocks.append(self.xor_bytes(previous, decrypted_block))
                previous = i

        # Unir los bloques descifrados
        decrypted_data = b"".join(decrypted_blocks)

        # Eliminar el relleno PKCS7
        decrypted_data = self.unpad(decrypted_data)

        # Escribir los datos descifrados en un archivo de salida
        with open(output_filename, 'wb') as output_file:
            output_file.write(decrypted_data)

        print(f"Archivo descifrado y guardado como {output_filename}")

        


def main():
    parser = argparse.ArgumentParser(description="Algoritmo de cifrado y descifrado AES")
    # Argumentos y opciones
    parser.add_argument("-c", action="store_true", help="Cifrar un archivo")
    parser.add_argument("-d", action="store_true", help="Descifrar un archivo")
    parser.add_argument("-k", required=True, help="Clave")
    parser.add_argument("-p", required=True, help="Polinomio Irreducible")
    parser.add_argument("-i", required=True, help="Archivo de entrada")

    args=parser.parse_args()
    
    if args.c or args.d:
        if args.k and args.p:
            # Convertir el valor del polinomio irreducible a entero
            polinomio_irreducible = int(args.p, 16)
            key = bytes.fromhex(args.k)
            aes = AES(key, polinomio_irreducible)
            if args.c:
                aes.encrypt_file(args.i)
            elif args.d:
                aes.decrypt_file(args.i)
        else:
            print("Se requieren los argumentos -k y -p.")
    else:
        parser.print_usage()

if __name__ == "__main__":
    main()
