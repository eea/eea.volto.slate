from collections import deque


def iterate_children(value):
    queue = deque(value)
    while len(queue):
        child = queue.pop()
        yield child
        if child.get("children"):
            queue.extend(child["children"] or [])
