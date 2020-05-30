import astor
import ast
import sys
from hook_predicate import HookPredicate
from fun_parse import FunParse

class FunEval:
    def __init__(self, fun_parse):
        self.fun_parse = fun_parse

    def get_input_fitness(self, target_branch_number, target_boolean, input_list):
        hook_pred = HookPredicate()
        exec(self.fun_parse.whole_source, locals())
        fun_call_source = self.fun_parse.fun_node.name + str(tuple(input_list))
        eval(fun_call_source)

        for cf_key in hook_pred.cf_evaled.keys():
            self.fun_parse.cf_input[cf_key] = tuple(input_list)

        for cf_key in hook_pred.cf_evaled.keys():
            if cf_key == (target_branch_number, target_boolean):
                return 0

        reversed_target_path = self.fun_parse.get_target_path(
            target_branch_number, target_boolean)
        reversed_target_path.reverse()

        for k, v in hook_pred.cf_evaled.items():
            print(k)
            print(v)
            print()

        for approach_level in range(len(reversed_target_path)):
            path_node, path_boolean = reversed_target_path[approach_level].get_key()
            branch_distance = hook_pred.cf_evaled.get((path_node, not path_boolean))
            if branch_distance is not None:
                normalised_branch_distance = 1.0 - pow(1 + 0.001, -branch_distance)
                return normalised_branch_distance + approach_level

        return 1e+4

    # def find_input_all_cfs(self):
    #     for cf_key in self.fun_parse.cf_input.keys():
    #         if self.fun_parse.cf_input[cf_key] is None:

if __name__ == "__main__":
    aa = astor.code_to_ast.parse_file(sys.argv[1])
    for node in aa.body:
        if isinstance(node, ast.FunctionDef) and node.name == sys.argv[2]:
            fp = FunParse(aa, node.name)
            # fp.cfg.print_recursive(0)
            print(astor.to_source(fp.whole_ast))
            fe = FunEval(fp)
            print(fe.get_input_fitness(4, True, [3]))