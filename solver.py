import numpy as np
import copy
import time

def matrix_operations(start, dim):
    """
    Creates matrices that perform row operations that are equivalent 
    to the inverse of the matrix that describes the effect of every 
    square click on every square.
    
    (int, int) -> (np.array)
    
    """
    #creates the initial indentity matrix
    matrix_op = []
    for i in range(dim):
        matrix_op.append([0] * dim)
        matrix_op[i][i] = 1
        
    #Algorithm that simulates the row opperations necessary to invert matrix that describes the problem in dimention dim
    last = start
    for lp in range(start + 1, dim):
        for col in range(len(matrix_op)):
            matrix_op[lp][col] -= matrix_op[last][col]
            
        if (lp + 1 - start) % 3 == 0:
            continue
        last = lp
        
    last = dim - 1
    for ln in range(dim - 2, start - 1, -1):
        if (ln + 2 - start) % 3 == 0:
            continue
            
        for col in range(len(matrix_op)):
            matrix_op[ln][col] -= matrix_op[last][col]

        last = ln
    for l in range(start, dim):
        if (l - start) % 3 != 0:
            if (l - start) % 3 == 1:
                lastm_op = matrix_op[l]

            if (l - start) % 3 == 2:
                matrix_op[l - 1] = matrix_op[l]
                matrix_op[l] = lastm_op
    
    #Returns this matrix as an np.array
    return np.array(matrix_op)

def solve(board, m, matrix_opa = [], matrix_opb = [], prime=False, ):
    """
    Returns a list of a solution of moves that solves the arrow puzzle.
    
    (list(list(m :int))) -> (list(tuple(int, int, int)))
    """
    board = copy.deepcopy(board)
    a, b = len(board), len(board[0])
    
    #Dealing with the edge cases where two square clicks have same effect
    if a < 3 or b < 3:
        if a < 3:
            board = [board[1]]
            a = 1
        if b < 3:
            for i in range(len(board)):
                board[i] = [board[i][1]]
            b = 1
    #If the board becomes a 1x1, returns the solution
        if a == 1 and b == 1:
            return [(0, 0, m - board[0][0])]
    #Setting dimention and start variables
    starta, startb = 0, 0
    
    #Removing redundent squares by setting them to zero and setting new starts for inverse row operations
    if (a - 5) % 3 == 0:
        starta = 1
        board[0] = [0] * b
        
    if (b - 5) % 3 == 0:
        startb = 1
        for line in range(len(board)):
                board[line][0] = 0

    #Creating inverse row operation matrices for a and b dimensions to prime solver
    if prime:
        matrix_opa = matrix_operations(starta, a)
        matrix_opb = matrix_operations(startb, b)
        return matrix_opa,matrix_opb
    
    #Creating a new board with the number of clicks per square
    new_board = (np.array([[m] * b] * a) - np.array(board)) % m
    
    
    
    if not prime:
        #Setting up the vectors by performing the inverse row operations in dimention a
        vectors = np.dot(matrix_opa, new_board) % m
    
        #Solving the matrix by performing the inverse row operations in dimention b
        solutions = np.dot(vectors, matrix_opb) % m

        #Deconstructing the solutions into a list of tuples of coordinates and clicks
        moves = []
        for i in range(len(solutions)):
            for l in range(len(solutions[0])):
                num = int(solutions[i][l])
                if num != 0:
                    moves.append((i, l, num))
        
        return moves