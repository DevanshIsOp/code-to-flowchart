import ast
from graphviz import Digraph

class FlowchartConverter(ast.NodeVisitor):
    def __init__(self):
        self.graph = Digraph('flowchart', format='png')
        self.node_id = 0
        self.last_node = None

    def new_node(self, label):
        self.node_id += 1
        node_name = f'node{self.node_id}'
        self.graph.node(node_name, label)
        return node_name

    def visit_Module(self, node):
        start = self.new_node('Start')
        self.last_node = start

        for stmt in node.body:
            self.visit(stmt)
        end = self.new_node('End')
        self.graph.edge(self.last_node, end)

    def visit_Expr(self, node):
        code = ast.unparse(node)
        node_name = self.new_node(code)
        self.graph.edge(self.last_node, node_name)
        self.last_node = node_name

    def visit_Assign(self, node):
        code = ast.unparse(node)
        node_name = self.new_node(code)
        self.graph.edge(self.last_node, node_name)
        self.last_node = node_name

    def visit_If(self, node):
        test = ast.unparse(node.test)
        cond_node = self.new_node(f'if {test}?')

        self.graph.edge(self.last_node, cond_node)

        # Visit body (if true)
        self.last_node = cond_node
        for stmt in node.body:
            self.visit(stmt)
        true_end = self.last_node

        # Visit orelse (if false)
        self.last_node = cond_node
        if node.orelse:
            for stmt in node.orelse:
                self.visit(stmt)
            false_end = self.last_node
        else:
            false_end = cond_node

        # Create a dummy join node
        join_node = self.new_node('')

        self.graph.edge(true_end, join_node)
        if false_end != cond_node:
            self.graph.edge(false_end, join_node)
        else:
            self.graph.edge(cond_node, join_node, label='False')

        self.last_node = join_node

    def visit_For(self, node):
        target = ast.unparse(node.target)
        iter_ = ast.unparse(node.iter)
        loop_node = self.new_node(f'for {target} in {iter_}?')
        self.graph.edge(self.last_node, loop_node)

        self.last_node = loop_node
        for stmt in node.body:
            self.visit(stmt)
        self.graph.edge(self.last_node, loop_node)

        # Continue after loop
        after_loop = self.new_node('')
        self.graph.edge(loop_node, after_loop, label='False')
        self.last_node = after_loop

    def visit_While(self, node):
        test = ast.unparse(node.test)
        loop_node = self.new_node(f'while {test}?')
        self.graph.edge(self.last_node, loop_node)

        self.last_node = loop_node
        for stmt in node.body:
            self.visit(stmt)
        self.graph.edge(self.last_node, loop_node)

        after_loop = self.new_node('')
        self.graph.edge(loop_node, after_loop, label='False')
        self.last_node = after_loop

def generate_flowchart(source_code, output_file='flowchart'):
    tree = ast.parse(source_code)
    converter = FlowchartConverter()
    converter.visit(tree)
    converter.graph.render(output_file, view=True)

if __name__ == "__main__":
    sample_code = '''
x = 10
if x > 5:
    print("Greater than 5")
else:
    print("Less or equal to 5")

for i in range(3):
    print(i)
    '''
    generate_flowchart(sample_code)
