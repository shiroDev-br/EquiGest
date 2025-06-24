from enum import Enum

class MareType(Enum):
    RECEIVER = "RECEIVER"
    HEADQUARTERS = "HEADQUARTERS"

class PaymentAccessStatus(Enum):
    TRIAL = "TRIAL"
    PAYED = "PAYED"
    DEFEATED = "DEFEATED"

class DeleteType(Enum):
    FAIL_PREGNANCY = "FAIL_PREGNANCY"
    SUCCESS_PREGNANCY = "SUCCESS_PREGNANCY"