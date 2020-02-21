from contextlib import contextmanager
import numpy as np
from snddata import Snd
from .utils import timeparams

__all__ = ['create_snddc', 'create_sndnoise']

def create_snddc(value=1.0, fs=44100, duration=10., ntimeframes=None,
                 nchannels=1, dtype='float32', startdatetime='NaT'):
    (ntimesamples, fs, duration) = timeparams(ntimesamples=ntimeframes, fs=fs, duration=duration)
    samples = np.empty((ntimesamples, nchannels), dtype=dtype)
    samples[:] = value
    return Snd(samples=samples, fs=fs, startdatetime=startdatetime)

def create_sndnoise(fs=44100, duration=10., ntimeframes=None,
                    nchannels=1, dtype='float32', startdatetime='NaT'):
    (ntimesamples, fs, duration) = timeparams(ntimesamples=ntimeframes, fs=fs, duration=duration)
    samples = np.random.random((ntimesamples, nchannels)) - 0.5
    if not np.issubdtype(dtype, samples.dtype):
        samples = samples.astype(dtype)
    return Snd(samples=samples, fs=fs, startdatetime=startdatetime)





# __all__ = ['dc', 'testdc', 'noise_episodes']
# def dc(sstor, name, value=0.0, fs=44100, duration=10.,
#        ntimeframes=None, nchannels=1, dtype='float32', h5c='performance',
#        overwrite=False):
#     (ntimeframes, fs, duration) = timeparams(ntimesamples=ntimeframes, fs=fs,
#                                              duration=duration)
#     snd = sb.create_sound(sstor=sstor, name=name, fs=fs, samples=None,
#                           ntimeframes=ntimeframes,
#                           nchannels=nchannels, scalefactor=1.0,
#                           startdatetime='NaT',
#                           timeorigin=0, dflt=value, dtype=dtype,
#                           overwrite=overwrite, h5c=h5c,
#                           nexpectedframes=ntimeframes)
#
#     return snd
#
#
# @contextmanager
# def testdc(value=0.0, fs=44100, duration=10., ntimeframes=None,
#            dtype='float32', h5c='performance'):
#     with sb.create_tempsstor(root='/') as sstor:
#         yield dc(sstor=sstor, name='dc', value=value, fs=fs, duration=duration,
#                  ntimeframes=ntimeframes, dtype=dtype, h5c=h5c)
#
#
# def noise_episodes(sstor, name, minnoisedur=0.015, maxnoisedur=0.5,
#                    minsilencedur=0.007, maxsilencedur=10., fs=44100,
#                    targetsounddur=60.*10,
#                    dtype='float32', h5c='performance', overwrite=False):
#     if not maxnoisedur <= targetsounddur:
#         raise ValueError("maxnoiseduration should not be larger than "
#                          "targetsounddur")
#     sndseq = sb.create_soundsequence(sstor=sstor, name=name, fs=fs,
#                           nchannels=1, scalefactor=1.0,
#                           startdatetime='NaT', dtype=dtype,
#                           overwrite=overwrite, h5c=h5c,
#                           nexpectedframes=int(targetsounddur*fs))
#     minnl = int(np.round(minnoisedur*fs))
#     maxnl = int(np.round(maxnoisedur*fs))
#     minsl = int(np.round(minsilencedur*fs))
#     maxsl = int(np.round(maxsilencedur*fs))
#     with sstor.open():
#         t = 0.0
#         while t < targetsounddur:
#             noiselen = np.random.randint(low=minnl,high=maxnl, size=None)
#             sndseq.append(samples=np.random.rand(noiselen,1)*2.-1.,
#                        starttime=t)
#             silencelen = np.random.randint(low=minsl,high=maxsl, size=None)
#             t += (noiselen+silencelen)/float(fs)
#     return sndseq
#
#
