import io

from imu import IMUData


def output_to_csv(file: io.TextIOBase, data: IMUData):
    file.write(str(data) + "\n")
