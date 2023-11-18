from G_F import G_F
import random

class AES:
	'''
	Documento de referencia:
	Federal Information Processing Standards Publication (FIPS) 197: Advanced Encryption
	Standard (AES) https://doi.org/10.6028/NIST.FIPS.197-upd1
	
	El nombre de los metodos, tablas, etc son los mismos (salvo capitalizacion)
	que los empleados en el FIPS 197
	'''

	def __init__(self, key, Polinomio_Irreducible = 0x15f):
		'''
		Entrada:
		key: bytearray de 16 24 o 32 bytes
		Polinomio_Irreducible: Entero que representa el polinomio para construir
		el cuerpo

		SBox: equivalente a la tabla 4, pag. 14
		InvSBOX: equivalente a la tabla 6, pag. 23
		Rcon: equivalente a la tabla 5, pag. 17
		InvMixMatrix : equivalente a la matriz usada en 5.3.3, pag. 24
		'''

		#Convertim la key, que es una bytearray, a un string (basicament perque tot ho haviem programat com si la clau d'entrada fos un string)
		self.key = key
		aux = ""
		for i in self.key:
			hex_string = f"{i:02x}"
			aux+= hex_string[:2]
		self.key = aux


		self.Polinomio_Irreducible = Polinomio_Irreducible
		self.CosFinit = G_F(self.Polinomio_Irreducible)
		self.Nb = 0
		self.Nk = 0
		self.Nr = 0
  
		#Segons la longitud de la clau indiquem els valors de Nb, Nk i Nr adients
		if len(self.key) == 32:
			self.Nb = 4 
			self.Nk = 4 
			self.Nr = 10
		# 192-bit key
		elif len(self.key) == 48:
			self.Nb = 4; self.Nk = 6; self.Nr = 12
		# 256-bit key
		elif len(self.key) == 64:
			self.Nb = 4; self.Nk = 8; self.Nr = 14

		self.circulant = [	[1, 0, 0, 0, 1, 1, 1, 1],
							[1, 1, 0, 0, 0, 1, 1, 1],
							[1, 1, 1, 0, 0, 0, 1, 1],
							[1, 1, 1, 1, 0, 0, 0, 1],
							[1, 1, 1, 1, 1, 0, 0, 0],
							[0, 1, 1, 1, 1, 1, 0, 0],
							[0, 0, 1, 1, 1, 1, 1, 0],
							[0, 0, 0, 1, 1, 1, 1, 1]]


		#Calculem Matriu SBox
		self.SBox = [0] * 256
		self.InvSBox = [0] * 256
		self.CreateSBox()
		
		#Calculem Matriu Rcon
		self.Rcon = [[0] * 4 for _ in range(10)]
		value = 1
		for i in range(10):
			self.Rcon[i][0] = value
			value = self.CosFinit.producto(value,2)

		self.InvMixMatrix = [
		0x0e, 0x0b, 0x0d, 0x09, 
		0x09, 0x0e, 0x0b, 0x0d,
		0x0d, 0x09, 0x0e, 0x0b, 
		0x0b, 0x0d, 0x09, 0x0e]

	def CreateSBox(self):
		size = len(self.SBox)
		for b in range(size):
			b_prima = self.CosFinit.inverso(b)
			b_bits = list("{0:08b}".format(b_prima))
			b_bits = b_bits[::-1]
			resultat_bits = [0] * 8
			for j in range(len(b_bits)):
				parcial = 0
				for i in range(len(b_bits)):
					parcial += (self.circulant[j][i]*int(b_bits[i]))%2
				resultat_bits[j] = parcial%2

			resultat_bits = resultat_bits[::-1]
			resultat = (int("".join(str(i) for i in resultat_bits), 2)^0x63)
			self.SBox[b] = resultat
			self.InvSBox[resultat] = b

	def SubBytes(self, State):
		'''
		5.1.1 SUBBYTES()
		FIPS 197: Advanced Encryption Standard (AES)
		'''
		n_column = len(State[0])
		n_row = len(State)
		for row in range(n_row):
			for col in range(n_column):
				State[row][col] = self.SBox[State[row][col]]
		return State

	def InvSubBytes(self, State):
		'''
		5.3.2 INVSUBBYTES()
		FIPS 197: Advanced Encryption Standard (AES)
		'''
		n_column = len(State[0])
		n_row = len(State)
		for row in range(n_row):
			for col in range(n_column):
				State[row][col] = self.InvSBox[State[row][col]]
		return State

	def ShiftRows(self, State):
		'''
		5.1.2 SHIFTROWS()
		FIPS 197: Advanced Encryption Standard (AES)
		'''
		new_state = [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]

		for row in range(4):
			for col in range(4):
				new_state[row][col] = State[row][(col + row) % 4]

		return new_state

	def InvShiftRows(self, State):
		''' G_F(self.Polinomio_Irreducible)
		5.3.1 INVSHIFTROWS()
		FIPS 197: Advanced Encryption Standard (AES)
		'''
		new_state = [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]

		for row in range(4):
			for col in range(4):
				new_state[row][(col + row) % 4] = State[row][col]

		return new_state

	def MixColumns(self, State):
		'''
		5.1.3 MIXCOLUMNS()
		FIPS 197: Advanced Encryption Standard (AES)
		'''
		mixMatrix = [[2,3,1,1], [1,2,3,1],[1,1,2,3],[3,1,1,2]]
		new_state = [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]

		for i in range(4):
			for j in range(4):
				suma = 0
				for k in range(4):
					suma ^= self.CosFinit.producto(mixMatrix[j][k],State[k][i])
				new_state[j][i] = suma
		
		return new_state

	def InvMixColumns(self, State):
		'''typecryption Standard (AES)
		'''
		mixMatrix = [[0x0e,0x0b,0x0d,0x09],[0x09,0x0e,0x0b,0x0d],[0x0d,0x09,0x0e,0x0b],[0x0b,0x0d,0x09,0x0e]]
		new_state = [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]	
		
		for i in range(4):
			for j in range(4):
				suma = 0
				for k in range(4):
					suma ^= self.CosFinit.producto(mixMatrix[j][k],State[k][i])
				new_state[j][i] = suma
		
		return new_state

	def RotWord(self, column):
		size = len(column)
		new_column = [[0] * size for _ in range(size)]
		for i in range(size):
			new_column[i] = column[(i+1)%size]
		return new_column

	def SubWord(self, column):
		size = len(column)
		for i in range(size):
			column[i] = self.SBox[column[i]]
		return column

	def XorWord(self, column1, column2):
		size = len(column1)
		for i in range(size):
			column1[i] ^= column2[i]
		return column1

	def matrix2column(self, matrix, n_column):
		size = len(matrix)
		column = [[0] * size for _ in range(size)]
		for j in range(size):
			column[j] = matrix[j][n_column]
		return column

	def KeyExpansion(self, key):
		'''
		5.2 KEYEXPANSION()
		FIPS 197: Advanced Encryption Standard (AES)   2b7e151628aed2a6abf7158809cf4f3c
		'''
		key = self.string2matrix(key)
		expanded_key = [[0 for _ in range(4 * (self.Nr+1))] for _ in range(4)]
		for i in range(4):
			for j in range(self.Nk):
				expanded_key[i][j] = key[i][j]

		i = self.Nk
		while (i <= 4*self.Nr+3):
			temp = self.matrix2column(expanded_key,i-1)
			if (i%self.Nk == 0):
				column = self.RotWord(temp)
				column = self.SubWord(column)
				column2 = self.Rcon[i//self.Nk-1]
				temp = self.XorWord(column,column2)			
			elif (self.Nk > 6 and i % self.Nk == 4):
				temp = self.SubWord(temp)


			temp1 = self.matrix2column(expanded_key,i-self.Nk)
			temp = self.XorWord(temp1,temp)
			for j in range(4):
				expanded_key[j][i] = temp[j]
			i+=1
   
		return expanded_key

	def AddRoundKey(self, state, key):
		size = len(state[0])
		column_size = len(key)

		for i in range(size):
			column = self.XorWord(self.matrix2column(key,i), self.matrix2column(state,i))
			for j in range(column_size):
				state[j][i] = column[j]

		return state

	def Cipher(self, State, Nr, Expanded_KEY):
		'''
		5.1 Cipher(), Algorithm 1 pag. 12
		FIPS 197: Advanced Encryption Standard (AES)
		'''	
		size = len(State[0])
		State = self.AddRoundKey(State, Expanded_KEY[:size])

		for i in range(1, Nr):
			State = self.SubBytes(State)
			State = self.ShiftRows(State)
			State = self.MixColumns(State)
			State = self.AddRoundKey(State, [fila[size*i:size*(i+1)] for fila in Expanded_KEY])

		State = self.SubBytes(State)
		State = self.ShiftRows(State)
		State = self.AddRoundKey(State, [fila[size*(Nr):size*(Nr+1)] for fila in Expanded_KEY])

		return State


	def InvCipher(self, State, Nr, Expanded_KEY):
		'''
		5. InvCipher()
		Algorithm 3 pag. 20 o Algorithm 4 pag. 25. Son equivalentes
		FIPS 197: Advanced Encryption Standard (AES)
		'''

		# InvExpanded_KEY = self.invert_expanded_key(Expanded_KEY)

		size = len(State[0])
		State = self.AddRoundKey(State, [fila[size*(Nr):size*(Nr+1)] for fila in Expanded_KEY])
		# print(Nr)
		for i in range(Nr-1,0,-1):
			State = self.InvShiftRows(State) #OK
			State = self.InvSubBytes(State) #OK
			State = self.AddRoundKey(State, [fila[size*i:size*(i+1)] for fila in Expanded_KEY])
			State = self.InvMixColumns(State)

		State = self.InvShiftRows(State)
		State = self.InvSubBytes(State)
		State = self.AddRoundKey(State, Expanded_KEY[:size])

		return State
	

	def string2matrix(self, key_string):
		length = len(key_string)/2
		key_matrix = [[0 for _ in range(int(length/4))] for _ in range(4)]

		for i in range(int(length/4)):
			for j in range(4):
				key_matrix[j][i] = int(key_string[(i*4+j)*2:(i*4+j)*2+2], 16)

		return key_matrix

	def	file2bytes(self, file):		 							#FIXME NOMS HORROROSOS (BUSCAR MILLOR NOMS PER FUNCIONS)
		matriu = []
		fila_actual = []
		for element in file:
			fila_actual.append(element)
			if len(fila_actual) == self.Nb:
				matriu.append(fila_actual)
				fila_actual = []
		if fila_actual:
			matriu.append(fila_actual)
		return matriu

	def add_padding(self, data, block_size):
		padding_size = block_size - (len(data) % block_size)
		padding = bytes([padding_size] * padding_size)
		return bytes(data) + padding

	def XorMatrix(self, matrix1, matrix2):
		if (len(matrix1) != len(matrix2) or len(matrix1) != len(matrix2)):
			print("[ERROR]: Les matrius estat i CBC són de diferents mides i no podem fer XOR")
			exit()
		for i in range(len(matrix1)):
			for j in range(len(matrix1)):
				matrix1[i][j] ^= matrix2[i][j]
		return matrix1

	def girarMatriu(self, matriu):
		matriu_girada = [[0 for _ in range(len(matriu))] for _ in range(len(matriu[0]))]
		for i in range(len(matriu)):
			for j in range(len(matriu[0])):
				matriu_girada[j][i] = matriu[i][j]
		return matriu_girada

	def encrypt_file(self, file):
		'''
		Entrada: Nombre del fichero a cifrar
		Salida: Fichero cifrado usando la clave utilizada en el constructor
		de la clase.
		Para cifrar se usara el modo CBC, con IV generado aleatoriamente
		y guardado en los 16 primeros bytes del fichero cifrado.
		El padding usado sera PKCS7.
		El nombre de fichero cifrado sera el obtenido al a~nadir el sufijo .enc
		al nombre del fichero a cifrar: NombreFichero --> NombreFichero.enc
		'''
		resultat = bytearray()

		file_data = open(file, "rb").read()
		expanded_key = self.KeyExpansion(self.key)
		llista_bytes = [byte for byte in file_data]
	
		padded_data = self.add_padding(llista_bytes, self.Nb*4)
		states = self.file2bytes(padded_data)

		iv = [[random.randint(0, 255) for _ in range(4)] for _ in range(4)]

		# Escrivim iv en la bytearray
		for j in range(len(iv[0])):
			for i in range(len(iv)):
				resultat.append(iv[i][j])


		for i in range(0, len(states), self.Nb):
			state = states[i:i+4]
			state = [[row[i] for row in state] for i in range(len(state[0]))]
			
			ciphered_state = self.XorMatrix(iv, state)
			ciphered_state = self.Cipher(ciphered_state, self.Nr, expanded_key)
			iv = ciphered_state     #Ara el nou "estat" amb el que farem la XOR es l'estat anterior xifrat
   
			#Escrivim l'estat a la bytearray
			for j in range(len(ciphered_state[0])):
				for i in range(len(ciphered_state)):
					resultat.append(ciphered_state[i][j])

		#Escrivim al fitxer .enc
		with open(file+".enc", "wb") as f:
			f.write(resultat)		
   

	def decrypt_file(self, file):
		'''
		Entrada: Nombre del fichero a descifrar
		Salida: Fichero descifrado usando la clave utilizada en el constructor
		de la clase.
		Para descifrar se usara el modo CBC, con el IV guardado en los 16
		primeros bytes del fichero cifrado, y se eliminara el padding
		PKCS7 a~nadido al cifrar el fichero.
		El nombre de fichero descifrado sera el obtenido al a~nadir el sufijo .dec
		al nombre del fichero a descifrar: NombreFichero --> NombreFichero.dec
		'''
  
		llista_estats_desxifrats = []
  
		file_data = open(file, "rb").read()
		x = len(file_data)

		expanded_key = self.KeyExpansion(self.key)
	
		while (x > 16):   #Els 16 primers bytes seran el IV que no formen part del fitxer original
			final = bytearray()
			a=file_data[x-16:x]
			state = [[0] * 4 for _ in range(4)]
			for i in range(4):
				for j in range(4):
					state[j][i] = a[i * 4 + j]

			state = self.InvCipher(state,self.Nr,expanded_key)
			b=file_data[x-32:x-16]
			previous_state = [[0] * 4 for _ in range(4)]

			for i in range(4):
				for j in range(4):
					previous_state[j][i] = b[i * 4 + j]

			orig_state = self.XorMatrix(previous_state,state)
   
			for j in range(len(orig_state[0])):
				for i in range(len(orig_state)):
					final.append(orig_state[i][j])	
     
			llista_estats_desxifrats.append(final)
			x-=16
   
		llista_estats_desxifrats = llista_estats_desxifrats[::-1] #Girem perque hem començat a llegir desde el últim byte 

		resultat = bytearray()
		for byte in llista_estats_desxifrats:
			for b in byte:
				resultat.append(b)

		pad = resultat[-1] #Numero de bytes que corresponen al padding
		resultat = resultat[:-pad] #treiem els bytes del padding

		#Escrivim al fitxer .dec
		with open(file+".dec", "wb") as f:
			f.write(resultat)
		

aes = AES(b'ace468cbaf7d820188be6e5f5fafd301')
aes.decrypt_file("cifrado.txt")

