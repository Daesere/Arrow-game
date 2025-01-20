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
"To test out the limits of the solver, it is recommended to keep within a 350x350 board \n"
"(Unless you want to see a fully green screen) \n"
"Good luck!")

#Asking user for data on board
print("Give dimensions of board:")
while True:
    dim = [input("width: "), input("height: ")]
    if dim[0].isdigit() and dim[1].isdigit:
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

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 1000

#Setting colours
screen_colour = (10,10,10)
arrow_colour = (36, 204, 68)

#Setting the box size
box_size = int(min(SCREEN_WIDTH/dim[0], SCREEN_HEIGHT/dim[1]))
box_size = min(100, box_size)
#Setting text font, size and position correction based off box size
font = pygame.font.SysFont('Consolas', int(box_size * 0.8))
correction = np.array([int(0.4 * box_size), int(0.4 * box_size)])
#Setting the inital state of the game to display arrows and not numbers
numbers = False
#Creating the arrows
arrow_vertices = np.array([(-5, -50), (5, -50), (5,0), (30,0), (0,50), (-30, 0), (-5,0)]) * (box_size/100) * 0.9
arrow_list = []

#Creating the rotated arrow vertices, important for large boards
rotated_arrow_vertices = [arrow_vertices]
rotation_matrix = np.array([[math.cos(angle_rot), math.sin(angle_rot)],
                          [-math.sin(angle_rot), math.cos(angle_rot)]])
for angle in range(rot):
    rotated_arrow_vertices.append(np.dot(rotated_arrow_vertices[-1], rotation_matrix))

#Making screen
screen = pygame.display.set_mode((box_size * dim[0], box_size*dim[1]))

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
    
    if multiple:
        return rect_list

#Generates text based off position and rotation value
def generate_text(pos, num):
    pos = pos - correction + [(0.2 * box_size if num < 10 else 0),0]
    text = font.render(str(num), True, arrow_colour)

    screen.blit(text, pos)

#Creating list of arrows
for i in range(dim[1]):
    arrow_list.append([])
    for j in range(dim[0]):
        arrow_list[i].append([((0.5 + j) * box_size, (0.5 + i) * box_size), random.randint(0,rot)])

#Generates a board with only the arrows' rotation values
def generate_board(empty = False):
    
    board = []
    for i in range(dim[1]):
        board.append([])
        for j in range(dim[0]):
            board[i].append(arrow_list[i][j][1])

    return board

#Primes the solver
board = generate_board()
matrix_opa, matrix_opb = solver.solve(board, rot, prime=True)

#Solves the board quickly for large boards and finding solvable boards
def quick_solve(solution, reverse = False, display = False):
    mult, add = 1, 0
    rect_list = []

    skip_rot = int(len(solution) * rot/2 /30000)
    skip_frame = int((len(solution)/10000) ** 3)

    print(skip_frame, "skip_frame")
    print(skip_rot, "skip_rot")
    frame = 0

    if reverse:
        mult = -1
        add = rot

    for move in solution:
        if display:
            if skip_rot > 1:
                if skip_frame > 1:
                    if frame % skip_frame == 0:
                        rotate([move[0], move[1]], render=True, display = True, rotations=move[2], multiple=False, rect_list=rect_list)
                        rect_list = []
                        frame = 0
                    else:
                        rect_list = rotate([move[0], move[1]], render=True, display = False, rotations=move[2], multiple=True, rect_list=rect_list)
                    frame += 1
                else:
                    rotate([move[0], move[1]], render=True, display=True, rotations=move[2], rect_list=rect_list)
                    rect_list = []
            else:
                rotate([move[0], move[1]], render=True, display=True, rotations=min(skip_rot,move[2]), rect_list=rect_list)
                rect_list = []
        else:
            rotate([move[0], move[1]], render=False, display=False, rotations=add + mult * move[2], rect_list=rect_list)
            rect_list = []

#If the board is of certain dimentions, it is not necessarily solvable
if (dim[0] - 5) % 3 == 0 or (dim[1] - 5) % 3 == 0:
    start = time.time()
    solution = solver.solve(board, rot, matrix_opa=matrix_opa, matrix_opb=matrix_opb)
    print(time.time() - start, "solving")
    #Setting solving to true to avoid recalculating the solution
    solved = True

    quick_solve(solution)

    #Making the boards solvable
    if (dim[0] - 5) % 3 == 0:
        for line in arrow_list:
            line[0][1] = 0

    if (dim[1] - 5) % 3 == 0:
        for arrow in arrow_list[0]:
            arrow[1] = 0

    #Undoing the solution to get to the original state of the board
    quick_solve(solution, reverse = True)

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
solved = False

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

                solved = False
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
                solved = True

                #Setting the start time of the solving process
                start = time.time()

                #Setting a delay based off the number of moves to make it visible at small scales
                moves = len(solution)
                delay = (4 - moves * 0.001 * rot)/(moves * rot) * 2

                #Displays the solution
                if moves * rot < 100:
                    
                    for move in solution:
                        for step in range(move[2]):
                            if delay > 0:
                                time.sleep(delay)
                            rotate([move[0], move[1]], render=True, display=True)
                            
                else:
                    quick_solve(solution, reverse=False, display=True)
                    
                end = time.time()
                print((end - start)/moves)
                print(moves)
            #If "Space" is pressed, switches displays between numbers and arrows
            if event.key == pygame.K_SPACE:
                numbers = not numbers
                update_screen()
