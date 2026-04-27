from services.google_auth import get_credentials

if __name__ == "__main__":
    creds = get_credentials()
    print("Autenticación OK")
