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
        self.heading = 0
        self.speed = speed
        self.pos = [0, 0]
        Thread(lambda: self.keep_pos(sensor))

    def drive(self, spot, wait=False):
        distance = math.sqrt(spot[0]**2 + spot[1]**2)
        self.turn(math.atan2(spot[1], spot[0])*180/math.pi)
        left_group.spin_for(FORWARD, distance, DEGREES,
                            self.speed, PERCENT, False)
        right_group.spin_for(FORWARD, distance, DEGREES,
                             self.speed, PERCENT, wait)
        self.pos += spot

    def turn(self, angle):
        nt = angle - self.heading
        speed = abs(nt-180) * 5 / 9
        while speed > 1:
            dir = FORWARD
            nt = angle - self.heading
            if nt < 0:
                nt += 360
            if 0 < nt and nt < 180:
                dir = REVERSE
            speed = abs(nt-180) * 5 / 9
            if control.buttonX.pressing():
                break
            left_group.spin(dir, speed+10, PERCENT)
            right_group.spin(dir, -speed-10, PERCENT)

        left_group.stop()
        right_group.stop()

    def keep_pos(self, sensor):
        while True:
            self.heading = sensor.heading()

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
    wait(2.5, SECONDS)
    print("\ncalibrated")
    drive_train = DriveTrain(left_group, right_group, sensor, 100)
    control.buttonDown.pressed(lambda: drive_train.turn(0))
    control.buttonRight.pressed(lambda: drive_train.turn(90))
    control.buttonUp.pressed(lambda: drive_train.turn(180))
    control.buttonLeft.pressed(lambda: drive_train.turn(270))
    control.buttonY.pressed(sensor.reset_heading)
    driver()


main()
