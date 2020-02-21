import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from .sndplay import play
from .spectrotemporal import spectrogram
from .utils import eps

__all__ = ['ampprofile', 'maxprofile', 'pressureprofile', 'rmsprofile',
           'plot_ampprofile',
           'plot_pressureprofile', 'stft', 'Spectrogram']

def _iter_frames(snd, framesize, nframes=2000, starttime=None, endtime=None):

    framedur = framesize/float(snd.fs)
    if starttime is None:
        starttime = 0.
    if endtime is None:
        endtime = snd.duration
    for t in np.linspace(starttime, endtime-framedur, nframes):
        yield snd.read(starttime=t, endtime=t+framedur)

def _profile(funcs, varnames, snd, framesize, nframes, starttime=None,
             endtime=None):

    rd = {}
    for varname in varnames:
        rd[varname] = np.empty((nframes, snd.nchannels), dtype='float64')
    starttimes = np.empty(nframes, dtype='float64')
    endtimes = np.empty(nframes, dtype='float64')
    for i, frame in enumerate(_iter_frames(snd=snd, framesize=framesize,
                                           nframes=nframes, starttime=starttime,
                                           endtime=endtime)):
        for func, varname in zip(funcs, varnames):
            rd[varname][i] = func(frame.read_frames(), snd._timeaxis)
        starttimes[i] = frame.starttime
        endtimes[i] = frame.starttime + frame.duration

    dfs = []
    for chi in range(snd.nchannels):
        d = {  # 'starttime': np.array(starttimes, dtype='m8[ms]'),
            'starttime': starttimes,
            'endtime': endtimes}
        for varname in varnames:
            d['{}'.format(varname)] = rd[varname][:,chi]
        d = pd.DataFrame(d)[['starttime', 'endtime']+list(varnames)]
        dfs.append(d)
    return dfs

def _pressure(samples, timeaxis):
    mid = samples.shape[timeaxis]//2
    return np.take(samples, indices= [mid], axis=timeaxis)

# FIXME switch nframes and framesize
def pressureprofile(snd, framesize, nframes, starttime=None, endtime=None):
     return _profile(funcs=[_pressure], snd=snd, framesize=1, nframes=nframes,
                     starttime=starttime, endtime=endtime,
                     varnames=['pressureprofile'])


def _rms(samples, timeaxis):
    return np.power(np.mean(np.power(samples, 2.), axis=timeaxis), 0.5)

def rmsprofile(snd, framesize, nframes, starttime=None, endtime=None):
     return _profile(funcs=[_rms], snd=snd, framesize=framesize, nframes=nframes,
                     starttime=starttime, endtime=endtime,
                     varnames=['rmsprofile'])

def _max(samples, timeaxis):
    return np.max(samples, axis=timeaxis)

def maxprofile(snd, framesize, nframes, starttime=None, endtime=None):
     return _profile(funcs=[_max], snd=snd, framesize=framesize, nframes=nframes,
                     starttime=starttime, endtime=endtime,
                     varnames=['maxprofile'])

def _min(samples, timeaxis):
    return np.min(samples, axis=timeaxis)

def minprofile(snd, framesize, nframes, starttime=None, endtime=None):
     return _profile(funcs=[_min], snd=snd, framesize=framesize, nframes=nframes,
                     starttime=starttime, endtime=endtime,
                     varnames=['maxprofile'])

def ampprofile(snd, framesize=4100, nframes=1000, starttime=None, endtime=None):
    return _profile(funcs=[_max, _min, _rms], snd=snd, framesize=framesize,
                    nframes=nframes, starttime=starttime, endtime=endtime,
                    varnames=['maxprofile', 'minprofile', 'rmsprofile'])


# def spectrogram(snd, framesize=512, nt=1000, starttime=None, endtime=None,
#                 window='hann'):
#     window = scipy.signal.windows.get_window(window, framesize)
#     scale = 1.0 / window.sum() ** 2
#     freqs = np.fft.helper.rfftfreq(framesize, d=1/float(snd.fs))
#     input = np.empty((nt, framesize, snd.nchannels), dtype=snd.dtype)
#     starttimes = np.empty(nt, dtype='float64')
#     endtimes = np.empty(nt, dtype='float64')
#     frameduration= framesize / float(snd.fs)
#     for i,frame in enumerate(_iter_frames(snd=snd, framesize=framesize,
#                                           nframes=nt,
#                               starttime=starttime, endtime=endtime)):
#         input[i] = frame.samples * window[:,np.newaxis]
#         starttimes[i] = frame.starttime
#         endtimes[i] = frame.starttime + frameduration
#     v = np.fft.rfft(input, axis=1)
#     sg = 10 * np.log10(np.abs(v * v.conjugate() * scale) + eps)
#     return starttimes, endtimes, freqs, sg

# def spectrogram(snd, framesize=512, nt=1000, startframe=None, endframe=None,
#                 starttime=None, endtime=None, window='hann'):
#     window = scipy.signal.windows.get_window(window, framesize)
#     scale = 1.0 / window.sum() ** 2
#     freqs = np.fft.helper.rfftfreq(framesize, d=1/float(snd.fs))
#     input = np.empty((nt, framesize, snd.nchannels), dtype=snd.dtype)
#     starttimes = np.empty(nt, dtype='float64')
#     endtimes = np.empty(nt, dtype='float64')
#     windowdur = framesize / float(snd.fs)
#     for i,w in enumerate(snd.iter_samplewindows(windowsize=framesize,
#                                                 nwindows=nt,
#                                                 startframe=startframe,
#                                                 endframe=endframe,
#                                                 starttime=starttime,
#                                                 endtime=endtime)):
#         input[i] = w.samples * window[:,np.newaxis]
#         starttimes[i] = w.starttime
#         endtimes[i] = w.starttime + windowdur
#     v = np.fft.rfft(input, axis=1)
#     sg = 10 * np.log10(np.abs(v * v.conjugate() * scale) + eps)
#     return starttimes, endtimes, freqs, sg




class _PlotDisplay(object):

    def __init__(self, snd, starttime, endtime):
        self.snd = snd
        self.minstarttime = 0.0 if starttime is None else starttime
        self.maxendtime = snd.duration if endtime is None else endtime
        # self.delta = self.maxendtime - self.minstarttime

        self.fig, self.axes = plt.subplots(nrows=snd.nchannels, ncols=1,
                                           sharex=True, squeeze=False,
                                           figsize=(12, 3 * snd.nchannels))
        plt.tight_layout()
        self.lims = self.axes[0][0].viewLim
        self._format_axes()

    def _format_axes(self):
        for ax, in self.axes:
            ax.set_facecolor('#EAEAF2')
            plt.setp(list(ax.spines.values()), color='white')
            plt.setp([ax.get_xticklines(), ax.get_yticklines()], color='white')

    def play(self, *args, **kwargs):
        starttime, endtime = self.lims.x0, self.lims.x1
        play(snd=self.snd, starttime=starttime, endtime=endtime)

    def stop_playing(self, *args, **kwargs):
        self.snd._stop_playing=True


class _AmpDisplay(_PlotDisplay):

    def __init__(self, snd, framesize, nt, starttime=None,
                 endtime=None, func=ampprofile, plotkwargs=None,
                 waveformmaxdur=0.5, autoframesize=True, minframesize=None):

        super(self.__class__, self).__init__(snd=snd, starttime=starttime,
                                        endtime=endtime)

        self.framesize = framesize
        self.curframesize = framesize
        self.nt = nt
        self.autoframesize = autoframesize
        self.minframesize = minframesize if minframesize is not None else int(
            self.snd.fs / 100.)
        self.func = func
        self.plotkwargs = plotkwargs if plotkwargs is not None else {}
        self.waveformaxdur = waveformmaxdur
        self.waveformlines = None
        self.dfs = dfs = self._zoom(self.minstarttime, self.maxendtime)
        self.varnames = sorted([cn for cn in list(dfs[0].columns.values) if
                                cn not in ('starttime', 'endtime')])
        self.lines = self._plot()
        for (ax,) in self.axes:
            ax.set_autoscale_on(False)  # Otherwise, infinite loop
            ax.callbacks.connect('xlim_changed', self._update)


    def _plot(self):
        lines = []
        for (ax,), df in zip(self.axes, self.dfs):
            axlines = []
            time = (df['starttime'] + df['endtime']) / 2.0
            for varname in self.varnames:
                plotkwargs = self.plotkwargs.get(varname, {})
                line, = ax.plot(time, df[varname], **plotkwargs)
                axlines.append(line)
            lines.append(axlines)
        return lines


    def _plot_waveform(self, starttime, endtime):
        lines = []
        rs = self.snd.read(starttime=starttime, endtime=endtime)
        for chn, (ax,) in enumerate(self.axes):
            plotkwargs = {'color': 'black', 'linewidth': 1.0}
            line, = ax.plot(rs.samplingtimes + rs.starttime, rs.samples[:, chn],
                            **plotkwargs)
            lines.append(line)
        return lines


    def _zoom(self, starttime, endtime):
        self.snd._stop_playing = True
        if starttime < self.minstarttime:
            starttime = self.minstarttime
        if endtime > self.maxendtime:
            endtime = self.maxendtime
        duration = endtime - starttime
        if duration <= self.waveformaxdur:
            self.waveformlines = self._plot_waveform(starttime, endtime)
        elif self.waveformlines is not None:
            for i in range(len(self.waveformlines)):
                self.waveformlines.pop(0).remove()
            self.waveformlines = None

        if self.autoframesize:
            ntimeframes = int(duration * self.snd.fs)
            framesize = int(max(self.minframesize,
                                min(self.framesize,
                                    (ntimeframes / float(self.nt)))))
        else:
            framesize = self.framesize
        self.curframesize = framesize
        return self.func(snd=self.snd, framesize=framesize,
                         nframes=self.nt, starttime=starttime,
                         endtime=endtime)

    def _update(self, ax):
        self.lims = lims = ax.viewLim
        # if np.abs(lims.width - self.delta) > 1e-8:
        #     self.delta = lims.width
        xstart, xend = lims.intervalx
        self.dfs = dfs = self._zoom(xstart, xend)
        time = (dfs[0]['endtime'] + dfs[0]['starttime']) / 2.0
        for j, ((ax,), df) in enumerate(zip(self.axes, dfs)):
            for i, varname in enumerate(self.varnames):
                self.lines[j][i].set_data(time, df[varname])
        ax.figure.canvas.draw_idle()

class Spectrogram(_PlotDisplay):


    def __init__(self, snd, nt=1000, starttime=None, endtime=None,
                 nperseg=512, nfft=1024, cmap='viridis', dynrange=(-75., -35.),
                 maxfreq=10e3):
        super(self.__class__, self).__init__(snd=snd, starttime=starttime,
                                             endtime=endtime)
        self.nt = nt
        self.nperseg = nperseg
        self.nfft = nfft
        self.cmap = cmap
        self.dynrange = dynrange
        self.maxfreq = maxfreq
        self.freqscalingfactor = 1e-3
        self.sgs = self._calc_specgrams(starttime=self.minstarttime, endtime=self.maxendtime)
        self.starttime = 0.
        self.endtime = snd.duration
        self.ais = self._imshow()
        for (ax,) in self.axes:
            ax.set_autoscale_on(False)  # Otherwise, infinite loop
            ax.callbacks.connect('xlim_changed', self._xlim_changed)
        self.fig.canvas.mpl_connect('key_press_event', self._keypress)


    def _keypress(self, event):
        if event.key == 'ctrl+i':
            self._zoomin()
        elif event.key == 'ctrl+o':
            self._zoomout()
        elif event.key == 'ctrl+f':
            self._forward()
        elif event.key == 'ctrl+b':
            self._backward()


    def _zoomin(self):
        starttime, endtime = self.lims.intervalx
        midtime = (starttime + endtime) / 2.
        dur = endtime - starttime
        newstarttime = midtime - dur / 4.
        newendtime = midtime + dur / 4.
        for (ax,) in self.axes:
            ax.set_xlim(newstarttime, newendtime)

    def _zoomout(self):
        starttime, endtime = self.lims.intervalx
        midtime = (starttime + endtime) / 2.
        dur = endtime - starttime
        newstarttime = midtime - dur
        newendtime = midtime + dur
        for (ax,) in self.axes:
            ax.set_xlim(newstarttime, newendtime)

    def _forward(self):
        starttime, endtime = self.lims.intervalx
        dur = endtime - starttime
        timeshift = 0.9 * dur
        newstarttime = starttime + timeshift
        newendtime = endtime + timeshift
        for (ax,) in self.axes:
            ax.set_xlim(newstarttime, newendtime)

    def _backward(self):
        starttime, endtime = self.lims.intervalx
        dur = endtime - starttime
        timeshift = 0.9 * dur
        newstarttime = starttime - timeshift
        newendtime = endtime - timeshift
        for (ax,) in self.axes:
            ax.set_xlim(newstarttime, newendtime)

    def _imshow(self):
        ais = []
        start, end = self.starttime,self.endtime
        # if str(self.snd.startdatetime) != 'NaT':
        #     start, end = self.snd.sndtime_to_datetime([start, end])
        clim = self.dynrange
        for (ax,), sg in zip(self.axes, self.sgs):
            # if str(self.snd.startdatetime) != 'NaT':
            #     ax.xaxis_date()
            #     date_format = matplotlib.dates.DateFormatter('%H:%M:%S')
            #     ax.xaxis.set_major_formatter(date_format)
            extent = [start, end, 0., self.freqscalingfactor*self.snd.fs//2]
            ai = ax.imshow(sg, extent=extent, origin='lower',
                           interpolation='nearest', aspect='auto',
                           cmap=self.cmap, clim=clim)
            ax.set_ylim(0., self.maxfreq*self.freqscalingfactor)
            ais.append(ai)
        return ais

    def set_cmap(self, cmap):
        for ai in self.ais:
            ai.set_cmap(cmap)

    def set_clim(self, clim):
        for ai in self.ais:
            ai.set_clim(clim)
        self.fig.canvas.draw()

    set_dynrange = set_clim

    def set_freqrange(self, freqrange):
        for (ax,) in self.axes:
            ax.set_ylim(freqrange)

    def set_nt(self, nt):
        self.nt=nt
        self._xlim_changed(self.axes[0][0])

    def set_nperseg(self, nperseg):
        self.nperseg=nperseg
        self.nfft = max(self.nfft, nperseg)
        self._xlim_changed(self.axes[0][0])

    def set_nfft(self, nfft):
        nfft = max(nfft, self.nperseg)
        self.nfft=nfft
        self._xlim_changed(self.axes[0][0])

    def set_freqsmoothing(self, factor):
        self.set_nfft(int(factor*self.nperseg))

    def _calc_specgrams(self, starttime, endtime):
        self.snd._stop_playing = True
        if starttime < self.minstarttime:
            starttime = self.minstarttime
        if endtime > self.maxendtime:
            endtime = self.maxendtime
        f,t,sgs = spectrogram(self.snd,
                          nperseg=self.nperseg,
                          nfft=self.nfft,
                          nt=self.nt,
                          starttime=starttime,
                          endtime=endtime)
        psgs = 10*np.log10(sgs + eps)
        # psgs = [np.flipud(np.rot90(psgs[:,:,chi])) for chi in range(psgs.shape[-1])]
        return [psgs[:,:,i] for i in range(psgs.shape[-1])]

    def _xlim_changed(self, ax):
        self.lims = lims = ax.viewLim
        # if np.abs(lims.width - self.delta) > 1e-8:
        # self.delta = lims.width
        xstart, xend = lims.intervalx
        # ax.set_xlabel('{}-{}'.format(xstart,xend))
        self.sgs = \
                self._calc_specgrams(xstart, xend)
        self.starttime, self.endtime = xstart,xend
        # times = (self.starttimes + self.endtimes) / 2.
        for ai, sg in zip(self.ais, self.sgs):
            ai.set_data(sg)
            ai.set_extent([self.starttime, self.endtime, 0., self.freqscalingfactor*self.snd.fs//2.])
        # ax.figure.canvas.draw_idle()
        # ax.figure.canvas.blit()


def plot_ampprofile(snd, framesize=44100, nframes=1000, starttime=None,
                   endtime=None, waveformmaxdur=2.0, autoframesize=True,
                    plotkwargs=None):

    pa = {'rmsprofile': {'linewidth': 1.0, 'color': '#a03623'},
          'maxprofile': {'linewidth': 1.0, 'color': '#047495'},
          'minprofile': {'linewidth': 1.0, 'color': '#047495'},
          'pressure': {'linewidth': 1.0, 'color': '#cccccc'}}

    if plotkwargs is not None:
        pa.update(plotkwargs)

    d = _AmpDisplay(snd=snd, framesize=framesize, nt=nframes,
                    starttime=starttime, endtime=endtime, func=ampprofile,
                    plotkwargs=pa,
                    waveformmaxdur=waveformmaxdur,
                    autoframesize=autoframesize)
    return d


def plot_pressureprofile(snd, nframes=1000, starttime=None, endtime=None):
    d = _AmpDisplay(snd=snd, framesize=1, nt=nframes,
                    starttime=starttime, endtime=endtime, func=pressureprofile)

    return d