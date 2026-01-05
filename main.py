import pygame
from pynput.keyboard import Controller, Key, Listener

pygame.init()
pygame.joystick.init()
keyboard = Controller()

if pygame.joystick.get_count() == 0:
    print("No controller detected!")
    exit()

controller = pygame.joystick.Joystick(0)
controller.init()
print(f"Connected: {controller.get_name()}")

quit_flag = False

def on_press(key):
    """Listen for the = key to quit"""
    global quit_flag
    try:
        if key.char == '=':
            print("\n'=' key pressed - Exiting...")
            quit_flag = True
    except AttributeError:
        pass

listener = Listener(on_press=on_press)
listener.start()

# Button mapping (PS5 controller -> Keyboard)
BUTTON_MAP = {
    0: 'c',          # X (Cross) -> C
    1: 'e',          # Circle -> E
    2: 'x',          # Square -> Q
    3: 'y',          # Triangle -> Y
    4: 'tab',        # Share -> Tab
    6: 'm',          # Options -> M
    9: 's',          # L1 -> S
    10: Key.shift,   # R1 -> Shift
    11: Key.up,         # D-pad Up -> UP
    12: Key.down,         # D-pad Down -> DOWN
    13: Key.left,         # D-pad Left -> LEFT
    14: Key.right,         # D-pad Right -> RIGHT
}

pressed_buttons = set()


DEADZONE = 0.2

def press_key(key):
    """Press a keyboard key"""
    if isinstance(key, str):
        keyboard.press(key)
    else: 
        keyboard.press(key)

def release_key(key):
    """Release a keyboard key"""
    if isinstance(key, str):
        keyboard.release(key)
    else:
        keyboard.release(key)

print("\nController to Keyboard Mapper Running!")
print("Press '=' key to exit\n")
print("Button Mappings:")
print("  X (Cross) -> Space")
print("  Circle -> E")
print("  Square -> Q")
print("  Triangle -> F")
print("  L1 -> Shift")
print("  R1 -> Ctrl")
print("  D-pad -> WASD")
print("  Left Stick -> Arrow Keys")
print("  L2 -> Left Click (held)")
print("  R2 -> Right Click (held)")

running = True
clock = pygame.time.Clock()

left_stick_keys = {'up': False, 'down': False, 'left': False, 'right': False}

try:
    while running and not quit_flag:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.JOYBUTTONDOWN:
                button = event.button
                if button in BUTTON_MAP:
                    key = BUTTON_MAP[button]
                    press_key(key)
                    pressed_buttons.add(button)
                    print(f"Button {button} pressed -> {key}")
            

            elif event.type == pygame.JOYBUTTONUP:
                button = event.button
                if button in BUTTON_MAP:
                    key = BUTTON_MAP[button]
                    release_key(key)
                    pressed_buttons.discard(button)
        

        left_x = controller.get_axis(0)
        left_y = controller.get_axis(1)
        

        if left_y < -DEADZONE:  # Up
            if not left_stick_keys['up']:
                keyboard.press(Key.up)
                left_stick_keys['up'] = True
        else:
            if left_stick_keys['up']:
                keyboard.release(Key.up)
                left_stick_keys['up'] = False
        
        if left_y > DEADZONE:  # Down
            if not left_stick_keys['down']:
                keyboard.press(Key.down)
                left_stick_keys['down'] = True
        else:
            if left_stick_keys['down']:
                keyboard.release(Key.down)
                left_stick_keys['down'] = False
        
        if left_x < -DEADZONE:  # Left
            if not left_stick_keys['left']:
                keyboard.press(Key.left)
                left_stick_keys['left'] = True
        else:
            if left_stick_keys['left']:
                keyboard.release(Key.left)
                left_stick_keys['left'] = False
        
        if left_x > DEADZONE:  # Right
            if not left_stick_keys['right']:
                keyboard.press(Key.right)
                left_stick_keys['right'] = True
        else:
            if left_stick_keys['right']:
                keyboard.release(Key.right)
                left_stick_keys['right'] = False
        

        left_trigger = controller.get_axis(4)
        right_trigger = controller.get_axis(5)
        

        if left_trigger > 0.5:
            if 'l2' not in pressed_buttons:
                keyboard.press('1')
                pressed_buttons.add('l2')
        else:
            if 'l2' in pressed_buttons:
                keyboard.release('1')
                pressed_buttons.discard('l2')
        
        if right_trigger > 0.5:
            if 'r2' not in pressed_buttons:
                keyboard.press('2')
                pressed_buttons.add('r2')
        else:
            if 'r2' in pressed_buttons:
                keyboard.release('2')
                pressed_buttons.discard('r2')
        
        clock.tick(60)  # 60 FPS

except KeyboardInterrupt:
    print("\nExiting...")
finally:
    listener.stop()
    
    for button in BUTTON_MAP.values():
        try:
            release_key(button)
        except:
            pass
    pygame.quit()