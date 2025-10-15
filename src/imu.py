import math
import time
from dataclasses import dataclass

import board
import busio
import numpy as np
from adafruit_bno08x import (
    BNO_REPORT_GEOMAGNETIC_ROTATION_VECTOR,
    BNO_REPORT_GYROSCOPE,
    BNO_REPORT_LINEAR_ACCELERATION,
    BNO_REPORT_MAGNETOMETER,
    BNO_REPORT_ROTATION_VECTOR,
)
from adafruit_bno08x.i2c import BNO08X_I2C
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

    @override
    def __str__(self):
        return (
            f"{self.dev_id},{self.time},{self.accel_x},{self.accel_y},{self.accel_z},"
            + f"{self.gyro_x},{self.gyro_y},{self.gyro_z},{self.mag_x},{self.mag_y},"
            + f"{self.mag_z},{self.yaw},{self.pitch},{self.roll}"
        )


class BNO08X_YPR(BNO08X_I2C):
    def __init__(
        self,
        *args,
        report_interval_ms=10,
        **kwargs,
    ):
        # Sometimes, the IMU can have an address
        # that is different from what the library expects
        print("constructed bno class")
        try:
            super().__init__(*args, **kwargs)
        except:
            super().__init__(address=0x4B, *args, **kwargs)

        # report_interval is in microseconds
        # so all of these are 10 ms (the default is 50ms)
        self.enable_feature(
            BNO_REPORT_LINEAR_ACCELERATION, report_interval=report_interval_ms * 1000
        )
        self.enable_feature(
            BNO_REPORT_GYROSCOPE, report_interval=report_interval_ms * 1000
        )
        self.enable_feature(
            BNO_REPORT_MAGNETOMETER, report_interval=report_interval_ms * 1000
        )
        self.enable_feature(
            BNO_REPORT_ROTATION_VECTOR, report_interval=report_interval_ms * 1000
        )
        self.enable_feature(
            BNO_REPORT_GEOMAGNETIC_ROTATION_VECTOR,
            report_interval=report_interval_ms * 1000,
        )

    def read_data(self) -> IMUData:
        """
        Read accelerometer, gyroscope, magnetometer, and orientation data from the IMU

        start_time: The first value of time.perf_counter_ns before this function is run
        """
        self._process_available_packets()

        read_time = int(time.time_ns() / 1e6)
        accel_x, accel_y, accel_z = self.linear_acceleration
        gyro_x, gyro_y, gyro_z = self.gyro
        mag_x, mag_y, mag_z = self.magnetic
        rot_y, rot_p, rot_r = self._quat_to_ypr(self.quaternion)

        return IMUData(
            "bno085-testing",
            read_time,
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
        )

    @property
    def rotation(self) -> tuple[float, float, float] | None:
        """The IMU's rotation in terms of yaw, pitch, and roll"""
        self._process_available_packets()
        try:
            return self._quat_to_ypr(self._readings[BNO_REPORT_ROTATION_VECTOR])
        except KeyError:
            raise RuntimeError("No quaternion report found, is it enabled?") from None

    def _normalize_quaternion(self, q: tuple[float, float, float, float]):
        w, x, y, z = q
        magnitude = np.sqrt(w**2 + x**2 + y**2 + z**2)

        if magnitude == 0:
            raise ValueError("Cannot normalize a zero quaternion.")

        return w / magnitude, x / magnitude, y / magnitude, z / magnitude

    # @cache
    def _quat_to_ypr(
        self, q: tuple[float, float, float, float]
    ) -> tuple[float, float, float]:
        """
        Internal function to convert the quaternion rotation to yaw, pitch, and roll
        quat: quaternion in the form of (w, x, y, z)
        """
        # r = R.from_quat(q)
        #
        # yaw, pitch, roll = r.as_euler("zyx", degrees=True)
        # return (yaw, pitch, roll)
        w, x, y, z = self._normalize_quaternion(q)

        # Calculate the yaw, pitch, and roll in radians
        yaw = np.arctan2(2.0 * (y * z + w * x), 1 - 2 * (x * x + y * y))
        pitch = np.arcsin(2.0 * (w * y - x * z))
        roll = np.arctan2(2.0 * (x * y + w * z), 1 - 2 * (y * y + z * z))

        # Convert from radians to degrees
        yaw = np.degrees(yaw)
        pitch = np.degrees(pitch)
        roll = np.degrees(roll)

        # I would wrap the yaw, but it gives incorrect results if I do that
        if pitch > 0:
            pitch = 180 - pitch
        else:
            pitch = abs(pitch)
        if roll > 0:
            roll = 180 - roll
        else:
            roll = abs(roll)

        return yaw, pitch, roll


class IMU:
    _imu: BNO08X_YPR | None = None

    @staticmethod
    def get_conn() -> BNO08X_YPR:
        if not IMU._imu:
            i2c = busio.I2C(board.SCL, board.SDA)
            IMU._imu = BNO08X_YPR(i2c)

        return IMU._imu
