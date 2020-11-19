from kids_britannica import KidsBritannicaDataSet
import os
from pathlib import Path
from kids_britannica.utils import sanitize_filename
from kids_britannica.download import download_image, download_video, download_audio
from pprint import pprint

data_dir = Path('data')
ds = KidsBritannicaDataSet(data_dir)

media_dir = data_dir / 'media'
os.makedirs(media_dir, exist_ok=True)
os.makedirs(media_dir / 'kids', exist_ok=True)
os.makedirs(media_dir / 'students', exist_ok=True)
os.makedirs(media_dir / 'scholars', exist_ok=True)

for article in ds.articles:
    tier = article['tier']
    article_id = article['id']
    article_title = article['title']
    folder_name = f"{article_id} {article_title}"
    folder_name = sanitize_filename(folder_name)

    article_media_dir = media_dir / tier / folder_name
    os.makedirs(article_media_dir, exist_ok=True)

    for media in article['media']:
        try:
            media_type = media['media-type']
            media_id = media['id']
            media_file_type = media['data']['file-type']
            media_filename = f"{media_id}.{media_file_type}"
            output_path = article_media_dir / media_filename
            print(str(output_path))
            if not output_path.exists():
                if media_type == 'VIDEO':
                    continue
                    video_url = media['data']['manifest-url']
                    download_video(video_url, output_path)

                elif media_type == 'IMAGE':
                    continue
                    image_url = media['data']['src']
                    download_image(image_url, output_path)

                elif media_type == 'AUDIO':
                    audio_url = media['data']['src']
                    download_image(audio_url, output_path)
        except:
            pass