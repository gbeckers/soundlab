import numpy as np
import pandas as pd

__all__ = ['calc_features', 'featurefunctions']

def rms(samples, **kwargs):
    return np.mean(samples**2.0)**0.5

def maxamp(samples, **kwargs):
    return np.max(samples)

def minamp(samples, **kwargs):
    return np.min(samples)

def duration(samples, fs, **kwargs):
    return len(samples)/float(fs)

featurefunctions = {'rms': rms,
                    'maxamp': maxamp,
                    'minamp': minamp,
                    'duration': duration}

def calc_features(soundlist, soundepisodes, featurefunctions=featurefunctions):

    features = [] # list of channels
    for i in range(soundlist.nchannels):
        features.append(dict((key, []) for key, _ in featurefunctions.items()))
    for index,rowdict in soundepisodes.iterrows():
        rs = soundlist.read_byindex(**rowdict)
        for i in range(soundlist.nchannels):
            for featurename, featurefunction in featurefunctions.items():
                samples = rs.samples.take(i, axis=soundlist._channelaxis)
                features[i][featurename].append(featurefunction(samples=samples,
                                                                fs=rs.fs))
    dfs = []
    for i in range(soundlist.nchannels):
        df = pd.DataFrame(features[i], index=soundepisodes.index)
        df= pd.merge(soundepisodes,df, left_index=True, right_index=True)
        dfs.append(df)
    return dfs