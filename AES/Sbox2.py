def generate_Sbox(p):
    t = [0] * 256
    x = 1
    for i in range(256):
        t[i] = x
        x ^= (x << 1) ^ ((x >> 7) *p)

    Sbox = [0] * 256
    Sbox[0] = 0x63
    for i in range(255):
        x = t[255 - i]
        x |= x << 8
        x ^= (x >> 4) ^ (x >> 5) ^ (x >> 6) ^ (x >> 7)
        Sbox[t[i]] = (x ^ 0x63) & 0xFF

    return Sbox

# You can call the function like this, providing the value of 'p':
p_value = 0x11B  # Replace with your desired 'p' value
result_Sbox = generate_Sbox(p_value)
#Result to hexadecimal
result_Sbox = [hex(i) for i in result_Sbox]
print(result_Sbox)
