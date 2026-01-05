import pygame
from pynput.keyboard import Controller, Key, Listener
import time

# Initialize
pygame.init()
pygame.joystick.init()
keyboard = Controller()

# Check for controller
if pygame.joystick.get_count() == 0:
    print("No controller detected!")
    exit()

controller = pygame.joystick.Joystick(0)
controller.init()
print(f"Connected: {controller.get_name()}")

# Flag for quitting
quit_flag = False

# Auto-movement variables
auto_move_active = False
auto_move_direction = None  # 'left' or 'right'
auto_move_steps = 0
auto_move_step_duration = 0.15  # seconds per step
auto_move_timer = 0
auto_move_loop = False  # Whether to loop the movement
auto_move_phase = 'right'  # Start with right phase

def on_press(key):
    """Listen for the = key to quit"""
    global quit_flag
    try:
        if key.char == '=':
            print("\n'=' key pressed - Exiting...")
            quit_flag = True
    except AttributeError:
        pass

# Start keyboard listener in background
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
    11: Key.up,      # D-pad Up -> UP
    12: Key.down,    # D-pad Down -> DOWN
    13: Key.left,    # D-pad Left -> LEFT
    14: Key.right,   # D-pad Right -> RIGHT
}

# Track pressed buttons to avoid repeats
pressed_buttons = set()

# Deadzone for analog sticks
DEADZONE = 0.2

def press_key(key):
    """Press a keyboard key"""
    if isinstance(key, str):
        keyboard.press(key)
    else:  # Special keys like Key.shift
        keyboard.press(key)

def release_key(key):
    """Release a keyboard key"""
    if isinstance(key, str):
        keyboard.release(key)
    else:
        keyboard.release(key)

def start_auto_move(direction, steps, loop=False):
    """Start automatic movement in a direction for a number of steps"""
    global auto_move_active, auto_move_direction, auto_move_steps, auto_move_timer, auto_move_loop, auto_move_phase
    auto_move_active = True
    auto_move_direction = direction
    auto_move_steps = steps
    auto_move_timer = time.time()
    auto_move_loop = loop
    auto_move_phase = direction
    
    # Press the initial direction key
    if direction == 'left':
        keyboard.press(Key.left)
    elif direction == 'right':
        keyboard.press(Key.right)
    
    if loop:
        print(f"Auto-move loop started: {direction} ↔ (5 steps each direction)")
    else:
        print(f"Auto-move started: {direction} for {steps} steps")

def stop_auto_move():
    """Stop automatic movement and release keys"""
    global auto_move_active, auto_move_direction, auto_move_steps, auto_move_loop
    if auto_move_active and auto_move_direction:
        # Release the movement key
        if auto_move_direction == 'left':
            keyboard.release(Key.left)
        elif auto_move_direction == 'right':
            keyboard.release(Key.right)
    auto_move_active = False
    auto_move_direction = None
    auto_move_steps = 0
    auto_move_loop = False
    print("Auto-move stopped")

print("\nController to Keyboard Mapper Running!")
print("Press '=' key to exit\n")
print("Button Mappings:")
print("  X (Cross) -> C")
print("  Circle -> E")
print("  Square -> X")
print("  Triangle -> Y")
print("  L1 -> S")
print("  R1 -> Shift")
print("  D-pad -> Arrow Keys")
print("\nAuto-Movement:")
print("  Press L2 -> Start looping LEFT/RIGHT (5 steps each)")
print("  Press R2 -> STOP auto-move loop")

running = True
clock = pygame.time.Clock()

# Track analog stick key states
left_stick_keys = {'up': False, 'down': False, 'left': False, 'right': False}

try:
    while running and not quit_flag:
        current_time = time.time()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Button pressed
            elif event.type == pygame.JOYBUTTONDOWN:
                button = event.button
                if button in BUTTON_MAP:
                    key = BUTTON_MAP[button]
                    if not auto_move_active:  # Don't allow button presses during auto-move
                        press_key(key)
                        pressed_buttons.add(button)
                        print(f"Button {button} pressed -> {key}")
            
            # Button released
            elif event.type == pygame.JOYBUTTONUP:
                button = event.button
                if button in BUTTON_MAP:
                    key = BUTTON_MAP[button]
                    if not auto_move_active:
                        release_key(key)
                        pressed_buttons.discard(button)
        
        # Handle auto-movement logic
        if auto_move_active:
            elapsed = current_time - auto_move_timer
            
            # Check if we've completed a step
            if elapsed >= auto_move_step_duration:
                auto_move_steps -= 1
                auto_move_timer = current_time
                
                if auto_move_steps <= 0:
                    if auto_move_loop:
                        # Switch direction and continue
                        keyboard.release(Key.left if auto_move_direction == 'left' else Key.right)
                        
                        # Switch to opposite direction
                        if auto_move_direction == 'right':
                            auto_move_direction = 'left'
                            auto_move_phase = 'left'
                            keyboard.press(Key.left)
                            print("← Switching to LEFT (5 steps)")
                        else:
                            auto_move_direction = 'right'
                            auto_move_phase = 'right'
                            keyboard.press(Key.right)
                            print("→ Switching to RIGHT (5 steps)")
                        
                        auto_move_steps = 5  # Reset to 5 steps for next direction
                    else:
                        print("Auto-move completed!")
                        stop_auto_move()
                else:
                    print(f"Steps remaining: {auto_move_steps}")
        
        # Handle triggers for auto-move control
        left_trigger = controller.get_axis(4)
        right_trigger = controller.get_axis(5)
        
        # L2 pressed - Start looping movement
        if left_trigger > 0.5:
            if 'l2' not in pressed_buttons:
                if not auto_move_active:
                    start_auto_move('right', 5, loop=True)
                pressed_buttons.add('l2')
        else:
            pressed_buttons.discard('l2')
        
        # R2 pressed - Stop auto-move
        if right_trigger > 0.5:
            if 'r2' not in pressed_buttons:
                if auto_move_active:
                    stop_auto_move()
                pressed_buttons.add('r2')
        else:
            pressed_buttons.discard('r2')
        
        # Handle left analog stick -> Arrow keys (disabled during auto-move)
        if not auto_move_active:
            left_x = controller.get_axis(0)
            left_y = controller.get_axis(1)
            
            # Up/Down
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
            
            # Left/Right
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
        
        clock.tick(60)  # 60 FPS

except KeyboardInterrupt:
    print("\nExiting...")
finally:
    # Stop auto-move if active
    stop_auto_move()
    
    # Stop the keyboard listener
    listener.stop()
    
    # Release all keys
    for button in BUTTON_MAP.values():
        try:
            release_key(button)
        except:
            pass
    
    # Release analog stick keys
    for key_name in left_stick_keys:
        try:
            if key_name == 'up':
                keyboard.release(Key.up)
            elif key_name == 'down':
                keyboard.release(Key.down)
            elif key_name == 'left':
                keyboard.release(Key.left)
            elif key_name == 'right':
                keyboard.release(Key.right)
        except:
            pass
    
    pygame.quit()