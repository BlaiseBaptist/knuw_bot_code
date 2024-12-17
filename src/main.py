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
sensor = Inertial(Ports.PORT21)


class DriveTrain:
    def __init__(self, left_group, right_group, sensor, speed) -> None:
        self.left_group = left_group
        self.right_group = right_group
        self.pos = [0, 0]

    def drive(self, spot, speed, wait=False, reverse=False):
        diff = [self.pos[0] - spot[0], self.pos[1] - spot[1]]
        distance = math.sqrt(diff[0]**2 + diff[1]**2)
        target_angle = math.atan2(diff[1], diff[0])*180/math.pi + 180*reverse
        self.turn(target_angle)
        print(sensor.heading() - target_angle)
        left_group.reset_position()
        right_group.reset_position()
        dir = FORWARD
        if reverse:
            dir = REVERSE
        left_group.spin_for(dir, distance, DEGREES,
                            speed, PERCENT, False)
        right_group.spin_for(dir, distance, DEGREES,
                             speed, PERCENT, wait)
        self.pos = spot

    def drive2(self, spot, speed, wait, reverse):
        diff = [self.pos[0] - spot[0], self.pos[1] - spot[1]]
        distance = math.sqrt(diff[0]**2 + diff[1]**2)
        self.turn(math.atan2(diff[1], diff[0])*180/math.pi + 180*reverse)
        left_group.reset_position()
        right_group.reset_position()
        dir = FORWARD
        if reverse:
            dir = REVERSE

    def turn(self, angle):
        nt = angle+180 - sensor.heading()
        speed = abs(nt-180) * 5 / 9
        while control.buttonUp.pressing() or control.buttonDown.pressing() or control.buttonLeft.pressing() or control.buttonRight.pressing():
            sleep(10, TimeUnits.MSEC)
        while speed > 1:
            dir = FORWARD
            nt = angle+180 - sensor.heading()
            if nt < 0:
                nt += 360
            if 0 < nt and nt < 180:
                dir = REVERSE
            speed = abs(nt-180) * 5 / 9
            if control.buttonUp.pressing():
                break
            if control.buttonDown.pressing():
                break
            if control.buttonLeft.pressing():
                break
            if control.buttonRight.pressing():
                break
            left_group.spin(dir, speed+10, PERCENT)
            right_group.spin(dir, -speed-10, PERCENT)
        left_group.stop()
        right_group.stop()

    def set_zero(self):
        sensor.reset_heading()
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
    return 0 if x == 0 else x/abs(x) - 0.01*x


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


drive_train = DriveTrain(left_group, right_group, sensor, 100)


def auto():
    while True:
        drive_train.drive([4000, 0], 100, True, False)
        drive_train.drive([0000, 0], 100, True, True)


def main():
    sensor.calibrate()
    wait(2.5, SECONDS)
    print("\ncalibrated")
    control.buttonUp.pressed(lambda: drive_train.turn(0))
    control.buttonRight.pressed(lambda: drive_train.turn(90))
    control.buttonDown.pressed(lambda: drive_train.turn(180))
    control.buttonLeft.pressed(lambda: drive_train.turn(270))
    control.buttonY.pressed(drive_train.set_zero)
    control.buttonB.pressed(lambda: drive_train.drive([3000, 0], 50))
    Competition(driver, auto)


main()
