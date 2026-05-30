class SPACE_STATUSES:
    AVAILABLE = "AV"
    CHARGING = "CH"
    BUSY = "BU"
    DISABLED = "DI"
    BOOKED = "BO"


class SPACE_MODES:
    PRODUCTION = "PROD"
    TEST = "TEST"


class METER_MODELS:
    M_234_ART_02_POR = "M_234_ART_02_POR"  # старый с реле и RS-485
    M_234_ARTM2_02_POBR_R = "M_234_ARTM2_02_POBR_R"  # новый с реле и RS-485
    M_206_PRNO = "M_206_PRNO"


class PARKLOCK_TYPES:
    TTLOCK = "ttlock"
    QH_COM_PARKINGLOCK = "qh.com.parkinglock"
