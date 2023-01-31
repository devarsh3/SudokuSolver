import copy


class Sudoku:
    """
    How does the ac3 algorithm work?

    Step 1: We first setup the constraint
            Create arcs.
    Step 2: We assign and add constraints into a working queue list.
    Step 3: We pick one of the arc from the working queue list  and then check if the selected arc passed the puzzle.
    Step 4: If the arc is done checking then we remove it from the agenda and we also remove inconsistent values.
    Step 5: If the domain changes then we need to add the the appropriate constraint back into the agenda if it doesn't already exist in the agenda.
    Step 6: Repeat until the agenda is empty.
    """

    def __init__(self, fileName) -> None:
        self.fileName = fileName
        self.puzzle = self.getSudoku()
        self.domain = self.getDomain()
        self.constraints = []
        self.subGrid = {}
        self.generateSubGrid()
        self.relatedCells = {}
        self.generateRelatedCellsDomain()
        self.pruned = {}
        self.generatePrunedSet()

    def getSudoku(self):
        """
        This function will read the sudoku puzzle from a file and return the puzzle.
        """
        sudokuPuzzle = []
        with open(self.fileName, "r") as f:
            lines = f.readlines()
            intLine = []
            for line in lines:
                line = line.replace("|", "").strip().split()
                intLine = [int(value) for value in line]
                sudokuPuzzle.append(intLine)
        return sudokuPuzzle

    def printSudoku(self):
        """
        This function will print the sudoku puzzle.
        """
        for i in range(len(self.puzzle)):
            for j in range(len(self.puzzle[i])):
                print(self.puzzle[i][j], end=" ")
            print()
        print("\n")

    def getDomain(self):
        """
        Create domain for the puzzle.
        """
        domain = {}
        for column in range(len(self.puzzle)):
            for row in range(len(self.puzzle)):
                value = self.puzzle[column][row]
                if (value) != 0:
                    domain[str((column, row))] = [value]
                else:
                    domain[str((column, row))] = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        return domain

    def generateSubGrid(self):
        """
        This function will generate the 9 subgrid for the sudoku puzzle that we get from the file.
        """
        r = 0
        c = 0
        for box in range(0, 9, 1):
            if box == 0 or box == 1 or box == 2:
                r = 0
            elif box == 3 or box == 4 or box == 5:
                r = 3
            elif box == 6 or box == 7 or box == 8:
                r = 6
            c = box % 3 * 3
            for row in range(r, r + 3, 1):
                for col in range(c, c + 3, 1):
                    if self.subGrid.get(str(box)) == None:
                        self.subGrid[str(box)] = [str((row, col))]
                    else:
                        self.subGrid[str(box)].append(str((row, col)))

    def getRelatedCell(self, var):
        """
        Get all the related cells for a particular cell coordinate.
            - Column cells
            - Row cells
            - Sub-grid cells
        """
        relatedCells = []
        splitVar = (
            var.strip().replace("(", "").replace(")", "").replace(" ", "").split(",")
        )
        selectedDomainBox = -1

        for x in range(len(self.puzzle)):
            if str((int(splitVar[0]), x)) not in relatedCells:
                # Row
                relatedCells.append(str((int(splitVar[0]), x)))
            if str((x, int(splitVar[1]))) not in relatedCells:
                # Column
                relatedCells.append(str((x, int(splitVar[1]))))
            if var in self.subGrid.get(str(x)):
                selectedDomainBox = x

        for v in self.subGrid.get(str(selectedDomainBox)):
            if v not in relatedCells:
                relatedCells.append(v)

        return relatedCells[1:]

    def generateConstraints(self):
        """
        This function will generate the binary constraints for the sudoku puzzle.
            - Tuple coordinate values to check if the values are different.
            - ((0,0), (0,1))
        """
        for i in range(len(self.puzzle)):
            self.addRowConstraints(i)
            self.addColumnConstraints(i)
            self.addSquareConstraints(i)

    def generateRelatedCellsDomain(self):
        """
        This function is a helper function.
        """
        for coordinate in self.domain:
            relatedCells = self.getRelatedCell(coordinate)
            self.relatedCells[str(coordinate)] = relatedCells

    def generatePrunedSet(self):
        """
        This function is also a helper function.
        """
        for coordinate in self.domain:
            self.pruned[coordinate] = []

    def addRowConstraints(self, row):
        """
        Add the row arcs to the agenda
            - ((0,0), (0,1))
        """
        for i in range(len(self.puzzle) - 1):
            for j in range(i + 1, len(self.puzzle), 1):
                if (str((row, i)), str((row, j))) not in self.constraints:
                    self.constraints.append((str((row, i)), str((row, j))))
                if (str((row, j)), str((row, i))) not in self.constraints:
                    self.constraints.append((str((row, j)), str((row, i))))

    def addColumnConstraints(self, col):
        """
        Add the column arcs to the agenda
            - ((0,0), (1,0))
        """
        for i in range(len(self.puzzle) - 1):
            for j in range(i + 1, len(self.puzzle), 1):
                if ((str((i, col)), str((j, col)))) not in self.constraints:
                    self.constraints.append((str((i, col)), str((j, col))))
                if ((str((j, col)), str((i, col)))) not in self.constraints:
                    self.constraints.append((str((j, col)), str((i, col))))

    def addSquareConstraints(self, square):
        """
        Add the square arcs to the agenda
            - ((0,0), (1,0))
        """
        squareArcs = self.subGrid.get(str(square))
        for arcs in squareArcs:
            for arc in squareArcs:
                if arcs != arc:
                    if (arcs, arc) not in self.constraints:
                        self.constraints.append((arcs, arc))
                    if ((arc, arcs)) not in self.constraints:
                        self.constraints.append((arc, arcs))

    def ac3(self):
        """
        This function will run the ac3 algorithm.
        """
        queue = list(self.constraints)  # Assign all the constraints to the queue
        while len(queue) != 0:
            arc = queue.pop(0)  # Take the first arc from all the constraints.
            if self.revise(arc):  # Checking if the constraint is valid for the domain.
                if len(self.domain.get(arc[0])) == 0:
                    # If the domain changes and the length of the domain for the arc turns to 0.
                    print("No solution can be found for arc: ", arc[0])
                    print(self.domain)
                    return False
                for x in self.constraints:
                    # Put back the constraints for the ones that have xi on the right hand side of the constraint.
                    if arc[0] == x[1] and x not in queue:
                        queue.append(x)
                        # append the arc back into the queue at the end to maintain the queue structure.
            print("Length of the queue: ", len(queue))

        if self.solvedCheck(
            self.domain
        ):  # Check if the sudoku is solved after reaching the length of the queue to 0.
            print("\nSudoku puzzle is solved using just AC-3 Algorithm.")
            self.displayResult(self.domain)
            return True
        else:
            print("-" * 50)
            print("\nSudoku puzzle is not solved.")
            print("Sudoku puzzle domain: ", self.domain)
            solution = self.backtracking_search(self.domain)
            # If the sudoku is not solved then we try to solve it using the backtracking algorithm
            if self.solvedCheck(solution):
                # After performing the backtracking algorithm we check if the sudoku is solved
                print("\nSolution found using backtracking algorithm!\n")
                self.displayResult(solution)
            else:
                print("Unable to solve it after performing backtracking algorithm.")
                return False

    def revise(self, arc):
        """
        This function will check if the domain is revised for a particular arc.
        """
        revised = False
        for x in self.domain.get(arc[0]):
            if not self.checkConstraint(x, arc):
                self.domain.get(arc[0]).remove(x)
                revised = True
        return revised

    def checkConstraint(self, value, arc):
        """
        This function will check the constraint by going through the domain.
        """
        for y in self.domain.get(arc[1]):
            if value != y:
                return True
        return False

    def solvedCheck(self, domain):
        """
        This function will check if the puzzle is solved.
        """
        for key in domain:
            if len(domain.get(key)) != 1:
                return False
        return True

    """
    *Backtracking functions

    Backtracking algorithm is used to solve the puzzle once domain of the original puzzle is reduced using ac3 algorithm. 
    - We will need assignments list (dictionary) 
        - We going to keep updating this upon selecting an assignment for a particular coordinate
    - We will be only assigning a value to a coordinate that is not already set


    *Pseudocode for backtracking

    function Backtracking-Search(csp) returns a solution or failure
        return Backtrack({}, csp)

    function Backtrack(assignment, csp) returns a solution or failure
        if assignment is complete then return assignment
        var <- Select-Unassigned-Variable(csp)
        for each value in Order-Domain-Variables(var, assignment, csp) do
            if value is consistent with assignment then
                add {var = value } to assignment
                inferences <- inference(csp, var, value)
                if inferences != failure then
                    add inferences to assignment
                    result = Backtrack(assignment, csp)
                    if result != failure then
                        return result
            remove {var == value} and inferences from assignment.
    return failure

    *successor function: assign a value to an unassigned variable that does not conflict with current assignment -> fail if no legal assignments
    
    !When a variable has no more values to assign, we will backtrack

    Backtracking search is the basic uninformed algorithm for CSPs.
    """

    def backtracking_search(self, domain):
        """
        This function will return the value after recursively backtracking.
        """
        print("\nEnd of the execution for the ac3 algorithm.")
        print("-" * 50)
        print("Solving the puzzle using backtrack search...")
        assignment = {}  # Create an assignment set

        # Assign values to the assignment set based on the output of ac3 algorithm.
        for cell in domain:
            if len(domain.get(cell)) == 1:
                assignment[cell] = [domain.get(cell)[0]]

        domainCopy = copy.deepcopy(domain)
        return self.backtrack(assignment, domainCopy)

    def backtrack(self, assignment, domain):
        """
        This is a backtracking function that helps solve the sudoku puzzle.
        """
        # print("Length assignment: ", len(assignment))
        # print("Assignment: ", assignment)
        # print("Domain: ", self.domain)
        if len(assignment) == len(domain):
            # Check if we have assigned a value to all of the cells. 81.
            print("Returning solution...")
            return assignment

        # Select one of the unassigned variable
        var = self.select_unassigned_variable(domain, assignment)

        # Order the domain in a decreasing form based on the number of conflicts from the related cells.
        orderedDomain = self.order_domain_values(var, domain)
        for value in orderedDomain:  # Go through the domain for the arc
            if self.isConsistence(var, value, assignment):
                # Check if the assignment is consistent with the already assigned variables.

                self.assign(
                    var, value, assignment, domain
                )  # Assign a value to the assignment set.
                result = self.backtrack(assignment, domain)  # Recursive
                if result:  # If we find the result then we return the result.
                    return result
                self.unAssign(var, assignment, domain)
                # If we encounter any issue after assigning a value then we revert back.
        return False

    def select_unassigned_variable(self, domain: dict, assignment):
        """
        This function will take a look at the domain provided and selects one unassigned variable
        """
        unassigned = []

        for key, value in domain.items():
            if key not in assignment:
                unassigned.append(key)
        return min(
            unassigned, key=lambda x: len(domain.get(x))
        )  # Select only the arc that has the lowest in the domain.

    def order_domain_values(self, var, domain):
        """
        This function will sort the domain for the var based on the least number of conflicts.
        """
        if len(domain.get(var)) == 1:
            return domain.get(var)

        sortCriteria = lambda val: self.sortByConflict(
            domain, var, val, self.relatedCells[var]
        )
        return sorted(domain.get(var), key=sortCriteria)

    def sortByConflict(self, domain, var, val, relatedCellDomain):
        """
        This is a helper function which will count the number of conflicts between two domain.
        """
        conflicts = 0
        for key in relatedCellDomain:
            if key != var:
                if val in domain.get(key) and len(domain.get(key)) != 1:
                    conflicts += 1
        return conflicts

    def isConsistence(self, var, value, assignment):
        """
        Checks to see if the value in the assignment consistent
        (0,0):4
        """
        isConsistent = True

        for key, cell_val in assignment.items():
            if cell_val == value and key in self.relatedCells[var]:
                isConsistent = False

        return isConsistent

    def assign(self, var, value, assignment, domain):
        """
        Assign it into assignment.
        """
        assignment[var] = [value]  # assign example: (0,0): 4
        # self.pruned[var] = domain.get(var)
        # domain[var] = [value]

        if domain:
            # domain for all the related cells
            for cells in self.relatedCells[
                var
            ]:  # go through the related cells for a particular cell
                if (
                    cells not in assignment
                ):  # We also check if the cell is not in the assignment
                    if value in domain.get(cells):
                        # we removed the value from each of the related cells domain
                        domain.get(cells).remove(value)
                        # keeping track of the values using another set called pruned.
                        # (0,0) = {((0,1),5), ((0,2),3)}
                        if var not in self.pruned:
                            self.pruned[var] = [(cells, value)]
                        else:
                            self.pruned[var].append((cells, value))

    def unAssign(self, var, assignment, domain):
        """
        The assignment didn't work so we need to remove and add back to the values accordingly.
        """
        if var in assignment:
            for (cell_coordinate, value) in self.pruned[var]:
                domain.get(cell_coordinate).append(value)
            self.pruned[var] = []
            del assignment[var]

    def displayResult(self, domain):
        """
        This is a helper function to display the results.
        """
        for row in range(len(self.puzzle)):
            print("|", end=" ")
            for column in range(len(self.puzzle)):
                print(domain.get(str((row, column)))[0], end=" ")
            print("|", end="\n")
