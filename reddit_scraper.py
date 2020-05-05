#!/usr/bin/python3
import praw
import re
import requests
import sys
from bs4 import BeautifulSoup

def main():
    reddit_url = "https://www.reddit.com/r/FreeEBOOKS/comments/g34xi5/408_free_ebooks_from_springer/"
    reddit_subid = "g34xi5"
    reddit = praw.Reddit(client_id="my_client_id",
                         client_secret="my_client_secret",
                         user_agent="my_user_agent")

    # Both the author's submission and first comment contain the links to the hosting site
    submission = reddit.submission(reddit_subid)
    text = submission.selftext + "\t" + submission.comments[0].body
    text = text.split("\t")
    print(f"Scraping {reddit_url}...")

    links = []
    for i,line in enumerate(text):
        idx = line.find("\n\n")
        if idx != -1:
            link = None
            pre = line[:idx]
            post = line[(idx+2):]
            if "http" in pre:
                link = pre
            elif "http" in post:
                link = post
            if link is not None:
                links.append(link)
        else:
            if "http" in line:
                links.append(line) # cover "last" case with no newlines

    print(f"Found {len(links)} links, beginning downloads")

    # build pdf links programatically, then download
    # TODO multi-threading
    for i,link in enumerate(links):
        r = requests.get(link, allow_redirects=True)
        soup = BeautifulSoup(r.content, 'html.parser')
        title = soup.h1.get_text()
        title = title.replace("/","_") # replace chars that can mess with file path lookup

        locale = None
        for l in soup.findAll('a', attrs={'href': re.compile("pdf")}):
            # accept first pdf link with blue button -- may require page-specific modification
            # depending on which pdf download link we are targeting
            if "blue" in ' '.join(l.get('class')):
                locale = l.get('href')
                break

        if locale is None:
            print(f"Skipping {title}: no download link available!")
            continue

        pdf = "https://link.springer.com" + locale
        print(f"Downloading {i+1} ({title}) ==> {pdf} ...")

        try:
            book_file = '/tmp/' + title + '.pdf'
            with requests.get(pdf, stream=True) as r:
                with open(book_file, 'wb') as f:
                    for chunk in r.iter_content(2048):
                        f.write(chunk)
            print(f"[+] Download of {title} e-book to {book_file} complete!\n")
        except:
            raise

if __name__ == "__main__":
    sys.exit(main())
