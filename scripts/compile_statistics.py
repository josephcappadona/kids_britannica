from kids_britannica import KidsBritannicaDataSet
from pprint import pprint
ds = KidsBritannicaDataSet('data')
stats = ds.statistics
pprint(stats)