import time

from sense_hat import SenseHat

from ..typedefs import IMUData
from ..utils import output_to_csv


def main():
    sense = SenseHat()
    sense.set_imu_config(True, True, True)

    while True:
        try:
            rate = int(input("Polling rate (in ms): "))
            assert rate > 0
            break
        except:
            print("Not a valid option")

    with open("data/sensehat-test.csv", "w+") as file:
        file.write(
            "time_ns,accel_x,accel_y,accel_z,gyro_x,gyro_y,gyro_z,mag_x,mag_y,mag_z\n"
        )

        start = time.monotonic_ns()
        while True:
            data = IMUData(
                time.monotonic_ns() - start,
                sense.accel_raw["x"],
                sense.accel_raw["y"],
                sense.accel_raw["z"],
                sense.gyro_raw["x"],
                sense.gyro_raw["y"],
                sense.gyro_raw["z"],
                sense.compass_raw["x"],
                sense.compass_raw["y"],
                sense.compass_raw["z"],
            )

            output_to_csv(file, data)

            time.sleep(rate / 1000)


if __name__ == "__main__":
    main()
