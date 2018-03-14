import constdb
import tempfile
import os.path

with tempfile.TemporaryDirectory() as temp_dir:
    file_name = os.path.join(temp_dir, 'test_file')
    with constdb.create(file_name) as db:
        db.add(-2, b'7564')
        db.add(3, b'23')
        db.add(-1, b'66')

    with constdb.read(file_name) as db:
        assert db.get(-2) == b'7564'
        assert db.get(-1) == b'66'
        assert db.get(3) == b'23'