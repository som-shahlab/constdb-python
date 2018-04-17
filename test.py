import constdb
import tempfile
import os.path

def test_mmap():
    with tempfile.TemporaryDirectory() as temp_dir:
        file_name = os.path.join(temp_dir, 'test_file')
        with constdb.create(file_name) as db:
            db.add(-2, b'7564')
            db.add(3, b'23')
            db.add(-1, b'66')
            db.add('Hello world', b'67')
            db.add(6, b'26')

        with constdb.read(file_name) as db:
            assert db.get(-2) == b'7564'
            assert db.get(-1) == b'66'
            assert db.get(3) == b'23'
            assert db.get('Hello world') ==  b'67'
            assert db.get(6) == b'26'

            assert db.keys() == [-2, 3, -1, 'Hello world', 6]

        with constdb.read(file_name, keys_to_read={'Hello world', 3}) as db:
            assert db.get(-2) is None
            assert db.get(-1) is None
            assert db.get(3) == b'23'
            assert db.get('Hello world') ==  b'67'
            assert db.get(6) is None

            assert db.keys() == [3, 'Hello world']


def test_fseek():
    with tempfile.TemporaryDirectory() as temp_dir:
        file_name = os.path.join(temp_dir, 'test_file')
        with constdb.create(file_name) as db:
            db.add(-2, b'7564')
            db.add(3, b'23')
            db.add(-1, b'66')
            db.add('Hello world', b'67')
            db.add(6, b'26')

        with constdb.read(file_name, mmap=False) as db:
            assert db.get(-2) == b'7564'
            assert db.get(-1) == b'66'
            assert db.get(3) == b'23'
            assert db.get('Hello world') ==  b'67'
            assert db.get(6) == b'26'

            assert db.keys() == [-2, 3, -1, 'Hello world', 6]

        with constdb.read(file_name, keys_to_read={'Hello world', 3}, mmap=False) as db:
            assert db.get(-2) is None
            assert db.get(-1) is None
            assert db.get(3) == b'23'
            assert db.get('Hello world') ==  b'67'
            assert db.get(6) is None

            assert db.keys() == [3, 'Hello world']