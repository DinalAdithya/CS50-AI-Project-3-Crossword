import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for variable in self.domains:
            slot_len = variable.length

            for word in set(self.domains[variable]):
                if slot_len != len(word):
                    self.domains[variable].remove(word)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        trash_words = set()
        overlap = self.crossword.overlaps[x, y]

        if overlap is None:
            return False
        else:
            i, j = overlap
            for x_word in self.domains[x]:
                if not any(x_word[i] == y_word[j] for y_word in self.domains[y]):
                    trash_words.add(x_word)

        if trash_words:
            self.domains[x] -= trash_words
            return True

    def ac3(self, arcs=None):

        # if arcs not provided, initialize it with all arcs in the domain
        arcs = arcs if arcs is not None else [
            (x, y) for x, y in self.crossword.overlaps.keys() if self.crossword.overlaps[x, y] is not None
        ]
        seen_arcs = set()
        while arcs:  # get arcs until the q is empty
            x, y = arcs.pop()
            if (x, y) not in seen_arcs:
                seen_arcs.add((x, y))
                if self.revise(x, y):  # applied revise fun above

                    if not self.domains[x]:
                        return False  # domain[x] is empty then False

                    for z in self.crossword.variables:  # if there is more that y that overlap with x then add them to arcs


                        if z != y and z != x and (x, z) not in seen_arcs:
                            arcs.append((x, z))
                            seen_arcs.add((x, z))

        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        f_count = 0
        for variable in self.crossword.variables:
            if assignment[variable] is not None:
                continue
            else:
                return False
        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """

        if len(assignment) != len(set(assignment.values())):
            return False

        for variable1, variable2 in self.crossword.overlaps:

            if variable1 in assignment and variable2 in assignment:
                overlap = self.crossword.overlaps.get((variable1, variable2))
                if overlap is not None:
                    i, j = overlap
                    if assignment[variable1][i] != assignment[variable2][j]:
                        return False
                    else:
                        continue
        return True

    def order_domain_values(self, var, assignment):

        conflict_count = {}
        for value in self.domains[var]:
            count = 0
            for neighbours in self.crossword.neighbors(var):
                overlap = self.crossword.overlaps.get(
                    (var, neighbours))  # using get here to avoid error if there is and missing keys

                if overlap is not None:
                    i, j = overlap

                    for neighbours_value in self.domains[neighbours]:
                        if value[i] != neighbours_value[j]:
                            count += 1

            conflict_count[value] = count

        sorted_value = sorted(self.domains[var], key=lambda values: conflict_count[value])
        return sorted_value

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        unassigned_var = []

        for variable in self.domains:
            if variable not in assignment:
                unassigned_var.append(variable)

        if not unassigned_var:
            return None

        lowest_value = float('inf')
        lowest_value_neighbors_count = -1
        best_var = None

        for var in unassigned_var:
            value = len(self.domains[var])
            value_neighbour_count = len(self.crossword.neighbors(var))

            if value < lowest_value:
                lowest_value = value
                lowest_value_neighbors_count = value_neighbour_count
                best_var = var

            elif lowest_value == value:
                if value_neighbour_count > lowest_value_neighbors_count:
                    lowest_value_neighbors_count = value_neighbour_count
                    best_var = var

        return best_var

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if len(assignment) == len(self.domains):
            return assignment
        """
        else:
            not_assigned = [variable
                            for variable in self.domains if variable not in assignment
                            ]
        """
        selected_variable = self.select_unassigned_variable(assignment)

        for value in self.domains[selected_variable]:
            if self.consistent(assignment):
                assignment[selected_variable] = value

                # recursively call
                result = self.backtrack(assignment)

                if result is not None:
                    return result
                else:
                    del assignment[selected_variable]

        return None # If no valid assignment found

def main():
    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
