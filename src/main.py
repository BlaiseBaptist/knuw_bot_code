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
left_front = Motor(Ports.PORT11, GearSetting.RATIO_6_1, False)
left_middle = Motor(Ports.PORT12, GearSetting.RATIO_6_1, False)
left_back = Motor(Ports.PORT13, GearSetting.RATIO_6_1, False)
right_front = Motor(Ports.PORT14, GearSetting.RATIO_6_1, True)
right_middle = Motor(Ports.PORT15, GearSetting.RATIO_6_1, True)
right_back = Motor(Ports.PORT16, GearSetting.RATIO_6_1, True)
conveyor = Motor(Ports.PORT7, GearSetting.RATIO_18_1, False)
intake = Motor(Ports.PORT6, GearSetting.RATIO_18_1, True)
wall_stakes = Motor(Ports.PORT8, GearSetting.RATIO_36_1, False)
drive_motors = {"left_front": left_front, "left_middle": left_middle, "left_back": left_back,
                "right_front": right_front, "right_middle": right_middle, "right_back": right_back}
left_group = MotorGroup(left_front, left_middle, left_back)
right_group = MotorGroup(right_front, right_middle, right_back)
grabber = DigitalOut(brain.three_wire_port.a)
flex_wheel_lift = DigitalOut(brain.three_wire_port.b)
control = Controller(PRIMARY)
sensor = Inertial(Ports.PORT21)


class DriveTrain:
    def __init__(self, left_group, right_group, sensor, speed) -> None:
        self.left_group = left_group
        self.right_group = right_group
        self.pos = [0, 0]

    def drive(self, spot, speed, reverse=False):
        diff = [self.pos[0] - spot[0], self.pos[1] - spot[1]]
        dir = FORWARD
        if reverse:
            dir = REVERSE
        while abs(diff[0]) + abs(diff[1]) > 100:
            target_angle = math.atan2(
                diff[0], diff[1])*180/math.pi + 180*reverse + 180
            angle_off = abs(target_angle - sensor.heading())
            if angle_off > 1.5:
                print("off:", angle_off, "current:",
                      sensor.heading(), "pos", self.pos)
                self.turn(target_angle)
            left_group.reset_position()
            right_group.reset_position()
            left_group.spin(dir, speed, PERCENT)
            right_group.spin(dir, speed, PERCENT)
            distance = (left_group.position(DEGREES) +
                        right_group.position(DEGREES))/2
            self.pos[0] += distance*math.cos(sensor.heading())
            self.pos[1] += distance*math.sin(sensor.heading())
            diff = [self.pos[0] - spot[0], self.pos[1] - spot[1]]
            sleep(10, MSEC)

    def turn(self, angle):
        nt = angle - sensor.heading()
        speed = abs(nt-180) * 5 / 9
        while speed > 0.5:
            dir = FORWARD
            nt = angle - sensor.heading()
            if nt < 0:
                nt += 360
            if 0 < nt and nt < 180:
                dir = REVERSE
            speed = abs(nt-180) * 5 / 9
            left_group.spin(dir, speed+10, PERCENT)
            right_group.spin(dir, -speed-10, PERCENT)
            if control.buttonB.pressing():
                break
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
    return 0 if x == 0 else x/abs(x) - x/125
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


drive_train = DriveTrain(left_group, right_group, sensor, 100)


def auto():
    drive_train.turn(360)
#    drive_train.drive([0, 1000], 100,  False)


def spin_full_intake(direction):
    intake.spin(direction, 100, PERCENT)
    conveyor.spin(direction, 100, PERCENT)


def stop_full_intake():
    intake.stop()
    conveyor.stop()


def main():
    sensor.calibrate()
    wait(2.5, SECONDS)
    print("\ncalibrated")
    control.buttonL1.pressed(lambda: spin_full_intake(FORWARD))
    control.buttonL2.pressed(lambda: spin_full_intake(REVERSE))
    control.buttonL1.released(stop_full_intake)
    control.buttonL2.released(stop_full_intake)
    control.buttonR1.pressed(lambda: wall_stakes.spin(FORWARD, 100, PERCENT))
    control.buttonR2.pressed(lambda: wall_stakes.spin(REVERSE, 100, PERCENT))
    control.buttonR1.released(wall_stakes.stop)
    control.buttonR2.released(wall_stakes.stop)
    control.buttonA.pressed(lambda: grabber.set(not (grabber.value())))
    control.buttonA.pressed(lambda: grabber.set(not (grabber.value)))
    control.buttonB.pressed(lambda: flex_wheel_lift.set(
        not (flex_wheel_lift.value())))
    control.buttonB.pressed(
        lambda: flex_wheel_lift.set(not (flex_wheel_lift.value)))
    Competition(driver, auto)


main()
