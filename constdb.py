import struct
import mmap

def create(name):
    return Writer(name)

def read(name):
    return Reader(name)

table_offset_format = '<q'
table_entry_format = '<qqq'

class Writer:
    def __init__(self, name):
        self.file = open(name, 'wb')
        self.current_offset = 0
        self.offsets = {}

    def add(self, key, value):
        self.offsets[key] = (self.current_offset, self.current_offset + len(value))
        self.file.write(value)
        self.current_offset += len(value)

    def close(self):
        location_of_offsets = self.current_offset

        for key, (begin, end) in self.offsets.items():
            self.file.write(struct.pack(table_entry_format, key, begin, end))

        self.file.write(struct.pack(table_offset_format, location_of_offsets))

        self.file.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

class Reader:
    def __init__(self, name):
        with open(name, 'rb') as file:
            self.map = mmap.mmap(file.fileno(), 0, prot=mmap.PROT_READ)

        size_of_table_offset = struct.calcsize(table_offset_format)
        size_of_table_entry = struct.calcsize(table_entry_format)

        table_offset, = struct.unpack(table_offset_format, self.map[-size_of_table_offset:])

        num_entries = (len(self.map) - size_of_table_offset - table_offset) // size_of_table_entry

        self.offsets = {}

        for i in range(num_entries):
            key, begin, end = struct.unpack(table_entry_format, self.map[table_offset + i*size_of_table_entry: table_offset + (i+1)*size_of_table_entry])
            self.offsets[key] = (begin, end)

    def get(self, key):
        if key not in self.offsets:
            return None
        else:
            begin, end =  self.offsets[key]

            return self.map[begin:end]

    def close(self):
        self.map.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()