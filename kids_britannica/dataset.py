from .imports import *
from .utils import *
from .urls import *
from .download import ArticleDownloader

class KidsBritannicaDataSet:
    def __init__(self, data_dir='data', username=None, password=None):
        make_directories(data_dir)
        self.data_dir = Path(data_dir)
        self.session = login(username, password)
    
    @property
    def articles(self):
        for article in self.kids_articles:
            yield article
        for article in self.students_articles:
            yield article
        for article in self.scholars_articles:
            yield article
    
    @property
    def kids_articles(self):
        if not hasattr(self, 'kids_article_paths'):
            self.kids_article_paths = KidsBritannicaDataSet.get_article_paths(self.data_dir, tier='kids')
        for json_path in self.kids_article_paths:
            yield json.load(open(json_path, 'rt'))
    
    @property
    def students_articles(self):
        if not hasattr(self, 'students_article_paths'):
            self.students_article_paths = KidsBritannicaDataSet.get_article_paths(self.data_dir, tier='students')
        for json_path in self.students_article_paths:
            yield json.load(open(json_path, 'rt'))
    
    @property
    def scholars_articles(self):
        if not hasattr(self, 'scholars_article_paths'):
            self.scholars_article_paths = KidsBritannicaDataSet.get_article_paths(self.data_dir, tier='scholars')
        for json_path in self.scholars_article_paths:
            yield json.load(open(json_path, 'rt'))
    
    @property
    def metadata(self):
        if not hasattr(self, '_metadata'):
            metadata_path = self.data_dir / 'articles' / 'metadata.json'
            if not metadata_path.exists():
                self._metadata = self.compile_metadata()
            else:
                print('Loading metadata from file...')
                self._metadata = json.load(open(metadata_path, 'rt'))
        return self._metadata

    def compile_metadata(self):
        print('Compiling metadata...')
        metadata = []
        metadata_keys = ['id', 'url', 'tier', 'title']
        for article in self.articles:
            article_metadata = {key:article[key] for key in metadata_keys}
            metadata.append(article_metadata)
        metadata_path = self.data_dir / 'articles' / 'metadata.json'
        write_json(metadata_path, metadata)
        return metadata

    def download_urls(self, overwrite=True, limit=None, verbose=1):
        data_dir = self.data_dir
        urls_filepath = Path(data_dir) / 'urls.json'
        if not urls_filepath.exists() or overwrite:
            all_urls = get_all_urls(session=self.session, limit=limit, verbose=verbose)

            write_json(urls_filepath, all_urls)
            return all_urls
    
    def download_articles(self, urls=None, limit=None, **kwargs):
        if urls is None:
            url_json_path = self.data_dir / 'urls.json'
            if not url_json_path.exists():
                print("No URLs downloaded yet. Downloading now...")
                urls = KidsBritannicaDataSet.download_urls(data_dir=self.data_dir, limit=limit)
            else:
                print("Loading URLs from file...")
                urls = json.load(open(url_json_path, 'rt'))

        print("Loading saved article IDs...")
        saved_ids = get_saved_ids(self.data_dir)
        urls = [url for url in urls if get_id_from_url(url) not in saved_ids] # filter
        if limit:
            urls = rand.choices(urls, k=limit) # random selection
        print(f"{len(saved_ids)} articles already downloaded.")
        print(f"Downloading {len(urls)} articles...")

        dl = ArticleDownloader(data_dir=self.data_dir, session=self.session, **kwargs)
        dl.download_urls(urls)
    
    @staticmethod
    def download_media(data_dir='data'):
        raise NotImplemented

    @staticmethod
    def get_article_paths(data_dir, tier='*'):
        article_paths = glob(str(data_dir / 'articles' / tier / '*.json'))
        if len(article_paths) == 0:
            raise ValueError(f"No articles could not be found in {str(data_dir)}. Please download the data first.")
        return article_paths