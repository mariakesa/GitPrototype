import hashlib
import os

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

if __name__ == '__main__':
    store = ObjectStore()
    blob = Blob(b'hello world\n')
    sha = store.store(blob)
    print(f'Stored blob with hash {sha}')
    raw = store.load(sha)
    print(raw)