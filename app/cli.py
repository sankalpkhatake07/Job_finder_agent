import sys
from .db import init_db, SessionLocal
from .services.pipeline import run_scan

def main():
    init_db()
    if len(sys.argv)<2 or sys.argv[1] != "scan":
        print("Usage: python -m app.cli scan"); return 2
    with SessionLocal() as db: print(run_scan(db)); return 0
if __name__ == "__main__": raise SystemExit(main())
