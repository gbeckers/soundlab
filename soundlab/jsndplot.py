from ipywidgets import widgets
from IPython.display import display
from . import sndplot

__all__ = ['jspecgram']

def jspecgram(snd, nt=1000, starttime=None, endtime=None,
                 nperseg=512, freqsmoothing=1, cmap='viridis', dynrange=(-90., -40.),
                 maxfreq=10e3):
    nfft = int(nperseg*freqsmoothing)
    d = sndplot.Spectrogram(snd, nt=nt, starttime=starttime, endtime=endtime,
                            nperseg=nperseg, nfft=nfft, cmap=cmap, dynrange=dynrange,
                            maxfreq=maxfreq)
    button_play = widgets.Button(description='play')
    button_play.on_click(d.play)
    button_stop = widgets.Button(description='stop')
    button_stop.on_click(d.stop_playing)
    display(widgets.HBox((button_play, button_stop)))
    drs = widgets.FloatRangeSlider(value=(-75, -35), min=-120, max=0, step=1, description='dynamic range (dB)')
    drs.observe(lambda change: d.set_clim(change['new']), names='value')
    display(drs)
    freqs = widgets.FloatRangeSlider(value=(0, 10), min=0, max=snd.fs/2e3, step=0.1,
                                     description='frequency range (kHz)')
    freqs.observe(lambda change: d.set_freqrange(change['new']), names='value')
    display(freqs)
    npersegw = widgets.IntText(value=nperseg, min=1, max=4096 * 2,
                               description='nperseg')
    npersegw.observe(lambda change: d.set_nperseg(change['new']),
                     names='value')
    display(npersegw)
    return d