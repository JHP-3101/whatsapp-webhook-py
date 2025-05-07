from enum import Enum

class Menu (str, Enum):
    MENU_1 = "menu-1"
    MENU_2 = "menu-2"
    
class ChecksumPin (str, Enum):
    PIN = "SaltNyaSaltNyaSaltNyaSaltNyaSalt"
    
class PLMSSecretKey (str, Enum):
    SECRET_KEY = "XJeS2iaUvWDV4qlmhotUc02VAbFGy5r46vdYAIrx"

class PLMSUser(str, Enum):
    USERNAME = "MIDIKRING"
    PASSWORD = "1lGwrMtZgw"
    
class PLMSEndpoint (str, Enum):
    ENDPOINT = "https://stg-partnerv2.gli.id/v2/midikring"



