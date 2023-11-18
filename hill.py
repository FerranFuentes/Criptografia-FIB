#open text file 
#from numpy import *
import itertools
from sympy import *
from collections import Counter

f = open('enc.txt', 'r')
text = f.read()

#get characters in groups of 3
groups = []
for i in range(0, len(text), 3):
    groups.append(text[i:i+3])

#get the 3 mosrtr repeated groups
most_repeated = Counter(groups).most_common(3)

lista = ['THE', 'AND', 'ING', 'HER', 'HAT', 'HIS', 'THA', 'ERE', 'FOR', 'ENT']

trigramas = itertools.permutations(lista, 3)
iter = 0

for perm in trigramas:

    matrixC = Matrix(3, 3, [0, 0, 0, 0, 0, 0, 0, 0, 0])
    matrixM = Matrix(3, 3, [0, 0, 0, 0, 0, 0, 0, 0, 0])

    for i in range(3):
        for j in range(3):
            word = most_repeated[i][0]
            matrixC[i, j] = ord(word[j]) - 65

    for i in range(3):
        for j in range(3):
            word = perm[i]
            matrixM[i, j] = ord(word[j]) - 65


    if gcd(matrixM.det(), 26) != 1:
        print("Matrix M is not invertible")
        continue

    A = matrixM.inv_mod(26) * matrixC

    A = A%26

    A = A.transpose()

    A = A.inv_mod(26)

    for i in range(int(len(text) / 3)):
        vectorD = Matrix(3,1, [0, 0, 0])
        for j in range(3):
                vectorD[j] = ord(text[i * 3 + j]) - 65
        result = A * vectorD

        for j in range(3):
            char = int((result[j] % 26) + 65)
            #print(chr(char), end='')
            open('hill_decrypted' + str(iter)+ '.txt', 'a').write(chr(char))

    iter = iter+1

exit()



