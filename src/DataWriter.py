import socket
from datetime import datetime
from typing import ContextManager

from package.client import Client

from imu import IMUData


class DataWriter(ContextManager):
    def __init__(
        self,
        csv_fname=f"data/bno08X-{datetime.now()}.csv",
        mqtt_broker_ip="127.0.0.1",
        mqtt_broker_port=1883,
    ):
        self.csv_fname = csv_fname
        self.mqtt_broker_ip = mqtt_broker_ip
        self.mqtt_broker_port = mqtt_broker_port

    def __enter__(self):
        self.csv_file = open(self.csv_fname, "w+")
        self.csv_file.write(
            "dev_id,time_ms,datetime,"
            + "accel_x,accel_y,accel_z,"
            + "gyro_x,gyro_y,gyro_z,"
            + "mag_x,mag_y,mag_z,"
            + "yaw,pitch,roll\n"
        )
        try:
            self.mqtt_client = Client(
                broker_ip=self.mqtt_broker_ip,
                broker_port=self.mqtt_broker_port,
                client_type=Client.IMU,
                device_id=socket.gethostname(),
            )
        except Exception as _:
            self.mqtt_client = None
        
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.csv_file.close()

        if self.mqtt_client:
            self.mqtt_client.disconnect()
        return False

    def write_data(self, data: IMUData):
        self._output_to_csv(data)

        if self.mqtt_client:
            self._output_mqtt(data)

    def _output_to_csv(self, data: IMUData):
        out = (
            f"{data.dev_id},{data.time},{datetime.fromtimestamp(data.time / 1000)},{data.accel_x},{data.accel_y},{data.accel_z},"
            + f"{data.gyro_x},{data.gyro_y},{data.gyro_z},{data.mag_x},{data.mag_y},"
            + f"{data.mag_z},{data.yaw},{data.pitch},{data.roll}"
        )
        self.csv_file.write(out + "\n")

    def _output_mqtt(self, data: IMUData):
        self.mqtt_client.publish(
            f"{data.dev_id},{data.time},{data.accel_x},{data.accel_y},{data.accel_z},"
            + f"{data.gyro_x},{data.gyro_y},{data.gyro_z},{data.mag_x},{data.mag_y},"
            + f"{data.mag_z},{data.yaw},{data.pitch},{data.roll}"
        )
