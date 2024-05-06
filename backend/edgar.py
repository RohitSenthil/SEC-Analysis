import os
import shutil
from typing import Optional

from sec_edgar_downloader import Downloader


def download_filing(ticker: str) -> Optional[str]:
    dl = Downloader(os.environ["COMPANY_NAME"], os.environ["EMAIL_ADDRESS"])
    try:
        dl.get("10-K", ticker, download_details=False, limit=1)
        cik = os.listdir(f"./sec-edgar-filings/{ticker}/10-K/").__iter__().__next__()
        with open(
            f"./sec-edgar-filings/{ticker}/10-K/{cik}/full-submission.txt", "r"
        ) as f:
            filing = f.read()
        shutil.rmtree(f"./sec-edgar-filings/{ticker}/")
        return filing
    except:
        return None
