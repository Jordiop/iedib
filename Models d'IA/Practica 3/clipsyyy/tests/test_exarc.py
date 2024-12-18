import numpy as np

# Funció auxiliar per mostrar els resultats
def test_centering(input_grid, name="Test"):
    print(f"\n{name}:")
    print("Input:")
    print(input_grid)
    result = center_shape(input_grid)
    print("\nOutput:")
    print(result)
    print("-" * 30)

# Cas 1: Forma petita
test_case1 = np.array([
    [0, 0, 0, 0, 0],
    [0, 1, 1, 0, 0],
    [0, 1, 1, 0, 0],
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0]
])

# Cas 2: Forma a la cantonada
test_case2 = np.array([
    [1, 1, 0, 0, 0],
    [1, 1, 0, 0, 0],
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0]
])

# Cas 3: Forma rectangular
test_case3 = np.array([
    [0, 0, 0, 0, 0, 0],
    [0, 1, 1, 1, 0, 0],
    [0, 1, 1, 1, 0, 0],
    [0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0]
])

# Executar tots els casos de prova
test_centering(test_case1, "Cas 1: Forma petita")
test_centering(test_case2, "Cas 2: Forma a la cantonada")
test_centering(test_case3, "Cas 3: Forma rectangular")