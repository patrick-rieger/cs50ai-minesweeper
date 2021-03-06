import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        # Any time the number of cells is equal to the count, 
        # we know that all of that sentence’s cells must be mines.
        if len(self.cells) == self.count:
            return self.cells
        return set()

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        # Any time we have a sentence whose count is 0,
        # we know that all of that sentence’s cells must be safe.
        if self.count == 0:
            return self.cells
        return set()

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        # if cell in self.cells:
        #     self.cells.remove(cell)
        self.cells.discard(cell)


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        def mark_mine_or_safe():
            # Mark any additional cells as safe or as mines
            # if it can be concluded based on the AI's knowledge base
            copy_knowledge = self.knowledge.copy()
            while copy_knowledge:
                sentence = copy_knowledge.pop()
                for safe_cell in sentence.known_safes().copy():
                    self.mark_safe(safe_cell)
                for mine_cell in sentence.known_mines().copy():
                    self.mark_mine(mine_cell)
                # The for need to be a copy of the set returned from 
                # know_safes or known_mines because it'll be modified

        # 1) Mark the cell as one of the moves made in the game
        self.moves_made.add(cell)

        # 2) Mark the cell as a safe cell, 
        # updating any sentences that contain the cell as well
        self.mark_safe(cell)

        # 3) Add a new sentence to the AI’s knowledge base, based on the value of cell and count, 
        # to indicate that count of the cell’s neighbors are mines. Only include cells 
        # whose state is still undetermined in the sentence
        i, j = cell
        cells = set()
        new_count = count
        for x in range(-1, 2):
            for y in range(-1, 2):
                if 0 <= i+x < self.height and 0 <= j+y < self.width:
                    # for all cell’s neighbors
                    nearby_cell = (i+x, j+y)
                    if nearby_cell not in (self.safes | self.moves_made) and nearby_cell != cell:
                        if nearby_cell in self.mines:
                            new_count -= 1
                        else:
                            cells.add(nearby_cell)
        sentence = Sentence(cells, new_count)
        if sentence not in self.knowledge:
            self.knowledge.append(sentence)

        # 4
        mark_mine_or_safe()

        self.knowledge = [sentence for sentence in self.knowledge if len(sentence.cells) > 0]
        # Remove all sentences from the knowledge base that have 0 cells

        # 5) Any time we have two sentences set1 = count1 and set2 = count2 where 
        # set1 is a subset of set2, then we can construct the new sentence:
        # set2 - set1 = count2 - count1
        copy_knowledge = self.knowledge.copy()
        while copy_knowledge:
            sentence1 = copy_knowledge.pop()
            set1, count1 = sentence1.cells, sentence1.count
            for sentence2 in copy_knowledge:
                set2, count2 = sentence2.cells, sentence2.count
                if set1.issubset(set2):
                    s = Sentence(set2 - set1, count2 - count1)
                    if s not in self.knowledge:
                        self.knowledge.append(s)
            mark_mine_or_safe() # Maybe is possible to mark new mines or safe cells

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        moves = self.safes - (self.moves_made | self.mines)
        if moves:
            return random.choice(tuple(moves))
        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        all_moves = {(i, j) for i in range(0, self.height) for j in range(0, self.width)}
        moves = all_moves - (self.mines | self.moves_made)
        if moves:
            return random.choice(tuple(moves))
        return None
