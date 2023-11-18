import numpy as np

class G_F:
    '''
    Genera un cuerpo finito usando como polinomio irreducible el dado
    representado como un entero. Por defecto toma el polinomio del AES.
    Los elementos del cuerpo los representaremos por enteros 0<= n <= 255.
    '''
    def __init__(self, Polinomio_Irreducible = 0x11B):
        '''
        Entrada: un entero que representa el polinomio para construir el cuerpo
        Tabla_EXP y Tabla_LOG dos tablas, la primera tal que en la posicion
        i-esima tenga valor a=g**i y la segunda tal que en la posicion a-esima
        tenga el valor i tal que a=g**i. (g generador del cuerpo finito
        representado por el menor entero entre 0 y 255.)
        '''
        self.Polinomio_Irreducible = Polinomio_Irreducible
        self.grado_polinomio = self.calcula_grado_polinomio()
        self.Tabla_EXP = np.ones(2**self.grado_polinomio,dtype=int)
        self.Tabla_LOG = np.zeros(2**self.grado_polinomio,dtype=int)

        g = self.buscar_generador()  #Busquem el generador i creem le taules EXP i LOG que ens serviran per fer les multiplicacions i divisions mès ràpidament

    def calcula_grado_polinomio(self):  #Retorna el grau del polinomi ireducible. Ho fa passant la representació del polinomi en binari i contant el numero de bits que hi ha
        return len(bin(self.Polinomio_Irreducible)[2:])-1
    

    def buscar_generador(self):
        q = 2**self.grado_polinomio-1  #Com a molt 2^n - 1 elements en un cos finit GF(2^n) sense contar el 0
        
        #Mirem cadascun dels elements que pot ser un generador
        for g in range(2,q):
            cnt = 1
            j = 1
            m = g  #En m anirem guardant les diferents g^j
            while (m!= 1):    #Quan trobem el 1 ja haurem acabat el cicle començant desde l'element g
                self.Tabla_EXP[j] = m  #Actualitzem les taules. Ho podem anar fent tot el rato perqué la ultima iteració que fem serà amb el generador i per tant ja estaran correctes
                self.Tabla_LOG[m] = j
                m = self.producte_lent(m,g)  #calculem g^j * g
                cnt+=1
                j+=1
            if (cnt == q): return g   #Si hem trobat tots els elements es que g es un generador

    def xTimes(self, n):
        '''
        Entrada: un elemento del cuerpo representado por un entero entre 0 y 255
        Salida: un elemento del cuerpo representado por un entero entre 0 y 255
        que es el producto en el cuerpo de ’n’ y 0x02 (el polinomio X).
        '''
        if (n < 2**(self.grado_polinomio-1)): #En aquest cas nomès cal desplaçar els bits cap a l'esquerra ja que no obtindrem un polinomi de grau > grado_polinomio
            return n << 1
        else:
            return (n << 1) ^ self.Polinomio_Irreducible   #Cal fer la XOR per obtindre un polinomi amb grau < grado_polinomio
        
    def producte_lent(self,a,b):
        resultat = 0
        control = 1  #Ens servirà per mirar si el bit de b ès 0 o 1
        for i in range(self.grado_polinomio): 
            if (b & control != 0):   #Si el bit es 1, cal sumar el valor de a*x^i al resultat final
                resultat ^= a
                
            control = control << 1  #Desplacem per mirar el següent bit de b
            a = self.xTimes(a)   #Multipliquem (a*x^i)*x
        return resultat % self.Polinomio_Irreducible #Retornem el resultat assegurant que cau dins del camp finit generat pel polinomi

    def producto(self, a, b):
        '''
        Entrada: dos elementos del cuerpo representados por enteros entre 0 y 255
        Salida: un elemento del cuerpo representado por un entero entre 0 y 255
        que es el producto en el cuerpo de la entrada.
        Atenci´on: Se valorar´a la eficiencia. No es lo mismo calcularlo
        usando la definici´on en t´erminos de polinomios o calcular
        usando las tablas Tabla_EXP y Tabla_LOG.
        '''
        if (a == 0 or b == 0): return 0
        return self.Tabla_EXP[(self.Tabla_LOG[a] + self.Tabla_LOG[b])%255]

    
    def inverso(self, n):
        '''
        Entrada: un elementos del cuerpo representado por un entero entre 0 y 255
        Salida: 0 si la entrada es 0,
        el inverso multiplicativo de n representado por un entero entre
        1 y 255 si n <> 0.
        Atenci´on: Se valorar´a la eficiencia.
        '''
        if (n == 0): return 0
        return self.Tabla_EXP[255-self.Tabla_LOG[n]]

cos = G_F(2**8+2**7+2**2+2**1+1)

m = 0x80
H = 0x02
print(cos.producto(m,H))
#AES Rijndael Flash
