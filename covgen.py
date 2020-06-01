import argparse
from input_generation import InputGeneration

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('file_path', type=str)
    parser.add_argument('-f', '--function_name', type=str, default=None)

    parser.add_argument('--input_low', type=int, default=-1000)
    parser.add_argument('--input_high', type=int, default=1000)
    parser.add_argument('--optimize_max_iter', type=int, default=100)
    parser.add_argument('--variable_max_iter', type=int, default=100)

    parser.add_argument('--out_op', type=str, default=None,
            choices=['print_list', 'print_tree', 'gen_testfile'])

    args = parser.parse_args()

    input_gen = InputGeneration(args.file_path, 
            (args.input_low, args.input_high), 
            args.optimize_max_iter, args.variable_max_iter)
    
    print_list, print_tree, gen_testfile = True, True, True
    if args.out_op is not None:
        print_list, print_tree, gen_testfile = False, False, False
        if args.out_op == 'print_list':
            print_list = True
        elif args.out_op == 'print_tree':
            print_tree = True
        elif args.out_op == 'gen_testfile':
            gen_testfile = True

    if args.function_name is None:
        input_gen.all_fun_input_generate(print_list, print_tree, gen_testfile)
    else:
        input_gen.fun_name_input_generate(args.function_name, 
                print_list, print_tree, gen_testfile)