import secrets as scr
import os


def get_length():
    """Prompt the user for a positive integer number of bytes."""
    while True:
        try:
            value = int(input("how many bytes do you need? "))
            if value <= 0:
                print("Please enter a positive integer.")
                continue
            return value
        except ValueError:
            print("Please enter a valid integer.")


long_bytes = get_length()
os.makedirs("data_file", exist_ok=True)
random_bytes = scr.token_bytes(long_bytes)
password_bytes = random_bytes.hex()

with open("data_file/Token.txt", "w", encoding="utf-8") as f:
    f.write(password_bytes)

print(f"Generated password ({long_bytes} bytes): {password_bytes}")

# now just generate the password by myself.
