import io
import time
from collections.abc import Callable

from typedefs import IMUData


def output_to_csv(file: io.TextIOBase, data: IMUData):
    file.write(str(data) + "\n") 
