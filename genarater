import secrets as scr
import os
import math

long_bytes=int(input("how bit password do you need?"))
os.makedirs("date file",exist_ok=True)
radome_byte=scr.token_bytes(long_bytes)
password_bytes= radome_byte.hex()

with open("date file/Token.txt","w",encoding='utf-8') as f:
    f.write(password_bytes)

#now just generate the password by my self..

