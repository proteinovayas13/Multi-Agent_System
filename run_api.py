"""
Run LangGraph Agent API
"""
import sys
import os

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from src.api import app
    import uvicorn
    
    if __name__ == "__main__":
        print("="*60)
        print(" LangGraph Agent API")
        print("="*60)
        print(" API: http://localhost:8000")
        print(" Docs: http://localhost:8000/docs")
        print("="*60)
        uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()