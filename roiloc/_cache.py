import tempfile
from shutil import rmtree


def handle_cache(func):
    """Decorator to handle cache

    It fixes https://github.com/ANTsX/ANTsPy/issues/117
    """

    def cache(*args, **kwargs):
        tmp = tempfile.mkdtemp()
        output = func(*args, outprefix=tmp, **kwargs)
        rmtree(tmp, ignore_errors=True)

        return output

    return cache
