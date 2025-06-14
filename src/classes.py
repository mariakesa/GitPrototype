import hashlib
import os      
import time

class Blob:
    def __init__(self, content: bytes):
        self.content = content
        self.type = b'blob'

    def serialize(self) -> bytes:
        header = self.type + b' ' + str(len(self.content)).encode() + b'\0'
        return header + self.content

    def hash(self) -> str:
        return hashlib.sha1(self.serialize()).hexdigest()


class ObjectStore:
    def __init__(self, git_dir='git'):
        self.objects_dir = os.path.join(git_dir, 'objects')
        os.makedirs(self.objects_dir, exist_ok=True)

    def store(self, obj) -> str:
        obj_data = obj.serialize()
        obj_hash = hashlib.sha1(obj_data).hexdigest()
        path = os.path.join(self.objects_dir, obj_hash)
        with open(path, 'wb') as f:
            f.write(obj_data)
        return obj_hash

    def load(self, obj_hash: str) -> bytes:
        path = os.path.join(self.objects_dir, obj_hash)
        with open(path, 'rb') as f:
            return f.read()

class Commit:
    def __init__(self, tree_hash: str, parent: str = None, author: str = "Maria <maria@example.com>", message: str = ""):
        self.tree_hash = tree_hash        # hash of the tree this commit snapshots
        self.parent = parent              # hash of previous commit (can be None)
        self.author = author
        self.message = message
        self.timestamp = int(time.time()) # UNIX timestamp
        self.type = b'commit'

    def serialize(self) -> bytes:
        lines = []

        lines.append(f"tree {self.tree_hash}")
        if self.parent:
            lines.append(f"parent {self.parent}")
        lines.append(f"author {self.author} {self.timestamp} +0000")
        lines.append(f"committer {self.author} {self.timestamp} +0000")
        lines.append("")  # blank line
        lines.append(self.message)

        content = "\n".join(lines).encode()
        header = self.type + b' ' + str(len(content)).encode() + b'\0'
        return header + content

    def hash(self) -> str:
        return hashlib.sha1(self.serialize()).hexdigest()

class TreeEntry:
    def __init__(self, mode: str, obj_type: bytes, obj_hash: str, name: str):
        self.mode = mode          # File permissions, like "100644"
        self.obj_type = obj_type  # Either b'blob' or b'tree'
        self.obj_hash = obj_hash  # The hash of the blob/tree it points to
        self.name = name          # The filename or folder name

    def serialize(self) -> bytes:
        head = f"{self.mode} {self.name}".encode() + b'\0'
        return head + bytes.fromhex(self.obj_hash)

class Tree:
    def __init__(self):
        self.entries: list[TreeEntry] = []
        self.type = b'tree'   

    def add_entry(self, mode: str, obj_type: bytes, obj_hash: str, name: str):
        self.entries.append(TreeEntry(mode, obj_type, obj_hash, name))
    
    def serialize(self) -> bytes:
        content = b''.join(entry.serialize() for entry in self.entries)
        header = self.type + b' ' + str(len(content)).encode() + b'\0'
        return header + content
    
    def hash(self) -> str:
        return hashlib.sha1(self.serialize()).hexdigest()

import time

class Commit:
    def __init__(self, tree_hash: str, parent: str = None, author: str = "Maria <maria@example.com>", message: str = ""):
        self.tree_hash = tree_hash        # hash of the tree this commit snapshots
        self.parent = parent              # hash of previous commit (can be None)
        self.author = author
        self.message = message
        self.timestamp = int(time.time()) # UNIX timestamp
        self.type = b'commit'

    def serialize(self) -> bytes:
        lines = []

        lines.append(f"tree {self.tree_hash}")
        if self.parent:
            lines.append(f"parent {self.parent}")
        lines.append(f"author {self.author} {self.timestamp} +0000")
        lines.append(f"committer {self.author} {self.timestamp} +0000")
        lines.append("")  # blank line
        lines.append(self.message)

        content = "\n".join(lines).encode()
        header = self.type + b' ' + str(len(content)).encode() + b'\0'
        return header + content

    def hash(self) -> str:
        return hashlib.sha1(self.serialize()).hexdigest()

'''

if __name__ == '__main__':
    store = ObjectStore()
    blob = Blob(b'hello world\n')
    sha = store.store(blob)
    print(f'Stored blob with hash {sha}')
    raw = store.load(sha)
    print(raw)'''

if __name__ == "__main__":
    store = ObjectStore()

    # Make a blob and store it
    hello = Blob(b"hello world\n")
    hello_hash = store.store(hello)

    # Make a tree with that blob
    tree = Tree()
    tree.add_entry('100644', b'blob', hello_hash, 'hello.txt')
    tree_hash = store.store(tree)

    # Make a commit from that tree
    commit = Commit(tree_hash, author="Maria Kesa <maria@turing.ai>", message="First commit 🥳")
    commit_hash = store.store(commit)

    print(f"Stored commit with hash: {commit_hash}")
