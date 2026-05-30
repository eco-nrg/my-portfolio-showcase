from config import Config

_config = Config()

start_message = _config.BOT_TEXTS_START_MESSAGE
choose_connector_message = _config.BOT_TEXTS_CHOOSE_CONNECTOR_MESSAGE
choose_question_message = _config.BOT_TEXTS_CHOOSE_QUESTION_MESSAGE
parking_places = {
    'Магаданская 66а': [
        'Tesla US',
    ],
    'Петра Феленкова, 5/3': [
        'GB/T',
        'J1772',
        'IEC 62196',
    ],
    'Уральская 138': [
        'IEC 62196',
    ],
    'Конгрессная 31к1': [
        'Tesla EU - 3ф',
        'Tesla US - 1ф',
        'Jesla jp-us 1ф',
    ],
}
