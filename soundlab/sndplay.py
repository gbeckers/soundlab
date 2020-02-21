import time
import threading
import numpy as np

__all__ = ['play']


# FIXME this really should be a class Player
def _play(snd, starttime, endtime, frames_per_buffer=1024*10):

    import pyaudio # here so that we only import dependency when really used

    startindex = int(np.round(snd.fs*starttime))
    endindex = int(np.round(snd.fs*endtime))

    snd.curpos = startindex
    snd._playing = True
    snd._stop_playing = False

    def callback(in_data, frame_count, time_info, status):
        startframe = min(snd.curpos, endindex)
        endframe = min(startframe + frame_count, endindex)
        data = snd.read_frames(startframe=startframe, endframe=endframe).astype(np.float32).tostring()
        snd.curpos = endframe
        if snd._stop_playing:
            callback_flag = pyaudio.paComplete
        else:
            callback_flag = pyaudio.paContinue
        return (data, callback_flag)


    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paFloat32,
                    channels=snd.nchannels,
                    rate=int(snd.fs),
                    output=True,
                    stream_callback=callback,
                    frames_per_buffer=frames_per_buffer)
    with snd.open():
        stream.start_stream()
        while stream.is_active():
            time.sleep(0.1)
        stream.stop_stream()
        stream.close()
        p.terminate()
        snd._playing = False

def play(snd, starttime, endtime):

    thread = threading.Thread(target=_play, args=(snd, starttime, endtime))
    thread.start()