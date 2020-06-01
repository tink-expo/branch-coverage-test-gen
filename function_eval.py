from hook_predicate import HookPredicate

INF = 1e+4

class Fitness:
    def __init__(self, branch_distance, approach_level):
        self.branch_distance = branch_distance
        self.approach_level = approach_level

    def is_zero(self):
        return self.branch_distance == 0 and self.approach_level == 0

    def __eq__(self, other):
        return (self.branch_distance == other.branch_distance and 
            self.approach_level == other.approach_level)

    def __lt__(self, other):
        if self.approach_level != other.approach_level:
            return self.approach_level < other.approach_level
        else:
            return self.branch_distance < other.branch_distance

    def __gt__(self, other):
        if self.approach_level != other.approach_level:
            return self.approach_level > other.approach_level
        else:
            return self.branch_distance > other.branch_distance

    def __le__(self, other):
        return self.__eq__(other) or self.__lt__(other)

    def __ge__(self, other):
        return self.__eq__(other) or self.__gt__(other)

    def get_value(self):
        return 1.0 - pow(1.001, -self.branch_distance) + self.approach_level

    def print_all(self):
        print(self.branch_distance, self.approach_level, self.get_value())


# Calculate fitness and record evaled cfs
# NOTE: This mutates fun_obj (Modifies fun_obj.cf_input)
class FunctionEval:

    def __init__(self, fun_obj, target_branch_number, target_boolean):
        self.fun_obj = fun_obj
        self.target_branch_number = target_branch_number
        self.target_boolean = target_boolean

        self.reversed_target_path = self.fun_obj.get_target_path(
                self.target_branch_number, self.target_boolean)
        self.reversed_target_path.reverse()

    def get_input_fitness(self, input_list):
        hook_pred = HookPredicate()
        try:
            exec(self.fun_obj.whole_source, locals())
            fun_call_source = self.fun_obj.fun_node.name + str(tuple(input_list))
            eval(fun_call_source)
        except:
            # Exception thrown during executing user code should be catched.
            pass

        for cf_key in hook_pred.cf_evaled.keys():
            assert(cf_key in self.fun_obj.cf_input)
            self.fun_obj.cf_input[cf_key] = tuple(input_list)

        for cf_key in hook_pred.cf_evaled.keys():
            if cf_key == (self.target_branch_number, self.target_boolean):
                return Fitness(0, 0)

        for approach_level in range(len(self.reversed_target_path)):
            path_node, path_boolean = self.reversed_target_path[approach_level].get_key()
            branch_distance = hook_pred.cf_evaled.get((path_node, not path_boolean))
            if branch_distance is not None:
                return Fitness(branch_distance, approach_level)

        return Fitness(0, INF)