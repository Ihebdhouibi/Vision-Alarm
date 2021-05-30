# Importing FireDetection Package

try:
    from . import FireDetection
except Exception as e:
    print("Vision-Alarm.MachineVision.__init__ : could not import module FireDetection "+str(e))
