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
grabber = DigitalOut(brain.three_wire_port.h)
flex_wheel_lift_up = DigitalOut(brain.three_wire_port.a)
flex_wheel_lift_down = DigitalOut(brain.three_wire_port.b)
doinker = DigitalOut(brain.three_wire_port.c)
control = Controller(PRIMARY)
sensor = Inertial(Ports.PORT17)


class DriveTrain:
    def __init__(self, left_group, right_group) -> None:
        self.left_group = left_group
        self.right_group = right_group
        self.pos = [0, 0]
        self.prog_count = 0

    def drive(self, spot, speed, reverse=False, wait=False):
        diff = [self.pos[0] - spot[0], self.pos[1] - spot[1]]
        target_angle = math.atan2(
            diff[0], diff[1])*180/math.pi + 180*reverse
        self.turn(target_angle)
        left_group.reset_position()
        right_group.reset_position()
        distance = math.sqrt(
            pow(diff[0], 2) + pow(diff[1], 2)) * (-1 if reverse else 1)
        left_group.spin_to_position(distance, DEGREES, speed, PERCENT, False)
        right_group.spin_to_position(distance, DEGREES, speed, PERCENT, wait)

        self.pos[0] = spot[0]
        self.pos[1] = spot[1]

    def turn(self, angle):
        nt = angle - sensor.heading()
        speed_factor = 1
        speed = (abs(nt-180)/3.6) * speed_factor
        while speed > (1*speed_factor)/3.6:
            dir = REVERSE if (0 < nt and nt < 180) else FORWARD
            nt = angle - sensor.heading()
            if nt < 0:
                nt += 360
            speed = (abs(nt-180)/3.6) * speed_factor
            left_group.spin(dir, speed+2.4, PERCENT)
            right_group.spin(dir, -speed-2.4, PERCENT)
            if control.buttonB.pressing():
                break
        left_group.stop()
        right_group.stop()


def blaise_drive(throttle, turn):
    left = (blaise_slope(throttle)+1) * turn + throttle
    right = (-blaise_slope(throttle)-1) * turn + throttle
    return (left, right)


def cal(x):
    return 0 if abs(x) < 5 else math.tan(x/100)*64.2092615934*0.75


def blaise_slope(x):
    return 0 if x == 0 else x/abs(x) - x/100
    # bigger is more sensitive
    # dont put lower than 100


def monitor_temp():
    overtemp = []
    for name, motor_obj in drive_motors.items():
        overtemp.append(motor_obj.temperature())
    return (sum(overtemp)/len(overtemp), max(overtemp))


def skills():
    # grabber.set(True)
    programing_skills()
    driver()
    # second_prog()


def driver():
    print("starting driver")
    control.rumble(".")
    while Competition.is_driver_control():
        wait(.02, SECONDS)
        drive_code = blaise_drive
        throttle, turn = cal(-control.axis3.position()), cal(
            control.axis1.position())
        Left, Right = drive_code(throttle, turn)
        left_group.spin(FORWARD, Left, PERCENT)
        right_group.spin(FORWARD, Right, PERCENT)
        # if control.buttonY.pressing():
        #     second_prog()
        #     control.rumble(".")
        #     break


drive_train = DriveTrain(left_group, right_group)


def programing_skills():
    if drive_train.prog_count > 0:
        return
    drive_train.prog_count += 1
    brain.timer.reset()
    sensor.set_heading(0)
    drive_train.pos = [0, 0]
    wall_stakes.set_velocity(100, PERCENT)
    wall_stakes.spin_for(FORWARD, 800, MSEC)
    wall_stakes.spin(REVERSE, 100, PERCENT)
    grabber.set(False)
    # drive is [x,y] x is away and y is across in this case
    drive_train.drive([400, 800], 100, False)
    wait(300, MSEC)
    wall_stakes.stop()
    grabber.set(True)
    spin_full_intake(FORWARD)
    drive_train.drive([1200, 800], 100, True, True)
    drive_train.drive([1100, 2000], 100, True, True)
    if Competition.is_driver_control():
        print("starting driver at: ", brain.timer.time(), "ms", sep="")
        return
    drive_train.drive([0, 1600], 75, True, True)
    wait(750, MSEC)
    drive_train.drive([-300, 2200], 100, False, False)
    wait(2000, MSEC)
    stop_full_intake()
    grabber.set(False)
    drive_train.drive([500, 1900], 100, True, True)
    drive_train.drive([-200, 0], 100, False, True)
    drive_train.drive([-200, -1000], 100, False, False)
    wait(400, MSEC)
    grabber.set(True)
    drive_train.drive([-1000, -1000], 100, True, False)
    wait(750, MSEC)
    drive_train.pos = [0, 0]
    spin_full_intake(FORWARD)
    drive_train.drive([400, 0], 100, False, True)
    drive_train.drive([1200, -100], 100, True, True)
    drive_train.drive([1200, -1200], 100, True, True)
    drive_train.drive([400, -1200], 100, True, True)
    drive_train.drive([0, -1800], 100, True, False)
    wait(2000, MSEC)
    drive_train.pos = [0, 0]
    drive_train.drive([600, 0], 100, False, True)
    drive_train.drive([0, 0], 100, False, True)
    grabber.set(False)
    # drive_train.drive([3000, 200], 100, True, True)
    print("total time: ", brain.timer.time(), "ms", sep="")


def second_prog():
    print("starting second prog")
    sensor.set_heading(180)
    spin_full_intake(FORWARD)
    drive_train.drive([0, 1200], 100, True, True)
    drive_train.drive([1200, 1200], 100, True, True)
    drive_train.drive([800, 800], 100, True, True)
    Thread(driver)


def monitor_conveyor():
    while True:
        if conveyor.current() < 2.5:
            continue
        if conveyor.velocity(PERCENT) > 70:
            continue
        conveyor.spin(REVERSE)
        wait(500, MSEC)
        conveyor.spin(FORWARD)


def auto_right():
    brain.timer.reset()
    drive_train.pos = [0, 0]
    print("Starting AUTOrightv.3.3")
    grabber.set(False)
    sensor.set_heading(0)
    wall_stakes_time = 1400
    wall_stakes.spin(FORWARD, 100, PERCENT)
    wait(wall_stakes_time, MSEC)
    wall_stakes.spin(REVERSE, 100, PERCENT)
    wait(wall_stakes_time-100, MSEC)
    wall_stakes.stop()
    drive_train.turn(90)
    right_group.spin(FORWARD, 30, PERCENT)
    left_group.spin(FORWARD, 30, PERCENT)
    wait(500, MSEC)
    right_group.stop()
    left_group.stop()
    print("auto time", brain.timer.value())


def auto_left():
    brain.timer.reset()
    print("Starting AUTOleftv.20.7")
    grabber.set(False)
    wall_stakes_time = 1400
    sensor.set_heading(0)
    wall_stakes.spin(FORWARD, 100, PERCENT)
    wait(wall_stakes_time, MSEC)
    wall_stakes.spin(REVERSE, 100, PERCENT)
    wait(500, MSEC)
    spin_full_intake(REVERSE)
    flex_wheel_lift_down.set(True)
    flex_wheel_lift_up.set(False)
    single_ring_time = 200
    left_group.spin(REVERSE, 100, PERCENT)
    right_group.spin(REVERSE, 100, PERCENT)
    wait(single_ring_time, MSEC)
    left_group.spin(FORWARD, 100, PERCENT)
    right_group.spin(FORWARD, 100, PERCENT)
    wait(single_ring_time, MSEC)
    left_group.stop()
    right_group.stop()
    drive_train.turn(250)
    spin_full_intake(FORWARD)
    flex_wheel_lift_down.set(False)
    wait(wall_stakes_time-500, MSEC)
    wall_stakes.stop()
    left_group.spin(FORWARD, 40, PERCENT)
    right_group.spin(FORWARD, 40, PERCENT)
    wait(1300, MSEC)
    grabber.set(True)
    left_group.stop()
    right_group.stop()
    drive_train.turn(340)
    left_group.spin(REVERSE, 30, PERCENT)
    right_group.spin(REVERSE, 30, PERCENT)
    wait(750, MSEC)
    left_group.stop()
    right_group.stop()
    drive_train.turn(220)
    left_group.spin(REVERSE, 40, PERCENT)
    right_group.spin(REVERSE, 40, PERCENT)
    back_time = 1800
    wait(500, MSEC)
    flex_wheel_lift_down.set(False)
    flex_wheel_lift_up.set(True)
    wait(500, MSEC)
    flex_wheel_lift_up.set(False)
    wait(back_time-1000, MSEC)
    left_group.stop()
    right_group.stop()
    Thread(lower_flexes)
    wait(50, MSEC)
    drive_train.turn(90)
    left_group.spin(REVERSE, 40, PERCENT)
    right_group.spin(REVERSE, 40, PERCENT)
    wait(1000, MSEC)
    left_group.stop()
    right_group.stop()
    print("auto time", brain.timer.value())


def spin_full_intake(direction):
    intake.spin(direction, 100, PERCENT)
    conveyor.spin(direction, 100, PERCENT)


def stop_full_intake():
    intake.stop()
    conveyor.stop()


def lift_flexes():
    flex_wheel_lift_down.set(False)
    flex_wheel_lift_up.set(True)
    wait(100, MSEC)
    flex_wheel_lift_up.set(False)


def lower_flexes():
    flex_wheel_lift_down.set(True)
    flex_wheel_lift_up.set(False)
    wait(100, MSEC)
    flex_wheel_lift_down.set(False)


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
    control.buttonUp.pressed(lift_flexes)
    control.buttonDown.pressed(lower_flexes)
    control.buttonB.pressed(lambda: doinker.set(not (doinker.value())))
    # control.buttonX.pressed(driver)
    Competition(skills, programing_skills)
    while True:
        avg, max = monitor_temp()
        out = 'avg{:2.0f},max{:2.0f}'.format(avg, max)
        control.screen.set_cursor(0, 3)
        control.screen.clear_line(3)
        control.screen.print(out)
        wait(500, MSEC)


main()
