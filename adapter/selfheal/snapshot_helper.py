import yaml


def load_snapshot(path: str) -> list:
    with open(path, "r") as f:
        return yaml.safe_load(f)


def find_elements_by_text(snapshot: list, text: str) -> list:
    matches = []

    def walk(node, root_parent=None, current_parent=None):
        if isinstance(node, dict):
            for k, v in node.items():
                # Set root_parent only once (highest level)
                new_root = root_parent or k

                if text.lower() in k.lower():
                    matches.append((k, new_root, current_parent))

                walk(v, new_root, k)

        elif isinstance(node, list):
            for item in node:
                walk(item, root_parent, current_parent)

        elif isinstance(node, str):
            if text.lower() in node.lower():
                matches.append((node, root_parent, current_parent))

    walk(snapshot)
    return matches
