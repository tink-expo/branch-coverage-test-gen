import ast
import astor

import sys

class CFNode:
    def __init__(self, brach_number):
        self.brach_number = brach_number
        self.true_children = []
        self.false_children = []

        self.phase = True

    def add_child(self, node):
        if self.phase:
            self.true_children.append(node)
        else:
            self.false_children.append(node)

    def print_tree(self, indent):
        print('  ' * indent + str(self.brach_number))
        for n in self.true_children:
            n.print_tree(indent + 1)
        for n in self.false_children:
            n.print_tree(indent + 1)
        

class CodeInjectionTreeWalk(astor.TreeWalk):
    def __init__(self):
        astor.TreeWalk.__init__(self)

        self.branch_number = 0
        self.cfg = CFNode(self.branch_number)
        self.cfg_stack = [self.cfg]

    def _code_inject(self, node, branch_number):
        op_name = ''
        lhs = ''
        rhs = ''

        if not hasattr(node, 'left') or not hasattr(node, 'comparators'):
            op_name = ast.Eq.__name__
            lhs = 'True'
            rhs = astor.to_source(node).rstrip()

        else:
            op_name = type(node.ops[0]).__name__
            lhs = astor.to_source(node.left).rstrip()
            rhs = astor.to_source(node.comparators[0]).rstrip()

        return ast.parse(
            'hook.test_eval({}, {}, {}, {})'.format(
                branch_number, op_name, lhs, rhs), 
            '', 'eval').body

    def _pre_Conditional(self):
        self.branch_number += 1

        self.cur_node.test = self._code_inject(self.cur_node.test, self.branch_number)

        assert(len(self.cfg_stack) > 0)
        new_cfg_node = CFNode(self.branch_number)
        self.cfg_stack[-1].add_child(new_cfg_node)
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
        if isinstance(self.parent, ast.If):
            assert(len(self.cfg_stack) > 0)
            self.cfg_stack[-1].phase = False

    def post_orelse_name(self):
        if isinstance(self.parent, ast.If):
            assert(len(self.cfg_stack) > 0 and self.cfg_stack[-1].phase == False)
            self.cfg_stack[-1].phase = True

if __name__ == "__main__":
    aa = astor.code_to_ast.parse_file(sys.argv[1])
    for node in aa.body:
        if isinstance(node, ast.FunctionDef) and node.name == sys.argv[2]:
            cw = CodeInjectionTreeWalk()
            cw.walk(node)
            print(astor.to_source(aa))
            cw.cfg.print_tree(0)
    



        