from .imports import *


SLEEP_TIME = 1  # 100ms

def make_directories(data_dir='data'):
    data_dir = Path(data_dir)
    articles_dir = data_dir / 'articles'
    media_dir = data_dir / 'media'
    kids_dir = articles_dir / 'kids'
    students_dir = articles_dir / 'students'
    scholars_dir = articles_dir / 'scholars'
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(articles_dir, exist_ok=True)
    os.makedirs(media_dir, exist_ok=True)
    os.makedirs(kids_dir, exist_ok=True)
    os.makedirs(students_dir, exist_ok=True)
    os.makedirs(scholars_dir, exist_ok=True)

def exists(obj):
    return obj is not None

def clean_text(text):
    return ' '.join(text.split())

def print_article_summary(article):
    """Prints a summary of the specified article.

    Args:
        article: A dictionary, the article to summarize.
    """
    print(article['title'])
    print(article['url'])
    n_sections = len(article['text'])
    n_words = 0
    for section_title, section_text in article['text']:
        for paragraph in section_text:
            n_words += len(paragraph.split())
    print(f"{n_sections} section(s) containing {n_words} words")
    n_media = len(article['media'])
    n_images = len([m for m in article['media'] if m['media-type'] == 'IMAGE'])
    n_videos = len([m for m in article['media'] if m['media-type'] == 'VIDEO'])
    n_audios = len([m for m in article['media'] if m['media-type'] == 'AUDIO'])
    print(f"{n_media} piece(s) of media consisting of {n_images} image(s), {n_videos} video(s), and {n_audios} audio(s)")
    n_related_articles = len(article['related_articles'])
    n_related_websites = len(article['related_websites'])
    print(f"{n_related_articles} related article(s) and {n_related_websites} related website(s)")

def write_json(output_path, data):
    with open(output_path, 'w+') as f:
        json.dump(data, f)

def get_saved_ids(data_dir):
    data_dir = Path(data_dir)
    json_paths = glob(str(data_dir / 'articles' / '*' / '*.json'))
    ids = {Path(json_path).stem.split(' ')[0] for json_path in json_paths}
    return ids

def get_chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

all_letters = set(string.ascii_letters + string.digits + " .,;'")
def sanitize_filename(filename):
    return ''.join(
        c for c in unicodedata.normalize('NFD', filename)
        if unicodedata.category(c) != 'Mn'
        and c in all_letters
    )

IMG_FILE_TYPES = set(['.png', '.jpg', '.jpeg', '.gif'])
AUDIO_FILE_TYPES = set(['.wav', '.mp3', '.m4a'])
VIDEO_FILE_TYPES = set(['.avi', '.mp4', '.flv'])
FILE_TYPES = IMG_FILE_TYPES.union(AUDIO_FILE_TYPES).union(VIDEO_FILE_TYPES)
def unzip(zip_output, data_dir):
    from .zipfile2 import ZipFile
    with ZipFile(zip_output, 'r') as zip_ref:
        zip_ref.extractall(zip_output.parent)

def download_and_unzip(url, zip_output, overwrite=False, delete_zip=False):
    
    print(f'Downloading {zip_output.name} from {url} ...')
    if not zip_output.exists() or overwrite:
        import gdown
        gdown.download(url, str(zip_output), quiet=False)
    
    data_dir = zip_output.parent
    unzip(zip_output, data_dir)
    
    if delete_zip:
        os.remove(zip_output)
    print(f'Wrote {str(zip_output.parent)}')

