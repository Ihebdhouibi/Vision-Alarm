try:
    from .base import QValkkaRobberyDetectorProcess
except ImportError as e:
    print("Could not import QValkkaRobberyDetectorProcess "+str(e))


try:
    from .PersonDetector import PersonDetector
except ImportError as e:
    print("Could not import PersonDetector "+str(e))