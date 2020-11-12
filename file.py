import os


class File:
    def __init__(self, path, size):
        self.path = path
        self.size = size

        self.directory_list = self.path.split("/")
        self.name = self.directory_list.pop(-1)
        self.extension = os.path.splitext(self.name)[1]
