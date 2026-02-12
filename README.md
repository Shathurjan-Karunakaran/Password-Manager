# Password Manager

A lightweight command-line password manager built with Python, featuring encrypted password storage and secure master password authentication.

## Features

- **Master Password Protection**: Secure authentication using a master password
- **Encryption**: Passwords are encrypted using Fernet (symmetric encryption) from the `cryptography` library
- **Key Derivation**: PBKDF2HMAC with SHA-256 for deriving encryption keys from master password
- **Simple CLI Interface**: Easy-to-use command-line interface for managing passwords
- **Add & View Passwords**: Store new passwords and retrieve existing ones
- **Failed Attempt Protection**: Limited to 3 failed master password attempts

## Requirements

- Python 3.7+
- `cryptography` library

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/password-manager.git
cd password-manager
```

2. Install dependencies:
```bash
pip install cryptography
```

3. **Initial Setup** (One-Time):
   - Uncomment the following lines in `key_create.py`:
   ```python
   # master_pwd = input("Set master password: ")
   # key = create_key(master_pwd)
   # write_key(key)
   # print("key created successfully, you can now comment out this part")
   ```
   - Run `key_create.py` and set your master password
   - Comment the lines back out to prevent overwriting your key
   - This generates `key.key` and `salt.bin` files

## Usage

Run the password manager:
```bash
python main.py
```

You'll be prompted for your master password. After successful authentication, choose from:
- **view**: Display all stored passwords
- **add**: Add a new password entry
- **q**: Quit the application

### Example Session:
```
What's the master password: ****
Would you like to add a new password or view existing ones (view, add, q): add
Username: github
Password: my_secure_password
Would you like to add a new password or view existing ones (view, add, q): view
username: github | password: my_secure_password
Would you like to add a new password or view existing ones (view, add, q): q
Password manager closed...
```

## Project Structure

```
password-manager/
├── main.py              # Main application entry point
├── key_create.py        # Key generation and management
├── passwords.txt        # Encrypted password storage (auto-created)
├── key.key             # Master encryption key (auto-generated)
├── salt.bin            # Salt for key derivation (auto-generated)
└── README.md           # This file
```

## How It Works: Encryption & Key Derivation

This password manager uses industry-standard cryptographic techniques to secure your passwords. Here's a detailed breakdown:

### 1. **Salt (salt.bin)**

**What is Salt?**
- A salt is a random string of bytes (in this case, random binary data) that is mixed with your master password
- It's stored in `salt.bin` and is NOT secret—it doesn't need to be hidden
- Each password manager generates a unique salt during setup

**Why Use Salt?**
- Prevents **rainbow table attacks** (pre-computed password-to-hash lookups)
- Ensures the same master password generates different encryption keys on different systems
- Without salt, two users with the same password would produce identical encryption keys

**How It Works:**
```
Master Password: "MyPassword123"
Salt (from salt.bin): [random 16 bytes]
        ↓
    Combined Together
        ↓
    PBKDF2 Key Derivation → Unique 32-byte Encryption Key
```

### 2. **Key Derivation (PBKDF2-SHA256)**

**What is Key Derivation?**
- Your master password is converted into a cryptographic key suitable for encryption
- This process is deliberately slow to prevent brute-force attacks

**How It Works:**
```python
PBKDF2HMAC(
    algorithm=SHA256,
    length=32 bytes (256 bits),
    salt=salt from salt.bin,
    iterations=1,200,000  # Very slow & secure
)
```

**The Process:**
1. Takes your master password + salt
2. Runs 1.2 million iterations of SHA-256 hashing
3. Produces a 32-byte encryption key
4. Each attempt to crack the password requires 1.2 million computations

**Why 1,200,000 iterations?**
- Slows down brute-force attacks significantly (takes seconds even with correct password)
- Makes automated cracking attempts impractical
- Recommended by NIST (National Institute of Standards and Technology)

### 3. **Encryption (Fernet - AES-128)**

**What is Fernet?**
- A symmetric encryption algorithm combining AES (Advanced Encryption Standard) with HMAC for authentication
- Ensures data is both encrypted AND tamper-proof
- Part of Python's `cryptography` library

**How Passwords Are Encrypted:**
```
Plain Password: "my_gmail_password_456"
               ↓
           Encrypt with Fernet Key (derived from master password)
               ↓
    Encrypted Data: "gAAAAABnx4k2xY9zK...encrypted_bytes...dQ=="
               ↓
           Store in passwords.txt
```

**What Makes It Secure:**
- **AES-128**: Military-grade encryption algorithm
- **HMAC**: Ensures no one has tampered with encrypted data
- **Authentication Tag**: Verifies the encryption key is correct when decrypting

### 4. **Decryption & Authentication**

**When You Log In:**
```
Master Password Input: "MyPassword123"
               ↓
        PBKDF2 Derivation (same salt, 1.2M iterations)
               ↓
       Generated Key (32 bytes)
               ↓
       Compare with stored key.key
               ↓
   Matches? ✅ → Grant Access
   Doesn't Match? ❌ → Deny Access (3 tries max)
```

**When You View Passwords:**
```
Encrypted Password: "gAAAAABnx4k2xY9zK...dQ=="
               ↓
     Decrypt with Verified Key
               ↓
    Plain Password: "my_gmail_password_456"
               ↓
           Display to User
```

### 5. **File Structure & Security**

| File | Purpose | Sensitive? | Can Be Public? |
|------|---------|------------|----------------|
| `salt.bin` | Random salt for key derivation | No | ✅ Yes |
| `key.key` | Derived encryption key | YES | ❌ Never |
| `passwords.txt` | Encrypted password storage | YES | ❌ Never |
| `main.py` | Application code | No | ✅ Yes |
| `key_create.py` | Key setup code | No | ✅ Yes |

**Important:** `key.key` and `passwords.txt` should NEVER be committed to GitHub or shared. If leaked, someone could decrypt all your passwords.

### 6. **Security Chain Summary**

```
┌─────────────────────────────────────────────────────────┐
│  You Enter Master Password                              │
└────────────────────┬────────────────────────────────────┘
                     ↓
        ┌────────────────────────────┐
        │ Read salt.bin (public)     │
        └────────────┬───────────────┘
                     ↓
     ┌──────────────────────────────────┐
     │ PBKDF2 Derivation (1.2M rounds)│
     │ master_pwd + salt → 32-byte key  │
     └────────────┬─────────────────────┘
                  ↓
        ┌─────────────────────┐
        │ Compare with key.key│
        └────────┬────────────┘
                 ↓
        ┌──────────────────┐        ┌─────────────┐
        │  Key Matches?    │        │ Wrong: Try  │
        │  ✅ YES ❌ NO    │        │ Again (3x)  │
        └────┬─────────────┘        └─────────────┘
             ↓
    ┌────────────────────────┐
    │ Access Granted!        │
    │ Use key to encrypt/    │
    │ decrypt passwords.txt  │
    └────────────────────────┘
```

## Security Considerations

⚠️ **Important**: This is an educational project. For production use, consider:

- **File Permissions**: The stored key and passwords should have restricted file permissions (chmod 600 on Unix systems)
- **Memory Security**: Implement proper password clearing from memory after use
- **No Remote Backup**: Currently stores everything locally without backup mechanisms
- **Master Password Strength**: Use a strong, unique master password
- **No Audit Logging**: Consider adding logging for security events
- **Environment Security**: Run in a secure environment; don't share credentials

## Suggestions for Improvement

Here are some enhancement ideas:

1. **Search/Filter**: Add ability to search passwords by username/service name
2. **Password Generation**: Generate strong random passwords
3. **Export/Import**: Allow exporting and importing passwords
4. **Delete Function**: Remove specific password entries
5. **Edit Function**: Update existing password entries
6. **Database Integration**: Use SQLite instead of plain text file
7. **Clipboard Support**: Copy password directly to clipboard
8. **Config File**: Store settings in a configuration file
9. **Master Password Reset**: Implement secure password recovery mechanism
10. **Cross-Platform GUI**: Build a GUI using tkinter or PyQt
11. **Cloud Sync**: Optional cloud synchronization with encryption
12. **OTP Support**: Two-factor authentication support
13. **Password Strength Meter**: Evaluate password strength at entry time
14. **Duplicate Detection**: Warn about duplicate passwords

## Contributing

Contributions are welcome! Feel free to fork this repository and submit pull requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This password manager is provided as an educational tool. While it uses proper encryption libraries, it's recommended for learning purposes. For critical password management in production environments, use established password managers like KeePass, Bitwarden, or 1Password.

---

**Author**: Shathurjan K  
**Last Updated**: February 2026
