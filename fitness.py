import ast
import astor
import copy
import sys

def target_fun(whole_ast, fun_name=None):
    for node in ast.walk(whole_ast):
        if type(node) == ast.FunctionDef and (fun_name is None or node.name == fun_name):
            return node
    return None

def target_branch_parent_list(fun_body, target_brach_num, target_bool):
    class IfVisitor(ast.NodeVisitor):
        def __init__(self):
            super().__init__()
            self.if_node_count = 0
            self.parent_list = []
            self.parent_list_final = None

        def visit_If(self, node):
            self.if_node_count += 1
            print(self.if_node_count, ast.dump(node.test.comparators[0]))
            if (self.if_node_count <= target_brach_num):
                if (self.if_node_count == target_brach_num):
                    self.parent_list_final = copy.copy(self.parent_list)
                    self.parent_list_final.append((node, target_bool))
                else:
                    # Ignore test node.
                    self.parent_list.append((node, True))
                    for n in node.body:
                        self.visit(n)
                    self.parent_list.pop()
                    self.parent_list.append((node, False))
                    for n in node.orelse:
                        self.visit(n)
                    self.parent_list.pop()

    visitor = IfVisitor()
    visitor.visit(fun_body)
    return visitor.parent_list_final


def main(argv):
    if len(argv) <= 1:
        raise ValueError("File name argument missing.")

    file_path = argv[1]
    whole_ast = astor.code_to_ast.parse_file(file_path)
    fun = target_fun(whole_ast, argv[2] if len(argv) > 2 else None)

    print(astor.dump_tree(fun))

    print("-" * 50)

    parent_list = target_branch_parent_list(fun, 5, True)
    for p, b in parent_list:
        print(ast.dump(p.test.comparators[0]))
        print(b)
        print()

    # if_node = fun_body[1]
    # predicate = if_node.test
    # predicate_result_id = 'predicate_result_{}'.format(1)
    # fun_body.insert(1, ast.Assign(
    #         targets=[ast.Name(id=predicate_result_id)], value=predicate))
    # if_node.test = ast.Name(id=predicate_result_id)

    # print(astor.to_source(whole_ast))


if __name__ == "__main__":
    main(sys.argv)