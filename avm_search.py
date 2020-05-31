import random
import function_eval
import copy

# Reference : avmf
class AvmSearch:
    def __init__(self, fun_obj, target_branch_number, target_boolean,
            random_range, search_max_iter=100, optimize_max_iter=100):
        random.seed(0)
        self.fun_num_args = fun_obj.num_args
        self.fun_eval = function_eval.FunctionEval(fun_obj, target_branch_number, target_boolean)
        self.search_max_iter = search_max_iter
        self.optimize_max_iter = optimize_max_iter
        self.random_range = random_range
    
    def _get_random_vector(self):
        return [random.randint(*self.random_range) 
            for _ in range(self.fun_num_args)]

    def _eval_input_fitness(self, vector, vector_idx, x):
        old_x = vector[vector_idx]
        vector[vector_idx] = x
        fitness = self.fun_eval.get_input_fitness(vector)
        vector[vector_idx] = old_x
        return fitness

    def _variable_search(self, vector, vector_idx):
        x = vector[vector_idx]
        fitness = self._eval_input_fitness(vector, vector_idx, x)

        if fitness.is_zero():
            return vector, fitness

        while True:
            fitness_decr = self._eval_input_fitness(vector, vector_idx, x - 1)
            fitness_incr = self._eval_input_fitness(vector, vector_idx, x + 1)

            # fitness.print_all()
            # fitness_decr.print_all()
            # fitness_incr.print_all()
            # print('-' * 100)

            if fitness <= fitness_decr and fitness <= fitness_incr:
                break

            k = 1 if fitness_decr > fitness_incr else -1
            while True:
                fitness_next = self._eval_input_fitness(vector, vector_idx, x + k)
                # print(x, k)
                # fitness.print_all()
                # fitness_next.print_all()
                # print('=' * 100)

                if fitness_next >= fitness:
                    # print(x, k)
                    # print('-' * 100)
                    break
                else:
                    x = x + k
                    k = 2 * k
                    fitness = copy.copy(fitness_next)
        # print('=' * 100)
        vector[vector_idx] = x
        return vector, fitness

    def _alternating_variable_search(self, vector):
        fitness = function_eval.INF

        for i in range(max(len(vector), self.search_max_iter)):
            vector_idx = i % len(vector)
            vector, fitness = self._variable_search(vector, vector_idx)
            if fitness.is_zero():
                break

        return vector, fitness

    def optimize(self):
        vector = None
        fitness = function_eval.INF

        for _ in range(self.optimize_max_iter):
            vector, fitness = self._alternating_variable_search(self._get_random_vector())
            if fitness.is_zero():
                break

        return vector, fitness.get_value()
        
            