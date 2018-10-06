#! /usr/bin/python
# -*- coding: utf-8 -*-
"""Make new folder with scanned name from reader, pull picture from PI"""
import os

raspiIP = "192.168.1.144"
piPath = "/home/pi/card-cap"
setupCamCommand = \
'''ssh pi@{} "raspistill -t 100 -s -o {}/current.jpg" '''.format(raspiIP, piPath)
print(setupCamCommand)
# os.system(setupCamCommand)

homePath = "/home/steven/code/osurc-card-reader"
os.chdir(homePath)

def main():
    while True:
        cardNumber = input("Scanned Card # \n")
        cardDir = "scanned_cards/{}/".format(cardNumber)
        os.makedirs(cardDir)

        takePictureCommand = "pkill -SIGUSR1 raspistill"
        backupPictureCommand = "cp {}/current.jpg {}/{}".format(piPath, piPath, cardNumber)
        sshCommands = ''' ssh pi@{} " {} && {} " '''.format(raspiIP, takePictureCommand, backupPictureCommand)
        print(sshCommands)
        # os.system(sshCommands)

        fullPath = os.path.join(homePath, cardDir)
        print("Full path: {}".format(fullPath))

        scpCommand = "scp pi@{}:/home/pi/card-cap/card.jpg {}".format(raspiIP,fullPath)
        print(scpCommand)
        # os.system(scpCommand)
        print("DONE!")

if __name__ == '__main__': main()
