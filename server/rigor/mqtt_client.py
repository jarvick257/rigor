from typing import Callable

import paho.mqtt.client as mqtt
from loguru import logger

from .encoder import EncoderAction
from .content import Content
from .input_handler import InputHandler
from .renderer import Renderer
from .const import *
from threading import Timer


class MqttClient(InputHandler, Renderer):
    def __init__(self, host: str, port: int):
        self._host = host
        self._port = port
        self._client = mqtt.Client(client_id="ZigorServer")
        self._client.on_connect = self._on_connect
        self._client.on_message = self._on_message
        self._input_callback: Callable[[EncoderAction], None] = lambda _: None
        self._state_callback: Callable[[bool], None] = lambda _: None
        self._content: Content | None = None
        self._disconnect_timer: Timer | None = None

    def _on_message(self, client, userdata, message) -> None:
        _, _ = client, userdata
        parts = message.topic.split("/")
        if len(parts) != 3 or parts[0] != "rigor":
            logger.error("Message topic must be rigor/<topic>/<client_id>")
        _, topic, client_id = parts
        if topic == MQTT_INPUT_TOPIC.split("/")[1]:
            action = EncoderAction[message.payload.decode()]
            logger.info(f"Received action {action}")
            self._input_callback(action)
        elif topic == MQTT_STATE_TOPIC.split("/")[1]:
            state = message.payload.decode()
            logger.info(f"Client {client_id} is {state}")
            if state == "ON":
                self._cancel_disconnect_timer()
                self._state_callback(True)
            elif state == "OFF":
                self._start_disconnect_timer()

    def _on_connect(self, client, userdata, flags, rc) -> None:
        logger.info(f"Connected")
        _, _, _, _ = client, userdata, flags, rc
        self._client.subscribe(MQTT_INPUT_TOPIC)
        self._client.subscribe(MQTT_STATE_TOPIC)
        self._publish_content()

    def _start_disconnect_timer(self):
        self._cancel_disconnect_timer()
        self._disconnect_timer = Timer(30, self._on_client_disconnected)
        self._disconnect_timer.start()

    def _cancel_disconnect_timer(self) -> None:
        if self._disconnect_timer is None:
            return
        self._disconnect_timer.cancel()
        self._disconnect_timer = None

    def _on_client_disconnected(self) -> None:
        self._state_callback(False)
        self._cancel_disconnect_timer()

    def _publish_content(self) -> None:
        if self._content == None or not self._client.is_connected:
            return
        payload = self._content.to_json()
        logger.info(f"Publishing {self._content} on {MQTT_CONTENT_TOPIC}")
        logger.debug(payload)
        self._client.publish(MQTT_CONTENT_TOPIC, payload, retain=True)

    def on_input(self, callback: Callable[[EncoderAction], None]):
        self._input_callback = callback

    def on_client_state(self, callback: Callable[[bool], None]):
        self._state_callback = callback

    def render(self, content: Content):
        self._content = content
        self._publish_content()

    def run(self) -> None:
        logger.info(f"Connecting to MQTT Broker at {self._host}:{self._port}")
        self._client.connect(host=self._host, port=self._port)
        try:
            self._client.loop_forever()
        except KeyboardInterrupt:
            logger.info(f"Caught Keyboard Interrupt")
        except Exception as e:
            logger.error(f"Error: {e}")
            raise
