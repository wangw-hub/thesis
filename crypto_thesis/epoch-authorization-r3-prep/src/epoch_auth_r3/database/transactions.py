from contextlib import contextmanager


@contextmanager
def transaction(connection):
    with connection.transaction():
        yield connection
