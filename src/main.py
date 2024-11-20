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
left_16 = Motor(Ports.PORT16, GearSetting.RATIO_6_1, False)
left_19 = Motor(Ports.PORT19, GearSetting.RATIO_6_1, False)
left_18 = Motor(Ports.PORT18, GearSetting.RATIO_6_1, False)
right_12 = Motor(Ports.PORT12, GearSetting.RATIO_6_1, True)
right_11 = Motor(Ports.PORT11, GearSetting.RATIO_6_1, True)
right_13 = Motor(Ports.PORT13, GearSetting.RATIO_6_1, True)
conv = Motor(Ports.PORT17, GearSetting.RATIO_18_1, True)
lady_brown = Motor(Ports.PORT10, GearSetting.RATIO_36_1, False)
grab = DigitalOut(brain.three_wire_port.a)
doink = DigitalOut(brain.three_wire_port.d)
da_hood = DigitalOut(brain.three_wire_port.b)
drive_motors = {"left_16": left_16, "left_19": left_19, "left_18": left_18,
                "right_12": right_12, "right_11": right_11, "right_13": right_13}
left_group = MotorGroup(left_18, left_16, left_19)
right_group = MotorGroup(right_11, right_12, right_13)
control = Controller(PRIMARY)
sensor = Inertial(Ports.PORT8)


class DriveTrain:
    def __init__(self, left_group, right_group, sensor, speed) -> None:
        self.left_group = left_group
        self.right_group = right_group
        self.heading = 0
        self.speed = speed
        self.pos = [0, 0]
        Thread(lambda: self.keep_pos(sensor))

    def drive(self, distance, wait=False):
        left_group.spin_for(FORWARD, 180, DEGREES, self.speed, PERCENT, False)
        right_group.spin_for(FORWARD, 180, DEGREES, self.speed, PERCENT, wait)

    def turn(self, angle):
        pass

    def keep_pos(self, sensor):
        heading_computed = 0
        while True:
            self.heading = sensor.heading()
            diff = right_group.position(DEGREES) - left_group.position(DEGREES)

            self.pos = [0, 0]

    def driving_turn(self):
        pass


def blaise_drive(ithrottle, iturn):
    left = (blaise_slope(ithrottle)+1) * iturn + ithrottle
    right = (-blaise_slope(ithrottle)-1) * iturn + ithrottle
    return (left, right)


def cal(x):
    return x if abs(x) > 5 else 0


def blaise_slope(x):
    return 0 if x == 0 else x/abs(x) - 0.007*x


def driver():
    print("starting driver")
    while True:
        wait(.02, SECONDS)
        drive_code = blaise_drive
        igo, iturn = cal(control.axis3.position()), cal(
            control.axis1.position())
        Left, Right = drive_code(igo, iturn)
        left_group.spin(FORWARD, Left, PERCENT)
        right_group.spin(FORWARD, Right, PERCENT)


def auto():
    pass


def main():
    sensor.calibrate()
    wait(3, SECONDS)
    print("\ncalibrated")
    sensor.heading(RotationUnits.RAW)
    grab.set(False)
    control.buttonL1.pressed(lambda: conv.spin(FORWARD, 100, PERCENT))
    control.buttonL2.pressed(lambda: conv.spin(REVERSE, 100, PERCENT))
    control.buttonL1.released(conv.stop)
    control.buttonL2.released(conv.stop)
    control.buttonA.pressed(lambda: grab.set(not grab.value()))
    control.buttonB.pressed(lambda: doink.set(not doink.value()))
    control.buttonX.pressed(lambda: da_hood.set(not da_hood.value()))
    control.buttonR1.pressed(lambda: lady_brown.spin(FORWARD, 100, PERCENT))
    control.buttonR2.pressed(lambda: lady_brown.spin(REVERSE, 70, PERCENT))
    control.buttonR1.released(lady_brown.stop)
    control.buttonR2.released(lady_brown.stop)
    _ = Competition(driver, auto)


main()
