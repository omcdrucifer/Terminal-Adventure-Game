# Player, Enemy and Combat could also be a tree, going to try building a tree to see if I prefer that 
# to making a JSON table for each
class CharTreeNode:
    def __init__(self, char_class):
        self.char_class = char_class
        self.attributes = []

    def add_child(self, child_node):
        self.attributes.append(child_node)

    def remove_child(self, child_node):
        self.attributes = [child for child in self.attributes if child != child_node]

    def traverse(self):
        nodes_to_visit = [self]
        while len(nodes_to_visit) > 0:
            current_node = nodes_to_visit.pop()
            nodes_to_visit += current_node.attributes


# Attach nodes to the tree in a hierarchy that declares class, level, stats
