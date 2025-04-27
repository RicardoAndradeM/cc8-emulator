class LoadRom:
    def __init__(self, path: str):
        # TODO: implement correct ROM verification
        with open(path, 'rb') as file:
            self.data: bytes = file.read()