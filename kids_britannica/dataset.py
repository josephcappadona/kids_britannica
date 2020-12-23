from .imports import *
from .utils import *
from .urls import *
from .download import ArticleDownloader

Article = edict.LazyLoad

class KidsBritannicaDataSet:
    def __init__(self, data_dir='data'):
        make_directories(data_dir)
        self.data_dir = Path(data_dir)
        self.articles_dir = self.data_dir / 'articles'
        self.kids_article_paths = KidsBritannicaDataSet.get_article_paths(self.data_dir, tier='kids')
        self.students_article_paths = KidsBritannicaDataSet.get_article_paths(self.data_dir, tier='students')
        self.scholars_article_paths = KidsBritannicaDataSet.get_article_paths(self.data_dir, tier='scholars')
        self.metadata_filepath = self.data_dir / 'metadata.json'
        if self.metadata_filepath.exists():
            print('Loading metadata from file...')
            self._metadata = json.load(open(self.metadata_filepath, 'rt'))
    
    def article_by_id(self, article_id):
        md = self.metadata[article_id]
        filename = f"{md['id']} {md['title']}.json"
        filename = sanitize_filename(filename)
        article_path = self.articles_dir / md['tier'] / filename
        return Article(article_path)
    
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
    
    @property
    def metadata(self):
        if not hasattr(self, '_metadata'):
            if self.metadata_filepath.exists():
                print('Loading metadata from file...')
                self._metadata = json.load(open(self.metadata_filepath, 'rt'))
            else:
                print("Building metadata from scratch...")
                print("This could take anywhere from a few seconds to a couple hours depending "
                      "on how much data you're processing and the speed of your computer")
                metadata_keys = ['id', 'url', 'tier', 'title', 'aligned_ids', 'aligned_urls']
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
                write_json(self.metadata_filepath, self._metadata)
        return self._metadata
    
    @property
    def statistics(self):
        from .statistics import *
        if not hasattr(self, '_statistics'):
            stats_path = self.data_dir / 'stats.json'
            if stats_path.exists():
                print('Loading stats from file...')
                stats, structures = json.load(open(stats_path, 'rt'))
            else:
                print('Building stats from scratch...')
                stats = {}
                structures = {}
                limit = None
                for tier, articles in zip(['kids', 'students', 'scholars'],
                                        [self.kids_articles, self.students_articles, self.scholars_articles]):
                    stats[tier], structures[tier] = aggregate_statistics(articles, limit=limit)
                write_json(stats_path, [stats, structures])
            self._statistics = stats
            self._structures = structures
        return self._statistics

    @property
    def structures(self):
        from .statistics import aggregate_statistics
        if not hasattr(self, '_structures'):
            stats_path = self.data_dir / 'stats.json'
            if stats_path.exists():
                print('Loading stats from file...')
                stats, structures = json.load(open(stats_path, 'rt'))
            else:
                print('Building stats from scratch...')
                stats = {}
                structures = {}
                limit = None
                for tier, articles in zip(['kids', 'students', 'scholars'],
                                        [self.kids_articles, self.students_articles, self.scholars_articles]):
                    stats[tier], structures[tier] = aggregate_statistics(articles, limit=limit)
                write_json(stats_path, [stats, structures])
            self._statistics = stats
            self._structures = structures
        return self._structures

class KidsBritannicaDataSetDev(KidsBritannicaDataSet):
    
    def __init__(self, *args, **kwargs, username=None, password=None):
        super().__init__(*args, **kwargs)
        if username and password:
            self.session = login(username, password)

    @staticmethod
    def get_article_paths(data_dir, tier='*'):
        article_paths = glob(str(data_dir / 'articles' / tier / '*.json'))
        if len(article_paths) == 0:
            raise ValueError(f"No articles could not be found in {str(data_dir)}. Please download the data first.")
        return article_paths

    def download_urls(self, overwrite=True, limit=None, verbose=1):
        data_dir = self.data_dir
        urls_filepath = Path(data_dir) / 'urls.json'
        if not urls_filepath.exists() or overwrite:
            all_urls = get_all_urls(session=self.session, limit=limit, verbose=verbose)

            write_json(urls_filepath, all_urls)
            return all_urls
    
    def download_articles(self, urls=None, limit=None, **kwargs):
        from .download import ArticleDownloader
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
    def write_articles_from_html(data_dir, overwrite=False):
        from .scraping import parse_article_from_html
        data_dir = Path(data_dir)
        make_directories(data_dir)
        html_paths = glob(str(data_dir / 'html' / '*.json'))
        for html_path in html_paths:
            article = parse_article_from_html(html_path, data_dir=data_dir, overwrite=overwrite)
