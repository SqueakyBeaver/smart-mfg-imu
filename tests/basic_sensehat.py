from sense_hat import SenseHat
import asyncio

def main():
    sense = SenseHat()
    sense.set_imu_config(True, True, True)
    
    while True:
        print(f"Orientation: {sense.orientation}")
        print(f"Magnetometer: {sense.compass_raw}")
        print(f"Gyro: {sense.gyro_raw}")
        print(f"Accelerometer: {sense.accel_raw}")
        print("")

        asyncio.sleep(.1)

if __name__ == "__main__":
    main()
