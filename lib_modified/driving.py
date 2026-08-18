import struct
import time

from autocar3g.absclient import AbstractPopClient


class Driving(AbstractPopClient):
    def __init__(self, wait=False): # wait는 기본적으로 원격 수신 대기용
        super().__init__()
        self._client.subscribe(self._TOPIC_HEADER + '/drive/steering')
        self._client.subscribe(self._TOPIC_HEADER + '/drive/throttle')
        self._client.subscribe(self._TOPIC_HEADER + '/int')
        
        # 내부 로컬 상태값 초기화
        self.__steering_value = 0.0
        self.__throttle_value = 0

    def _decode(self, message):
        # 수신받은 현재 상태 업데이트 (조회용)
        if 'steering' in message.topic:
            self.__steering_value = struct.unpack("<f", message.payload)[0]
        elif 'throttle' in message.topic:
            self.__throttle_value = struct.unpack("<i", message.payload)[0]

    @property
    def steering(self):
        return self.__steering_value

    @steering.setter
    def steering(self, value: float):
        if not (-1.0 <= value <= 1.0):
            raise ValueError("Wrong steering value.")
        self.__steering_value = value
        # 로컬 변수에 보관된 throttle과 함께 즉시 전송
        msg_info = self._client.publish(self._TOPIC_HEADER + "/drive/set", struct.pack('<fi', self.__steering_value, self.__throttle_value), 0)
        msg_info.wait_for_publish(timeout=0.1)  # 전송 완료 대기 (0.1초)

    @property
    def throttle(self):
        return self.__throttle_value

    @throttle.setter
    def throttle(self, value: int):
        if not (-99 <= value <= 99):
            raise ValueError("Wrong throttle value.")
        self.__throttle_value = value
        # 로컬 변수에 보관된 steering과 함께 즉시 전송
        msg_info = self._client.publish(self._TOPIC_HEADER + "/drive/set", struct.pack('<fi', self.__steering_value, self.__throttle_value), 0)
        msg_info.wait_for_publish(timeout=0.1)  # 전송 완료 대기 (0.1초)

    # 동시 변경용 전용 메서드 (권장)
    def set_drive(self, steering: float, throttle: int):
        if not (-1.0 <= steering <= 1.0):
            raise ValueError("Wrong steering value.")
        if not (-99 <= throttle <= 99):
            raise ValueError("Wrong throttle value.")
            
        self.__steering_value = steering
        self.__throttle_value = throttle
        msginfo = self._client.publish(self._TOPIC_HEADER + "/drive/set", struct.pack('<fi', steering, throttle), 0)
        msginfo.wait_for_publish(timeout=0.1)  # 전송 완료 대기 (0.1초)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # 프로그램 종료 시 안전하게 차를 세우고 통신 종료
        try:
            self.set_drive(0.0, 0)
            time.sleep(0.05)
        finally:
            self._client.loop_stop()
            self._client.disconnect()
