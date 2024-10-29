import os 
import yaml 
from pathlib import Path 
from typing import List, Union
from .definitions import BibleBook, BIBLE_BOOKS


def load_bible_book_from_file (
        bible_book_file :Union[str, Path], 
        encoding :str = "utf-8"
) -> BibleBook: 
    """
    Load a BibleBook object from a YAML file
    """
    # check the parameter 
    if (not isinstance(bible_book_file, Path)): 
        bible_book_file = Path(bible_book_file)
    assert(bible_book_file.is_file()), f"Bible file does not exist: {bible_book_file}"

    with open(bible_book_file, "r", encoding=encoding) as f: 
        return BibleBook(**yaml.safe_load(f))


def load_bible_from_dir (
        bible_directory :Union[str, Path]
) -> List[BibleBook]: 
    """
    Load a Bible, a list of bible books, from a directory
    """
    # Check the parameters 
    if (not isinstance(bible_directory, Path)): 
        bible_directory = Path(bible_directory)
    assert(bible_directory.is_dir()), f"Bible directory does not exist: {bible_directory}"

    # Load the bible books from the directory 
    bible_books = [] 
    for bible_book_file in os.listdir(bible_directory.as_posix()): 
        bible_books.append(load_bible_book_from_file(bible_book_file)) 

    # Sort the bible books
    for bb in bible_books: 
        # Validate that every book is a valid book 
        if (bb.metadata["book"] not in BIBLE_BOOKS): 
            assert(False), f"Invalid bible book: {bb.metadata['book']}"

    bible_books = sorted(
        bible_books, 
        key=lambda bb: BIBLE_BOOKS.index(bb.metadata["book"])
    )

    # Return 
    return bible_books


def load_verse_context (
        bible_book :BibleBook, 
        chapter :int, 
        verse :int, 
        context_scope :str, # "book", "chapter", or "verse"
        n_prev_context_verses :int = 2, 
        n_next_context_verses :int = 2
) -> str: 
    """
    Given a BibleBook object, bible_book, loads a string as the "context" of the verse. 
    Here is how the context being generated: 
    1. Load n_prev_context_verses verses before the targeted verse (chapter, verse), the verse itself, and n_next_context_verses after the targeted verse. 
    2. Chop the verses loaded from the previous step by context_scope. If context_scope is "book", verses of the same book of the targeted verse will be include. Similarly, if context_scope is "chapter", verses of the same chapter will be included. If context_scope is "verse", the targeted verse itself is included.
    """
    # Check parameters 
    assert(n_prev_context_verses >= 0)
    assert(n_next_context_verses >= 0)

    # Located the targeted verse 
    i_targeted_verse = 0 
    while (i_targeted_verse < len(bible_book.verses)): 
        targeted_verse = bible_book.verses[i_targeted_verse]
        if (targeted_verse.metadata["chapter"] == chapter and targeted_verse.metadata["verse"] == verse): 
            break # the targeted verse located 
        i_targeted_verse += 1

    assert(i_targeted_verse < len(bible_book.verses)), f"The targeted verse {bible_book.metadata['book']}{chapter}:{verse} not found"

    # Load the surrounding verses 
    i_from = max(0, i_targeted_verse - n_prev_context_verses) 
    i_to = min(len(bible_book.verses), i_targeted_verse + 1 + n_next_context_verses)

    context_verses = bible_book.verses[i_from : i_to]

    # chop the verses based on context_scope 
    if (context_scope == "book"): 
        pass 

    elif (context_scope == "chapter"): 
        context_verses = list(filter(
            lambda cv: cv.metadata["chapter"] == chapter
        ))

    elif (context_scope == "verse"): 
        context_verses = bible_book.verses[i_targeted_verse:i_targeted_verse+1]

    else: 
        assert(False), f"Invalid {context_scope = }"

    # return 
    return " ".join(list(map(
        lambda cv: cv.text, 
        context_verses 
    )))
