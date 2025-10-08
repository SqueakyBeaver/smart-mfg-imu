import time
from curses import curs_set, window

from imu import IMU
from utils import output_to_csv


def _next_time_step(t0: int, change_ns: int):
    while True:
        t0 += change_ns
        yield t0


def unattended_reading():
    """
    The function that will read, log, and send the data.
    For 'normal' use
    """
    bno = IMU.get_conn()

    interval_ms = 10
    t0 = time.time_ns()
    timer = _next_time_step(t0, int(interval_ms * 1e6))
    last_time = t0

    with open("data/bno_test.csv", "w+") as file:
        file.write(
            "dev_id,time_ms,accel_x,accel_y,accel_z,"
            + "gyro_x,gyro_y,gyro_z,mag_x,mag_y,mag_z,"
            + "yaw,pitch,roll\n"
        )

        while True:
            data = bno.read_data()

            output_to_csv(file, data)

            next_time = next(timer)
            while time.time_ns() < next_time:
                pass


def attended_reading(scr: window):
    """
    The function that will read, log, and display the data.
    For 'ui' use
    """
    bno = IMU.get_conn()

    scr.addstr(0, 0, "Basic reading")
    curs_set(False)

    interval_ms = 10
    t0 = time.time_ns()
    timer = _next_time_step(t0, int(interval_ms * 1e6))
    last_time = t0

    scr.refresh()
    with open("data/bno_test.csv", "w+") as file:
        file.write(
            "dev_id,time_ms,accel_x,accel_y,accel_z,"
            + "gyro_x,gyro_y,gyro_z,mag_x,mag_y,mag_z,"
            + "yaw,pitch,roll\n"
        )

        while True:
            data = bno.read_data()

            scr.addstr(
                1,
                0,
                f"Accel X:{data.accel_x: 08.3F}\n"
                + f"Accel Y:{data.accel_y: 08.3F}\n"
                + f"Accel Z:{data.accel_z: 08.3F}",
            )
            scr.addstr(
                4,
                0,
                f"Gyro X:{data.gyro_x: 08.3F}\n"
                + f"Gyro Y:{data.gyro_y: 08.3F}\n"
                + f"Gyro Z:{data.gyro_z: 08.3F}",
            )
            scr.addstr(
                7,
                0,
                f"Mag X:{data.mag_x: 08.3F}\n"
                + f"Mag Y:{data.mag_y: 08.3F}\n"
                + f"Mag Z:{data.mag_z: 08.3F}",
            )
            scr.addstr(
                10,
                0,
                f"Yaw (z):{data.yaw: 08.3F}\n"
                + f"Pitch (y):{data.pitch: 08.3F}\n"
                + f"Roll (x):{data.roll: 08.3F}\n",
            )
            scr.addstr(
                13,
                0,
                f"ms since last iteration: {(time.perf_counter_ns() - last_time) / 1e6: 08.3F}\n",
            )
            last_time = time.perf_counter_ns()

            scr.refresh()
            output_to_csv(file, data)

            next_time = next(timer)
            while time.time_ns() < next_time:
                pass
