import re 


def preproc_for_embedding (
        text :str 
) -> str: 
    """
    Pre-process a text for embedding 
    """
    text = re.sub(r"[。，、；：'?!（）\(\)〔〕]", " ", text) # remove chinese punctuation
    text = re.sub(r"\s+", " ", text) # shrink spaces  
    text = text.strip() 

    return text 