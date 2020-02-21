import numpy as np
import scipy.signal
from .utils import check_episode

__all__ = ['spectrogram']


# for reference only
def _spectrogram_scipy(snd, window=('tukey', 0.25), nperseg=256, noverlap=None,
                       nfft=None, detrend='constant', return_onesided=True,
                       scaling='density'):# , mode='psd'): # for new scipy
    f, t, Sxx = scipy.signal.spectrogram(x=snd.read_frames(), fs=snd.fs,
                                        window=window,
                                        nperseg=nperseg,
                                        noverlap=noverlap,
                                        nfft=nfft,
                                        detrend=detrend,
                                        return_onesided=return_onesided,
                                        scaling=scaling, axis=0)# ,
                                        # mode=mode)
    return f, t, Sxx


def spectrogram(snd, nt=1000, nperseg=512, nfft=None, scaling='density',
                window='hann', startframe=None, endframe=None,
                starttime=None, endtime=None, dtype=np.float64):
    startframe, endframe = check_episode(startframe=startframe,
                                         endframe=endframe,
                                         starttime=starttime,
                                         endtime=endtime,
                                         fs=snd.fs,
                                         nframes=snd.nframes)
    nperseg = int(nperseg)
    if nperseg < 1:
        raise ValueError('nperseg must be a positive integer')
    if nfft is None:
        nfft = nperseg
    elif nfft < nperseg:
        raise ValueError('nfft must be greater than or equal to nperseg.')
    else:
        nfft = int(nfft)
    nt = int(nt)
    if nt < 1:
        raise ValueError('nt must be larger than zero.')
    window = scipy.signal.windows.get_window(window, nperseg)
    f = np.fft.rfftfreq(n=nfft, d=1 / float(snd.fs))
    if scaling == 'density':
        scale = 1.0 / (snd.fs * (window * window).sum())
    elif scaling == 'spectrum':
        scale = 1.0 / window.sum() ** 2
    else:
        raise ValueError('Unknown scaling: %r' % scaling)
    input = np.zeros((nfft, nt, snd.nchannels), dtype=dtype)
    starts = np.linspace(startframe, endframe - nperseg, nt, dtype='int64')
    t = (starts.astype('float64') + nperseg / 2.0) / float(snd.fs)
    with snd.open():
        for i, start in enumerate(starts):
            input[:nperseg,i] = snd.read_frames(startframe=start,
                                                 endframe=start + nperseg).astype(dtype)
    input[:nperseg] *= window[:,np.newaxis, np.newaxis]
    v = np.fft.rfft(input, axis=0)
    sg = np.abs(v * v.conjugate()) * scale
    if nfft % 2:
        sg[1:] *= 2
    else:
        # Last point is unpaired Nyquist freq point, don't double
        sg[1:-1] *= 2
    return f, t, sg

