import time
from collections.abc import Callable

from typedefs import IMU
from utils import output_to_csv

bno: IMU


def _next_time_step(t0: int, change_ns: int):
    while True:
        t0 += change_ns
        yield t0


def basic_reading():
    global bno

    interval_ms = float(input("Polling rate in ms: "))

    t0 = time.perf_counter_ns()
    timer = _next_time_step(t0, int(interval_ms * 1e6))

    with open("data/bno_test.csv", "w+") as file:
        file.write(
            "dev_id,time_ms,accel_x,accel_y,accel_z,"
            + "gyro_x,gyro_y,gyro_z,mag_x,mag_y,mag_z,"
            + "yaw,pitch,roll\n"
        )

        while True:
            data = bno.read_data(t0)
            output_to_csv(file, data)

            time.sleep(max((next(timer) - time.perf_counter_ns()) / 1e9, 0))


def snapshot():
    with open("data/bno_test.csv", "w+") as file:
        file.write(
            "snapshot_label,dev_id,time_ms,accel_x,accel_y,accel_z,"
            + "gyro_x,gyro_y,gyro_z,mag_x,mag_y,mag_z,"
            + "yaw,pitch,roll\n"
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

            data = bno.read_data(0)
            data.time = 0

            save_or_redo = input("r to discard the snapshot. Press s to save it\n")

            if save_or_redo.lower() == "r":
                continue

            label = input("Snapshot taken. Make a label for it: ")
            file.write(f'"{label}",')

            output_to_csv(file, data)


def main():
    print("""Choose what you want to do:
    1. Basic test 
    2. Snapshot orientations""")
    choice = int(input(""))

    choices: dict[int, Callable[..., None]] = {
        1: basic_reading,
        2: snapshot,
    }

    choices[choice]()


if __name__ == "__main__":
    bno = IMU()
    main()
