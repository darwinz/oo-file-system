SEPARATOR = '\\'


def file_path(parent_path: str, name: str):
    return f'{parent_path}{SEPARATOR}{name}'


def recursive_size_update(node):
    if hasattr(node, 'parent'):
        node.parent.set_size()
        recursive_size_update(node.parent)
