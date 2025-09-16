import time
from collections.abc import Callable
from scipy.spatial.transform import Rotation as R

import board
import busio
from adafruit_bno08x import (
    BNO_REPORT_ACCELEROMETER,
    BNO_REPORT_GYROSCOPE,
    BNO_REPORT_MAGNETOMETER,
    BNO_REPORT_ROTATION_VECTOR,
)
from adafruit_bno08x.i2c import BNO08X_I2C

from typedefs import IMUData
from utils import output_to_csv

bno: BNO08X_I2C


def _next_time_step(t0: int, change_ns: int):
    while True:
        t0 += change_ns
        yield t0


def setup():
    global bno

    i2c = busio.I2C(board.SCL, board.SDA)
    # Sometimes, the IMU can have an address
    # that is different from what the library expects
    try:
        bno = BNO08X_I2C(i2c)
    except:
        bno = BNO08X_I2C(i2c, address=0x4B)

    bno.enable_feature(BNO_REPORT_ACCELEROMETER)
    bno.enable_feature(BNO_REPORT_GYROSCOPE)
    bno.enable_feature(BNO_REPORT_MAGNETOMETER)
    bno.enable_feature(BNO_REPORT_ROTATION_VECTOR)

def basic_reading():
    global bno

    interval_ms = float(input("Polling rate in ms: "))

    t0 = time.perf_counter_ns()
    timer = _next_time_step(t0, int(interval_ms * 1e6))

    with open("data/bno_test.csv", "w+") as file:
        file.write(
            "dev_id,time_ms,accel_x,accel_y,accel_z,"
            + "gyro_x,gyro_y,gyro_z,mag_x,mag_y,mag_z,"
            + "rot_i,rot_j,_rot_k,rot_real\n"
        )

        while True:
            accel_x, accel_y, accel_z = bno.acceleration
            gyro_x, gyro_y, gyro_z = bno.gyro
            mag_x, mag_y, mag_z = bno.magnetic
            rot_i, rot_j, rot_k, rot_real = qrot = bno.quaternion
            
            print(qrot)
            data = IMUData(
                "bno085-testing",
                time.perf_counter_ns() - t0,
                accel_x,
                accel_y,
                accel_z,
                gyro_x,
                gyro_y,
                gyro_z,
                mag_x,
                mag_y,
                mag_z,
                rot_i,
                rot_j,
                rot_k,
                rot_real,
            )

            output_to_csv(file, data)

            time.sleep(max((next(timer) - time.perf_counter_ns()) / 1e9, 0))


def snapshot():
    with open("data/bno_test.csv", "w+") as file:
        file.write(
            "snapshot_label,dev_id,time_ms,accel_x,accel_y,accel_z,"
            + "gyro_x,gyro_y,gyro_z,mag_x,mag_y,mag_z,"
            + "rot_i,rot_j,_rot_k,rot_real\n"
        )

        while True:
            inp = input("q to quit. Anything else to take a snapshot\n")
            if inp.lower() == "q":
                break

            print("Taking a snapshot in 3...")
            time.sleep(1)
            print("Taking a snapshot in 2...")
            time.sleep(1)
            print("Taking a snapshot in 1...")
            time.sleep(1)

            accel_x, accel_y, accel_z = bno.acceleration
            gyro_x, gyro_y, gyro_z = bno.gyro
            mag_x, mag_y, mag_z = bno.magnetic
            rot_i, rot_j, rot_k, rot_real = bno.quaternion

            data = IMUData(
                "bno085-testing",
                0,
                accel_x,
                accel_y,
                accel_z,
                gyro_x,
                gyro_y,
                gyro_z,
                mag_x,
                mag_y,
                mag_z,
                rot_i,
                rot_j,
                rot_k,
                rot_real,
            )

            save_or_redo = input("r to discard the snapshot. Press s to save it\n")
            
            if save_or_redo.lower() == "r":
                continue

            label = input("Snapshot taken. Make a label for it: ")
            file.write(f'"{label}",')

            output_to_csv(file, data)

def yaw_pitch_roll():
    global bno
    
    while True:
        rot_i, rot_j, rot_k, rot_real = qrot = bno.quaternion

        # The quaternion should never be all 0's,
        # but it is as soon as the program starts, for some reason
        if (qrot) == (0, 0, 0, 0):
            continue

        rot = R.from_quat([rot_i, rot_j, rot_k, rot_real])

        print(rot.as_euler("xyz", degrees=True))

def main():
    setup()
    print("""Choose what you want to do:
    1. Basic test 
    2. Snapshot orientations""")
    choice = int(input(""))

    choices: dict[int, Callable[..., None]] = {1: basic_reading, 2: snapshot, 3: yaw_pitch_roll}

    choices[choice]()


if __name__ == "__main__":
    main()
