import time
from threading import Event, Lock, Thread

import paho.mqtt.client as mqtt

product_file_path = "product"
TIMEOUT_SEC = 5

class AbstractPopClient:
    with open(product_file_path, 'r') as file:
        BROKER_DOMAIN = None
        DEV_NUM = None
        DEV_NAME = None
        INSITUTION_NAME = None
        for line in file:
            line = line.strip()
            if line.startswith('BROKER_DOMAIN='):
                BROKER_DOMAIN = line.split('=')[1].strip()
            if line.startswith('DEV_NUM='):
                DEV_NUM = line.split('=')[1].strip()
            if line.startswith('DEVICE_NAME='):
                DEV_NAME = line.split('=')[1].strip()
            if line.startswith('INSITUTION_NAME='):
                INSITUTION_NAME = line.split('=')[1].strip()
        if BROKER_DOMAIN is None:
            raise ValueError("[Error] There is no product file. Please make sure the device has product info")

    def __init__(self):
        self.__update_lock = Lock()
        self.__update_time_tag = time.time()
        self.__close_event = Event()
        self.is_healthy = True  # 통신 상태 확인용 플래그

        self._TOPIC_HEADER = __class__.DEV_NAME + '/' + __class__.INSITUTION_NAME + __class__.DEV_NUM
        self._client = mqtt.Client()
        self._client.on_connect = self._on_connect
        self._client.on_disconnect = self._on_disconnect
        self._client.on_message = self._on_message
        
        # 브로커 연결 (자동 재연결 활성화)
        self._client.connect(__class__.BROKER_DOMAIN, keepalive=60)
        self._client_enabled = False
        self._client.loop_start()

        wait_time_tag = time.time()
        while not self._client_enabled:
            if time.time() - wait_time_tag > 4:
                raise TimeoutError("Please check the broker connection state.")

    def __connection_check(self):
        """프로세스를 강제 종료하는 대신 상태 플래그만 변경하거나 경고를 출력합니다."""
        while not self.__close_event.is_set():
            time.sleep(1)
            with self.__update_lock:
                elapsed = time.time() - self.__update_time_tag
                
            if elapsed > TIMEOUT_SEC:
                if self.is_healthy:
                    print(f"[Warning] MQTT Data timeout ({elapsed:.1f}s). Checking connection...")
                    self.is_healthy = False
            else:
                self.is_healthy = True

    def _on_connect(self, client, userdata, flags, rc):
        self._client_enabled = True
        self.is_healthy = True
        
        # 데몬 스레드가 중복 생성되지 않도록 안전 처리
        if not hasattr(self, '_connection_check_thread') or not self._connection_check_thread.is_alive():
            self.__connection_check_thread = Thread(target=self.__connection_check, daemon=True)
            self.__connection_check_thread.start()

    def _on_disconnect(self, client, userdata, rc):
        self.is_healthy = False
        if rc != 0:
            print(f"[Warning] Unexpected MQTT disconnection (rc: {rc}). Retrying automatically...")

    def _on_message(self, client, userdata, message):
        with self.__update_lock:
            self.__update_time_tag = time.time()
        self._decode(message)

    def _decode(self, message):
        raise NotImplementedError()

    def disconnect(self):
        time.sleep(0.1)  # 큐에 남은 마지막 패킷이 전송될 때까지 잠깐 대기
        self.__close_event.set()
        self._client.loop_stop()
        self._client.disconnect()

