from kids_britannica import KidsBritannicaDataSet
from kids_britannica.scraping import *
#ds = KidsBritannicaDataSet('data')
session = requests.Session()
session.post('https://kids.britannica.com/login',
             data = {'username' : 'ccb@upenn.edu',
                     'password' : 'mjQDHHCMk3KnUL'})
url = "https://kids.britannica.com/scholars/article/Alaska/111277"
_, sections, _ = get_article_text(None, article_url=url, session=session)
print(sections[0])
