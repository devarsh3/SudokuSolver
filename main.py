# Need to make a program that solves a Sudoku puzzle using ac3.
# The program will take in a Sudoku puzzle from a file and solve it using ac3.

from sudoku import Sudoku

print("\nSudoku Pizzle Solver\n")
sudoku = Sudoku("sudoku.txt")
sudoku.printSudoku()
sudoku.generateConstraints()
sudoku.ac3()
