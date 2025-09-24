import math
import time
from dataclasses import dataclass
from functools import cache

import board
import busio
from adafruit_bno08x import (
    BNO_REPORT_GEOMAGNETIC_ROTATION_VECTOR,
    BNO_REPORT_GYROSCOPE,
    BNO_REPORT_LINEAR_ACCELERATION,
    BNO_REPORT_MAGNETOMETER,
    BNO_REPORT_ROTATION_VECTOR,
)
from adafruit_bno08x.i2c import BNO08X_I2C
from scipy.spatial.transform import Rotation as R
from typing_extensions import override


@dataclass
class IMUData:
    """Convenience class for keeping data read from the IMU"""

    dev_id: str
    time: float

    accel_x: float
    accel_y: float
    accel_z: float

    gyro_x: float
    gyro_y: float
    gyro_z: float

    mag_x: float
    mag_y: float
    mag_z: float

    yaw: float
    pitch: float
    roll: float

    geo_y: float = 0
    geo_p: float = 0
    geo_r: float = 0

    @override
    def __str__(self):
        return (
            f"{self.dev_id},{self.time},{self.accel_x},{self.accel_y},{self.accel_z},"
            + f"{self.gyro_x},{self.gyro_y},{self.gyro_z},{self.mag_x},{self.mag_y},"
            + f"{self.mag_z},{self.yaw},{self.pitch},{self.roll}"
        )


class IMU(BNO08X_I2C):
    def __init__(self):
        i2c = busio.I2C(board.SCL, board.SDA)
        # Sometimes, the IMU can have an address
        # that is different from what the library expects
        try:
            super().__init__(i2c)
        except:
            super().__init__(i2c, address=0x4B)

        self.enable_feature(BNO_REPORT_LINEAR_ACCELERATION)
        self.enable_feature(BNO_REPORT_GYROSCOPE)
        self.enable_feature(BNO_REPORT_MAGNETOMETER)
        self.enable_feature(BNO_REPORT_ROTATION_VECTOR)
        self.enable_feature(BNO_REPORT_GEOMAGNETIC_ROTATION_VECTOR)

    def read_data(self, start_time: int) -> IMUData:
        """
        Read accelerometer, gyroscope, magnetometer, and orientation data from the IMU

        start_time: The first value of time.perf_counter_ns before this function is run
        """
        accel_x, accel_y, accel_z = self.linear_acceleration
        gyro_x, gyro_y, gyro_z = self.gyro
        mag_x, mag_y, mag_z = self.magnetic
        rot_y, rot_p, rot_r = self._quat_to_ypr(self.quaternion)
        geo_y, geo_p, geo_r = self._quat_to_ypr(self.geo_quaternion)

        return IMUData(
            "bno085-testing",
            time.perf_counter_ns() - start_time,
            accel_x,
            accel_y,
            accel_z,
            math.degrees(gyro_x),
            math.degrees(gyro_y),
            math.degrees(gyro_z),
            mag_x,
            mag_y,
            mag_z,
            rot_y,
            rot_p,
            rot_r,
            geo_y,
            geo_p,
            geo_r,
        )

    @property
    def rotation(self) -> tuple[float, float, float] | None:
        """The IMU's rotation in terms of yaw, pitch, and roll"""
        self._process_available_packets()
        try:
            return self._quat_to_ypr(self._readings[BNO_REPORT_ROTATION_VECTOR])
        except KeyError:
            raise RuntimeError("No quaternion report found, is it enabled?") from None

    @cache
    def _quat_to_ypr(
        self, quat: tuple[float, float, float, float]
    ) -> tuple[float, float, float]:
        """
        Internal function to convert the quaternion rotation to yaw, pitch, and roll
        """
        r = R.from_quat(quat)

        yaw, pitch, roll = r.as_euler("zyx", degrees=True)
        return (yaw, pitch, roll)
