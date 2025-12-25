import logging
from pathlib import Path
import sys
import yaml

import click


PROJECT_ROOT = Path(__file__).parents[1].resolve()
sys.path.insert(0, str(PROJECT_ROOT / "py"))
from config import config
from data.definitions import Bible
from data.loaders import load_bible_from_dir
from data.splitters import split_bible_book
from db.vector_store import add_text_chunk, create_collection_if_not_exists

logger = logging.getLogger(__name__)
logging.getLogger("httpx").setLevel(logging.ERROR)
logging.getLogger("vector_store").setLevel(logging.ERROR)


@click.command()
def main():
    # Create the missed collection
    create_collection_if_not_exists()

    # Load Bible versions
    for bible_ver_dir in config["data"]["bible_versions"]:
        bible_ver_path = Path(bible_ver_dir)
        assert bible_ver_path.is_dir()

        logger.info("Loading a Bible version from %s", bible_ver_dir)
        bible_ver = load_bible_from_dir(bible_ver_path)
        assert isinstance(bible_ver, Bible)

        for bible_book in bible_ver.books:
            logging.info("-- Processing the book of %s", bible_book.book)
            book_chunks = split_bible_book(bible_book)
            for b_chunk in book_chunks:
                add_text_chunk(b_chunk)


if __name__ == "__main__":
    main()
