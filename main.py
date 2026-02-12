import key_create
from cryptography.fernet import Fernet

def load_key():
    try:
        file =  open("key.key",  "rb")
        key = file.read()
        file.close()
        return key
    except FileNotFoundError:
        print("Error: key.key file not found. Run setup first!")

stored_key = load_key()
fer = Fernet(stored_key)

# The encode() is take the string and convert it to bytes
# The decode() is take the bytes and convert it to string

def view():
    try:
        with open("passwords.txt", "r") as f:
            for line in f.readlines():
                data = line.rstrip() # get did of the newline character in the end
                if not data: # skip empty lines
                    continue
                user, passw = data.split("|")
                print("username:", user, "|", "password:", fer.decrypt(passw.encode()).decode())
    except FileNotFoundError:
        print("No passwords stored yet. Add a password first!")

# what the split do: "hello|kumar|yes|2" -> ["hello", "shathu"], "yes", "2"]
# only use 'w' mode to overwrites the file, if you don't wann overwrites it use 'a' mod
# b'hello' -> b is for bytes, the string is in bytes format, we need to decode it to get the original strin

def add():
    name = input("Username: ")
    pwd = input("Password: ")
    with open("passwords.txt", "a") as f:
        # f.write(name, "|", pwd) -> error
        f.write(name + "|" + fer.encrypt(pwd.encode()).decode() + "\n")

        # In above, first pwd change it to string to bytes then encrypt then
        # decode for making it to string to store in the text fil

attempt = 0
while attempt < 3:
    mas_pwd =  input("What's the master password: ")
    derived_key = key_create.create_key(mas_pwd)

    if stored_key == derived_key:
        while True:
            choice = input("Would you like to add a new password or view existing ones (view, add, q): ").lower()
            if choice == "view":
                view()
                continue
            elif choice == "add":
                add()
                continue
            elif choice == "q":
                print("Password manager closed...")
                break
            else:
                print("Invalid input, Try again")
                continue
        break
    else:
        print("Wrong key!, Try again")
        attempt += 1