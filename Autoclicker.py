# pip stuff
from pynput import keyboard
from pynput.keyboard import Key
import time
import mouse

# print binds

keybindings = ["UnPause = f6", "Pause = f5", "Kill = Del"]
print(keybindings)

# users input on shit
up = float(input("Time(seconds) between clicks: "))

# Main boolean
run = True

def on_press(key):
    global run, pause
    
        # Start bind
    if key == Key.f6:
           print("Start")
           run = True

# Stop bind 

    if key == Key.f5:
        print("Stopping")
        time.sleep(0.2)
        run = not run
        time.sleep(0.2)
        return up 
        
# kill
# make sure it isnt "While False" and is "Return false"

    if key == Key.delete:
        print("Killing")
        time.sleep(0.5)
        run = False
        return False


# Keyboard listens for keybind

# was looking for a on_press = stop_click not stop_click = stop_click
listener = keyboard.Listener(on_press=on_press)
listener.start()

# mouse loop -real simple

while True:
     if run:
          time.sleep(up)
          mouse.click('left')
