# Here we will import FireDetectionAnalyzer from FireDetection base.py file
try:
    from .base import QValkkaFireDetectorProcess
except ImportError as e:
    print("Could not import QValkkaFireDetectorProcess class : "+str(e))