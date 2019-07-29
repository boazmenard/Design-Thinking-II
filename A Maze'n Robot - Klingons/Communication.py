from __future__ import print_function
from PIL import Image
import Pyro4
import string
import random
import pickle
import base64
@Pyro4.expose
@Pyro4.behavior(instance_mode="single")
class StarfleetComm(object):
    def __init__(self):
        self.images = []
        self.commands = []
        self.hasNewCommand = False
        self.hasNewImage = False

    def list_images(self):
        return self.images

    def list_commands(self):
        return self.commands
    
    def getImage(self,index=0):
        img = None
        if index >= 0 and index < len(self.images) :
            name = self.images.pop(index)
            self.hasNewImage = False
            print("Popped image at index {0}.".format(index))
            img = Image.open(name)
            img.show()
        return img
    
    def sendImage(self, image):
        name = ''.join([string.ascii_letters[random.randint(0,len(string.ascii_letters)-1)] for i in range(25)])+'.jpg'
        self.images.insert(0,name)
        img = base64.b64decode(image['data'])
        img = pickle.loads(img)
        self.hasNewImage = True
        img.save(name)
        print("Inserted image at index 0")

    def isNewImagePosted(self):
        return self.hasNewImage

    def getCommand(self,index=0):
        command = None
        if index >= 0 and index < len(self.commands) :
            command = self.commands.pop(index)
            self.hasNewCommand = False
            print("Popped commond at index {0}.".format(index))
            print(command)
        return command
    def sendCommand(self, command):
        self.commands.insert(0,command)
        self.hasNewCommand = True
        print("Inserted command at index 0")

    def isNewCommandPosted(self):
        return self.hasNewCommand

def main():
    Pyro4.Daemon.serveSimple(
            {
                StarfleetComm: "starfleetcomm"
            },
	    host='192.168.100.136',
            ns = True)

if __name__=="__main__":
    main()
