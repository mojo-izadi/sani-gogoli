from anytree import Node, RenderTree
root = Node("root", lines=["c0fe", "c0de"])
s0 = Node("sub0", parent=root, lines=["ha", "ba"])
s0b = Node("sub0B", parent=s0, lines=["1", "2", "3"])
s0a = Node("sub0A", parent=s0, lines=["a", "b"])
s1 = Node("sub1", parent=root, lines=["Z"])


for pre, fill, node in RenderTree(root):
    print("%s%s" % (pre.encode('utf-16').decode('utf-16'), node.name))