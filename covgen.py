import sys
from input_generation import InputGeneration

if __name__=="__main__":
    ig = InputGeneration(sys.argv[1], (-1000, 1000), 100, 100)
    ig.all_fun_input_generate(True, True, True)
    # ig.fun_name_input_generate('f', True, True)