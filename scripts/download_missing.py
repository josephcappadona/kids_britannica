from kids_britannica import KidsBritannicaDataSet
from kids_britannica.scraping import *
ds = KidsBritannicaDataSet('data')

all_aligned_ids = set()
triples = set()
limit = None
for md in ds.metadata.values():
    if len(set( list(md['adjacent_ids'].keys()) + [md['tier']] )) == 3:
        id_ = md['id']
        if md['tier'] == 'kids' and (limit is None or len(triples) < limit):
            k_id = id_
            st_id = md['adjacent_ids']['students']
            sc_id = md['adjacent_ids']['scholars']
        elif md['tier'] == 'students' and (limit is None or len(triples) < limit):
            k_id = md['adjacent_ids']['kids']
            st_id = id_
            sc_id = md['adjacent_ids']['scholars']
        elif md['tier'] == 'scholars' and (limit is None or len(triples) < limit):
            k_id = md['adjacent_ids']['kids']
            st_id = md['adjacent_ids']['students']
            sc_id = id_
        all_aligned_ids.add(k_id)
        all_aligned_ids.add(st_id)
        all_aligned_ids.add(sc_id)
        triple = (k_id, st_id, sc_id)
        triples.add(triple)

print('n_triples', len(triples))
new_ids = set(id_ for id_ in all_aligned_ids if id_ not in ds.metadata)
print(f"Found {len(new_ids)} new articles")

session = requests.Session()
session.post('https://kids.britannica.com/login',
             data = {'username' : 'ccb@upenn.edu',
                     'password' : 'mjQDHHCMk3KnUL'})

for new_id in new_ids:
    url = f"https://kids.britannica.com/scholars/article/{new_id}"
    scrape_htmls(url, session=session)