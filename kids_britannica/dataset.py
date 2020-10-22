from .imports import *
from .utils import *
from .urls import *
from .download import ArticleDownloader


# class Article(File):
#     def __init__(self, filename):
#         super().__init__(self, open(filename))
#         #self['adjacent_ids'] = {get_tier_from_url(url):get_id_from_url(url) for url in get_adjacent_articles(self['htmls']['text'])}

Article = edict.LazyLoad

class KidsBritannicaDataSet:
    def __init__(self, data_dir='data', username=None, password=None):
        make_directories(data_dir)
        self.data_dir = Path(data_dir)
        self.articles_dir = self.data_dir / 'articles'
        self.session = login(username, password)
        self.kids_article_paths = KidsBritannicaDataSet.get_article_paths(self.data_dir, tier='kids')
        self.students_article_paths = KidsBritannicaDataSet.get_article_paths(self.data_dir, tier='students')
        self.scholars_article_paths = KidsBritannicaDataSet.get_article_paths(self.data_dir, tier='scholars')
        metadata_filepath = self.data_dir / 'metadata.json'
        if metadata_filepath.exists():
            print('Loading metadata from file...')
            self._metadata = json.load(open(metadata_filepath, 'rt'))
    
    @property
    def articles(self):
        for article in self.kids_articles:
            yield article
        for article in self.students_articles:
            yield article
        for article in self.scholars_articles:
            yield article

    @property
    def article_paths(self):
        for json_path in self.kids_article_paths:
            yield json_path
        for json_path in self.students_article_paths:
            yield json_path
        for json_path in self.scholars_article_paths:
            yield json_path
    
    @property
    def kids_articles(self):
        for json_path in self.kids_article_paths:
            yield Article(json_path)
    
    @property
    def students_articles(self):
        for json_path in self.students_article_paths:
            yield Article(json_path)
    
    @property
    def scholars_articles(self):
        for json_path in self.scholars_article_paths:
            yield Article(json_path)
    
    def article_by_id(self, article_id):
        md = self.metadata[article_id]
        filename = f"{md['id']} {md['title']}.json"
        filename = sanitize_filename(filename)
        article_path = self.articles_dir / md['tier'] / filename
        return Article(article_path)
    
    @property
    def metadata(self):
        if not hasattr(self, '_metadata'):
            metadata_filepath = self.data_dir / 'metadata.json'
            if metadata_filepath.exists():
                print('Loading metadata from file...')
                self._metadata = json.load(open(metadata_filepath, 'rt'))
            else:
                print('Building metadata from scratch...')
                metadata_keys = ['id', 'url', 'tier', 'title', 'adjacent_ids']
                self._metadata = {}
                for article, article_path in zip(self.articles, self.article_paths):
                    article_metadata = {}
                    for key in metadata_keys:
                        if key in article:
                            if not isinstance(article[key], edict.LazyLoad):
                                article_metadata[key] = article[key]
                            else:
                                article_metadata[key] = article[key].to_dict()
                    article_metadata['path'] = article_path
                    self._metadata[article_metadata['id']] = article_metadata
                print('Writing metadata to file...')
                write_json(metadata_filepath, self._metadata)
        return self._metadata

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