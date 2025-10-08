import argparse
from curses import window, wrapper
from imu import IMU
import readings

def ui(scr: window):
    scr.clear()
    scr.addstr(
        0,
        0,
        "Press any key to start capturing data",
    )
    _ = scr.getch()

    scr.erase()

    readings.attended_reading(scr)


def no_ui():
    readings.unattended_reading()


if __name__ == "__main__":
    # Initialize the connection early since it may take some time
    IMU.get_conn()

    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--ui", help="Run the program in ui mode", action="store_true")
    args = parser.parse_args()
    
    if args.ui:
        wrapper(ui)
    else:
        no_ui()

