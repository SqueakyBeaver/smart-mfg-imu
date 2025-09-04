import io

from ..typedefs import IMUData


def output_to_csv(file: io.TextIOBase, data: IMUData):
    file.write(
        f"{data.time},{data.accel_x},{data.accel_y},{data.accel_z},{data.gyro_x},"
        + f"{data.gyro_y},{data.gyro_z},{data.mag_x},{data.mag_y},{data.mag_z}\n"
    )
