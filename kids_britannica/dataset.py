from .imports import *
from .utils import *

def Article(p):
    try:
        return json.load(open(p))
    except:
        # if error with filename, glob for the article by its id
        path = Path(p)
        query = str(p.parent / f"{p.stem.split(' '[0])} *.json")
        fps = glob(query)
        if fps:
            return fps[0]
        else:
            return None
        

class KidsBritannicaDataSet:
    @staticmethod
    def download(size='small', data_dir='data', quiet=False, download_media=False, overwrite=False):
        import gdown, zipfile

        data_dir = Path(data_dir)
        os.makedirs(data_dir, exist_ok=True)
        if size == 'full':
            url = 'https://drive.google.com/uc?id=1lPZr1d6Hj2tcSrfZpaUHX-sEK9og-g70'
            full_dir = data_dir / 'kbds'
            output = full_dir / 'kbds_articles.zip'
        elif size == 'aligned':
            url = 'https://drive.google.com/uc?id=1G3zTflSwHMBW-uj17MOkbG2s_MhE5NiE'
            aligned_dir = data_dir / 'kbds_aligned'
            output =  aligned_dir / 'kbds_aligned_articles.zip'
        elif size == 'small':
            url = 'https://drive.google.com/uc?id=1y90AXopy9yx3wHg2zuoyEGSrbCrRp-Kv'
            output = data_dir / 'kbds_small.zip'
        else:
            raise ValueError(f'Invalid `size` ({size}): should be "small" or "full".')
        
        output_dir = output.parent
        articles_dir = output_dir / 'articles'
        if not output_dir.exists() or overwrite:
            os.makedirs(output_dir, exist_ok=True)
            print(f'Downloading {output.name} from {url} ...')
            gdown.download(url, str(output), quiet=quiet)
            with zipfile.ZipFile(output, 'r') as zip_ref:
                zip_ref.extractall(output_dir)
            # rm zip
            os.remove(output)
            print(f'Wrote {output_dir}')
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
                print("This could take anywhere from a few seconds to a several minutes depending "
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
            write_json(article_path, article)
        print(f'Wrote {len(article_ids)} to {str(article_path)}')

