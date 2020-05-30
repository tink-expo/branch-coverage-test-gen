import ast

K = 1.0

class HookPredicate:
    def __init__(self):
        self.cf_evaled = {}

    def _branch_distance(self, op_name, l_eval, r_eval):
        # Assert condition is false

        if op_name == ast.Eq.__name__:
            return abs(l_eval - r_eval)

        elif op_name == ast.NotEq.__name__:
            return K

        elif op_name == ast.Gt.__name__ or op_name == ast.GtE.__name__:
            return (r_eval - l_eval) + K

        elif op_name == ast.Lt.__name__ or op_name == ast.LtE.__name__:
            return (l_eval - r_eval) + K

        else:
            assert(False)

    def eval_predicate(self, branch_number, op_name, lhs, rhs):
        l_eval = lhs
        r_eval = rhs

        if op_name == ast.Eq.__name__:
            result = l_eval == r_eval
            branch_distance = self._branch_distance(
                ast.NotEq.__name__ if result else ast.Eq.__name__,
                l_eval, r_eval)

        elif op_name == ast.NotEq.__name__:
            result = l_eval != r_eval
            branch_distance = self._branch_distance(
                ast.Eq.__name__ if result else ast.NotEq.__name__,
                l_eval, r_eval)

        elif op_name == ast.Gt.__name__:
            result = l_eval > r_eval
            branch_distance = self._branch_distance(
                ast.LtE.__name__ if result else ast.Gt.__name__,
                l_eval, r_eval)

        elif op_name == ast.GtE.__name__:
            result = l_eval >= r_eval
            branch_distance = self._branch_distance(
                ast.Lt.__name__ if result else ast.GtE.__name__,
                l_eval, r_eval)

        elif op_name == ast.Lt.__name__:
            result = l_eval < r_eval
            branch_distance = self._branch_distance(
                ast.GtE.__name__ if result else ast.Lt.__name__,
                l_eval, r_eval)

        elif op_name == ast.LtE.__name__:
            result = l_eval <= r_eval
            branch_distance = self._branch_distance(
                ast.Gt.__name__ if result else ast.LtE.__name__,
                l_eval, r_eval)

        else:
            raise ValueError("{} op not supproted.".op_name)

        self.cf_evaled[(branch_number, result)] = branch_distance
        return result


