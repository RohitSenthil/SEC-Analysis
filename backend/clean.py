import re

import language_tool_python
from bs4 import BeautifulSoup, CData, NavigableString, PageElement, Tag
from unstructured.cleaners.core import (
    clean_extra_whitespace,
    clean_non_ascii_chars,
    group_broken_paragraphs,
    replace_unicode_quotes,
)
from unstructured.nlp.partition import is_possible_narrative_text

UNICODE_RE = re.compile(r"&#\d{3};")
BACKSPACE_RE = re.compile(r"&nbsp;")
CHAR_ENT_RE = re.compile(r"&\w+;")
DOC_START_RE = re.compile(r"<DOCUMENT>")
DOC_END_RE = re.compile(r"</DOCUMENT>")
BLANK_LINES_RE = re.compile(r"(\n\s*){2,}")
PAGE_NUM_RE = re.compile(r"^\s*\d+\s*", re.MULTILINE)
DATE_RE = re.compile(r"CONFORMED PERIOD OF REPORT:\s*\d{8}")


def text_filter(element: PageElement):
    return type(element) in (NavigableString, CData)


def tag_filter(element: PageElement):
    return type(element) == Tag


def parse_filing(filing: str) -> str:
    date = DATE_RE.search(filing).group()
    old = int(date[-8:-4]) <= 2001 and "<PAGE>" in filing
    text = UNICODE_RE.sub("", filing)
    text = BACKSPACE_RE.sub(" ", text)
    text = CHAR_ENT_RE.sub("", text)
    if old:
        text = re.sub(r"<C>", "", text)
        text = re.sub(r"<S>", "", text)
        text = re.sub(r"<CAPTION>", "", text)
        text = re.sub(r"^\s*\d+\s*\n", "", text, flags=re.MULTILINE)
    start = DOC_START_RE.search(text).start()
    *_, end = DOC_END_RE.finditer(text)
    text = replace_unicode_quotes(text[start : end.end()])
    text = f"<FILING>{date}</FILING>" + text
    soup = BeautifulSoup(text, "lxml")
    for doc in soup.find_all("document"):
        type_tag = doc.find("type")
        if type_tag:
            doc_type = str(type_tag.contents[0]).strip()
        if doc_type in ("XML", "GRAPHIC", "ZIP", "EXCEL", "JSON") or doc.find("xbrl"):
            doc.decompose()
    return clean_filing(soup, old)


def clean_text(element: PageElement) -> str:
    text = element.text
    if PAGE_NUM_RE.search(text) and "|" not in text:
        return ""
    if is_possible_narrative_text(text):
        text = group_broken_paragraphs(text)
    return text


def clean_filing(filing: BeautifulSoup, old: bool) -> str:
    tags = filter(text_filter, filing.descendants)
    tables_old = []
    for table in filing.find_all("table"):
        if old:
            if len(table.find_all("article")) != 0:
                table.append(format_old_table(table))
            tables_old.append(table.get_text())
            table.string = "|TABLE|"
        else:
            table.append(format_new_table(table))
    if old:
        text = filing.get_text()
        cleaned = ""
        for chunk in text.split("\n\n"):
            chunk = clean_extra_whitespace(group_broken_paragraphs(chunk))
            cleaned += f"{chunk}\n\n"
        i = 0
        TABLE_RE = re.compile(r"\|TABLE\|")
        while match := TABLE_RE.search(cleaned):
            cleaned = cleaned[: match.start()] + tables_old[i] + cleaned[match.end() :]
            i += 1
        text = cleaned
    else:
        text = "\n".join(clean_text(s) for s in tags)
    text = BLANK_LINES_RE.sub("\n\n", text)
    return clean_non_ascii_chars(text)


def format_new_table(element: PageElement) -> str:
    table = ""
    for row in filter(tag_filter, element.children):
        row_text = ""
        for cell in filter(tag_filter, row.children):
            cell_text = clean_extra_whitespace(cell.text) or "--"
            row_text += cell_text
            if cell_text != "$":
                row_text += "|"
        row.extract()
        if row_text:
            table += row_text[:-1] + "\n"
    return table + "\n"


def format_old_table(element: PageElement) -> str:
    table_text = ""
    curr = next(filter(tag_filter, element.find_all(True, recursive=False)))
    try:
        while True:
            curr.extract()
            if curr.name != "article":
                table_text += f"{curr.name}: {curr.contents[0]}"
            curr = next(filter(tag_filter, curr.find_all(True, recursive=False)))
    except:
        return table_text


def get_cleaned_filing(filing: str) -> str:
    parsed_text = parse_filing(filing)
    with language_tool_python.LanguageTool("en-US") as tool:
        cleaned_text = tool.correct(parsed_text)
    return clean_non_ascii_chars(cleaned_text)
