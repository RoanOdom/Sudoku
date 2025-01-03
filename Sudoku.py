import tkinter as tk
from tkinter import simpledialog
import time

class SudokuTileSystemGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Sudoku Grid")
        self.grid_values = [[0 for _ in range(9)] for _ in range(9)]
        self.is_immutable = [[False for _ in range(9)] for _ in range(9)]
        self.buttons = [[None for _ in range(9)] for _ in range(9)]
        self.puzzle_list = []  # To store 100 puzzles
        self.current_puzzle_index = 0
        self.start_time = None
        self.is_solving = False
        self.create_widgets()

    def create_widgets(self):
        # Create a frame for the entire board
        board_frame = tk.Frame(self.root, bg="black")
        board_frame.grid(row=0, column=0, padx=10, pady=10)

        # Create 3x3 subgrid frames
        for subgrid_row in range(3):
            for subgrid_col in range(3):
                subgrid_frame = tk.Frame(
                    board_frame,
                    bg="black",
                    bd=2,
                    relief="solid"
                )
                subgrid_frame.grid(row=subgrid_row, column=subgrid_col, padx=2, pady=2)

                # Create the 3x3 cells within each subgrid
                for cell_row in range(3):
                    for cell_col in range(3):
                        row = subgrid_row * 3 + cell_row
                        col = subgrid_col * 3 + cell_col
                        button = tk.Button(
                            subgrid_frame,
                            text='',
                            width=4,
                            height=2,
                            font=("Arial", 16, "bold"),
                            command=lambda r=row, c=col: self.edit_tile(r, c)
                        )
                        button.grid(row=cell_row, column=cell_col, padx=1, pady=1)
                        self.buttons[row][col] = button

        # Create a text box for Sudoku code input
        self.code_input = tk.Text(self.root, height=3, width=50)
        self.code_input.grid(row=1, column=0, padx=10, pady=(0, 10))

        # Add buttons
        self.load_button = tk.Button(
            self.root, text="Load Sudoku", command=self.load_sudoku
        )
        self.load_button.grid(row=2, column=0, pady=(0, 10))

        self.solve_button = tk.Button(
            self.root, text="Solve Sudoku", command=self.solve_sudoku
        )
        self.solve_button.grid(row=3, column=0, pady=(0, 10))

        batch_solve_button = tk.Button(
            self.root, text="Solve All Puzzles", command=self.solve_all_puzzles
        )
        batch_solve_button.grid(row=4, column=0, pady=(0, 10))

        self.counter_label = tk.Label(self.root, text="Puzzle: 0/10", font=("Arial", 14))
        self.counter_label.grid(row=5, column=0, pady=(10, 0))

        self.timer_label = tk.Label(self.root, text="Time: 0.00s", font=("Arial", 14))
        self.timer_label.grid(row=6, column=0, pady=(10, 0))

    def load_sudoku(self):
        # Get the code from the text box
        code = self.code_input.get("1.0", tk.END).strip()

        # Validate the code
        if len(code) != 81 or not all(c.isdigit() or c == '.' for c in code):
            return  # Invalid input, do nothing

        self.load_grid_from_code(code)

    def load_grid_from_code(self, code):
        # Populate the grid
        for i in range(9):
            for j in range(9):
                char = code[i * 9 + j]
                value = int(char) if char.isdigit() else 0
                self.grid_values[i][j] = value
                if value != 0:
                    self.is_immutable[i][j] = True
                    self.buttons[i][j].config(
                        text=str(value),
                        fg="black",
                        bg="#d9d9d9",
                        state="disabled"
                    )
                else:
                    self.is_immutable[i][j] = False
                    self.buttons[i][j].config(
                        text='', fg="black", bg="white", state="normal"
                    )

    def is_valid_move(self, row, col, value):
        

        # Check row
        if value in self.grid_values[row]:
            return False

        # Check column
        for r in range(9):
            if self.grid_values[r][col] == value:
                return False

        # Check subgrid
        start_row, start_col = 3 * (row // 3), 3 * (col // 3)
        for r in range(start_row, start_row + 3):
            for c in range(start_col, start_col + 3):
                if self.grid_values[r][c] == value:
                    return False

        return True

    def find_empty(self):
        # Find the next empty cell in the grid
        for row in range(9):
            for col in range(9):
                if self.grid_values[row][col] == 0:
                    return row, col
        return None
    


    def solve(self):
        changes_made = True
        while changes_made:
            self.eliminate_naked_pairs()
            changes_made = self.fill_unique_possible_values() or self.solve_single_possibilities()

            
        return self.solveBrute()


    def calculate_possible_values(self):
        self.possible_values = [[[] for _ in range(9)] for _ in range(9)]
        
        for row in range(9):
            for col in range(9):
                if self.grid_values[row][col] == 0:  # If the cell is empty
                    self.possible_values[row][col] = [
                        value for value in range(1, 10) if self.is_valid_move(row, col, value)
                    ]
                else:
                    self.possible_values[row][col] = []  # Non-empty cells have no possible values
        


    def fill_unique_possible_values(self):
        changes_made = False
        self.calculate_possible_values()

        # Check rows for unique possible values
        for row in range(9):
            value_counts = {v: 0 for v in range(1, 10)}
            cell_map = {v: None for v in range(1, 10)}

            for col in range(9):
                if self.grid_values[row][col] != 0:  # Skip filled cells
                    continue
                for value in self.possible_values[row][col]:
                    value_counts[value] += 1
                    cell_map[value] = (row, col)

            for value, count in value_counts.items():
                if count == 1:
                    r, c = cell_map[value]
                    if self.grid_values[r][c] == 0:  # Ensure the cell is still empty
                        self.grid_values[r][c] = value
                        self.buttons[r][c].config(text=str(value), fg="blue")
                        self.root.update()
                        changes_made = True
                        self.calculate_possible_values()  # Recalculate possible values

        # Check columns for unique possible values
        for col in range(9):
            value_counts = {v: 0 for v in range(1, 10)}
            cell_map = {v: None for v in range(1, 10)}

            for row in range(9):
                if self.grid_values[row][col] != 0:  # Skip filled cells
                    continue
                for value in self.possible_values[row][col]:
                    value_counts[value] += 1
                    cell_map[value] = (row, col)

            for value, count in value_counts.items():
                if count == 1:
                    r, c = cell_map[value]
                    if self.grid_values[r][c] == 0:  # Ensure the cell is still empty
                        self.grid_values[r][c] = value
                        self.buttons[r][c].config(text=str(value), fg="blue")
                        self.root.update()
                        changes_made = True
                        self.calculate_possible_values()  # Recalculate possible values

        # Check 3x3 subgrids for unique possible values
        for box_row in range(3):
            for box_col in range(3):
                value_counts = {v: 0 for v in range(1, 10)}
                cell_map = {v: None for v in range(1, 10)}

                for row in range(box_row * 3, box_row * 3 + 3):
                    for col in range(box_col * 3, box_col * 3 + 3):
                        if self.grid_values[row][col] != 0:  # Skip filled cells
                            continue
                        for value in self.possible_values[row][col]:
                            value_counts[value] += 1
                            cell_map[value] = (row, col)

                for value, count in value_counts.items():
                    if count == 1:
                        r, c = cell_map[value]
                        if self.grid_values[r][c] == 0:  # Ensure the cell is still empty
                            self.grid_values[r][c] = value
                            self.buttons[r][c].config(text=str(value), fg="blue")
                            self.root.update()
                            changes_made = True
                            self.calculate_possible_values()  # Recalculate possible values
        return changes_made

    def eliminate_naked_pairs(self):
        self.calculate_possible_values()

        # Helper function to find naked pairs in a list of possible values
        def find_naked_pairs(index_map):
            pairs = {}
            for index in index_map:
                values = self.possible_values[index[0]][index[1]]
                if len(values) == 2:
                    pair = tuple(sorted(values))
                    if pair in pairs:
                        return pair, pairs[pair], index
                    pairs[pair] = index
            return None, None, None

        # Eliminate naked pairs in rows
        for row in range(9):
            indices = [(row, col) for col in range(9) if self.grid_values[row][col] == 0]
            pair, index1, index2 = find_naked_pairs(indices)
            if pair:
                for col in range(9):
                    if (row, col) not in [index1, index2] and self.grid_values[row][col] == 0:
                        self.possible_values[row][col] = [v for v in self.possible_values[row][col] if v not in pair]

        # Eliminate naked pairs in columns
        for col in range(9):
            indices = [(row, col) for row in range(9) if self.grid_values[row][col] == 0]
            pair, index1, index2 = find_naked_pairs(indices)
            if pair:
                for row in range(9):
                    if (row, col) not in [index1, index2] and self.grid_values[row][col] == 0:
                        self.possible_values[row][col] = [v for v in self.possible_values[row][col] if v not in pair]

        # Eliminate naked pairs in 3x3 boxes
        for box_row in range(3):
            for box_col in range(3):
                indices = [
                    (row, col)
                    for row in range(box_row * 3, box_row * 3 + 3)
                    for col in range(box_col * 3, box_col * 3 + 3)
                    if self.grid_values[row][col] == 0
                ]
                pair, index1, index2 = find_naked_pairs(indices)
                if pair:
                    for row in range(box_row * 3, box_row * 3 + 3):
                        for col in range(box_col * 3, box_col * 3 + 3):
                            if (row, col) not in [index1, index2] and self.grid_values[row][col] == 0:
                                self.possible_values[row][col] = [v for v in self.possible_values[row][col] if v not in pair]




    def solve_single_possibilities(self):
        changes_made = False
        

        for row in range(9):
            for col in range(9):
                if self.grid_values[row][col] == 0:
                    possible_numbers = [
                        value for value in range(1, 10) 
                        if self.is_valid_move(row, col, value)
                    ]

                    if len(possible_numbers) == 1:
                        self.grid_values[row][col] = possible_numbers[0]
                        self.buttons[row][col].config(text=str(possible_numbers[0]), fg="blue")
                        self.root.update()
                        changes_made = True

        return changes_made


    def solveBrute(self):
        # Find an empty cell
        empty_cell = self.find_empty()
        if not empty_cell:
            return True  # No empty cells, solution found

        row, col = empty_cell

        for num in range(1, 10):
            if num not in self.possible_values[row][col]:
                continue
            if self.is_valid_move(row, col, num):
                # Make a tentative assignment
                self.grid_values[row][col] = num
                self.buttons[row][col].config(text=str(num), fg="blue")

                # Update the screen to show progress
                self.root.update()
                #time.sleep(0.01)

                
                changes_made = True
                while changes_made:
                    self.eliminate_naked_pairs()
                    changes_made = self.fill_unique_possible_values() or self.solve_single_possibilities()

                # Recursively try to solve the rest of the board
                if self.solveBrute():
                    return True

                # Undo the move (backtrack)
                self.grid_values[row][col] = 0
                self.buttons[row][col].config(text='')

                # Update the screen to show backtracking
                self.root.update()

        return False

    def solve_sudoku(self):
        if not self.solve():
            return False
        return True


    def update_timer(self):
        if self.is_solving:
            elapsed_time = time.time() - self.start_time
            self.timer_label.config(text=f"Time: {elapsed_time:.2f}s")
            self.root.after(100, self.update_timer)



    def solve_all_puzzles(self):
        # Set up the start time for the entire solving process
        self.start_time = time.time()
        self.timer_label.config(text="Time: 0.00s")  # Reset the total time label
        self.is_solving = True
        self.update_timer()
        self.code_input.grid_forget()
        self.load_button.grid_forget()
        self.solve_button.grid_forget()

        # Create labels to display group timings on the screen
        self.group_time_labels = []
        for i in range(5):
            label = tk.Label(self.root, text=f"Group {i+1} Time: 0.00s",font=("Arial", 16, "bold"),)
            label.grid(row=i+1, column=0, columnspan=2, sticky="w")
            self.group_time_labels.append(label)

        # Break the puzzles into 4 groups of 25
        total_puzzles = len(self.puzzle_list)
        group_size = 2
        groups = [self.puzzle_list[i:i + group_size] for i in range(0, total_puzzles, group_size)]

        # Solve the puzzles group by group
        for group_num, group in enumerate(groups, start=1):
            group_start_time = time.time()  # Time before processing the group

            for i, puzzle in enumerate(group):
                self.current_puzzle_index = group_num * group_size - group_size + i + 1
                self.counter_label.config(text=f"Puzzle: {self.current_puzzle_index}/{total_puzzles}")
                self.load_grid_from_code(puzzle)
                self.root.update()

                if not self.solve_sudoku():
                    print(f"Puzzle {self.current_puzzle_index} has no solution!")
                print(f"Puzzle {self.current_puzzle_index} solved in {round(time.time() - self.start_time, 3)}")

            # Time taken for the current group
            group_elapsed_time = time.time() - group_start_time
            # Update the respective label with the time for the current group
            self.group_time_labels[group_num - 1].config(text=f"Group {group_num} Time: {group_elapsed_time:.2f}s")

        # Mark the solving process as finished
        self.is_solving = False
        total_elapsed_time = time.time() - self.start_time
        self.timer_label.config(text=f"Total Time: {total_elapsed_time:.2f}s")


    def edit_tile(self, row, col):
        if self.is_immutable[row][col]:
            return

        value = simpledialog.askstring(
            "Edit Tile", f"Enter value (1-9) for cell ({row+1}, {col+1}) or leave blank to clear:"
        )

        if value is None or value.strip() == "":
            self.grid_values[row][col] = 0
            self.buttons[row][col].config(text='', fg="black")
            return

        try:
            value = int(value)
            if 1 <= value <= 9:
                if self.is_valid_move(row, col, value):
                    self.grid_values[row][col] = value
                    self.buttons[row][col].config(text=str(value), fg="black")
                else:
                    self.buttons[row][col].config(text=str(value), fg="red")
            else:
                raise ValueError
        except ValueError:
            self.grid_values[row][col] = 0
            self.buttons[row][col].config(text='', fg="black")

    def run(self):
        self.root.mainloop()


# Example usage
if __name__ == "__main__":
    sudoku_gui = SudokuTileSystemGUI()

    # Example: Load 100 pre-generated puzzles into the puzzle list
    sudoku_gui.puzzle_list = [
    '001020300403000520005060007008007005030286040100900600900030100072000408006050900',
    '012003000400050306030074000300700089000102000620005004000430060908010002000600570',
    '001020034000050006070300008005060300040000070009070200600007010300080000250040900',
    '000000001002003004560070003010200800009050600003004010100090052800100300700000000',
    '000650010007000000820009300004000500003007000570900006000080003950002800400000000',
    '006300000740801056000026040060000000300100500100008700608000420402087010010050003',
    '000100200003040005006000007001004080900020003050600100700000600200090300004008000',
    '000010020003020040010506030007002000600000003000800900040203010050070600080090000',
    '000001200300040000050006007004800030001000800070009400800500010000070006009200000',
    '000100200300040000105000040060002003070000080400900010080000607000030004009005000'

]

    sudoku_gui.run()
