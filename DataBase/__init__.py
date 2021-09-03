
try:
    from .dataBase import storeFallAlertData
except ImportError as e:
    print("Could not import storeFallAlertData function ",e)

try:
    from .dataBase import storeFireAlertData
except ImportError as e:
    print("Could not import storeFireAlertData function ",e)

try:
    from .dataBase import retrieve_fire_alerts
except ImportError as e:
    print("Could not import retrieve_fire_alerts function ",e)

try:
    from .dataBase import retrieve_robbery_alerts
except ImportError as e:
    print("Could not import retrieve_robbery_alerts function ",e)

try:
    from .dataBase import retrieve_fall_alerts
except ImportError as e:
    print("Could not import retrieve_fall_alerts function ",e)