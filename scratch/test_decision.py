import sys
import os

# Add the current directory to sys.path to allow imports from app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'trainds', 'backend')))

try:
    from app.services.decision_service import get_travel_decision
    print("Import successful")
    res = get_travel_decision("Dadar", 30)
    print("Result:", res)
except Exception as e:
    import traceback
    traceback.print_exc()
