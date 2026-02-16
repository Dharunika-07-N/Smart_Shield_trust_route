"""
Environment Variable Validator
Validates required environment variables on application startup
"""

import os
import sys
from typing import List, Dict, Optional
from dotenv import load_dotenv

load_dotenv()


class EnvironmentValidator:
    """Validates environment variables and provides helpful error messages"""
    
    # Required environment variables
    REQUIRED_VARS = [
        "SECRET_KEY",
        "JWT_SECRET_KEY",
        "DATABASE_URL",
    ]
    
    # Optional but recommended variables
    RECOMMENDED_VARS = [
        "GOOGLE_MAPS_API_KEY",
        "SMTP_SERVER",
        "SMTP_USERNAME",
        "SMTP_PASSWORD",
    ]
    
    # AI Provider variables (at least one required for AI features)
    AI_PROVIDER_VARS = [
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "GOOGLE_API_KEY",
    ]
    
    @classmethod
    def validate(cls, strict: bool = False) -> Dict[str, any]:
        """
        Validate environment variables
        
        Args:
            strict: If True, raise exception on missing required vars
            
        Returns:
            Dictionary with validation results
        """
        results = {
            "valid": True,
            "missing_required": [],
            "missing_recommended": [],
            "missing_ai_providers": [],
            "warnings": [],
            "errors": []
        }
        
        # Check required variables
        for var in cls.REQUIRED_VARS:
            value = os.getenv(var)
            if not value or value.startswith("placeholder") or value.startswith("change-me"):
                results["missing_required"].append(var)
                results["valid"] = False
                results["errors"].append(f"Required variable {var} is missing or has placeholder value")
        
        # Check recommended variables
        for var in cls.RECOMMENDED_VARS:
            value = os.getenv(var)
            if not value or value.startswith("placeholder"):
                results["missing_recommended"].append(var)
                results["warnings"].append(f"Recommended variable {var} is not set")
        
        # Check AI provider variables (at least one should be set)
        ai_providers_set = []
        for var in cls.AI_PROVIDER_VARS:
            value = os.getenv(var)
            if value and not value.startswith("placeholder") and not value.startswith("sk-placeholder"):
                ai_providers_set.append(var)
        
        if not ai_providers_set:
            results["missing_ai_providers"] = cls.AI_PROVIDER_VARS
            results["warnings"].append(
                "No AI provider API keys configured. AI features will not work. "
                "Set at least one of: OPENAI_API_KEY, ANTHROPIC_API_KEY, or GOOGLE_API_KEY"
            )
        
        # Validate specific formats
        cls._validate_database_url(results)
        cls._validate_jwt_secret(results)
        
        # Print results
        cls._print_results(results)
        
        # Raise exception if strict mode and validation failed
        if strict and not results["valid"]:
            raise EnvironmentError(
                f"Environment validation failed. Missing required variables: {', '.join(results['missing_required'])}"
            )
        
        return results
    
    @classmethod
    def _validate_database_url(cls, results: Dict):
        """Validate DATABASE_URL format"""
        db_url = os.getenv("DATABASE_URL")
        if db_url:
            if db_url.startswith("sqlite:///"):
                env = os.getenv("ENVIRONMENT", "development")
                if env == "production":
                    results["warnings"].append(
                        "Using SQLite in production is not recommended. Consider PostgreSQL."
                    )
    
    @classmethod
    def _validate_jwt_secret(cls, results: Dict):
        """Validate JWT secret strength"""
        jwt_secret = os.getenv("JWT_SECRET_KEY")
        if jwt_secret and len(jwt_secret) < 32:
            results["warnings"].append(
                "JWT_SECRET_KEY should be at least 32 characters long for security"
            )
    
    @classmethod
    def _print_results(cls, results: Dict):
        """Print validation results to console"""
        print("\n" + "="*60)
        print("🔍 ENVIRONMENT VALIDATION")
        print("="*60)
        
        if results["valid"]:
            print("✅ All required environment variables are set")
        else:
            print("❌ Environment validation failed!")
            print("\nMissing Required Variables:")
            for var in results["missing_required"]:
                print(f"  - {var}")
        
        if results["warnings"]:
            print("\n⚠️  Warnings:")
            for warning in results["warnings"]:
                print(f"  - {warning}")
        
        if results["missing_recommended"]:
            print("\n💡 Recommended Variables (not set):")
            for var in results["missing_recommended"]:
                print(f"  - {var}")
        
        print("\n" + "="*60 + "\n")


def validate_environment(strict: bool = False) -> Dict:
    """
    Convenience function to validate environment
    
    Args:
        strict: If True, raise exception on validation failure
        
    Returns:
        Validation results dictionary
    """
    return EnvironmentValidator.validate(strict=strict)


if __name__ == "__main__":
    # Run validation when executed directly
    strict_mode = "--strict" in sys.argv
    validate_environment(strict=strict_mode)
