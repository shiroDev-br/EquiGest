from pwdlib import PasswordHash

pwd_context = PasswordHash.recommended()


def hash_password(password: str):
    return pwd_context.hash(password)


def check_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)