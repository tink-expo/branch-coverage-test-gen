import astor
import ast
import sys
import io
import traceback
from function_module import FunctionModule
from avm_search import AvmSearch

class InputGeneration:
    def __init__(self, file_path, precision,
            avm_random_range, avm_variable_max_iter, avm_optimize_max_iter):
        try:
            self.whole_ast = astor.code_to_ast.parse_file(file_path)
        except FileNotFoundError as e:
            print(e)
            exit(0)
        else:
            self.precision = precision
            self.avm_random_range = avm_random_range
            self.avm_variable_max_iter = avm_variable_max_iter
            self.avm_optimize_max_iter = avm_optimize_max_iter

            self.module_name = '.'.join(file_path.replace('/', '.').split('.')[:-1])
            self.fun_name_input = {}

    def _fun_input_generate(self, fun_node):
        assert(isinstance(fun_node, ast.FunctionDef))

        fun_obj = FunctionModule(self.whole_ast, fun_node.name)
        for cf_key in fun_obj.cf_input.keys():
            if fun_obj.cf_input[cf_key] is None:
                avm_obj = AvmSearch(fun_obj, *cf_key, self.precision,
                        self.avm_random_range, self.avm_variable_max_iter, self.avm_optimize_max_iter)
                avm_obj.optimize()

        return fun_obj

    def write_testfile_from_input(self):
        src_ast = ast.parse('import {}'.format(self.module_name))
        for fun_name, input_set in self.fun_name_input.items():
            test_fun_src = ['def test_{}():'.format(fun_name)]
            if len(input_set) > 0:
                for input_tup in input_set:
                    test_fun_src.append('{}.{}{}'.format(self.module_name, fun_name, input_tup))
            else:
                test_fun_src.append('pass')
            src_ast.body.append(ast.parse(('\n' + ' ' * 4).join(test_fun_src)))

        testfile_name = '{}_test.py'.format(self.module_name.split('.')[-1])
        with open(testfile_name, 'w') as testfile:
            testfile.write(astor.to_source(src_ast))

        return testfile_name


    def fun_node_input_generate(self, fun_node, print_cf_input, print_cfg, write_testfile):
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
            if fun_obj_genned.get_num_branches() == 0:
                print('No branch detected for function \'{}\'.'.format(fun_node.name))
            else:
                if print_cf_input:
                    print(fun_obj_genned.get_cf_input_string_sorted_items())
                    print()
                if print_cfg:
                    print(fun_obj_genned.get_cfg_string_with_cf_input())
                    print()
                if write_testfile:
                    self.fun_name_input[fun_node.name] = fun_obj_genned.get_input_set()

    def fun_name_input_generate(self, fun_name, print_cf_input, print_cfg, write_testfile):
        for node in self.whole_ast.body:
            if isinstance(node, ast.FunctionDef) and node.name == fun_name:
                self.fun_node_input_generate(node, print_cf_input, print_cfg, write_testfile)
                print('=' * 60)
                break
        else:
            raise ValueError('{} is undefined.'.format(fun_name))

        if write_testfile:
            testfile_name = self.write_testfile_from_input()
            print('Test file generated. Run \'$ pytest {}\' to run the tests.'.format(testfile_name))
        print()

    def all_fun_input_generate(self, print_cf_input, print_cfg, write_testfile):
        fun_count = 0
        for node in self.whole_ast.body:
            if isinstance(node, ast.FunctionDef):
                fun_count += 1
                print('Function < {} >\n'.format(node.name))
                self.fun_node_input_generate(node, print_cf_input, print_cfg, write_testfile)
                print('=' * 60)

        print('Input generated for {} functions.'.format(fun_count))
        if write_testfile:
            testfile_name = self.write_testfile_from_input()
            print('Test file generated. Run \'$ pytest {}\' to run the tests.'.format(testfile_name))
        print()