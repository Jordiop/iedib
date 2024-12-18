import numpy as np

def find_shape(grid):
    """Troba la forma no-zero en la graella."""
    rows, cols = np.where(grid > 0)
    if len(rows) == 0:
        return None
    
    min_row, max_row = min(rows), max(rows)
    min_col, max_col = min(cols), max(cols)
    
    shape = grid[min_row:max_row+1, min_col:max_col+1]
    return shape, (min_row, min_col)

def get_center_position(grid_size, shape_size):
    """Calcula la posició central per a la forma."""
    grid_center = grid_size // 2
    shape_center = shape_size // 2
    return grid_center - shape_center

def center_shape(input_grid):
    """Centra la forma en la graella."""
    # Crear una nova graella buida
    output_grid = np.zeros_like(input_grid)
    
    # Trobar la forma original
    result = find_shape(input_grid)
    if result is None:
        return output_grid
        
    shape, (orig_row, orig_col) = result
    
    # Calcular posicions centrals
    center_row = get_center_position(input_grid.shape[0], shape.shape[0])
    center_col = get_center_position(input_grid.shape[1], shape.shape[1])
    
    # Col·locar la forma al centre
    output_grid[center_row:center_row+shape.shape[0], 
                center_col:center_col+shape.shape[1]] = shape
                
    return output_grid

# Dades d'entrenament
training_data = [
    {
        "input": np.array([
            [0, 0, 0, 0, 0],
            [0, 1, 1, 0, 0],
            [0, 1, 1, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0]
        ]),
        "output": np.array([
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 1, 1, 0, 0],
            [0, 1, 1, 0, 0],
            [0, 0, 0, 0, 0]
        ])
    }
]

# Dades de test
test_input = np.array([
    [0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0],
    [1, 1, 0, 0, 0, 0],
    [1, 1, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0]
])

# Comprovar amb dades d'entrenament
for example in training_data:
    result = center_shape(example["input"])
    print("Training example:")
    print("Input:\n", example["input"])
    print("Expected output:\n", example["output"])
    print("Actual output:\n", result)
    print("Correct:", np.array_equal(result, example["output"]))
    print()

# Comprovar amb dades de test
test_result = center_shape(test_input)
print("Test result:")
print("Input:\n", test_input)
print("Output:\n", test_result)