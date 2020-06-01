import astor
import ast
import sys
import io
import traceback
from function_module import FunctionModule
from avm_search import AvmSearch

class InputGeneration:
    def __init__(self, file_path, 
            avm_random_range, avm_variable_max_iter, avm_optimize_max_iter):
        self.whole_ast = astor.code_to_ast.parse_file(file_path)
        self.avm_random_range = avm_random_range
        self.avm_variable_max_iter = avm_variable_max_iter
        self.avm_optimize_max_iter = avm_optimize_max_iter

    def _fun_input_generate(self, fun_node):
        assert(isinstance(fun_node, ast.FunctionDef))

        fun_obj = FunctionModule(self.whole_ast, fun_node.name)
        for cf_key in fun_obj.cf_input.keys():
            if fun_obj.cf_input[cf_key] is None:
                avm_obj = AvmSearch(fun_obj, *cf_key,
                        self.avm_random_range, self.avm_variable_max_iter, self.avm_optimize_max_iter)
                avm_obj.optimize()

        return fun_obj

    def fun_node_input_generate(self, fun_node, print_cf_input, print_cfg):
        original_stdout = sys.stdout
        redirected_stdout = io.StringIO()
        sys.stdout = redirected_stdout
        try:
            fun_obj_genned = self._fun_input_generate(fun_node)
        except Exception as e:
            sys.stdout = original_stdout
            print('Exception occurred during generation: {}'.format(str(e)))
            print(redirected_stdout.getvalue())
        else:
            sys.stdout = original_stdout
            if print_cf_input:
                print(fun_obj_genned.get_cf_input_string_sorted_items())
            if print_cfg:
                print(fun_obj_genned.get_cfg_string_with_cf_input())

    def fun_name_input_generate(self, fun_name, print_cf_input, print_cfg):
        for node in self.whole_ast.body:
            if isinstance(node, ast.FunctionDef) and node.name == fun_name:
                self.fun_node_input_generate(node, print_cf_input, print_cfg)
                break
        else:
            raise ValueError('{} is undefined.'.format(fun_name))

    def all_fun_input_generate(self, print_cf_input, print_cfg):
        fun_count = 0
        for node in self.whole_ast.body:
            if isinstance(node, ast.FunctionDef):
                fun_count += 1
                print('Function < {} >'.format(node.name))
                self.fun_node_input_generate(node, print_cf_input, print_cfg)

        print('Input generated for {} functions.'.format(fun_count))

if __name__=="__main__":
    ig = InputGeneration(sys.argv[1], (-1000, 1000), 100, 100)
    ig.all_fun_input_generate(True, True)
    # ig.fun_name_input_generate('f', True, True)
            