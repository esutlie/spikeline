import pandas as pd


def make_meta_data():
    columns = ['description',
               'genotype',
               'sex',
               'species',
               'weight',
               'date_of_birth']
    meta_data = pd.DataFrame([
        ['ES029', 'wildtype', 'm', 'black 6', 25.4, '10-27-2021'],
        ['ES030', 'wildtype', 'f', 'black 6', 20.6, '04-10-2022'],
        ['ES031', 'wildtype', 'f', 'black 6', 23.7, '04-10-2022'],
        ['ES032', 'wildtype', 'f', 'black 6', 22.5, '04-10-2022'],
    ], columns=columns)
    pd.to_pickle(meta_data, 'meta_data.pkl')

def load_meta_data():
    meta_data = pd.read_pickle('meta_data.pkl')
    print(meta_data)

if __name__ == '__main__':
    load_meta_data()
