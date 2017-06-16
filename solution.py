import re
import itertools

def cross(A, B):
    return [s + t for s in A for t in B]

def diagonal_cross(rows, cols):
    return [i + j for i, j in zip(rows, cols)]
assignments = []
rows = 'ABCDEFGHI'
cols = '123456789'
boxes = cross(rows, cols)
row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC', 'DEF', 'GHI') for cs in ('123', '456', '789')]
diagonal_units = [diagonal_cross(rows, cols), diagonal_cross(rows, cols[::-1])]
unitlist = row_units + column_units + square_units + diagonal_units
units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s], [])) - set([s])) for s in boxes)

def assign_value(values, box, value):
	"""
	Assigns a value to a given box. If it updates the board record it.
	"""
    # Don't waste memory appending actions that don't actually change any values
	if values[box] == value:
		return values
	values[box] = value
	if len(value) == 1: assignments.append(values.copy())
	return values

def naked_twins(values): 
    """
    The naked twin strategy are only apply when we have boxes with only 2 digits which in a row,
    column and 3*3 blocks. To solve the naked twins problem, we discover twin boxes with 2 digit.
    Then, we scan through the others boxes that has same digit in row, column and 3*3 block and 
    eliminate the value that has common to the naked twin primes.
    """
    twin_box = [box for box in values.keys() if len(values[box]) == 2] # Discover twin boxes with 2 digit
    for box in twin_box:
        test = values[box]
        for unit_lines in units[box]:
            for box_unit in unit_lines:
                if (box_unit != box and values[box_unit] == test): # Discover naked twins that has same digit
                    for box_unit2 in unit_lines: # Scan through the others boxes that has same digit in row, column and 3*3 block
                        if values[box_unit2] != test: # eliminate the value that has common to the naked twin primes
                            values = assign_value(values, box_unit2, values[box_unit2].replace(test[0], ''))
                            values = assign_value(values, box_unit2, values[box_unit2].replace(test[1], ''))
    return values

def grid_values(grid):
	"""
	Convert grid into a dict of {square: char} with '123456789' for empties.
	Input: A grid in string form.
	Output: A grid in dictionary form
			Keys: The boxes, e.g., 'A1'
			Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
	chars = []
	digits = '123456789'
	for c in grid:
		if c in digits: chars.append(c)
		if c == '.': chars.append(digits)
	assert len(chars) == 81
	return dict(zip(boxes, chars))

def display(values):
	"""
	Display the values as a 2-D grid.
	Input: The sudoku in dictionary form
	Output: None
	"""
	width = 1+max(len(values[s]) for s in boxes)
	line = '+'.join(['-'*(width*3)]*3)
	for r in rows:
		print(''.join(values[r+c].center(width)+('|' if c in '36' else '') for c in cols))
		if r in 'CF': print(line)
	return

def eliminate(values):
    """
    Go through all the boxes, and whenever there is a box with a value, eliminate this value from the values of all its peers.
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    for box in solved_values:
        digit = values[box]
        for peer in peers[box]:
            assign_value(values, peer, values[peer].replace(digit, ''))
    return values

def only_choice(values):
	"""
	Go through all the units, and whenever there is a unit with a value that only fits in one box, assign the value to this box.
	Input: A sudoku in dictionary form.
	Output: The resulting sudoku in dictionary form.
	"""
	for unit in unitlist:
		for digit in '123456789':
			dplaces = [box for box in unit if digit in values[box]]
			if len(dplaces) == 1: values[dplaces[0]] = digit
	return values

def reduce_puzzle(values):
	"""
    Iterate eliminate() and only_choice(). If at some point, there is a box with no available values, return False.
    If the sudoku is solved, return the sudoku.
    If after an iteration of both functions, the sudoku remains the same, return the sudoku.
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """
	solved_values = [box for box in values.keys() if len(values[box]) == 1]
	stalled = False
	while not stalled:
		solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])
		values = eliminate(values)
		values = only_choice(values)
		solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
		stalled = solved_values_before == solved_values_after
		if len([box for box in values.keys() if len(values[box]) == 0]): return False
	return values

def search(values):
    "Using depth-first search and propagation, try all possible values."
    values = reduce_puzzle(values) # Reduce the puzzle using the previous function
    if values is False: return False ## Failed earlier
    if all(len(values[s]) == 1 for s in boxes): return values ## Solved!
    # Choose one of the unfilled squares with the fewest possibilities
    n,s = min((len(values[s]), s) for s in boxes if len(values[s]) > 1)
    # Now use recurrence to solve each one of the resulting sudokus, and 
    for value in values[s]:
        new_sudoku = values.copy()
        new_sudoku[s] = value
        attempt = search(new_sudoku)
        if attempt:
            return attempt

def solve(grid):
	# Find the solution to a Sudoku grid.
    return search(grid_values(grid))

if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments
        #visualize_assignments(assignments)
    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')