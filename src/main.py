# ---------------------------------------------------------------------------- #
#                                                                              #
# 	Module:       main.py                                                      #
# 	Author:       blase baptist                                                #
# 	Created:      9/19/2024, 4:52:59 PM                                        #
# 	Description:  V5 project                                                   #
#                                                                              #
# ---------------------------------------------------------------------------- #

# Library imports
from vex import *

# Brain should be defined by default
brain=Brain()

left_16 = Motor(Ports.PORT16, GearSetting.RATIO_6_1,False)
left_19 = Motor(Ports.PORT19, GearSetting.RATIO_6_1,False)
left_18 = Motor(Ports.PORT18, GearSetting.RATIO_6_1,False)
right_12 = Motor(Ports.PORT12, GearSetting.RATIO_6_1,True)
right_11 = Motor(Ports.PORT11, GearSetting.RATIO_6_1,True)
right_13 = Motor(Ports.PORT13, GearSetting.RATIO_6_1,True)
vision = Vision(Ports.PORT5)
conv = Motor(Ports.PORT17, GearSetting.RATIO_18_1,False)
lock = DigitalOut(brain.three_wire_port.b)
grab = DigitalOut(brain.three_wire_port.a)
motors = {"left_16":left_16,"left_19":left_19,"left_18":left_18,"right_12":right_12,"right_11":right_11,"right_13":right_13}

left_group = MotorGroup(left_18,left_16,left_19)
right_group = MotorGroup(right_11,right_12,right_13)

control = Controller(PRIMARY)
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
        left_group.spin(FORWARD,left,PERCENT)
        right_group.spin(FORWARD,right,PERCENT)
    
def driver():
    Thread(one_stick)
    control.buttonL1.pressed(lambda: conv.spin(FORWARD,100,PERCENT))
    control.buttonL2.pressed(lambda: conv.spin(REVERSE,100,PERCENT))
    control.buttonL1.released(conv.stop)
    control.buttonL2.released(conv.stop)
    control.buttonR1.pressed(lambda: grab.set(not grab.value()))
    control.buttonR2.pressed(lambda: lock.set(not lock.value()))

def auton():
    pass

c = Competition(driver,auton)