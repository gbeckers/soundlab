"""
This module provides functions to convert audio files from one format into
another.

All audio file conversion is done by sox (http://http://sox.sourceforge.net/),
via the python package pysox (https://github.com/rabitt/pysox).

"""

__all__ = ['convert_audiofile_to_audiofile', 'convert_audioglob']

import os
import glob

def convert_audiofile_to_audiofile(inputfilepath, outputfilepath,
                                   outputformat=None, inputformat=None):
    """ Convert an audiofile into a new audiofile with a different format

    Parameters
    ----------
    inputfilepath: string
    outputfilepath: string
    outputformat: dictionary, None (default)
        A dictionary of parameters that the conversion library (sox) uses to
        determine the output format (in addition to filename extension). Valid
        keys are: file_type, rate, bits, channels, encoding, comments,
        append_comments.
    inputformat: dictionary, None (default)
        A dictionary of parameters that the conversion library (sox) uses to
        determine the input format. This is primarily useful when dealing
        with audio files without a file extension. Overwrites any previously
        set input file arguments. If this function is not explicitly called the
        input format is inferred rom the file extension or the file's header.
        Valid keys are file_type, rate, bits, channels, encoding,
        ignore_length.

    Examples
    --------
    >>>convert_audiofile('noise.wav', 'noise.mp3')
    >>>convert_audiofile('noise.wav', 'noise_16bits.wav',
    ...                  outputformat={'bits: 16'})
    >>>convert_audiofile('noise', 'noise.mp3',
    ...                  inputformat={'filetype': 'wav')

    """

    import sox  # here so that we only import dependency when really used

    tfm = sox.Transformer(inputfilepath, outputfilepath)
    if outputformat is not None:
        tfm.set_output_format(**outputformat)
    if inputformat is not None:
        tfm.set_input_format(**inputformat)
    tfm.build()


# def iter_filenames(dirpath, extensions):
#     return (f for f in os.listdir(dirpath)
#               if (os.path.isfile(os.path.join(dirpath, f))
#                   and os.path.splitext(f)[1] in extensions))


def convert_audioglob(globpattern, outputfiletype,
                     outputformat=None, outputdirpath='./converted'):
    for ifp in glob.iglob(globpattern):
        ifd,ifn = os.path.split(ifp)
        odp = os.path.join(outputdirpath, ifd)
        if not os.path.exists(odp):
            os.makedirs(odp)
        ofp = os.path.join(odp, '{}.{}'.format(os.path.splitext(ifn)[0], outputfiletype))
        convert_audiofile_to_audiofile(ifp, ofp, outputformat=outputformat)
