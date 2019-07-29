### BY BOAZ MENARD AND BRANDON ELMORE ###
DISTANCE_THRESHOLD = 3  # distance in inches within which an object is detected
STARTING_SPEED = 50

from picamera import PiCamera
import traceback
import picar
from picar.obstacle_sensor import *
from picar.front_wheels import *
from picar.back_wheels import *
from picar.line_sensor import *
import time
import Pyro4
import pickle
from PIL import Image

steering = Front_Wheels()  # create a Front_Wheels object for steering the car
motors = Back_Wheels()    # create a Back_Wheels object to move the car
objSensor = Obstacle_Sensor()  # create an Object_Sensor() object to detect distance to objects
lineSensor = Line_Sensor() # create a Line_Sensor() object to detect lines on the floor
camera = PiCamera()
picar.setup()
steering.ready()
motors.speed = STARTING_SPEED
motors.ready()
hardRight = 135
slightRight = 100
str8 = 90
slightLeft = 80
hardLeft = 45

starfleetcomm = Pyro4.Proxy('PYRONAME:starfleetcomm')



def followLine():
    '''
    Read line sensor and return a two tuple with the first element the speed
    and the second element the turn angle ie (speed, angle).
    '''
    readings = lineSensor.read_digital()
    print('Line Sensor: ', readings)
    if readings == [0, 0, 0, 0, 0]:
        steering.turn(hardRight)
    elif readings == [1, 1, 1, 1, 1]:
        motors.stop()
        steering.turn_straight()
        motors.backward()
        time.sleep(.5)
        motors.stop()
        steering.turn_left()
        motors.forward()
        time.sleep(1)
        steering.turn(str8)
    elif readings == [0, 0, 1, 1, 1] or readings == [0, 0, 0, 1, 1] or readings == [0, 0, 0, 0, 1]:
        steering.turn(str8)
    elif readings == [0, 1, 1, 1, 0] or readings == [0, 0, 1, 0, 0] or readings == [0, 0, 1, 1, 0] or readings == [0, 1, 1, 0, 0]:
        steering.turn(slightLeft)
    elif readings == [1, 0, 0, 0, 0] or readings == [1, 1, 0, 0, 0] or readings == [1, 1, 1, 0, 0]:
        steering.turn(hardLeft)


      
def Obstacle():
    """Takes a picture when an object is detected then waits for an input from user"""
    if objSensor.distance() <= DISTANCE_THRESHOLD:
        motors.stop()
        camera.start_preview()
        time.sleep(.5)
        camera.capture('/home/pi/Desktop/TermProject/object.jpg')
        camera.stop_preview()
        img = Image.open('/home/pi/Desktop/TermProject/object.jpg')
        imge = pickle.dumps(img)
        starfleetcomm.sendImage(imge)
        while not starfleetcomm.isNewCommandPosted():
            time.sleep(2)
        Decision = starfleetcomm.getCommand()
        if Decision == 'M':
            steering.turn(45)
            steering.turn(135)
            steering.ready()
            time.sleep(3)
            motors.forward()
        elif Decision == 'I':
            motors.forward()
            steering.turn(45)
            time.sleep(2)
            traverseTheMaze()
        elif Decision == "S":
            motors.forward()
            time.sleep(1)
        
        
def traverseTheMaze():
    '''
    Continuosly steers the PiCar-S until no line is detected, where by
    the function exits.
    '''
    defaultSpeed = s = 20
    motors.speed = 20
    motors.forward()
    while s != 0:
        print(objSensor.distance())
        Obstacle()
        followLine()
        
        motors.speed = s
    motors.stop()
    motors.speed = defaultSpeed
#def steering():
    #steering.turn_left()
