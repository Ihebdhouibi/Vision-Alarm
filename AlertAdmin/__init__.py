try:
    from .AlertAdmin import send_sms
except ImportError as e:
    print("Failed to import send_sms "+str(e))

