# kids_britannica

## Usage

To learn how to use this library, see this Colab notebook: https://colab.research.google.com/drive/1r1xf4Xnk2Vej_l6GxiqFkxg89YFBqYQY

or follow this short code snippet:
```bash
pip install -q "git+https://github.com/josephcappadona/kids_britannica#egg=kids_britannica"
```

```python
from kids_britannica import KidsBritannicaDataSet as KBDS

data_path = KBDS.download(size='small', data_dir='data')
#data_path = KBDS.download(size='aligned', data_dir='data')
#data_path = KBDS.download(size='full', data_dir='data')

ds = KBDS(data_path)
```

The `KidsBritannicaDataSet` object possesses a variety of properties,

Metadata:
* `metadata`
* `statistics`

Article generators:
* `articles`
* `kids_articles`
* `kids_article_paths`
* `students_articles`

Aligned* article generators:
* `aligned_triple_ids`
* `aligned_triples`
* `aligned_kids`
* `aligned_students`
* `aligned_scholars`
* `aligned`

*Articles are "aligned" if there exists a version in all three tiers

Iterate over all articles:

```python
for article in ds.articles:
    print(article['title'])
```

or a subset of articles
```python
for article in ds.kids_articles:
    print(article['title'])
```

or aligned articles
```python
for article in ds.aligned:
    print(article['tier'], article['title'])
```


## Data

### Data Statistics:

#### All articles
|                                | kids     | students    | scholars    |
| ----                           | ----     | ----        | ----        |
|# articles                      | 4775     | 22128       | 104916      |
|# tokens                        | 1.89M    | 16.47M      | 108.49M     |
|avg # paragraphs per article    | 6.7      | 8.1         | 9.0         |
|avg # sentences per article     | 28.3     | 38.1        | 39.2        |
|avg # tokens per article        | 394.9    | 744.5       | 1034.1      |
|avg sentence parse height       | 5.3      | 6.1         | 7.1         |
|avg # entities per sentence     | 1.5      | 2.0         | 2.3         |
|avg # noun phrases per sentence | 3.7      | 4.8         | 6.3         |


#### Aligned articles

Aligned articles are only those articles that have versions in all 3 tiers

|                                | kids     | students    | scholars    |
| ----                           | ----     | ----        | ----        |
|# articles                      | 3948     | 3948        | 3948        |
|# tokens                        | 1.56M    | 7.76M       | 34.61M      |
|avg # paragraphs per article    | 6.6      | 21.7        | 66.0        |
|avg # sentences per article     | 28.3     | 102.1       | 322.6       |
|avg # tokens per article        | 395.9    | 1965.6      | 8765.7      |
|avg sentence parse height       | 5.3      | 6.12        | 7.2         |
|avg # entities per sentence     | 1.4      | 1.7         | 2.2         |
|avg # noun phrases per sentence | 3.7      | 4.8         | 6.5         |

## Changelog

* v0.2 - Improved interface, removed bloat, added `KBDS.aligned`

* v0.1 - Initial launch