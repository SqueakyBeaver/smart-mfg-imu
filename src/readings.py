import time
from curses import curs_set, window
from itertools import count

from DataWriter import DataWriter
from imu import IMU


def unattended_reading():
    """
    The function that will read, log, and send the data.
    For 'normal' use
    """
    with DataWriter() as writer:
        bno = IMU.get_conn()

        interval_ms = 10
        t0 = time.time_ns()
        timer = count(t0, int(interval_ms * 1e6))
        while True:
            data = bno.read_data()

            writer.write_data(data)

            next_time = next(timer)
            while time.time_ns() < next_time:
                pass


def attended_reading(scr: window):
    """
    The function that will read, log, and display the data.
    For 'ui' use
    """
    with DataWriter() as writer:
        bno = IMU.get_conn()

        scr.addstr(0, 0, "Basic reading")
        curs_set(False)

        interval_ms = 10
        t0 = time.time_ns()
        timer = count(t0, int(interval_ms * 1e6))
        last_time = t0

        scr.refresh()
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
            writer.write_data(data)

            next_time = next(timer)
            while time.time_ns() < next_time:
                pass
