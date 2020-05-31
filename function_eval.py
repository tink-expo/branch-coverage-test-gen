from hook_predicate import HookPredicate

INF = 1e+4

# Calculate fitness and record evaled cfs
class FunctionEval:

    def __init__(self, fun_obj, target_branch_number, target_boolean):
        self.fun_obj = fun_obj
        self.target_branch_number = target_branch_number
        self.target_boolean = target_boolean

    def get_input_fitness(self, input_list):
        hook_pred = HookPredicate()
        exec(self.fun_obj.whole_source, locals())
        fun_call_source = self.fun_obj.fun_node.name + str(tuple(input_list))
        eval(fun_call_source)

        for cf_key in hook_pred.cf_evaled.keys():
            assert(cf_key in self.fun_obj.cf_input)
            self.fun_obj.cf_input[cf_key] = tuple(input_list)

        for cf_key in hook_pred.cf_evaled.keys():
            if cf_key == (self.target_branch_number, self.target_boolean):
                return 0

        reversed_target_path = self.fun_obj.get_target_path(
            self.target_branch_number, self.target_boolean)
        reversed_target_path.reverse()

        for approach_level in range(len(reversed_target_path)):
            path_node, path_boolean = reversed_target_path[approach_level].get_key()
            branch_distance = hook_pred.cf_evaled.get((path_node, not path_boolean))
            if branch_distance is not None:
                normalised_branch_distance = 1.0 - pow(1 + 0.001, -branch_distance)
                return normalised_branch_distance + approach_level

        return INF