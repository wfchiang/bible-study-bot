from pydantic import BaseModel, Field
from typing import Dict, Union, List 


METADATA_TYPE = Dict[
    str, Union[str, int, float, List[str], List[int], List[float]]]

OLD_TESTAMENT = [
    "genesis", 
    "exodus", 
    "leviticus", 
    "numbers", 
    "deuteronomy", 
    "joshua", 
    "judges", 
    "ruth", 
    "1samuel", 
    "2samuel", 
    "1kings", 
    "2kings", 
    "1chronicles", 
    "2chronicles", 
    "ezra", 
    "nehemiah", 
    "esther", 
    "job", 
    "psalms", 
    "proverbs", 
    "ecclesiastes", 
    "songs", 
    "isaiah", 
    "jeremiah", 
    "lamentations", 
    "ezekiel", 
    "daniel", 
    "hosea", 
    "joel", 
    "amos", 
    "obadiah", 
    "jonah", 
    "micah", 
    "nahum", 
    "habakkuk", 
    "zephaniah", 
    "haggai", 
    "zechariah", 
    "malachi"
]
assert(len(OLD_TESTAMENT) == 39), "Invalid old testament listing..."

NEW_TESTAMENT = [
    "matthew", 
    "mark", 
    "luke", 
    "john", 
    "acts", 
    "romans", 
    "1corinthians", 
    "2corinthians", 
    "galatians", 
    "ephesians", 
    "philippians", 
    "colossians", 
    "1thessalonians", 
    "2thessalonians", 
    "1timothy", 
    "2timothy", 
    "titus", 
    "philemon", 
    "hebrews", 
    "james", 
    "1peter", 
    "2peter", 
    "1john", 
    "2john", 
    "3john", 
    "jude", 
    "revelation"
]
assert(len(NEW_TESTAMENT) == 27), "Invalid new testament listing..."

BIBLE_BOOKS = OLD_TESTAMENT + NEW_TESTAMENT

BIBLE_BOOKS_CUVS = {
    "genesis": "创世纪", 
    "exodus": "出埃及记", 
    "leviticus": "利未记", 
    "numbers": "民数记", 
    "deuteronomy": "申命记", 
    "joshua": "约书亚记", 
    "judges": "士师记", 
    "ruth": "路得记", 
    "1samuel": "撒母耳记上", 
    "2samuel": "撒母耳记下", 
    "1kings": "列王记上", 
    "2kings": "列王记下", 
    "1chronicles": "历代志上", 
    "2chronicles": "历代志下", 
    "ezra": "以斯拉记", 
    "nehemiah": "尼希米记", 
    "esther": "以斯帖记", 
    "job": "约伯记", 
    "psalms": "诗篇", 
    "proverbs": "箴言", 
    "ecclesiastes": "传道书", 
    "songs": "雅歌", 
    "isaiah": "以赛亚书", 
    "jeremiah": "耶利米书", 
    "lamentations": "耶利米哀歌", 
    "ezekiel": "以西结书", 
    "daniel": "但以理书", 
    "hosea": "何西阿书", 
    "joel": "约珥书", 
    "amos": "阿摩司书", 
    "obadiah": "俄巴底亚书", 
    "jonah": "约拿书", 
    "micah": "弥迦书", 
    "nahum": "那鸿书", 
    "habakkuk": "哈巴谷书", 
    "zephaniah": "西番雅书", 
    "haggai": "哈该书", 
    "zechariah": "撒迦利亚书", 
    "malachi": "玛拉基书", 
    "matthew": "马太福音", 
    "mark": "马可福音", 
    "luke": "路加福音", 
    "john": "约翰福音", 
    "acts": "使徒行传", 
    "romans": "罗马书", 
    "1corinthians": "哥林多前书", 
    "2corinthians": "哥林多后书", 
    "galatians": "加拉太书", 
    "ephesians": "以弗所书", 
    "philippians": "腓立比书", 
    "colossians": "歌罗西书", 
    "1thessalonians": "帖撒罗尼迦前书", 
    "2thessalonians": "帖撒罗尼迦后书", 
    "1timothy": "提摩太前书", 
    "2timothy": "提摩太后书", 
    "titus": "提多书", 
    "philemon": "腓利门书", 
    "hebrews": "希伯来书", 
    "james": "雅各书", 
    "1peter": "彼得前书", 
    "2peter": "彼得后书", 
    "1john": "约翰一书", 
    "2john": "约翰二书", 
    "3john": "约翰三书", 
    "jude": "犹大书", 
    "revelation": "启示录"
}
for ot in OLD_TESTAMENT: 
    assert(ot in BIBLE_BOOKS_CUVS), f"{ot} is not in CUVS"
assert(all([ot in BIBLE_BOOKS_CUVS for ot in OLD_TESTAMENT]))
assert(all([nt in BIBLE_BOOKS_CUVS for nt in NEW_TESTAMENT]))


class TextChunk(BaseModel): 
    text :str 
    metadata :METADATA_TYPE = Field(default_factory=dict)


class BibleVerse(TextChunk):
    chapter: int
    verse: int


class BibleBook(BaseModel):
    verses: List[BibleVerse]
    book: str

    @property
    def text(self) -> str:
        return " ".join(v.text for v in self.verses)
    

class Bible(BaseModel):
    books: List[BibleBook]
    version: str
