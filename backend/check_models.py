import sys
sys.exit(0) if __import__("app.models", fromlist=["Recruiter"]) else sys.exit(1)
