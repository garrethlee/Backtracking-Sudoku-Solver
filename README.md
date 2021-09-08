# Backtracking Sudoku Solver
A sudoku solver using the backtracking algorithm. Made using Python and Pygame.

Files:
- *main.py*: main file
- *requirements.txt*: prerequisite modules. Run `pip install -r requirements.txt`<br> before running the program

## How to Use:
- Each cell in the 9x9 grid can be inputted with a number (1-9)
- Use `BACKSPACE` to delete a number
- You can use arrow keys to navigate the board
- Enabling `Show Steps`displays every iteration of the algorithm. Disabling<br> it will make the program run faster, however, without the benefit of visualization.

## Note:
- The program has a **randomize** functionality, which serves to create a random <br>partially filled sudoku puzzle, which the algorithm will try to solve. Note that<br> the eventual configuration **might not always be solvable**.

- As expected by the usage of the most naive form of the backtracking algorithm, <br> certain configurations make the process of searching for a solution extremely <br> time consuming. This program serves to visualize the algorithm in action, as <br> well as highlight its weaknesses.
