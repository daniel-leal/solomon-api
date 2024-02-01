from enum import Enum


class Kinds(str, Enum):
    CREDIT = "credit"
    DEBIT = "debit"
    TRANSFER = "transfer"
    PIX = "pix"
    CASH = "cash"
