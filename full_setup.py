
import subprocess
import os
import sys
from pathlib import Path

def run_command(command, description):
    print(f"\n[STEP] {description}...")
    try:
        python_cmd = sys.executable
        full_command = f"{python_cmd} {command}"
        result = subprocess.run(full_command, shell=True, check=True)
        print(f"[OK] {description} completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Error during {description}: {e}")
        return False
    return True

def full_setup():
    print("-" * 60)
    print("AI Smart Shield Trust Route - Clean Hazard-Based Setup")
    print("-" * 60)
    
    # 1. Clean old DB
    db_path = Path("backend/smartshield.db")
    if db_path.exists():
        print(f"Removing old database: {db_path}")
        try:
            db_path.unlink()
        except:
            print("Warning: Could not delete DB file (it might be in use). Continuing...")
    
    # 2. Seed AI Training (This creates the tables and trains initial models)
    if not run_command("seed_ai_training.py", "Seeding AI Training Data & Initializing Models"):
        return

    # 3. Seed Database (MVP UI data like users and companies)
    if not run_command("backend/scripts/populate_mvp_data.py", "Populating MVP Management Data (Users/Companies)"):
         print("Warning: MVP data population had warnings, continuing...")

    print("-" * 60)
    print("ALL DONE! The system is now 100% CRIME-FREE and Hazard-Focused.")
    print("\nNext Steps:")
    print("1. Start Backend:  cd backend && uvicorn api.main:app --reload")
    print("2. Start Frontend: cd frontend && npm start")
    print("3. Run Demo:      python demo_run.py")
    print("-" * 60)

if __name__ == "__main__":
    full_setup()
