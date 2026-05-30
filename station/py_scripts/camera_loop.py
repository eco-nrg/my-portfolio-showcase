import os
import time
from concurrent.futures import Executor, ThreadPoolExecutor
from threading import Event, Thread
from urllib.parse import urljoin

import cv2
import numpy as np
import requests


from py_scripts.custom_logger import logger

os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp"

SAVE_IMG_PATH = os.path.abspath('images')
THREAD_TIMEOUTS = 10
SEND_IMAGE_INTERVAL = 4  # in seconds
RESTART_STREAM_AFTER = 8  # in seconds
IMG_QUALITY = 50

endpoint_path = "/main/api/v1/upload_camera_image/{}/"


class Client:
    def __init__(self, source, read_interval, timeout) -> None:
        self.source = source
        self.stream = None
        self.timeout = timeout
        self.read_interval = read_interval  # how often to read the stream
        self.__thread = None
        self.__terminate = Event()
        self.__stream_read = Event()
        self.__frame = None

    def start(self):
        self.__thread = Thread(target=self.__update, name='CameraLoop.update')
        self.__thread.daemon = True
        self.__thread.start()
        return self

    def __update(self):
        logger.info('Starting stream reader', source=self.source)
        self.stream = cv2.VideoCapture(self.source)
        logger.info('Connected to stream', source=self.source)

        prev_update = time.time()
        while not self.__terminate.is_set():
            self.__stream_read.clear()

            grabbed = self.stream.grab()
            if not grabbed:
                break

            now = time.time()
            dt = now - prev_update
            if dt > self.read_interval:
                prev_update = now
                ret, frame = self.stream.retrieve()
                if not ret:
                    logger.error('Failed to retrieve a frame',
                                 source=self.source)
                    break
                self.__frame = frame
                self.__stream_read.set()

        # signal stream is finished
        self.__frame = None
        self.__terminate.set()
        self.__stream_read.set()
        # might be blocked
        logger.info('Releasing stream', source=self.source)
        self.stream.release()
        logger.info('Released stream', source=self.source)

    def read(self):
        '''
        Блокирующе ждем следующий фрейм, но не больше self.timeout секунд.
        Возвращает np.ndarray картинку или None
        '''
        if self.__terminate.is_set():
            return None

        if self.__stream_read.wait(timeout=self.timeout):
            return self.__frame

        logger.warning('Read frame timeout in %s sec', self.timeout)
        return None

    def stop(self):
        logger.info('Terminating stream', source=self.source)
        self.__stream_read.set()
        self.__terminate.set()
        if self.__thread is not None:
            self.__thread.join(timeout=self.timeout)


def minify_img(img: np.ndarray):
    scale_percent = 50  # percent of original size
    width = int(img.shape[1] * scale_percent / 100)
    height = int(img.shape[0] * scale_percent / 100)
    dim = (width, height)
    resized = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)
    return resized


def send_file_to_server(filepath, camera_id, api_url, api_token, timeout):
    endpoint_url = urljoin(api_url, endpoint_path.format(camera_id))
    with open(filepath, "rb") as img:
        name_img = os.path.basename(filepath)
        files = {"image": (name_img, img, "image/jpeg", {"Expires": "0"})}
        r = requests.post(endpoint_url.format(camera_id),
                          files=files,
                          headers={'Authorization': 'Bearer ' + api_token},
                          timeout=timeout)
        logger.debug("camera loop %s status: %d", camera_id, r.status_code)


def save_img(frame, camera_id):
    os.makedirs(SAVE_IMG_PATH, exist_ok=True)
    frame_name = "frame_{}.jpg".format(camera_id)
    filepath = os.path.join(SAVE_IMG_PATH, frame_name)
    params = [int(cv2.IMWRITE_JPEG_QUALITY), IMG_QUALITY]
    if not cv2.imwrite(filepath, frame, params):
        logger.warning('Failed to save image at %s', filepath)
        return None
    return filepath


class ImageProcessor:
    def __init__(self, save_path, api_url, api_token, camera_id,
                 executor: Executor) -> None:
        self.save_path = save_path
        self.api_url = api_url
        self.api_token = api_token
        self.camera_id = camera_id
        self.executor = executor

    def process(self, frame: np.ndarray):
        if frame is not None:
            self.executor.submit(self.__process, frame.copy())

    def __process(self, frame):
        img = minify_img(frame)
        filepath = save_img(img, self.camera_id)
        if filepath is None:
            return
        try:
            send_file_to_server(filepath, self.camera_id,
                                self.api_url, self.api_token,
                                timeout=1)
        except IOError as err:
            logger.exception('Cannot send frame to API', exception=err, exc_info=True)


def run_loop(source, processor: ImageProcessor):
    logger.info("trying to connect to camera %s", source)

    client = Client(source,
                    read_interval=SEND_IMAGE_INTERVAL,
                    timeout=THREAD_TIMEOUTS)
    client.start()

    while True:
        frame = client.read()
        if frame is None:
            logger.info('Empty frame', source=client.source)
            break

        logger.debug('onframe', source=source)
        processor.process(frame)

    client.stop()
    logger.info('run_loop exit', source=source)


def camera_manager(source, processor: ImageProcessor) -> None:
    '''
    Запускает бесконечный цикл перезапуска потока конкретной камеры.
    Это мог бы быть systemd unit, но так как в рамках конфига можно получить много камер, то это происходит именно здесь.
    '''
    while True:
        try:
            run_loop(source, processor)
        except Exception as e:
            logger.exception('Unhandled exception', exception=e, exc_info=True)
        logger.info("Restart stream '%s' in %d seconds",
                    source, RESTART_STREAM_AFTER)
        # предыдущая команда могла завершиться только в том случае, если поток прервался
        # поэтому мы ждем некоторое время и пытаемся опять запустить цикл обработки камеры
        time.sleep(RESTART_STREAM_AFTER)


def main():
    # TODO: нужен механизм обновления конфига камеры
    # Раньше скрипт запускался каждую секунду, поэтому конфиг считывался полностью каждую секунду
    # что позволяло изменить натсроийки на лету.
    # но коннекция к rtsp потоку это дорогая и глючная операция, поэтому лучше один раз подцепиться и висеть.
    # Можно предусмотреть механизм, что конфиг перечитывается каждую секунду и если он поменялся, то перезапустить потоки.
    # Если бы конфиг был файлом, то это можно было бы сделать даже внешне

    from config import get_settings

    settings = get_settings()
    executor = ThreadPoolExecutor(
        max_workers=1,
        thread_name_prefix='uploader-')

    threads = []
    for camera in settings.cameras:
        processor = ImageProcessor(
            SAVE_IMG_PATH,
            api_url=settings.api_url,
            api_token=settings.api_token,
            camera_id=camera.id,
            executor=executor)
        t = Thread(
            target=camera_manager,
            args=(camera.rtsp_url, processor),
            daemon=True)
        threads.append(t)

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    executor.shutdown(wait=False)


def test():
    executor = ThreadPoolExecutor(max_workers=1,
                                  thread_name_prefix='uploader-')
    processor = ImageProcessor(
        SAVE_IMG_PATH,
        api_url='http://localhost:8000',
        api_token='???',
        camera_id='0',
        executor=executor)
    run_loop('rtp://127.0.0.1:9988', processor)


if __name__ == '__main__':
    main()

'''
Пример кода для запуска локального rtp стрим на вебкамере для тестирования:

ffmpeg \
  -f avfoundation \
  -pix_fmt yuyv422 \
  -video_size 640x480 \
  -framerate 30 \
  -i "0:0" -ac 2 \
  -vf format=yuyv422 \
  -vcodec libx264 -maxrate 2000k \
  -tune zerolatency \
  -f rtp_mpegts udp://127.0.0.1:9988
'''
