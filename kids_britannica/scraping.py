from .imports import *
from .utils import *
from .urls import *


def get_article_text(article_html, article_url=None, session=None):
    """Retrieves the text content of a particular Encyclopedia Britannica Kids article.

    Args:
        article_url: A string, the URL of the article to scrape.
    
    Returns:
        A tuple of the following items:
            * title [string]
            * text [list of tuples: (section_title, [paragraph1, paragraph2, ...])]
            * text_html [string]
    """
    if article_html is None:
        sleep(SLEEP_TIME)
        article_html = session.get(article_url).text
    article_soup = BeautifulSoup(article_html, features='html.parser')
    article_title = article_soup.find('body').find('header').find('h1').get_text()

    article_sections = article_soup.find('article').find_all('div', {'class': 'panel'})
    if not article_sections:
        article_sections = article_soup.find('article').find_all('section')

    article_text = []
    for section in article_sections:
        section_title_div = section.find(re.compile('^h[1-6]$'))
        if section_title_div:
            section_title = section_title_div.get_text().strip()
        else:
            section_title = ''

        section_text = []
        for paragraph in section.find_all('p'):
            text = clean_text(paragraph.get_text())
            if text:
                section_text.append(text)
        article_text.append([section_title, section_text])

    return article_title, article_text, article_html

def get_article_media(media_html, article_url=None, session=None):
    """Retrieves the media content of a particular Encyclopedia Britannica Kids article.

    Args:
        article_url: A string, the URL of the article to scrape.
    
    Returns:
        A tuple of the following items:
            * media [list of dictionaries] - each entry represents the metadata for an 
                image or video of the article and has the following keys:
                    * title [string]
                    * media-type [string] - either "IMAGE", "AUDIO", or "VIDEO"
                    * caption [string]
                    * data [dictionary]
                
                If "media-type" is "IMAGE" or "AUDIO", the "data" dictionary will have the following keys:
                    * src [string] - a URL to the source image
                
                If "media-type" is "VIDEO", the "data" dictionary will have the following keys:
                    * transcript [string]
                    * video-id [string]
                    * manifest-url [string]
                    
            * media_html [string]
    """
    if media_html is None:
        sleep(SLEEP_TIME)
        media_url = f"{article_url}/media"
        media_html = session.get(media_url).text
    media_soup = BeautifulSoup(media_html, features='html.parser')

    article_media = []
    media_list = media_soup.find('div', {'id': 'article-media-content'}).find('ul')
    if media_list:
        for media in media_list.find_all('li'):
            media = media.find('a')
            media_title = clean_html(media.get('data-title'))
            media_type = media.get('data-media-type')
            media_caption = clean_html(media.get('data-caption'))

            if media_type:
                media_info = {
                    'title': media_title,
                    'media-type': media_type,
                    'caption': media_caption,
                    'data': {}
                }
                if media_info['media-type'] == 'VIDEO':
                    media_info['data']['transcript'] = media.get('data-transcript') or ""
                    media_info['data']['video-id'] = video_id = media.get('data-jwplayer-id')
                    media_info['data']['manifest-url'] = f"https://content.jwplatform.com/manifests/{video_id}.m3u8"
                    manifest_url = Path(media_info['data']['manifest-url'])
                    media_info['id'] = manifest_url.stem
                    media_info['data']['file-type'] = 'mp4'

                elif media_info['media-type'] == 'IMAGE':
                    media_info['data']['src'] = media.get('data-full-path')
                    src_url = Path(media_info['data']['src'])
                    media_info['id'] = src_url.stem
                    media_info['data']['file-type'] = src_url.suffix.strip('.').lower()

                elif media_info['media-type'] == 'AUDIO':
                    media_info['data']['src'] = media.get('data-full-path')
                    src_url = Path(media_info['data']['src'])
                    media_info['id'] = src_url.stem
                    media_info['data']['file-type'] = src_url.suffix.strip('.').lower()
                article_media.append(media_info)

    return article_media, media_html

def get_related_articles_page(related_page_html, article_url=None, page=0, session=None):
    """Retrieves a single page of related articles.

    Args:
        article_url: A string, the URL of the article to scrape.
        page: A positive interger, the page of related articles to scrape.
    
    Returns:
        A tuple of the following items:
            * related_articles [list of strings] - the URLs to the specified page's related articles
            * related_article_page_html [list of strings] - the HTML of the specified page's related article listing
    """
    if related_page_html is None:
        sleep(SLEEP_TIME)
        related_page_url = f"{article_url}/related/main?page={page}"
        related_page_html = session.get(related_page_url).text
    related_page_soup = BeautifulSoup(related_page_html, features='html.parser')

    related_page_urls = []
    related_page_list = related_page_soup.find('ul', {'class': 'results'}).find_all('li')
    for related_item in related_page_list:
        related_item_href = related_item.find('a').get('href')
        related_item_url = f"https://kids.britannica.com{related_item_href}"
        related_page_urls.append(related_item_url)
    return related_page_urls, related_page_html

def get_related_articles(related_article_htmls, article_url=None, session=None):
    """Retrieves the related articles of a particular Encyclopedia Britannica Kids article.

    Args:
        article_url: A string, the URL of the article to scrape.
    
    Returns:
        A tuple of the following items:
            * related_articles [list of strings] - the URLs to the related articles
            * related_article_page_htmls [list of strings] - the HTMLs corresponding to the related article listings
    """
    related_article_urls = []
    related_article_htmls = related_article_htmls or []

    if related_article_htmls:
        for related_page_query_html in related_article_htmls:
            related_page_urls, _ = get_related_articles_page(related_page_query_html)
            related_article_urls.extend(related_page_urls)
    else:
        page = 1
        while True:
            try:
                related_page_urls, related_page_query_html = get_related_articles_page(None, article_url=article_url, page=page)
                related_article_urls.extend(related_page_urls)
                related_article_htmls.append(related_page_query_html)
                page += 1
            except:
                break
    return related_article_urls, related_article_htmls

def get_related_websites(related_websites_html, article_url=None, session=None):
    """Retrieves the related websites of a particular Encyclopedia Britannica Kids article.

    Returns:
        A tuple of the following items:
            * related_websites [list of strings] - the URLs to the related websites
            * related_website_page_html [string] - the HTML corresponding to the related website listing
    """
    if related_websites_html is None:
        sleep(SLEEP_TIME)
        related_websites_url = f"{article_url}/related/websites"
        related_websites_html = session.get(related_websites_url).text
    related_websites_soup = BeautifulSoup(related_websites_html, features='html.parser')

    related_website_urls = []
    try:
        related_website_list = related_websites_soup.find('ul', {'class': 'results-resources'}).find_all('li')
        for related_item in related_website_list:
            related_item_url = related_item.find('a').get('href')
            related_website_urls.append(related_item_url)
    except:
        pass
    return related_website_urls, related_websites_html

def get_adjacent_ids(article_html):
    article_soup = BeautifulSoup(article_html, features='html.parser')
    adjacent_article_divs = [li.find('a') for li in article_soup.find('ul', {'class': 'bk-reading-levels'}).find_all('li')]
    adjacent_articles = [f"https://kids.britannica.com{a.get('href')}" for a in adjacent_article_divs if a is not None and a.get('href') is not None and 'active' not in a.get('class')]
    return {get_tier_from_url(url):get_id_from_url(url) for url in adjacent_articles}


def scrape_article(article_url, session=None, data_dir=None):
    """Scrapes the text, media, and metadata of a particular Encyclopedia Britannica Kids article.

    Args:
        article_url: A string, the URL of the article to scrape.
    
    Returns:
        A dictionary with the following keys:
            * url [string]
            * id [string]
            * title [string]
            * text [list of tuples: (section_title, [paragraph1, paragraph2, ...])]
            * media [list of dictionaries]
            * related_articles [list of strings]
            * related_websites [list of strings]
            * htmls [dictionary]
    """
    tier = get_tier_from_url(article_url)
    id_ = get_id_from_url(article_url)

    artcile_id = Path(article_url).name
    tier = get_tier_from_url(article_url)
    title, text, text_html = get_article_text(article_url, session=session)
    adjacent_ids = get_adjacent_ids(text_html)
    media, media_html = get_article_media(article_url, session=session)
    related_articles, related_articles_pages_htmls = get_related_articles(article_url, session=session)
    related_websites, related_websites_page_html = get_related_websites(article_url, session=session)

    article = {
        'url': article_url,
        'id': artcile_id,
        'tier': tier,
        'title': title,
        'text': text,
        'media': media,
        'adjacent_ids': adjacent_ids,
        'related_articles': related_articles,
        'related_websites': related_websites,
    }
    htmls = {
        'text': text_html,
        'media': media_html,
        'related_articles': related_articles_pages_htmls,
        'related_websites': related_websites_page_html
    }

    # if data_dir is not None:
    #     filename = f"{metadata['id']} {metadata['title']}.json"
    #     filename = sanitize_filename(filename)
    #     html_path = Path(data_dir) / 'html' / filename
    #     write_json(htmls_path, htmls)
    return article, htmls

def scrape_htmls(article_url, session=None, sleep_time=0.1, write=False, data_dir=None):
    if session is None:
        raise ValueError
    id_ = get_id_from_url(article_url)

    title, _, text_html = get_article_text(None, article_url=article_url, session=session)
    sleep(sleep_time)

    media_url = f"{article_url}/media"
    media_html = session.get(media_url).text
    sleep(sleep_time)

    related_websites_url = f"{article_url}/related/websites"
    related_websites_html = session.get(related_websites_url).text
    sleep(sleep_time)

    _, related_article_htmls = get_related_articles(None, article_url=article_url, session=session)

    htmls = {
        'text': text_html,
        'media': media_html,
        'related_articles': related_article_htmls,
        'related_websites': related_websites_html
    }
    if data_dir is not None:
        filename = f"{id_} {title}.json"
        filename = sanitize_filename(filename)
        htmls_path = Path(data_dir) / 'html' / filename
        write_json(htmls_path, htmls)
    return htmls

def parse_article_from_html(article_id, ds):
    metadata = ds.metadata[article_id]
    data_dir = ds.data_dir
    
    filename = f"{metadata['id']} {metadata['title']}.json"
    filename = sanitize_filename(filename)

    htmls_path = data_dir / 'html' / filename
    if htmls_path.exists():
        htmls = json.load(open(htmls_path, 'rt'))
        text_html = htmls['text']
        media_html = htmls['media']
        related_articles_pages_htmls = htmls['related_articles']
        related_websites_page_html = htmls['related_websites']

        url = metadata['url']
        artcile_id = metadata['id']
        tier = metadata['tier']
        title, text, _ = get_article_text(text_html)
        adjacent_ids = get_adjacent_ids(text_html)
        media, _ = get_article_media(media_html)
        related_articles, _ = get_related_articles(related_articles_pages_htmls)
        related_websites, _ = get_related_websites(related_websites_page_html)

        return {
            'url': url,
            'id': artcile_id,
            'tier': tier,
            'title': title,
            'text': text,
            'media': media,
            'adjacent_ids': adjacent_ids,
            'related_articles': related_articles,
            'related_websites': related_websites,
        }
    return None