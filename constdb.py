import struct
import mmap

def create(name):
    return Writer(name)

def read(name):
    return Reader(name)

table_offset_format = '<q'
table_entry_format = '<iqq'

INT_KEY_TYPE = 0
STR_KEY_TYPE = 1
BYTES_KEY_TYPE = 2

class Writer:
    def __init__(self, name):
        self.file = open(name, 'wb')
        self.current_offset = 0
        self.offsets = {}

    def add(self, key, value):
        if type(key) is not int and type(key) is not str:
            raise ValueError('The key must be an integer or string')

        if key in self.offsets:
            raise ValueError('You cannot store duplicate keys')

        self.file.write(value)
        self.current_offset += len(value)
        self.offsets[key] = self.current_offset

    def close(self):
        location_of_offsets = self.current_offset

        for key, offset in self.offsets.items():
            if type(key) is int:
                self.file.write(struct.pack(table_entry_format, INT_KEY_TYPE, offset, key))
            elif type(key) is str:
                encoded_key = key.encode('utf-8')
                self.file.write(struct.pack(table_entry_format, STR_KEY_TYPE, offset, len(encoded_key)))
                self.file.write(encoded_key)

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

        current_location = table_offset
        last_offset = 0
        for i in range(num_entries):
            key_type, offset, key_val = struct.unpack(table_entry_format, self.map[current_location:current_location+size_of_table_entry])
            current_location += size_of_table_entry

            if key_type == INT_KEY_TYPE:
                key = key_val
            elif key_type == STR_KEY_TYPE:
                key = self.map[current_location:current_location+key_val].decode('utf-8')
                current_location += key_val

            self.offsets[key] = (last_offset, offset)
            last_offset = offset

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