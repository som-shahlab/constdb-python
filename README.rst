============
ConstDB
============

ConstDB is a very simple and fast read-only embedded key-value database. Keys consist of 64-bit integers and values consist of arbitrary byte strings.

Sample
===============

.. code-block:: python

  import constdb

  with constdb.create('db_name') as db:
      db.add(-2, b'7564')
      db.add(3, b'23')
      db.add(-1, b'66')

  with constdb.read('db_name') as db:
      assert db.get(-2) == b'7564'
      assert db.get(-1) == b'66'
      assert db.get(3) == b'23'

Documenation
===============

ConstDB contains only two functions: ``create`` and ``read``.

``create(filename)`` allows you to create a new ConstDB database. 
It takes a filename and returns a ConstDBWriter. A ConstDBWriter has two methods: 

- ``add(key, value)``: Adds a key-value pair to the database. The key must be a 64 bit integer. The value must be a byte string.
- ``close()``: Finalize and close the database.
  
``read(filename)`` allows you to read an existing ConstDB database.
It takes a filename and returns a ConstDBReader. A ConstDBReader has two methods: 

- ``get(key)``: Get a value from the database. The key must be a 64 bit integer. Returns the value if the key is in the database. Returns None if the key is not found.
- ``close()``: Finalize and close the database.
  
Requirements
===============

The only requirement for ConstDB is Python 3.
