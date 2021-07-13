
try:
    from .base import QValkkaFallDetection
except ImportError as e:
    print("Could not import QValkkaFallDetectionProcess class : "+str(e))