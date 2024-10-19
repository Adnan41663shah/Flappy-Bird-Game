import random
import sys
import pygame
from pygame.locals import *

# GLOBAL VARIABLES for game configuration
FRAME_RATE = 30
SCREEN_W = 289
SCREEN_H = 511
GAME_SCREEN = pygame.display.set_mode((SCREEN_W, SCREEN_H))
GROUND_Y_POS = SCREEN_H * 0.8
SPRITES = {}
SOUNDS = {}
PLAYER_IMG = 'gallery/sprites/bird1.png'
BG_IMG = 'gallery/sprites/background.jpeg'
PIPE_IMG = 'gallery/sprites/pipe1.png'

def loadHighScore():
    """
    Loads the current high score from a file.
    If the file is empty or doesn't contain a valid integer, returns 0.
    """
    try:
        with open('highscore.txt', 'r') as file:
            score = file.read().strip()
            if score:
                return int(score)
            else:
                return 0
    except (FileNotFoundError, ValueError):
        return 0

def saveHighScore(score):
    """
    Saves the new high score to a file.
    """
    with open('highscore.txt', 'w') as file:
        file.write(str(score))

def displayWelcome():
    """
    Display the welcome screen.
    Waits for the user to press space or up key to start the game.
    """
    player_x = int(SCREEN_W / 5)
    player_y = int((SCREEN_H - SPRITES['player'].get_height()) / 2)
    msg_x = int((SCREEN_W - SPRITES['message'].get_width()) / 2)
    msg_y = int(SCREEN_H * 0.26)
    base_x = 0

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                return

        GAME_SCREEN.blit(SPRITES['background'], (0, 0))
        GAME_SCREEN.blit(SPRITES['player'], (player_x, player_y))
        GAME_SCREEN.blit(SPRITES['message'], (msg_x, msg_y))
        GAME_SCREEN.blit(SPRITES['base'], (base_x, GROUND_Y_POS))
        pygame.display.update()
        GAME_CLOCK.tick(FRAME_RATE)

def gameLoop():
    """
    Main game loop where the game logic and rendering occur.
    """
    score = 0
    high_score = loadHighScore()
    print(f"High score is: {high_score}")

    player_x = int(SCREEN_W / 5)
    player_y = int(SCREEN_W / 2)
    base_x = 0

    pipe1 = generateRandomPipes()
    pipe2 = generateRandomPipes()

    upper_pipes = [{'x': SCREEN_W + 200, 'y': pipe1[0]['y']},
                   {'x': SCREEN_W + 200 + (SCREEN_W / 2), 'y': pipe2[0]['y']}]
    lower_pipes = [{'x': SCREEN_W + 200, 'y': pipe1[1]['y']},
                   {'x': SCREEN_W + 200 + (SCREEN_W / 2), 'y': pipe2[1]['y']}]

    pipe_velocity_x = -4
    player_velocity_y = -9
    player_accel_y = 1
    player_flap_velocity = -8
    is_flapping = False
    is_paused = False

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                if player_y > 0:
                    player_velocity_y = player_flap_velocity
                    is_flapping = True
                    SOUNDS['wing'].play()
            if event.type == KEYDOWN and event.key == K_p:
                is_paused = not is_paused

        if is_paused:
            continue

        if checkCollision(player_x, player_y, upper_pipes, lower_pipes):
            gameOver(score)  # Display game over message
            return

        player_mid_pos = player_x + SPRITES['player'].get_width() / 2
        for pipe in upper_pipes:
            pipe_mid_pos = pipe['x'] + SPRITES['pipe'][0].get_width() / 2
            if pipe_mid_pos <= player_mid_pos < pipe_mid_pos + 4:
                score += 1
                print(f"Your score is {score}")
                SOUNDS['point'].play()

        if player_velocity_y < 10 and not is_flapping:
            player_velocity_y += player_accel_y

        if is_flapping:
            is_flapping = False

        player_height = SPRITES['player'].get_height()
        player_y = player_y + min(player_velocity_y, GROUND_Y_POS - player_y - player_height)

        for upper_pipe, lower_pipe in zip(upper_pipes, lower_pipes):
            upper_pipe['x'] += pipe_velocity_x
            lower_pipe['x'] += pipe_velocity_x

        if 0 < upper_pipes[0]['x'] < 5:
            new_pipe = generateRandomPipes()
            upper_pipes.append(new_pipe[0])
            lower_pipes.append(new_pipe[1])

        if upper_pipes[0]['x'] < -SPRITES['pipe'][0].get_width():
            upper_pipes.pop(0)
            lower_pipes.pop(0)

        GAME_SCREEN.blit(SPRITES['background'], (0, 0))
        for upper_pipe, lower_pipe in zip(upper_pipes, lower_pipes):
            GAME_SCREEN.blit(SPRITES['pipe'][0], (upper_pipe['x'], upper_pipe['y']))
            GAME_SCREEN.blit(SPRITES['pipe'][1], (lower_pipe['x'], lower_pipe['y']))

        GAME_SCREEN.blit(SPRITES['base'], (base_x, GROUND_Y_POS))
        GAME_SCREEN.blit(SPRITES['player'], (player_x, player_y))

        displayScore(score)
        displayHighScore(high_score)

        pygame.display.update()
        GAME_CLOCK.tick(FRAME_RATE)

        if score > high_score:
            high_score = score
            saveHighScore(high_score)
            print(f"New high score is: {high_score}")

def gameOver(score):
    """
    Displays the Game Over message and waits for the player to press a key to restart.
    """
    font = pygame.font.Font(None, 55)
    game_over_text = font.render("Game Over", True, (255, 0, 50))
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    
    GAME_SCREEN.blit(game_over_text, (SCREEN_W / 6, SCREEN_H / 3))
    GAME_SCREEN.blit(score_text, (SCREEN_W / 4, SCREEN_H / 2))
    pygame.display.update()
    pygame.time.wait(2000)  # Wait for 2 seconds before returning to the welcome screen

def checkCollision(player_x, player_y, upper_pipes, lower_pipes):
    player_height = SPRITES['player'].get_height()
    if player_y + player_height >= GROUND_Y_POS or player_y < 0:
        SOUNDS['hit'].play()
        return True

    for pipe in upper_pipes:
        if player_y < pipe['y'] + SPRITES['pipe'][0].get_height() and abs(player_x - pipe['x']) < SPRITES['pipe'][0].get_width():
            SOUNDS['hit'].play()
            return True

    for pipe in lower_pipes:
        if player_y + player_height > pipe['y'] and abs(player_x - pipe['x']) < SPRITES['pipe'][0].get_width():
            SOUNDS['hit'].play()
            return True

    return False

def generateRandomPipes():
    pipe_height = SPRITES['pipe'][0].get_height()
    offset = SCREEN_H / 3
    base_height = SPRITES['base'].get_height()

    y2 = offset + random.randrange(0, int(SCREEN_H - base_height - 1.2 * offset))
    pipe_x = SCREEN_W + 10
    y1 = pipe_height - y2 + offset
    return [{'x': pipe_x, 'y': -y1}, {'x': pipe_x, 'y': y2}]

def displayScore(score):
    digits = [int(x) for x in list(str(score))]
    width = sum([SPRITES['numbers'][digit].get_width() for digit in digits])
    x_offset = (SCREEN_W - width) / 2

    for digit in digits:
        GAME_SCREEN.blit(SPRITES['numbers'][digit], (x_offset, SCREEN_H * 0.12))
        x_offset += SPRITES['numbers'][digit].get_width()

def displayHighScore(high_score):
    font = pygame.font.Font(None, 36)
    text = font.render(f"High Score: {high_score}", True, (200, 255, 200))
    GAME_SCREEN.blit(text, (10, 10))

if __name__ == "__main__":
    pygame.init()
    GAME_CLOCK = pygame.time.Clock()
    pygame.display.set_caption('Flappy Bird by Adnan Shah')

    SPRITES['numbers'] = (
        pygame.image.load('gallery/sprites/0.png').convert_alpha(),
        pygame.image.load('gallery/sprites/1.png').convert_alpha(),
        pygame.image.load('gallery/sprites/2.png').convert_alpha(),
        pygame.image.load('gallery/sprites/3.png').convert_alpha(),
        pygame.image.load('gallery/sprites/4.png').convert_alpha(),
        pygame.image.load('gallery/sprites/5.png').convert_alpha(),
        pygame.image.load('gallery/sprites/6.png').convert_alpha(),
        pygame.image.load('gallery/sprites/7.png').convert_alpha(),
        pygame.image.load('gallery/sprites/8.png').convert_alpha(),
        pygame.image.load('gallery/sprites/9.png').convert_alpha(),
    )

    SPRITES['message'] = pygame.image.load('gallery/sprites/message1.png').convert_alpha()
    SPRITES['base'] = pygame.image.load('gallery/sprites/base1.png').convert_alpha()
    SPRITES['pipe'] = (pygame.image.load(PIPE_IMG).convert_alpha(),
                       pygame.image.load(PIPE_IMG).convert_alpha())

    SOUNDS['hit'] = pygame.mixer.Sound('gallery/audio/hit.mp3')
    SOUNDS['point'] = pygame.mixer.Sound('gallery/audio/point.mp3')
    SOUNDS['wing'] = pygame.mixer.Sound('gallery/audio/wing.mp3')

    SPRITES['background'] = pygame.image.load(BG_IMG).convert()
    SPRITES['player'] = pygame.image.load(PLAYER_IMG).convert_alpha()

    while True:
        displayWelcome()
        gameLoop()
