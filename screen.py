import solver

import pygame
import numpy as np
import math
import time
import random

pygame.font.init()

print("Welcome to the arrow puzzle game! Get all the arrows pointing down to win!\n"
"By clicking an arrow, the arrow you clicked, as well as those surrounding it, will rotate. \n"
"To play, it is recommended to create a board smaller than 10x10 with less than 6 angles \n"
"To test out the limits of the solver, it is recommended to keep within a 250x250 board \n"
"(Unless you want to see a fully green screen) \n"
"Press left click to rotate arrows \n"
"Press s to solve \n"
"Press r to reset to a new board"
"Press space to switch to numbers"
"Good luck!")

#Asking user for data on board
print("Give dimensions of board:")
while True:
    dim = [input("width: "), input("height: ")]
    if dim[0].isdigit() and dim[1].isdigit and not (dim[0] == dim[1] == "2"):
        dim[0], dim[1] = int(dim[0]), int(dim[1])
        break
    print("Please enter in the correct format")

while True:
    rot = input("Give the number of possible rotations: ")
    if rot.isdigit():
        rot = int(rot)
        break
    print("Please enter a number")
angle_rot = 2 * math.pi/rot

SCREEN_WIDTH = 900
SCREEN_HEIGHT = 900

#Setting colours
screen_colour = (10,10,10)
arrow_colour = (36, 204, 68)

#Setting the box size
box_size = int(min(SCREEN_WIDTH/dim[0], SCREEN_HEIGHT/dim[1]))
box_size = min(100, box_size)
#Setting proportions
ARROW_PROPORTION = 0.9
FONT_PROPORTION = 0.8

#Setting text font, size and position correction based off box size
font = pygame.font.SysFont('Consolas', int(box_size * FONT_PROPORTION))
correction = np.array([int(0.4 * box_size), int(0.4 * box_size)])
#Setting the inital state of the game to display arrows and not numbers
numbers = False
#Creating the arrows
arrow_vertices = np.array([(-5, -50), (5, -50), (5,0), (30,0), (0,50), (-30, 0), (-5,0)]) * (box_size/100) * ARROW_PROPORTION
arrow_list = []

#Pre generating the rotated arrow vertices
rotated_arrow_vertices = [arrow_vertices]
rotation_matrix = np.array([[math.cos(angle_rot), math.sin(angle_rot)],
                          [-math.sin(angle_rot), math.cos(angle_rot)]])
for angle in range(rot):
    rotated_arrow_vertices.append(np.dot(rotated_arrow_vertices[-1], rotation_matrix))

#Making screen
screen = pygame.display.set_mode((box_size * dim[0], box_size*dim[1]))

#Generates a board with only the arrows' rotation values
def generate_board():
    board = []
    for i in range(dim[1]):
        board.append([])
        for j in range(dim[0]):
            board[i].append(arrow_list[i][j][1])

    return board

#Generates the arrow poygons
def generate_arrows(pos, angle):
    #Rotating the vertices of the arrow
    rotated_vertices = rotated_arrow_vertices[angle]
    #Drawing the arrow
    pygame.draw.polygon(screen, arrow_colour, rotated_vertices + np.array(pos))

#Rotates the arrows
def rotate(arrow_index, render = False, display = False, rotations = 1, multiple = False, rect_list = []):
    #Creating and drawing the Rect object to update that section of the screen
    rect_list.append(pygame.Rect((arrow_index[1] - 1) * box_size, (arrow_index[0] - 1) * box_size, 3 * box_size, 3 * box_size))
    pygame.draw.rect(screen, screen_colour, rect_list[-1])

    #Rotating the arrows around the selected/inputed arrow
    for i in range(max(arrow_index[0] - 1, 0), min(arrow_index[0] + 1, dim[1] - 1) + 1):
        for j in range(max(arrow_index[1]  - 1, 0), min(arrow_index[1] + 1, dim[0] - 1) + 1):
            arrow_list[i][j][1] = (arrow_list[i][j][1] + rotations) % rot

            #Rendering them only if render is true. While quicksolving the render is false
            if render:
                if not numbers:
                    generate_arrows(arrow_list[i][j][0], arrow_list[i][j][1])
                else:
                    generate_text(arrow_list[i][j][0],arrow_list[i][j][1])
    
    if display:
        pygame.display.update(rect_list)

#Generates text based off position and rotation value
def generate_text(pos, num):
    center = (1 - FONT_PROPORTION/2)/2 * box_size
    pos = pos - correction + [(center if num < 10 else 0),0]
    text = font.render(str(num), True, arrow_colour)

    screen.blit(text, pos)

#Solves the board quickly for large boards and finding solvable boards
def quick_solve(solution, reverse = False, display = False):
    rect_list = []

    #Cacluating the number of frames to be skipped to increase speed
    skip_frame = int((len(solution)/10000) ** 3)

    frame = 0

    for move in solution:
        #If in reverse, re-randomizes in a solvable way
        if reverse:
            rotate([move[0], move[1]], render=False, display=False, rotations=move[2], rect_list=rect_list)
            rect_list = []
        #Only display changes if necessary
        if display:
            #Skip frames if skip_frame > 1
            if skip_frame > 1:
                #Only display when frame % skip_fram == 0
                if frame % skip_frame == 0:
                    rotate([move[0], move[1]], render=True, display = True, rotations=move[2], multiple=False, rect_list=rect_list)
                    rect_list = []
                    frame = 0
                else:
                    #Create a list to display when frame % skip_fram == 0
                    rotate([move[0], move[1]], render=True, display = False, rotations=move[2], multiple=True, rect_list=rect_list)
                frame += 1
            #If skip_frame <= 1, display every frame
            else:
                rotate([move[0], move[1]], render=True, display=True, rotations=move[2], rect_list=rect_list)
                rect_list = []
        else:
            rotate([move[0], move[1]], render=False, display=False, rotations=move[2], rect_list=rect_list)
            rect_list = []

#If the board is of certain dimentions, it is not necessarily solvable
def correct_board(board):
    if (dim[0] - 5) % 3 == 0 or (dim[1] - 5) % 3 == 0 or dim[0] < 2 or dim[1] < 2:
        solution = solver.solve(board, rot, matrix_opa=matrix_opa, matrix_opb=matrix_opb)

        quick_solve(solution)

        #Making the boards solvable
        if (dim[0] - 5) % 3 == 0 or dim[1] < 2:
            for line in arrow_list:
                line[0][1] = 0

        if (dim[1] - 5) % 3 == 0 or dim[0] < 2:
            for arrow in arrow_list[0]:
                arrow[1] = 0
        
         

        #Undoing the solution to get to the original state of the board
        quick_solve(solution, reverse = True)

#Creating list of arrows
def random_board(arrow_list):
    for i in range(dim[1]):
        arrow_list.append([])
        for j in range(dim[0]):
            arrow_list[i].append([((0.5 + j) * box_size, (0.5 + i) * box_size), random.randint(0,rot)])
            
def new_board():
    random_board(arrow_list)
    board = generate_board()
    correct_board(board)

#Creates puzzle board
random_board(arrow_list)

#Priming the solver by finding solver matrices
board = generate_board()
matrix_opa, matrix_opb = solver.solve(board, rot, prime=True)

#Corrects board
correct_board(board)


#Updates the whole screen
def update_screen():
    #Draws backgroud
    screen.fill(screen_colour)
    
    #Generates arrows and numbers
    for line in arrow_list:
        for arrow in line:
            if numbers:              
                generate_text(arrow[0], arrow[1])
            else:
                generate_arrows(arrow[0], arrow[1])

    pygame.display.flip()

#Setting intital values
running = True
win = False

#Stops the program if running is False
while running:
    update_screen()
    #Checks for win
    if win == True:
        print("You win!!")
        running = False

    #Checks for events
    for event in pygame.event.get():
        #If quit is selected, running becomes False and the program stops
        if event.type == pygame.QUIT:
            running = False
        
        #If the mouse button is clicked, the arrows are rotated
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse = pygame.mouse.get_pos()
            
            #Making sure the arrows are within the bounds of the screen
            if mouse[0] < box_size * dim[0] and mouse[1] < box_size * dim[1]:
                arrow_index = [math.floor(mouse[1]/box_size), math.floor(mouse[0]/box_size)]
                rotate(arrow_index, render=True, display=True, rect_list=[])

                #Evaluating win
                win = True
                for line in arrow_list:
                    for arrow in line:
                        if arrow[1] % rot != 0:
                            win = False
                            break
                    if not win:
                        break
        
        #Checks if a key has been pressed
        if event.type == pygame.KEYDOWN:
            #If key pressed is "s", solves the board
            if event.key == pygame.K_s:
                board = generate_board()
                solution = solver.solve(board, rot, matrix_opa=matrix_opa, matrix_opb=matrix_opb)
                random.shuffle(solution)

                #Setting a delay based off the number of moves to make it visible at small scales
                moves = len(solution)
                delay = (4 - moves * 0.001 * rot/2)/(moves * rot + 1) * 2

                #Calculating the number of rotations to skip every move
                skip_rot = int((moves * rot/2)/30000)

                #It skip_rot <= 1, no rotation is skipped
                if skip_rot <= 1:
                    for move in solution:
                        for step in range(move[2]):
                            #If there are few moves, add a delay
                            if delay > 0:
                                time.sleep(delay)
                            rect_list = []
                            rotate([move[0], move[1]], render=True, display=True, rect_list=rect_list)
                else:
                    #If skip less than the total number of rotations, no frames are skipped either
                    if skip_rot < rot:
                        for move in solution:
                            times = move[2]
                            #Skipping rotations
                            while times != 0:
                                rect_list = []
                                rotate([move[0], move[1]], render=True, display=True, rotations=min(skip_rot, times), rect_list=rect_list)
                                times = max(times - skip_rot, 0)
                    else:
                        quick_solve(solution, reverse=False, display=True)
                    
                if moves > 10:
                    if moves > 100:
                        if moves > 1000:
                            rank = "Not very close!!"
                    else:
                        rank = "Somewhat close!!"
                else:
                    rank = "Very close!!"
                        
                print("You were", moves, "moves away from the solution! That is...", rank)
                print(moves)
            #If "Space" is pressed, switches displays between numbers and arrows
            if event.key == pygame.K_SPACE:
                numbers = not numbers
                update_screen()

            if event.key == pygame.K_r:

                arrow_list = []
                new_board()

                update_screen()
