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
SIG_1 = Signature(1, -4823, -4161, -4492, 2559, 4147, 3352, 2.5, 0)
SIG_2 = Signature(2, 5993, 8567, 7280, -2447, -917, -1682, 2.5, 0)
vision_4 = Vision(Ports.PORT4, 50, SIG_1, SIG_2)
left_16 = Motor(Ports.PORT16, GearSetting.RATIO_6_1, False)
left_19 = Motor(Ports.PORT19, GearSetting.RATIO_6_1, False)
left_18 = Motor(Ports.PORT18, GearSetting.RATIO_6_1, False)
right_12 = Motor(Ports.PORT12, GearSetting.RATIO_6_1, True)
right_11 = Motor(Ports.PORT11, GearSetting.RATIO_6_1, True)
right_13 = Motor(Ports.PORT13, GearSetting.RATIO_6_1, True)
conv = Motor(Ports.PORT17, GearSetting.RATIO_18_1, True)
lady_brown = Motor(Ports.PORT10, GearSetting.RATIO_36_1, False)
grab = DigitalOut(brain.three_wire_port.a)
doink = DigitalOut(brain.three_wire_port.b)
da_hood = DigitalOut(brain.three_wire_port.d)
drive_motors = {"left_16": left_16, "left_19": left_19, "left_18": left_18,
                "right_12": right_12, "right_11": right_11, "right_13": right_13}
left_group = MotorGroup(left_18, left_16, left_19)
right_group = MotorGroup(right_11, right_12, right_13)
control = Controller(PRIMARY)
sensor = Inertial(Ports.PORT8)


def get_team():
    draw()
    brain.screen.pressed(handle)


def draw():
    brain.screen.clear_screen()
    brain.screen.set_pen_width(5)
    brain.screen.set_pen_color(Color.BLUE)
    if BLUE_TEAM:
        brain.screen.set_pen_color(Color.BLACK)
    brain.screen.set_fill_color(Color.BLUE)
    brain.screen.draw_rectangle(0, 0, 240, 240)

    brain.screen.set_pen_color(Color.RED)
    if not BLUE_TEAM:
        brain.screen.set_pen_color(Color.BLACK)
    brain.screen.set_fill_color(Color.RED)
    brain.screen.draw_rectangle(240, 0, 240, 240)
    brain.screen.set_pen_color(Color.BLACK)

    brain.screen.set_font(FontType.MONO60)
    middle_y = 90
    middle_x = 60
    brain.screen.set_fill_color(Color.WHITE)
    brain.screen.print_at("Red", x=middle_x+240+15,
                          y=middle_y, opaque=(not BLUE_TEAM))
    brain.screen.print_at("Team", x=middle_x+240,
                          y=middle_y+60, opaque=(not BLUE_TEAM))
    brain.screen.print_at("Blue", x=middle_x, y=middle_y, opaque=BLUE_TEAM)
    brain.screen.print_at("Team", x=middle_x, y=middle_y+60, opaque=BLUE_TEAM)


def handle():
    global BLUE_TEAM
    if Competition.is_enabled():
        return
    BLUE_TEAM = brain.screen.x_position() <= 240
    draw()


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


BLUE_TEAM = True
AUTO_SPEED = 30


def go_for(time, dir):
    right_group.spin(dir, AUTO_SPEED, PERCENT)
    left_group.spin(dir, AUTO_SPEED, PERCENT)
    wait(time, TimeUnits.MSEC)
    right_group.stop()
    left_group.stop()


def full_go():
    left_group.spin(FORWARD, AUTO_SPEED, PERCENT)
    right_group.spin(FORWARD, AUTO_SPEED, PERCENT)


def turn_to(t_heading, speed):
    # cant turn 180
    c_heading = heading_curve(sensor.heading())
    diff = t_heading-c_heading
    while abs(t_heading - c_heading) > 0.1:
        diff = t_heading-c_heading
        c_heading = heading_curve(sensor.heading())
        r_speed = speed * diff_curve(diff)
        if diff < 0:
            left_group.spin(FORWARD, -r_speed, PERCENT)
            right_group.spin(FORWARD, r_speed, PERCENT)
        else:
            left_group.spin(FORWARD, r_speed, PERCENT)
            right_group.spin(FORWARD, -r_speed, PERCENT)
    left_group.stop(HOLD)
    right_group.stop(HOLD)


def diff_curve(x):
    return math.log(abs(x)+1)/8


def heading_curve(x):
    if x <= 180:
        return x
    else:
        return x-360


def change_team():
    global BLUE_TEAM
    print(BLUE_TEAM)
    control.screen.print(BLUE_TEAM)
    BLUE_TEAM = not BLUE_TEAM


def auto():
    brain.screen.clear_screen()
    print("starting auto")
    if BLUE_TEAM:
        print("on blue")
    else:
        print("on red")
    left_group.set_stopping(HOLD)
    right_group.set_stopping(HOLD)
    lady_brown.set_stopping(COAST)
    left_group.stop()
    right_group.stop()
    first_spin = 250  # DEGREES
    lady_brown.spin_for(FORWARD, first_spin * 3, DEGREES, 50, PERCENT)
    wait(50, TimeUnits.MSEC)
    go_for(200, FORWARD)
    lady_brown.spin_for(REVERSE, first_spin * 3 - 20,
                        DEGREES, 50, PERCENT, wait=False)
    turn_to(45, 25)
    conv.spin(FORWARD, 100, PERCENT)
    if detect == BLUE_TEAM:
        pass
    print("done")


def detect():
    while True:
        objs = vision_4.take_snapshot(SIG_1)
        if objs is not None:
            # its blue
            return True
        objs = vision_4.take_snapshot(SIG_2)
        if objs is not None:
            # its red
            return False


def main():
    get_team()
    sensor.calibrate()
    cal_time = 0
    while sensor.is_calibrating():
        cal_time += 0.01
        wait(10, MSEC)
    print("\ncalibraited in ", cal_time, "s", sep="")
    _ = Competition(driver, auto)
    control.buttonL1.pressed(lambda: conv.spin(FORWARD, 100, PERCENT))
    control.buttonL2.pressed(lambda: conv.spin(REVERSE, 100, PERCENT))
    control.buttonL1.released(conv.stop)
    control.buttonL2.released(conv.stop)
    control.buttonA.pressed(lambda: grab.set(not grab.value()))
    control.buttonB.pressed(lambda: doink.set(not doink.value()))
    control.buttonX.pressed(lambda: da_hood.set(not da_hood.value()))
    control.buttonR1.pressed(lambda: lady_brown.spin(FORWARD, 100, PERCENT))
    control.buttonR2.pressed(lambda: lady_brown.spin(REVERSE, 100, PERCENT))
    control.buttonR1.released(lady_brown.stop)
    control.buttonR2.released(lady_brown.stop)


main()
