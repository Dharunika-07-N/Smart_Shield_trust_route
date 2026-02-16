import secrets
import os

def generate_deployment_secrets():
    """Generate secure random strings for deployment."""
    secret_key = secrets.token_hex(32)
    jwt_secret = secrets.token_hex(32)
    
    print("--- 🛡️  Secure Secrets Generated ---")
    print(f"SECRET_KEY={secret_key}")
    print(f"JWT_SECRET_KEY={jwt_secret}")
    print("-----------------------------------")
    print("💡 Copy these into your .env.production file.")

if __name__ == "__main__":
    generate_deployment_secrets()
