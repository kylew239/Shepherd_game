import pygame

pygame.init()

joystick = pygame.joystick.Joystick(0)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.JOYBUTTONDOWN:
            # Read buttons
            print(f"Button {event.button} pressed")

    # Read the D-pad
    dpad_x, dpad_y = joystick.get_hat(0)
    if dpad_x == -1:
        print("D-Pad Left")
    elif dpad_x == 1:
        print("D-Pad Right")
    if dpad_y == -1:
        print("D-Pad Down")
    elif dpad_y == 1:
        print("D-Pad Up")

    # Only print if greater than 0.5 to prevent print spamming
    # Read left joystick
    if joystick.get_axis(0) > 0.5:
        print("Left-Joystick pointing Right")
    elif joystick.get_axis(0) < -0.5:
        print("Left-Joystick pointing Left")
    if joystick.get_axis(1) > 0.5:
        print("Left-Joystick pointing Down")
    elif joystick.get_axis(1) < -0.5:
        print("Left-Joystick pointing Up")

    # Read right joystick
    if joystick.get_axis(3) > 0.5:
        print("Right-Joystick pointing Right")
    elif joystick.get_axis(3) < -0.5:
        print("Right-Joystick pointing Left")
    if joystick.get_axis(4) > 0.5:
        print("Right-Joystick pointing Down")
    elif joystick.get_axis(4) < -0.5:
        print("Right-Joystick pointing Up")

    # Read Triggers
    if joystick.get_axis(2) > 0.5:
        print("Left Trigger pressed")
    if joystick.get_axis(5) > 0.5:
        print("Right Trigger pressed")
