import io
from datetime import datetime

from imu import IMUData


def output_to_csv(file: io.TextIOBase, data: IMUData):
    out = (
        f"{data.dev_id},{data.time},{datetime.fromtimestamp(data.time / 1000)},{data.accel_x},{data.accel_y},{data.accel_z},"
        + f"{data.gyro_x},{data.gyro_y},{data.gyro_z},{data.mag_x},{data.mag_y},"
        + f"{data.mag_z},{data.yaw},{data.pitch},{data.roll}"
    )
    file.write(out + "\n")
