
#!/usr/bin/env python

#-----------------------------------------------------------
# File name   : smdoor.py
# Description : Smart Door (keypad + motor)
# Author      : Ivan Igoshev
# Date        : 2018/03/01
#-----------------------------------------------------------

# Motor preferences
steps_moved = 140
speed = 0.003

# Sound preferences
# 0 = off
# 1 = original sound
# 2 = custom sound
sound = 2
# These preference are only relevant when sound == 2
# 0 = off
# 1 = short beep
# 2 = long beep
# 3 = double beep
wrong_password_beep = 3
before_door_unlocks_beep = 1
after_door_unlocks_beep = 1

# GPIO pins preferences
BeepPin = 40
BtnPin = 38
# Motor output pins
IN1 = 31 #yellow - 11  
IN2 = 29 #blue - 12
IN3 = 32 #orange - 13
IN4 = 33 #pink - 15

# List of permanent passwords
passwords = [
        [5, 4, 8, 7]
        ]

# List of weekday passwords
weekday_passwords = [
    [1, 3, 3, 7], 
    [1, 2, 5, 2],
    [0, 3, 2, 3],
    [5, 4, 8, 4],
    [4, 5, 9, 5],
    [2, 6, 7, 6],
    [3, 7, 2, 7]
    ]

# Weekday passwords preferences
disable_all_weekday_passwords = True
active_weekdays = [True,
                   True,
                   True,
                   True,
                   True,
                   True,
                   True
                   ]

# Random password preferences
disable_random_password = False

import RPi.GPIO as GPIO
import time
from random import randint

def beep(time_delay):
    GPIO.output(BeepPin, GPIO.HIGH)
    if time_delay == 1:
        time.sleep(0.15)
    else:
        time.sleep(0.9)
    GPIO.output(BeepPin, GPIO.LOW)

def double_beep():
    for a in range(0, 2):
        GPIO.output(BeepPin, GPIO.HIGH)
        time.sleep(0.15)
        GPIO.output(BeepPin, GPIO.LOW)
        time.sleep(0.2)

def door_operating(BeepPin, speed, steps_moved, message, sound, before_door_unlocks_beep):
    if sound == 1:
        GPIO.output(BeepPin, GPIO.HIGH)
    elif sound == 2 and before_door_unlocks_beep in (1, 2):
        beep(before_door_unlocks_beep)
    elif sound == 2 and before_door_unlocks_beep == 3:
        double_beep()

    print(message)
    print('door unlocking')
    backward(speed, steps_moved)
    print('door is unlocked')
    stop()

    if sound == 1:
        for a in range(0, 15):
            GPIO.output(BeepPin, GPIO.HIGH)
            time.sleep(0.1)
            GPIO.output(BeepPin, GPIO.LOW)
            time.sleep(0.1)
    else:
        if sound == 2 and after_door_unlocks_beep in (1, 2):
            beep(after_door_unlocks_beep)
        elif sound == 2 and after_door_unlocks_beep == 3:
            double_beep() 
        time.sleep(3)

    print('door locking')
    forward(speed, steps_moved)

    print('door is locked')
    stop()

def setStep(w1, w2, w3, w4):  
        GPIO.output(IN1, w1)  
        GPIO.output(IN2, w2)  
        GPIO.output(IN3, w3)  
        GPIO.output(IN4, w4)  

def stop():  
        setStep(0, 0, 0, 0)  

def forward(delay, steps):    
        for i in range(0, steps):  
                setStep(1, 0, 0, 0)  
                time.sleep(delay)  
                setStep(0, 1, 0, 0)  
                time.sleep(delay)  
                setStep(0, 0, 1, 0)  
                time.sleep(delay)  
                setStep(0, 0, 0, 1)  
                time.sleep(delay)  

def backward(delay, steps):    
        for i in range(0, steps):  
                setStep(0, 0, 0, 1)  
                time.sleep(delay)  
                setStep(0, 0, 1, 0)  
                time.sleep(delay)  
                setStep(0, 1, 0, 0)  
                time.sleep(delay)  
                setStep(1, 0, 0, 0)  
                time.sleep(delay)  

def setup():  
        GPIO.setwarnings(False)  
        GPIO.setmode(GPIO.BOARD)       # Numbers GPIOs by physical location  
        GPIO.setup(IN1, GPIO.OUT)      # Set pin's mode is output  
        GPIO.setup(IN2, GPIO.OUT)  
        GPIO.setup(IN3, GPIO.OUT)  
        GPIO.setup(IN4, GPIO.OUT)
        GPIO.setup(BtnPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        if sound != 0:
            GPIO.setup(BeepPin, GPIO.OUT)   # Set pin mode as output
            GPIO.output(BeepPin, GPIO.LOW)

class keypad():
    # CONSTANTS 
    KEYPAD = [
    [1,2,3,"A"],
    [4,5,6,"B"],
    [7,8,9,"C"],
    ["*",0,"#","D"]
    ]

    ROW         = [11,12,13,15]
    COLUMN      = [16,18,22,7]

    def __init__(self):
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD)

    def getKey(self):

        # Set all columns as output low
        for j in range(len(self.COLUMN)):
            GPIO.setup(self.COLUMN[j], GPIO.OUT)
            GPIO.output(self.COLUMN[j], GPIO.LOW)

        # Set all rows as input
        for i in range(len(self.ROW)):
            GPIO.setup(self.ROW[i], GPIO.IN, pull_up_down=GPIO.PUD_UP)

        # Scan rows for pushed key/button
        # A valid key press should set "rowVal"  between 0 and 3.
        rowVal = -1
        for i in range(len(self.ROW)):
            tmpRead = GPIO.input(self.ROW[i])
            if tmpRead == 0:
                rowVal = i

        # if rowVal is not 0 thru 3 then no button was pressed and we can exit
        if rowVal < 0 or rowVal > 3:
            self.exit()
            return

        # Convert columns to input
        for j in range(len(self.COLUMN)):
                        GPIO.setup(self.COLUMN[j], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        # Switch the i-th row found from scan to output
        GPIO.setup(self.ROW[rowVal], GPIO.OUT)
        GPIO.output(self.ROW[rowVal], GPIO.HIGH)

        # Scan columns for still-pushed key/button
        # A valid key press should set "colVal"  between 0 and 2.
        colVal = -1
        for j in range(len(self.COLUMN)):
            tmpRead = GPIO.input(self.COLUMN[j])
            if tmpRead == 1:
                colVal=j

        # if colVal is not 0 thru 2 then no button was pressed and we can exit
        if colVal < 0 or colVal > 3:
            self.exit()
            return
 
        # Return the value of the key pressed
        self.exit()
        return self.KEYPAD[rowVal][colVal]

    def exit(self):
        # Reinitialize all rows and columns as input at exit
        for i in range(len(self.ROW)):
                GPIO.setup(self.ROW[i], GPIO.IN, pull_up_down=GPIO.PUD_UP) 
        for j in range(len(self.COLUMN)):
                GPIO.setup(self.COLUMN[j], GPIO.IN, pull_up_down=GPIO.PUD_UP)

if __name__ == '__main__':
    # Initialize the keypad class
    kp = keypad()
    entered_password = [0, 0, 0, 0]
    no_of_digits = 0
    no_of_wrong_enters = 0
    no_of_PK_enters_when_disabled = 0
    no_of_PK_enters_when_enabled = 0
    no_of_random_passwords_enabled = 0
    setup()

    try:
        #if sound != 0:
        while True:
            digit = None
            digit = kp.getKey()

            if (int(time.strftime('%S')) == last_time_btn_pressed + 10) or (int(time.strftime('%S')) == last_time_btn_pressed - 50):
                no_of_digits = 0

            if digit != None:
                digit = str(digit)
                last_time_btn_pressed = int(time.strftime('%S'))

                if digit.isdigit(): # Next digit entered
                    digit = int(digit)
                    entered_password[no_of_digits] = digit
                    no_of_digits += 1

                    if no_of_digits == 4:
                        no_of_digits = 0

                        if (entered_password in passwords):
                            message = 'password is correct'
                            door_operating(BeepPin, speed, steps_moved, message, sound, before_door_unlocks_beep)

                            if no_of_wrong_enters == 1:
                                print('There was 1 random attempt to get in')
                            elif no_of_wrong_enters != 0:
                                print('There were {} random attempts to get in'.format(no_of_wrong_enters))

                            if no_of_PK_enters_when_disabled == 1:
                                print('There was 1 unsuccessful attempt for a Password Keeper to get in')
                            elif no_of_PK_enters_when_disabled != 0:
                                print('There were {} unsuccessful attempts for a Password Keeper to get in'.format(no_of_PK_enters_when_disabled))

                            if no_of_PK_enters_when_enabled == 1:
                                print('There was 1 successful attempt for a Password Keeper to get in')
                            elif no_of_PK_enters_when_enabled != 0:
                                print('There were {} successful attempts for a Password Keeper to get in'.format(no_of_PK_enters_when_enabled))

                            no_of_wrong_enters = 0
                            no_of_PK_enters_when_disabled = 0
                            no_of_PK_enters_when_enabled = 0

                        elif (entered_password == weekday_passwords[int(time.strftime('%w')) - 1]) and active_weekdays[int(time.strftime('%w')) - 1] == True and disable_all_weekday_passwords == False :
                            message = 'password keeper has entered the password'
                            door_operating(BeepPin, speed, steps_moved, message, sound, before_door_unlocks_beep)
                            no_of_PK_enters_when_enabled += 1

                        elif entered_password == [randint(0, 9), randint(0, 9), randint(0, 9), randint(0, 9)] and disable_random_password == False:
                            message = 'someone has guessed the random password; NOOOOOOO'
                            door_operating(BeepPin, speed, steps_moved, message, sound, before_door_unlocks_beep)
                            no_of_random_passwords_enabled += 1

                        else:
                            if (entered_password == weekday_passwords[int(time.strftime('%w')) - 1]) and (active_weekdays[int(time.strftime('%w')) - 1] == False or disable_all_weekday_passwords == True):
                                print("password keeper has typed in the correct password, but it has been disabled")
                                no_of_PK_enters_when_disabled += 1
                            elif entered_password == [randint(0, 9), randint(0, 9), randint(0, 9), randint(0, 9)] and disable_random_password == False:
                                print('aergerg')
                            else:
                                print('password is incorrect; {}'.format(entered_password))
                                no_of_wrong_enters += 1

                            if sound == 2 and wrong_password_beep in (1, 2):
                                beep(wrong_password_beep)
                            elif sound == 2 and wrong_password_beep == 3:
                                double_beep()

                elif digit == 'C':  # Erase all
                    no_of_digits = 0

                elif digit == 'B' and no_of_digits != 0:  # Go back 1 digit
                    no_of_digits -= 1

                time.sleep(0.5)

            elif GPIO.input(BtnPin) == GPIO.LOW:
                message = 'red button is pressed'
                no_of_digits = 0
                door_operating(BeepPin, speed, steps_moved, message, sound, before_door_unlocks_beep)

    except KeyboardInterrupt:
        if sound != 0:
            GPIO.output(BeepPin, GPIO.HIGH)
        GPIO.cleanup()
        print('\nSMdoor program was exited')
