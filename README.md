# Crossword Puzzle Solver

This project implements an AI-based crossword puzzle solver using Constraint Satisfaction Problems (CSPs). The solver efficiently fills crossword grids by applying backtracking, heuristics, and constraint propagation to meet word and positional constraints.

## Features

- **Constraint Satisfaction Problem (CSP) Approach**: Ensures all word and positional constraints are satisfied.
- **Backtracking Search**: Explores potential word placements to find a valid solution.
- **Heuristics**: Implements techniques like Minimum Remaining Values (MRV) and Least Constraining Values (LCV) for optimization.
- **Arc Consistency**: Utilizes AC-3 to enforce constraints and prune the search space.

## How It Works

1. **Define the crossword structure**: Specify grid dimensions and word placements.
2. **Apply CSP principles**:
   - Assign words to positions based on constraints.
   - Use backtracking and heuristics to explore solutions.
3. **Output the completed crossword grid**.

## Project Files

- `generate.py`: Main script to solve and display crossword puzzles.
- `crossword.py`: Contains classes and methods for managing the crossword structure and constraints.
- `data/`: Example crossword grids and word lists.
- `README.md`: Documentation for the project.

