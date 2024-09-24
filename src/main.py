# ---------------------------------------------------------------------------- #
#                                                                              #
# 	Module:       main.py                                                      #
# 	Author:       bbaptist                                                     #
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
right_12 = Motor(Ports.PORT12, GearSetting.RATIO_6_1,False)
right_11 = Motor(Ports.PORT11, GearSetting.RATIO_6_1,False)
right_13 = Motor(Ports.PORT13, GearSetting.RATIO_6_1,False)
lock = DigitalOut(brain.three_wire_port.b)
grab = DigitalOut(brain.three_wire_port.a)
motors = {"left_16":left_16,"left_19":left_19,"left_18":left_18,"right_12":right_12,"right_11":right_11,"right_13":right_13}

left_group = MotorGroup(left_18,left_16,left_19)
right_group = MotorGroup(right_11,right_12,right_13)

big_c = Controller(PRIMARY)
def one_stick():
    while True:
        throttle = big_c.axis3.position()
        turn = big_c.axis1.position()
        left = throttle-turn
        right = throttle+turn
        left_group.spin(FORWARD,left,PERCENT)
        right_group.spin(FORWARD,right,PERCENT)
    
def driver():
    Thread(one_stick)
    big_c.buttonA.pressed(lambda: grab.set(not grab.value()))
    big_c.buttonB.pressed(lambda: lock.set(not lock.value()))

def auton():
    pass

c = Competition(driver,auton)