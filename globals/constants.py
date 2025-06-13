from enum import Enum

class Menu (str, Enum):
    MEMBER = "menu-member"
    MENU_2 = "menu-2"
    MAIN_MENU = "main-menu"
    
    MEMBER_VALIDASI = "validasi-member"
    MEMBER_AKTIVASI = "aktivasi-member"
    MEMBER_CEK_POIN = "cek-poin-member"
    MEMBER_STATUS_KARTU = "status-kartu-member"
    MEMBER_RIWAYAT_TRANSAKSI_POIN = "riwayat-transaksi-poin-member"
    MEMBER_RESET_PIN = "reset-pin-member"
    
class ChecksumPin (str, Enum):
    PIN = "SaltNyaSaltNyaSaltNyaSaltNyaSalt"
    
class PLMSSecretKey (str, Enum):
    SECRET_KEY = "XJeS2iaUvWDV4qlmhotUc02VAbFGy5r46vdYAIrx"

class PLMSUser(str, Enum):
    USERNAME = "MIDIKRING"
    PASSWORD = "1lGwrMtZgw"
    
class PLMSEndpoint (str, Enum):
    ENDPOINT = "https://stg-partnerv2.gli.id/v2/midikring"
    
class WAFlow (str, Enum):
    # Flow Activate
    WAFLOW_MODE_ACTIVATE = "draft"
    WAFLOW_TOKEN_ACTIVATE = "wqcOJyw9BVAQQ5BYtmG0RBFOlzNrFbt2rEXp1m8jnWk="
    WAFLOW_ID_ACTIVATE = "645744804970894"
    
    # Flow Reset PIN
    WAFLOW_MODE_RESET_PIN = "draft"
    WAFLOW_ID_RESET_PIN = "1349590416116753"
    WAFLOW_TOKEN_RESET_PIN = "7u+0EqXmWZmw8Z+S15KiyGu8dlEFpjam3cYFMYz4IpM="
    

