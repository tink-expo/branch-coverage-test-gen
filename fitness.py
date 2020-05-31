import ast
import astor
import copy
import sys
import warnings
import itertools
from typedef import FailFitnessInfo, SuccessFitnessInfo

def get_target_fun_node(whole_ast, fun_name=None):
    for node in ast.walk(whole_ast):
        if type(node) == ast.FunctionDef and (fun_name is None or node.name == fun_name):
            return node
    return None

def get_target_path(fun_node, target_brach_num, target_bool):
    class IfVisitor(ast.NodeVisitor):
        def __init__(self):
            super().__init__()
            self.if_node_count = 0
            self.path_list = []
            self.path_list_final = None

        def visit_If(self, node):
            self.if_node_count += 1
            print(self.if_node_count, ast.dump(node.test.comparators[0]))
            if (self.if_node_count <= target_brach_num):
                if (self.if_node_count == target_brach_num):
                    self.path_list_final = copy.copy(self.path_list)
                    self.path_list_final.append((node, target_bool))
                else:
                    # Ignore test node.
                    self.path_list.append((node, True))
                    for n in node.body:
                        self.visit(n)
                    self.path_list.pop()
                    self.path_list.append((node, False))
                    for n in node.orelse:
                        self.visit(n)
                    self.path_list.pop()

    visitor = IfVisitor()
    visitor.visit(fun_node)
    return visitor.path_list_final

def transform_path_nodes(fun_node, path_list):
    class InsertVisitor(ast.NodeVisitor):
        def __init__(self):
            super().__init__()
            self.path_list_idx = 0

        def pre_insert(self, ast_list, ast_list_idx, path_list, path_list_idx):
            path_node, target_bool = path_list[path_list_idx]
            approach_level = len(path_list) - 1 - path_list_idx
            assert(isinstance(path_node, ast.If))

            if isinstance(path_node.test, ast.Compare):
                pass
            elif isinstance(path_node.test, ast.Name) or isinstance(path_node.test, ast.Num):
                path_node.test = ast.Compare(
                    left=path_node.test,
                    ops=[ast.NotEq()],
                    comparators=[ast.Num(n=0)])
            else:
                warnings.warn("Unsupported predicate format detected.", Warning)
                return ast_list_idx

            l_eval_id = "l_eval_{}".format(path_list_idx)
            r_eval_id = "r_eval_{}".format(path_list_idx)
            pred_eval_id = "pred_eval_{}".format(path_list_idx)
            target_bool_id = "True" if target_bool else "False"

            ast_list.insert(ast_list_idx, ast.Assign(
                targets=[ast.Name(id=l_eval_id)],
                value=path_node.test.left
            ))
            ast_list_idx += 1

            ast_list.insert(ast_list_idx, ast.Assign(
                targets=[ast.Name(id=r_eval_id)],
                value=path_node.test.comparators[0]
            ))
            ast_list_idx += 1

            ast_list.insert(ast_list_idx, ast.Assign(
                targets=[ast.Name(id=pred_eval_id)],
                value=ast.Compare(
                    left=ast.Name(id=l_eval_id),
                    ops=[path_node.test.ops[0]],
                    comparators=[ast.Name(id=r_eval_id)])
            ))
            ast_list_idx += 1

            ast_list.insert(ast_list_idx, ast.If(
                test=ast.Compare(
                    left=ast.Name(id=pred_eval_id),
                    ops=[ast.NotEq()],
                    comparators=[ast.Name(id=target_bool_id)]),
                body=[ast.Return(
                    value=ast.Call(
                        func=ast.Name(id=FailFitnessInfo.__name__),
                        args=[
                            ast.Name(id=l_eval_id),
                            ast.Name(id=r_eval_id),
                            ast.Name(id=path_node.test.ops[0].__class__.__name__),
                            ast.Num(n=approach_level)],
                        keywords=[]))],
                orelse=([ast.Return(
                    value=ast.Call(
                        func=ast.Name(id=SuccessFitnessInfo.__name__),
                        args=[],
                        keywords=[]))] 
                    if path_list_idx == len(path_list) - 1 else [])
            ))
            ast_list_idx += 1

            assert(ast_list[ast_list_idx] is path_node)
            
            path_node.test.left = ast.Name(id=l_eval_id)
            path_node.test.comparators[0] = ast.Name(id=r_eval_id)
            return ast_list_idx

        def generic_visit(self, node):
            for _, val in ast.iter_fields(node):
                if isinstance(val, list):
                    val_idx = 0
                    while (val_idx < len(val)):
                        item = val[val_idx]
                        if isinstance(item, ast.AST):
                            if self.path_list_idx < len(path_list) and item is path_list[self.path_list_idx][0]:
                                val_idx = self.pre_insert(val, val_idx, path_list, self.path_list_idx)
                                self.path_list_idx += 1
                            self.visit(item)
                        val_idx += 1
                elif isinstance(val, ast.AST):
                    self.visit(val)

    visitor = InsertVisitor()
    visitor.visit(fun_node)


def transform_for_fitness(whole_ast, target_fun_name, target_branch, target_bool):
    new_ast = copy.deepcopy(whole_ast)
    target_fun_node = get_target_fun_node(new_ast, target_fun_name)
    assert(target_fun_node is not None)

    target_path = get_target_path(target_fun_node, target_brach, target_bool)
    transform_path_nodes(target_fun_node, target_path)
    return new_ast

    
def cover_branches(whole_ast, target_fun_node):
    num_if_nodes = 0
    for node in ast.walk(target_fun_node):
        if isinstance(node, ast.If):
            num_if_nodes += 1
    
    for target_brach, target_bool in itertools.product(range(1, num_if_nodes + 1), (True, False)):
        # TODO: Optimize here 
        # (Redundant node insertion for 2 target bools -> only single True/False is different)
        transformed_ast = transform_for_fitness
            (whole_ast, target_fun_node.name,
            target_brach, target_bool)
        print(astor.to_source(transformed_ast))  

def main(argv):
    if len(argv) <= 1:
        raise ValueError("File name argument missing.")

    file_path = argv[1]
    whole_ast = astor.code_to_ast.parse_file(file_path)
    for item in whole_ast.body:
        if isinstance(item, ast.FunctionDef):
            print(item.name)
            cover_branches(whole_ast, item)


if __name__ == "__main__":
    main(sys.argv)