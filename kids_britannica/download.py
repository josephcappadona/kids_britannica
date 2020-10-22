from .imports import *
from .utils import *
from .urls import *
from .scraping import scrape_article


class ArticleDownloader:
    def __init__(self, data_dir='data', session=None, pool_size=2, chunk_size=1000, max_retries=1):
        self.data_dir = Path(data_dir)
        self.session = session
        self.pool = ThreadPool(pool_size)
        self.chunk_size = chunk_size
        self.max_retries = max_retries
    
    def get_worker_args(self, chunks):
        return zip(range(len(chunks)), chunks, [self.data_dir]*len(chunks), [self.session]*len(chunks))
    
    def download_urls(self, urls):
        # initial attempt
        print(f"Downloading {len(urls)} articles...")
        chunks = list(get_chunks(urls, self.chunk_size))
        args = self.get_worker_args(chunks)
        failed = concatenate(self.pool.map(self.batch, args))

        # retry if necessary
        retries = 0
        while len(failed) > 0 and retries < self.max_retries:
            logging.info(f"{len(failed)} failed, retrying")
            chunks = list(get_chunks(failed, self.chunk_size))
            args = self.get_worker_args(chunks)
            failed = concatenate(self.pool.map(self.batch, args))
            retries += 1
    
    @staticmethod
    def batch(data):
        id_, article_urls, data_dir, session = data
        
        failed = []
        for article_url in set(article_urls):
            article_id = get_id_from_url(article_url)
            try:
                article = scrape_article(article_url, session=session)
                filename = f"{article['id']} {article['title']}.json"
                filename = sanitize_filename(filename)
                filepath = data_dir / 'articles' / article['tier'] / filename
                write_json(filepath, article)
                print(f'{article_id} downloaded')
            except Exception as e:
                print(article_url)
                traceback.print_exception(type(e), e, e.__traceback__)
                failed.append(article_url)
        return failed


def download_image(url, output_path):
    wget.download(url, out=str(output_path))

def download_video(url, output_path):
    raise NotImplemented
    url_path = Path(url)
    if url_path.suffix == '.m3u8':
        downloader = M3u8Downloader(url, output_path)
        downloader.start()
    else:
        raise ValueError()

def download_audio(url, output_path):
    wget.download(url, out=str(output_path))

    