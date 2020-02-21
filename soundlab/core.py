import numpy as np
import pandas as pd

__all__ = ['soundepisodes', 'read_sound', 'iterread_sounds']

def soundepisodes(soundlist):
    df = pd.DataFrame(soundlist.read_records()).drop(['_startframe'], axis=1)
    colnames = df.columns.tolist()
    colnames.insert(0, 'startframe')
    df.loc[:,'startframe'] = pd.Series(np.zeros(len(df)), index=df.index)
    colnames.insert(0, 'soundindex')
    df.loc[:,'soundindex'] = pd.Series(df.index.values, index=df.index)
    df = df[colnames]
    df.rename(columns={'ntimeframes': 'endframe'}, inplace=True)
    return df

def read_sound(soundlist, soundepisodes, soundindex):
    return soundlist.read_byindex(**soundepisodes.loc[soundindex])

def iterread_sounds(soundlist, soundepisodes, soundindices=None):
    if not soundindices is None:
        soundepisodes = soundepisodes.loc[soundindices]
    with soundlist._db.open():
        for index, row in soundepisodes.iterrows():
            yield soundlist.read_byindex(**row)


