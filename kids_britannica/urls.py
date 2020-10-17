from .imports import *
from .utils import *


def get_letter_page_urls(letter, page, tier, session=None, limit=None):
    """Retrieves the URLs for a single page of the index for a particular letter of a particular tier.

    Args:
        letter: A string, a single letter of the alphabet.
        page: A positive integer, the page of `letter`'s index to query.
        tier: A string, one of "kids", "students", or "scholars".
        limit: [optional] A positive integer, the maximum number of URLs to retrieve. Useful for testing.
    
    Returns:
        A list of strings representing URLs of articles.
    """
    sleep(SLEEP_TIME)
    page_urls = []
    page_url = f'https://kids.britannica.com/{tier}/browse/alpha/{letter}/{page}'
    page_soup = BeautifulSoup(session.get(page_url).text, features='html.parser')
    content = page_soup.find('body').find('div', {'class': 'content'}).find('ul', {'class': 'seo-items'})
    for item in content.find_all('li'):
        href = item.find('dd').find('a').get('href')
        item_url = f'https://kids.britannica.com{href}'
        page_urls.append(item_url)
        if limit and len(page_urls) >= limit:
            break
    return page_urls

def get_letter_urls(letter, tier, session=None, limit=None):
    """Retrieves the URLs for a particular letter of a particular tier of Encyclopedia Britannica Kids.

    Args:
        letter: A string, a single letter of the alphabet.
        tier: A string, one of "kids", "students", or "scholars".
        limit: [optional] A positive integer, the maximum number of URLs to retrieve. Useful for testing.
    
    Returns:
        A list of strings representing URLs of articles.
    """
    letter_urls = []
    page = 1
    while True:
        page_urls = get_letter_page_urls(letter, page, tier, session=session, limit=limit)
        if not page_urls:
            break
        else:
            letter_urls.extend(page_urls)
            if limit and len(letter_urls) >= limit:
                break
            else:
                page += 1
    return letter_urls

def get_tier_urls(tier, session=None, limit=None, verbose=0):
    """Retrieves the URLs for a particular tier of Encyclopedia Britannica Kids.

    Args:
        tier: A string, one of "kids", "students", or "scholars".
        limit: [optional] A positive integer, the maximum number of URLs to retrieve. Useful for testing.
        verbose: [optional] An integer, the verbosity level.
    
    Returns:
        A list of strings representing URLs of articles.
    """
    if verbose >= 2:
        print(f"Getting {tier} URLs...")

    tier_urls = []
    for letter in ascii_lowercase:
        letter_urls = get_letter_urls(letter, tier, session=session, limit=limit)
        tier_urls.extend(letter_urls)
        if limit and len(tier_urls) >= limit:
            break

    if verbose >= 2:
        print(f"Scraped {max(len(tier_urls), limit)} {tier} URLs.")
    return tier_urls[:limit]

def get_all_urls(**kwargs):
    kids_urls = get_tier_urls('kids', **kwargs)
    students_urls = get_tier_urls('students', **kwargs)
    scholars_urls = get_tier_urls('scholars', **kwargs)
    all_urls = kids_urls + students_urls + scholars_urls
    return all_urls

def get_tier_from_url(article_url):
    split = article_url.split('/')
    base_idx = split.index('kids.britannica.com')
    tier = split[base_idx + 1]
    return tier

def get_id_from_url(article_url):
    split = article_url.split('/')
    base_idx = split.index('kids.britannica.com')
    id_ = split[base_idx + 4]
    id_cleaned = re.sub('[^0-9]', '', id_)  # remove non-numeric characters
    return id_cleaned