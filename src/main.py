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

# Brain should be defined by default
brain = Brain()

left_16 = Motor(Ports.PORT16, GearSetting.RATIO_6_1, False)
left_19 = Motor(Ports.PORT19, GearSetting.RATIO_6_1, False)
left_18 = Motor(Ports.PORT18, GearSetting.RATIO_6_1, False)
right_12 = Motor(Ports.PORT12, GearSetting.RATIO_6_1, True)
right_11 = Motor(Ports.PORT11, GearSetting.RATIO_6_1, True)
right_13 = Motor(Ports.PORT13, GearSetting.RATIO_6_1, True)
conv = Motor(Ports.PORT17, GearSetting.RATIO_18_1, False)
lady_brown = Motor(Ports.PORT10, GearSetting.RATIO_36_1, False)
lock = DigitalOut(brain.three_wire_port.b)
grab = DigitalOut(brain.three_wire_port.a)
doink = DigitalOut(brain.three_wire_port.c)
da_hood = DigitalOut(brain.three_wire_port.d)
drive_motors = {"left_16": left_16, "left_19": left_19, "left_18": left_18,
                "right_12": right_12, "right_11": right_11, "right_13": right_13}
left_group = MotorGroup(left_18, left_16, left_19)
right_group = MotorGroup(right_11, right_12, right_13)
control = Controller(PRIMARY)
sensor = Inertial(Ports.PORT8)


def one_stick():
    while True:
        throttle = control.axis3.position()
        turn = control.axis1.position()
        if (abs(throttle) + abs(turn) < 1):
            left_group.stop(BRAKE)
            right_group.stop(BRAKE)
            continue
        left = throttle+turn
        right = throttle-turn
        left_group.spin(FORWARD, left, PERCENT)
        right_group.spin(FORWARD, right, PERCENT)
        for name, motor_obj in drive_motors.items():
            print(name, motor_obj.velocity(RPM), end=" ")
        print("\n")


def driver():
    Thread(one_stick)
    lady_brown.set_stopping(HOLD)
    control.buttonL1.pressed(lambda: conv.spin(FORWARD, 100, PERCENT))
    control.buttonL2.pressed(lambda: conv.spin(REVERSE, 100, PERCENT))
    control.buttonL1.released(conv.stop)
    control.buttonL2.released(conv.stop)
    control.buttonA.pressed(lambda: grab.set(not grab.value()))
    control.buttonB.pressed(lambda: lock.set(not lock.value()))
    control.buttonX.pressed(lambda: da_hood.set(not da_hood.value()))
    control.buttonR1.pressed(lambda: lady_brown.spin(FORWARD, 100, PERCENT))
    control.buttonR2.pressed(lambda: lady_brown.spin(REVERSE, 100, PERCENT))
    control.buttonR1.released(lady_brown.stop)
    control.buttonR2.released(lady_brown.stop)


def go_for(left, right, time, dir):
    right_group.spin(dir, right, PERCENT)
    left_group.spin(dir, left, PERCENT)
    wait(time, TimeUnits.MSEC)
    right_group.stop()
    left_group.stop()


def end_auto_1():
    print("stoping")
    left_group.stop()
    right_group.stop()
    auto2()


def full_go():
    left_group.spin(FORWARD, AUTO_SPEED, PERCENT)
    right_group.spin(FORWARD, AUTO_SPEED, PERCENT)


def nothing():
    pass


def turn_to(t_heading, speed):
    while abs((sensor.heading() - t_heading)) >= 10:
        print(sensor.heading())

        dir = REVERSE
        if (sensor.heading() - t_heading) >= 0:
            dir = FORWARD
    print("turned!!!!")


def auto1():
    speed = 20
    left_group.spin(FORWARD, speed, PERCENT)
    right_group.spin(FORWARD,-speed, PERCENT)
    turn_to(90,speed)
    wait(50, SECONDS)
    right_group.set_stopping(HOLD)
    left_group.set_stopping(HOLD)
    lady_brown.set_stopping(COAST)
    full_go()
    wait(50, TimeUnits.MSEC)
    sensor.collision(end_auto_1)


def auto2():
    first_spin = 150  # DEGREES
    lady_brown.spin_for(FORWARD, first_spin * 3, DEGREES, 50, PERCENT)
    wait(50, TimeUnits.MSEC)
    lady_brown.spin_for(REVERSE, first_spin * 3 - 20,
                        DEGREES, 50, PERCENT, wait=False)
    # go(30,30,1300,REVERSE)
    pass


AUTO_SPEED = 30

sensor.calibrate()
c = Competition(driver, auto1)
