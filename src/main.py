import time
from curses import curs_set, window, wrapper

from typedefs import IMU
from utils import output_to_csv

bno: IMU


def _next_time_step(t0: int, change_ns: int):
    while True:
        t0 += change_ns
        yield t0


def basic_reading(scr: window):
    global bno
    scr.addstr(0, 0, "Basic reading")
    curs_set(False)

    interval_ms = 10
    t0 = time.perf_counter_ns()
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

            time.sleep(max((next(timer) - time.perf_counter_ns()) / 1e9, 0))


def main(scr: window):
    scr.clear()
    scr.addstr(
        0,
        0,
        "Press any key to start capturing data",
    )
    _ = scr.getch()

    scr.erase()
    basic_reading(scr)


if __name__ == "__main__":
    bno = IMU()
    wrapper(main)
