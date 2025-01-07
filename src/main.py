# ---------------------------------------------------------------------------- #
#                                                                              #
# 	Module:       main.py                                                      #
# 	Author:       blase baptist                                                #
# 	Created:      100/100/100, 13:70 PM                                        #
# 	Description:  V5 project                                                   #
#                                                                              #
# ---------------------------------------------------------------------------- #

# Library imports
from vex import *
import math

# Brain should be defined by default
brain = Brain()
left_front = Motor(Ports.PORT3, GearSetting.RATIO_6_1, False)
left_middle = Motor(Ports.PORT4, GearSetting.RATIO_6_1, False)
left_back = Motor(Ports.PORT5, GearSetting.RATIO_6_1, False)
right_front = Motor(Ports.PORT6, GearSetting.RATIO_6_1, True)
right_middle = Motor(Ports.PORT7, GearSetting.RATIO_6_1, True)
right_back = Motor(Ports.PORT9, GearSetting.RATIO_6_1, True)
drive_motors = {"left_front": left_front, "left_middle": left_middle, "left_back": left_back,
                "right_front": right_front, "right_middle": right_middle, "right_back": right_back}
left_group = MotorGroup(left_front, left_middle, left_back)
right_group = MotorGroup(right_front, right_middle, right_back)
control = Controller(PRIMARY)


def blaise_drive(ithrottle, iturn):
    left = (blaise_slope(ithrottle)+1) * iturn + ithrottle
    right = (-blaise_slope(ithrottle)-1) * iturn + ithrottle
    return (left, right)


def cal(x):
    return x if abs(x) > 5 else 0


def blaise_slope(x):
    return 0 if x == 0 else x/abs(x) - x/150
    # bigger is more sensitive
    # dont put lower than 100


def driver():
    print("starting driver")
    while Competition.is_driver_control():
        wait(.02, SECONDS)
        drive_code = blaise_drive
        igo, iturn = cal(control.axis3.position()), cal(
            control.axis1.position())
        Left, Right = drive_code(igo, iturn)
        left_group.spin(FORWARD, Left, PERCENT)
        right_group.spin(FORWARD, Right, PERCENT)


driver()
