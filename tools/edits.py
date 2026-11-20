# Wording changes made on purpose, on top of the Word file. build.py applies
# them to the content and check.py to the document it compares against, so
# the check still proves nothing else changed. Keyed by paragraph number
# (convert.py prints them): [(old text, new text), ...]. If the Word file
# changes and a paragraph moves, the assert below says which edit no longer fits.
EDITS = {
    # no keyboard shortcut for search (2026-11-20)
    35: [("press / from anywhere", "click the search box")],
}


def apply(blocks):
    """blocks: {paragraph number: block}; changes text and html in place"""
    for i, subs in EDITS.items():
        b = blocks[i]
        for old, new in subs:
            assert old in b["text"] and old in b["html"], "edit for paragraph %d no longer matches: %r" % (i, old)
            b["text"] = b["text"].replace(old, new)
            b["html"] = b["html"].replace(old, new)
