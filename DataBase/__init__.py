
try:
    from .dataBase import storeFallAlertData
except ImportError as e:
    print("Could not import storeFallAlertData function ",e)

try:
    from .dataBase import storeFireAlertData
except ImportError as e:
    print("Could not import storeFireAlertData function ",e)