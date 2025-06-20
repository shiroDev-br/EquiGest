from enum import Enum

class MareType(Enum):
    RECEIVER = "RECEIVER"
    HEADQUARTERS = "HEADQUARTERS"

class PaymentAccessStatus(Enum):
    TRIAL = "TRIAL"
    PAYED = "PAYED"
    DEFEATED = "DEFEATED"