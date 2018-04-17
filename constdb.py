import struct
import mmap
import os

def create(name):
    return Writer(name)

def read(name, keys_to_read=None, mmap=True):
    if mmap:
        return MmapReader(name, keys_to_read=keys_to_read)
    else:
        return FseekReader(name, keys_to_read=keys_to_read)

table_offset_format = '<q'
table_entry_format = '<iqqq'

INT_KEY_TYPE = 0
STR_KEY_TYPE = 1

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
        self.offsets[key] = (self.current_offset, self.current_offset + len(value))
        self.current_offset += len(value)

    def close(self):
        location_of_offsets = self.current_offset

        for key, (start, end) in self.offsets.items():
            if type(key) is int:
                self.file.write(struct.pack(table_entry_format, INT_KEY_TYPE, start, end, key))
            elif type(key) is str:
                encoded_key = key.encode('utf-8')
                self.file.write(struct.pack(table_entry_format, STR_KEY_TYPE, start, end, len(encoded_key)))
                self.file.write(encoded_key)

        self.file.write(struct.pack(table_offset_format, location_of_offsets))

        self.file.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

class FseekReader:
    def __init__(self, name, keys_to_read=None):
        self.file = open(name, 'rb')

        size_of_table_offset = struct.calcsize(table_offset_format)
        size_of_table_entry = struct.calcsize(table_entry_format)

        self.file.seek(-size_of_table_offset, os.SEEK_END)

        location_of_offset = self.file.tell()

        table_offset, = struct.unpack(table_offset_format, self.file.read(size_of_table_offset))

        self.offsets = {}

        self.file.seek(table_offset)

        current_location = table_offset
        while current_location < location_of_offset:
            key_type, begin, end, key_val = struct.unpack(table_entry_format, self.file.read(size_of_table_entry))
            current_location += size_of_table_entry

            if key_type == INT_KEY_TYPE:
                key = key_val
            elif key_type == STR_KEY_TYPE:
                key = self.file.read(key_val).decode('utf-8')
                current_location += key_val

            if keys_to_read is not None and key not in keys_to_read:
                continue

            self.offsets[key] = (begin, end)

        all_items = list(self.offsets.items())
        all_items.sort(key=lambda a:a[1][0])

        self.computed_keys = [a[0] for a in all_items]

    def get(self, key):
        if key not in self.offsets:
            return None
        else:
            begin, end =  self.offsets[key]

            self.file.seek(begin)

            return self.file.read(end - begin)

    def keys(self):
        return self.computed_keys

    def close(self):
        self.file.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

class MmapReader:
    def __init__(self, name, keys_to_read=None):
        with open(name, 'rb') as file:
            self.map = mmap.mmap(file.fileno(), 0, prot=mmap.PROT_READ)

        size_of_table_offset = struct.calcsize(table_offset_format)
        size_of_table_entry = struct.calcsize(table_entry_format)

        location_of_offset = len(self.map) - size_of_table_offset

        table_offset, = struct.unpack(table_offset_format, self.map[location_of_offset:])

        self.offsets = {}

        current_location = table_offset
        while current_location < location_of_offset:
            key_type, begin, end, key_val = struct.unpack(table_entry_format, self.map[current_location:current_location+size_of_table_entry])
            current_location += size_of_table_entry

            if key_type == INT_KEY_TYPE:
                key = key_val
            elif key_type == STR_KEY_TYPE:
                key = self.map[current_location:current_location+key_val].decode('utf-8')
                current_location += key_val

            if keys_to_read is not None and key not in keys_to_read:
                continue

            self.offsets[key] = (begin, end)

        all_items = list(self.offsets.items())
        all_items.sort(key=lambda a:a[1][0])

        self.computed_keys = [a[0] for a in all_items]

    def get(self, key):
        if key not in self.offsets:
            return None
        else:
            begin, end =  self.offsets[key]

            return self.map[begin:end]

    def keys(self):
        return self.computed_keys

    def close(self):
        self.map.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()