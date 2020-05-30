import ast
import astor
import copy
import sys

class CFNode:
    def __init__(self, branch_number, boolean):
        self.branch_number = branch_number
        self.boolean = boolean
        self.children = []

    def get_key(self):
        return (self.branch_number, self.boolean)

    # Except root
    def print_recursive(self, indent):
        for child in self.children:
            print('  ' * indent + str(child.get_key()))
            child.print_recursive(indent + 1)

    # Except root
    def store_recursive(self, cf_dict):
        for child in self.children:
            cf_dict[child.get_key()] = None
            child.store_recursive(cf_dict)

class CFPathFind:
    def _find(self, node, target_branch_number, target_boolean):
        if self.complete:
            return

        self.path.append(node)
        if (node.branch_number, node.boolean) == (target_branch_number, target_boolean):
            self.complete = True
        else:
            for child in node.children:
                self._find(child, target_branch_number, target_boolean)

            if not self.complete:
                self.path.pop()


    def find(self, root, target_branch_number, target_boolean):
        self.complete = False
        self.path = []
        self._find(root, target_branch_number, target_boolean)
        return self.path[1:] if self.complete else None

class CodeInjectionTreeWalk(astor.TreeWalk):
    def __init__(self):
        astor.TreeWalk.__init__(self)

        self.branch_number = 0
        self.cfg = CFNode(self.branch_number, True)
        self.cfg_stack = [self.cfg]

    def _code_inject(self, node, branch_number):
        if not hasattr(node, 'left') or not hasattr(node, 'comparators'):
            op_name = ast.Eq.__name__
            lhs = 'True'
            rhs = 'bool({})'.format(astor.to_source(node).rstrip())

        else:
            op_name = type(node.ops[0]).__name__
            lhs = astor.to_source(node.left).rstrip()
            rhs = astor.to_source(node.comparators[0]).rstrip()

        return ast.parse(
            "hook_pred.eval_predicate({}, '{}', {}, {})".format(
                branch_number, op_name, lhs, rhs), 
            '', 'eval').body

    def _pre_Conditional(self):
        self.branch_number += 1

        self.cur_node.test = self._code_inject(self.cur_node.test, self.branch_number)

        assert(len(self.cfg_stack) > 0)
        new_cfg_node = CFNode(self.branch_number, True)
        self.cfg_stack[-1].children.append(new_cfg_node)

        self.cfg_stack.append(new_cfg_node)

    def _post_Conditional(self):
        assert(len(self.cfg_stack) > 0)
        self.cfg_stack.pop()

    def pre_If(self):
        self._pre_Conditional()

    def pre_While(self):
        self._pre_Conditional()

    def post_If(self):
        self._post_Conditional()

    def post_While(self):
        self._post_Conditional()


    def pre_orelse_name(self):
        if isinstance(self.parent, ast.If) and len(self.cur_node) > 0:
            assert(len(self.cfg_stack) > 1)
            new_cfg_node = CFNode(self.cfg_stack[-1].branch_number, False)

            self.cfg_stack.pop()
            self.cfg_stack[-1].children.append(new_cfg_node)

            self.cfg_stack.append(new_cfg_node)


class FunParse:
    def __init__(self, original_ast, target_fun_name):
        self.whole_ast = copy.deepcopy(original_ast)

        self.fun_node = None
        for node in ast.walk(self.whole_ast):
            if isinstance(node, ast.FunctionDef) and node.name == target_fun_name:
                self.fun_node = node
                break
        if self.fun_node is None:
            raise ValueError("function {} is undefined.".format(target_fun_name))

        code_injection_walk = CodeInjectionTreeWalk()
        code_injection_walk.walk(self.fun_node)
        self.cfg = code_injection_walk.cfg
        
        self.cf_input = {}
        self.cfg.store_recursive(self.cf_input)

        self.whole_source = compile(self.whole_ast, '', 'exec')

    def get_target_path(self, target_branch_number, target_boolean):
        return CFPathFind().find(self.cfg, target_branch_number, target_boolean)



if __name__ == "__main__":
    aa = astor.code_to_ast.parse_file(sys.argv[1])
    for node in aa.body:
        if isinstance(node, ast.FunctionDef) and node.name == sys.argv[2]:
            fp = FunParse(aa, node.name)
            print(astor.to_source(fp.whole_ast))
            fp.cfg.print_recursive(0)
            for n in fp.cf_input:
                print(n)
            # for n in fp.get_target_path(5, True):
            #     print(n.get_key())
    



        