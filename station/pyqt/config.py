from kv.redis_kv import models
from typing import Dict
import qrcode

MAX_RETRIES = 3
WIDTH_SCREEN = 800
HEIGHT_SCREEN = 600


color_qr_code: Dict[str, str] = {
    models.STATE_IDLE: "#ffffff",
    models.STATE_BOOKED: "#EE6700",
}

url_qr_code: Dict[str, str] = {}

path_qr_code: Dict[str, str] = {
    models.STATE_IDLE: "pyqt/qml/pages/activation/img/qrcode_activate.png",
    models.STATE_BOOKED: "pyqt/qml/pages/booked/img/qrcode_booked.png",
}

connector_image_mapping = {
    "TES_US": "1",
    "IEC_62196": "2",
    "J1772": "3",
    "GB_T_AC": "4",
}

connector_name_mapping = {
    "TES_US": "Tesla US (NACT)",
    "IEC_62196": "IEC62196 (TYPE-II)",
    "J1772": "J1772 (TYPE-I)",
    "GB_T_C": "GB/T (AC)",
}


def generate_qr(color, url, width=444, height=444, path='pyqt/pages/activation/img/qrcode_activate.png'):
    qr_data = url

    qr = qrcode.QRCode(
        border=1,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)

    qr_image = qr.make_image(fill_color="black", back_color=color)

    qr_image = qr_image.resize((width, height))
    qr_image.save(path)


def is_generate_qr(state, url) -> bool:
    if (color_qr_code.get(state) is not None and (url_qr_code.get(state) is None or url_qr_code.get(state) != url)):
        url_qr_code[state] = url
        return True
    return False


def human_delta(seconds):
    """
    Converts total duration seconds in 'HH:mm:ss' format.
    Example: human_delta(17995.1) prints '04:59:55'
    """
    seconds = int(seconds)  # don't care about milliseconds
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    return f'{h:02}:{m:02}:{s:02}'
