from dataclasses import dataclass

@dataclass
class IMUData:
    """Convenience class for keeping data read from the IMU"""
    # Time since 0 in microseconds
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
