import logging
from pandas import DataFrame, Series

logging.basicConfig(filename='foo.log', filemode='w', level=logging.INFO, format='%(message)s')
logging.info('asd')
dataframe = DataFrame({'keys':[1, 0], 'state':[3, 2]})
logging.info(dataframe.to_string())