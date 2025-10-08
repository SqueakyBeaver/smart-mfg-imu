#! /usr/bin/env bash

# I think this'll work, but idk how reliable just appending to this file is
printf "# Set I2C clock frequency to 400kHz (more compatible with the BNO08X)\ndtparam=i2c_arm_baudrate=400000" | sudo tee -a /boot/firmware/config.txt
