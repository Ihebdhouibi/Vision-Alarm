# This is where we handle our imports within try exception blocks

try:
    from .base import QValkkaFallDetection
except ImportError as e:
    print("Could not import QValkkaFallDetectionProcess class : "+str(e))

try:
    from .CentroidTracker import CentroidTracker
except ImportError as e:
    print("Could not import CentroidTracker class : "+str(e))

try:
    from .FallDetector import FallDetector
except ImportError as e:
    print("Could not import FallDetector class : "+str(e))