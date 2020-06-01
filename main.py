import astor
import ast
import sys
from function_module import FunctionModule
from avm_search import AvmSearch

if __name__ == "__main__":
    try:
        aa = astor.code_to_ast.parse_file(sys.argv[1])
    except FileNotFoundError:
        print("{} doesn't exist.".format(sys.argv[1]))
    else:
        random_range = (int(sys.argv[2]), int(sys.argv[3]))
        for node in aa.body:
            if isinstance(node, ast.FunctionDef):
                fun_obj = FunctionModule(aa, node.name)
                print("<{}>".format(node.name))
                for cf_key in fun_obj.cf_input.keys():
                    if fun_obj.cf_input[cf_key] is None:
                        avm_obj = AvmSearch(fun_obj, *cf_key, random_range, variable_max_iter=100, optimize_max_iter=100)
                        vec, fit = avm_obj.optimize()
                    #     print(cf_key, vec, fit)
                    # else:
                    #     print(cf_key, fun_obj.cf_input[cf_key])

                for k, v in sorted(fun_obj.cf_input.items(), key=lambda item : 2 * item[0][0] + int(not item[0][1])):
                    print('{}{} {}'.format(k[0], 'T' if k[1] else 'F', v))
                print()
                fun_obj.cfg.print_with_cf_dict_recursive(fun_obj.cf_input, '')

            