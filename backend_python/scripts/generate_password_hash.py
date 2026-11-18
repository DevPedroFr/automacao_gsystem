import getpass
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.auth import hash_password


def main():
    password = getpass.getpass("Nova senha: ")
    confirmation = getpass.getpass("Confirme a senha: ")
    if not password or password != confirmation:
        raise SystemExit("As senhas estão vazias ou não coincidem.")
    print(hash_password(password))


if __name__ == "__main__":
    main()
