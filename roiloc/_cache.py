import logging
import tempfile
from shutil import rmtree

log = logging.getLogger(__name__)


def handle_cache(func):
    """Decorator to handle cache

    It fixes https://github.com/ANTsX/ANTsPy/issues/117
    """

    def cache(*args, **kwargs):
        """Cache wrapper"""

        cache_dir = tempfile.mkdtemp() + "/"
        log.debug(f"Cache dir: {cache_dir}")
        kwargs["outprefix"] = cache_dir

        try:
            return func(*args, **kwargs)
        finally:
            rmtree(cache_dir)

    return cache
