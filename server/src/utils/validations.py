import re

from server.src.error_handling.exceptions.validationException import PasswordCommonError,PasswordSpaceError,PasswordLengthError,PasswordComplexityError,UsernameLengthError,UsernameFormatError

PASSWORD_REGEX = re.compile(
    r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&]).+$"
)

COMMON_PASSWORDS = {
    "password", "password123", "12345678", "123456789",
    "qwerty", "qwertyuiop", "admin", "admin123"
}

def validate_password(password: str) -> str:
    password = password.strip()

    # length
    if not (8 <= len(password) <= 30):
        raise PasswordLengthError()

    # complexity
    if not PASSWORD_REGEX.match(password):
        raise PasswordComplexityError

    # common passwords (case-insensitive)
    if password.lower() in COMMON_PASSWORDS:
        raise PasswordCommonError()

    # no spaces inside
    if " " in password:
        raise PasswordCommonError()


    return password


# ---------------- USERNAME ----------------
USERNAME_REGEX = re.compile(r"^[a-zA-Z0-9_]+$")

def validate_username(username: str) -> str:
    if not (3 <= len(username) <= 30):
        raise UsernameLengthError()

    if not USERNAME_REGEX.match(username):
        raise UsernameFormatError()


    return username


# ---------------- EMAIL NORMALIZATION ----------------
def normalize_email(email: str) -> str:
    return email.strip().lower()
