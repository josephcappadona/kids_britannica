from .imports import *
from .utils import *

def Article(p):
    try:
        return json.load(open(p))
    except:
        # if error with filename, glob for the article by its id
        path = Path(p)
        query = str(path.parent / f"{path.stem.split(' ')[0]} *.json")
        fps = glob(query)
        if fps:
            return json.load(open(fps[0]))
        else:
            return None
        

class KidsBritannicaDataSet:
    @staticmethod
    def download(size='small', data_dir='data', quiet=False, download_media=False, overwrite=False):
        
        data_dir = Path(data_dir)
        os.makedirs(data_dir, exist_ok=True)
        if size == 'full':
            full_dir = data_dir / 'kbds'
            os.makedirs(full_dir, exist_ok=True)

            article_url = 'https://drive.google.com/uc?id=1lPZr1d6Hj2tcSrfZpaUHX-sEK9og-g70'
            media_url = 'https://drive.google.com/uc?id=1OLiRne5Tm8vw5emRe6FImJOGieUhPOHn'
            
            article_output = full_dir / 'kbds_articles.zip'
            media_output = full_dir / 'kbds_media.zip'

        elif size == 'aligned':
            aligned_dir = data_dir / 'kbds_aligned'
            os.makedirs(aligned_dir, exist_ok=True)

            article_url = 'https://drive.google.com/uc?id=1G3zTflSwHMBW-uj17MOkbG2s_MhE5NiE'
            article_output =  aligned_dir / 'kbds_aligned_articles.zip'

            media_url = None
            media_output =  aligned_dir / 'kbds_aligned_media.zip'
        elif size == 'small':
            small_dir = data_dir / 'kbds_small'
            os.makedirs(small_dir, exist_ok=True)

            article_url = 'https://drive.google.com/uc?id=1WYNOwQ3vrnoZvtfR6ym3n-iP1Ty-Chhj'
            article_output = small_dir / 'kbds_small_articles.zip'

            media_url = None
            media_output = small_dir / 'kbds_small_media.zip'
        else:
            raise ValueError(f'Invalid `size` ({size}): should be "small" "aligned" or "full".')
        
        output_dir = article_output.parent
        articles_dir = output_dir / 'articles'
        if not articles_dir.exists() or overwrite:
            download_and_unzip(article_url, article_output)
            if download_media and media_url:
                download_and_unzip(media_url, media_output)

        return output_dir
        
        
    def __init__(self, data_dir='data/kbds_small'):
        data_dir = Path(data_dir)
        if not data_dir.exists():
            stem  = data_dir.stem
            if stem.endswith('_small'):
                size = 'small'
            elif stem.endswith('_aligned'):
                size = 'aligned'
            else:
                size = 'full'
            KidsBritannicaDataSet.download(size, data_dir.parent)
        self.data_dir = data_dir
        self.articles_dir = self.data_dir / 'articles'
        self.media_dir = self.data_dir / 'media'
        self.kids_article_paths = KidsBritannicaDataSet.get_article_paths(self.data_dir, tier='kids')
        self.students_article_paths = KidsBritannicaDataSet.get_article_paths(self.data_dir, tier='students')
        self.scholars_article_paths = KidsBritannicaDataSet.get_article_paths(self.data_dir, tier='scholars')
        self.metadata_filepath = self.data_dir / 'metadata.json'
        if self.metadata_filepath.exists():
            print('Loading metadata from file...')
            self._metadata = json.load(open(self.metadata_filepath, 'rt'))
    
    @staticmethod
    def get_article_paths(data_dir, tier='*'):
        article_paths = glob(str(data_dir / 'articles' / tier / '*.json'))
        if len(article_paths) == 0:
            raise ValueError(f"No articles could not be found in {str(data_dir)}. Please download the data first.")
        return article_paths
    
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
    def aligned_triple_ids(self):
        seen = set()
        for article_id, md in self.metadata.items():
            if md['tier'] == 'kids':
                tier_to_id = {**md['aligned_ids'], **{md['tier']: article_id}}
                if len(tier_to_id) == 3 and article_id not in seen:
                    triple = (tier_to_id['kids'], tier_to_id['students'], tier_to_id['scholars'])
                    seen.update(triple)
                    yield triple
        
    @property
    def aligned_triples(self):
        for ids in self.aligned_triple_ids:
            yield tuple(self.article_by_id(id_) if id_ in self.metadata else None
                        for id_ in ids)
    
    @property
    def kids_aligned(self):
        for kids_id, _, _ in self.aligned_triple_ids:
            if kids_id in self.metadata:
                yield self.article_by_id(kids_id)
    
    @property
    def students_aligned(self):
        for _, student_id, _ in self.aligned_triple_ids:
            if student_id in self.metadata:
                yield self.article_by_id(student_id)
    
    @property
    def scholars_aligned(self):
        for _, _, scholars_id in self.aligned_triple_ids:
            if scholars_id in self.metadata:
                yield self.article_by_id(scholars_id)
    
    @property
    def aligned(self):
        for kids_id, scholars_id, students_id in self.aligned_triple_ids:
            yield self.article_by_id(kids_id)
            yield self.article_by_id(scholars_id)
            yield self.article_by_id(students_id)
    
    @property
    def metadata(self):
        if not hasattr(self, '_metadata'):
            if self.metadata_filepath.exists():
                print('Loading metadata from file...')
                self._metadata = json.load(open(self.metadata_filepath, 'rt'))
            else:
                print("Building metadata from scratch...")
                print("This could take several minutes.")
                metadata_keys = ['id', 'url', 'tier', 'title', 'aligned_ids', 'aligned_urls']
                self._metadata = {}
                for article, article_path in zip(self.articles, self.article_paths):
                    article_metadata = {}
                    for key in metadata_keys:
                        if key in article:
                            article_metadata[key] = article[key]
                    article_metadata['path'] = article_path
                    
                    self._metadata[article_metadata['id']] = article_metadata
                print('Writing metadata to file...')
                write_json(self.metadata_filepath, self._metadata)
        return self._metadata
    
    @property
    def statistics(self):
        from .statistics import aggregate_statistics
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
    
    def copy_subset(self, article_ids, new_data_dir='data/kbds_aligned'):
        new_data_dir = Path(new_data_dir)
        make_directories(new_data_dir)
        article_dir = new_data_dir / 'articles'
        for article_id in article_ids:
            article = self.article_by_id(article_id)
            filename = f"{article['id']} {article['title']}.json"
            filename = sanitize_filename(filename)
            article_path = article_dir / article['tier'] / filename
            print(str(article_path))
            write_json(article_path, article)
        print(f'Wrote {len(article_ids)} articles to {str(article_dir)}')
    
    def medias_by_article_id(self, article_id, types=['IMAGE', 'VIDEO', 'AUDIO']):
            article = self.article_by_id(article_id)
            for media in article['media']:
                if media['data'] and media['media-type'] in types:
                    media_fp = self.media_dir / article['tier'] / sanitize_filename(f"{article['id']} {article['title']}") / f"{media['id']}.{media['data']['file-type']}"
                    media['filepath'] = str(media_fp)
                    yield media