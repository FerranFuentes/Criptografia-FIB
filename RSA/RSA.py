import hashlib
import copy
import sympy
import random
import math

d = 16

class block: 
    def __init__(self):
        self.block_hash
        self.previous_block_hash
        self.transaction = transaction(150, RSAkey())
        self.seed

    def genesis(self, transaction):
        """
        genera el primer bloque de una cadena con la transacci´on "transaction"
        que se caracteriza por:
            - previous_block_hash=0
            - ser v´alido
        """
        self.transaction = transaction
        self.previous_block_hash = 0
        self.getBlockHash(transaction)
    
    def next_block(self, transaction):
        """
        genera un bloque v´alido seguiente al actual con la transacci´on "transaction"
        """
        self.transaction = transaction
        self.previous_block_hash = self.block_hash
        self.getBlockHash(transaction)

    def verify_block(self):
        """
        Verifica si un bloque es v´alido:
            -Comprueba que el hash del bloque anterior cumple las condiciones exigidas
            -Comprueba que la transacci´on del bloque es v´alida
            -Comprueba que el hash del bloque cumple las condiciones exigidas
        Salida: el booleano True si todas las comprobaciones son correctas;
        el booleano False en cualquier otro caso.
        """
        previous_block_check = self.previous_block_hash < 2**(256-d)
        transaction_check = self.transaction.verify()
        current_check = self.block_hash < 2**(256-d) and self.getHash(self.seed, self.transaction) == self.block_hash
        return previous_block_check and transaction_check and current_check
    
    def getBlockHash(self, transaction):
        seed = 0
        h = self.getHash(seed, transaction)
        while h > 2**(256-d):
            seed += 1
            h = self.getHash(seed, transaction)
        self.seed = seed
        self.block_hash = h

    def getHash(self, seed, transaction):
        entrada = str(self.previous_block_hash)
        entrada += str(transaction.public_key.publicExponent)
        entrada += str(transaction.public_key.modulus)
        entrada += str(transaction.message)
        entrada += str(self.transaction.signature)
        entrada += str(seed)
        h = int(hashlib.sha256(entrada.encode()).hexdigest(), 16)
        return h


class transaction: 
    def __init__(self, message, RSAkey):
        self.public_key = rsa_public_key(RSAkey)
        self.message = message
        self.signature = RSAkey.sign(message)

    def verify(self): 
        """
        Salida: el booleano True si "signature" se corresponde con la
        firma de "message" hecha con la clave RSA asociada a la clave
        p´ublica RSA;
        el booleano False en cualquier otro caso.
        """
        return self.public_key.verify(self.message, self.signature)

class block_chain:
    def __init__(self, transaction):
        block = block()
        block.genesis(transaction)
        self.list_of_blocks = [block]
    
    def add_block(self, transaction):
        """
        Añade un bloque a la cadena v´alido generado con la transacci´on "transaction"
        """
        new_block = copy.deepcopy(self.list_of_blocks[-1])
        new_block.next_block(transaction)
        self.list_of_blocks.append(new_block)

        

    def verify(self):
        """
        verifica si la cadena de bloques es v´alida:
        - Comprueba que todos los bloques son v´alidos
        - Comprueba que el primer bloque es un bloque "genesis"
        - Comprueba que para cada bloque de la cadena el siguiente es correcto
        Salida: el booleano True si todas las comprobaciones son correctas;
        en cualquier otro caso, el booleano False y un entero
        correspondiente al ´ultimo bloque v´alido
        """
        if self.list_of_blocks[0].previous_block_hash != 0:
            return False, 0 
        for i in range(1, len(self.list_of_blocks)):
            if not self.list_of_blocks[i].verify_block():
                return False, i-1
            if  i > 0 and self.list_of_blocks[i].previous_block_hash != self.list_of_blocks[i-1].block_hash:
                return False, i-1
        return True


class RSAkey:
    def __init__(self, bits_modulo=2048, e = 2**16+1):
        self.publicExponent = e
        self.privateExponent = int(sympy.gcdex(e, self.phi)[0])
        self.primeP, self.primeQ =  self.getPrimes(e, bits_modulo)
        self.modulus = self.primeP*self.primeQ
        self.phi = (self.primeP-1)*(self.primeQ-1)
        self.privateExponentModulusPhiP = int(self.privateExponent % (self.primeP-1))
        self.privateExponentModulusPhiQ = int(self.privateExponent % (self.primeQ-1))
        self.inverseQModulusP = int(sympy.mod_inverse(self.primeQ, self.primeP))

        self.check_congruence(self.privateExponent * self.publicExponent, 1, self.phi)
        self.check_congruence(self.privateExponentModulusPhiP, self.privateExponent, 1, self.primeP-1)
        self.check_congruence(self.privateExponentModulusPhiQ, self.privateExponent, 1, self.primeQ-1)
        self.check_congruence(self.inverseQModulusP * self.primeQ, 1, self.primeP)

    def check_congruence(self, a, c, m):
        if (a % m) != (c % m):
            exit("Congruencia no valida")
        else:
            return True
    
    def sign(self, message):
        """
        Salida: un entero que es la firma de "message" hecha con la clave RSA usando el TCR
        """
        a = pow(message, self.privateExponentModulusPhiP, self.primeP)
        b = pow(message, self.privateExponentModulusPhiQ, self.primeQ)
        qq = self.inverseQModulusP * self.primeQ
        pp = 1 - qq
        return qq*a + pp*b

    def sign_slow(self, message):
        """
        Salida: un entero que es la firma de "message" hecha con la clave RSA sin usar el TCR
        """
        return pow(message, self.privateExponent, self.modulus)
    
    def verify(self, message, signature):
        return pow(signature, self.publicExponent, self.modulus) == message
    
    def getPrimes(self, e, bits_modulo):
        while True:
            p = random.getrandbits(bits_modulo)
            retry = 1
            while not sympy.isprime(p):
                retry += 1
                p = random.getrandbits(bits_modulo)
            q = random.getrandbits(bits_modulo)
            while not sympy.isprime(q) or p == q:
                retry += 1
                q = random.getrandbits(bits_modulo)
            if math.gcd(e,p*q) == 1 and e < (p-1)*(q-1):
                return int(p), int (q)

class rsa_public_key:
    def __init__(self, rsa_key):
        self.modulus
        self.publicExponent

    def verify(self, message, signature):
        """
        Salida: el booleano True si "signature" se corresponde con la
        firma de "message" hecha con la clave RSA asociada a la clave
        p´ublica RSA;
        el booleano False en cualquier otro caso.
        """
        return pow(signature, self.publicExponent, self.modulus) == message
    

