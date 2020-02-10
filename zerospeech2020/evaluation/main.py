#!/usr/bin/env python
"""Evaluate submission for the zerospeech2020 challenge"""
import sys
import logging
import argparse
from .evaluation_2020 import Evaluation2020

# setup logging
logging.basicConfig(format='%(message)s', level=logging.DEBUG)
log = logging.getLogger()


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter,
        description=__doc__,
        epilog='See https://zerospeech.com/2020 for complete documentation')
    parser.add_argument(
        'submission',
        help='path to submission (can be a directory or a zip archive)')
    parser.add_argument(
        'output',
        help="path to the output folder. If doesn't exist, will be created")
    parser.add_argument(
        '-j', '--njobs', type=int, default=1, help="Number of jobs")

    # define subparsers for editions/tracks
    subparser = parser.add_subparsers(
        help='''Choose the edition you want to evaluate. Choices are
        2017, 2019, both. If None are chosen, will try to evaluate everything
        with default settings.''',  dest="edition")
    parser_17 = subparser.add_parser('2017')
    parser_19 = subparser.add_parser('2019')
    parser_all = subparser.add_parser('both')

    # if 2017 edition chosen
    parser_17.add_argument(
        '-l', '--language', default=None,
        choices=['english', 'french', 'mandarin', 'lang1', 'lang2'],
        help='Choose language to evaluate. If None chosen, '
        'all will be evaluated.')

    subparser_17 = parser_17.add_subparsers(
        help='''Choose which track of the 2017 Challenge you want to evaluate.
        Choices are track1, track2. If None are chosen, will try to evaluate
        all with default settings.''', dest="track")
    track1_17 = subparser_17.add_parser('track1')

    track1_17.add_argument(
        '-d', '--distance', default='cosine',
        choices=['cosine', 'KL'], help='Choose metric for ABX score')
    track1_17.add_argument(
        '-dr', '--duration',
        choices=['1s', '10s', '120s'],
        default=['1s', '10s', '120s'],
        help='Evaluate only one subset of test set')
    track1_17.add_argument(
        '-n', '--normalize', default=1,
        help="choose to normalize DTW distance")
    track1_17.add_argument(
        'task_folder',
        help='Folder containing the ABX tasks')

    # track2_17 = subparser_17.add_parser('track2')

    # if 2019 edition chosen
    parser_19.add_argument(
        '-l', '--language', default=None,
        choices=['english', 'surprise'],
        help='''choose language to evaluate. If None chosen,
        all will be evaluated''')
    parser_19.add_argument(
        '-d', '--distance', default='cosine',
        choices=['cosine', 'KL', 'levenshtein'],
        help='Choose metric for ABX score')
    parser_19.add_argument(
        '-n', '--normalize', default=1,
        help="choose to normalize DTW distance")
    parser_19.add_argument(
        'task_folder',
        help='Folder containing the ABX tasks')

    # # If both editions are chosen
    # parser_all.add_argument(
    #     '-l', '--language', choices=['english', 'surprise'], nargs='+',
    #     help='choose language to evaluate. If None chosen, '
    #     'all will be evaluated')

    parser_all.add_argument(
        'task_folder',
        help='Folder containing the ABX tasks')
    parser_all.add_argument(
        '-d17', '--distance17',
        default='cosine', choices=['cosine', 'KL'],
        help='Choose metric for ABX score for 2017 edition')
    parser_all.add_argument(
        '-d19', '--distance19',
        default='cosine', choices=['cosine', 'KL', 'levenshtein'],
        help='Choose metric for ABX score for 2019 edition')

    args = parser.parse_args()

    # Default values and subparsers

    # tracks
    if 'track' in args:
        track = args.track
    else:
        track = None

    # edition
    if args.edition is None:
        log.error('Must choose an edition to evaluate.'
                  'Add "-h" to see options.')
        sys.exit(1)
    else:
        edition = args.edition

    if args.edition == "2017" and track is None:
        log.error('Must choose a track for 2017. Add "-h" to see options')
        sys.exit(1)

    # distance function
    if edition == "both":
        distance = [args.distance17, args.distance19]
        normalize = args.normalize
    elif edition == "2017" and args.track == "track2":
        distance = None
        normalize = None
    elif edition == "2019" or edition == "2017":
        distance = args.distance
        normalize = args.normalize

    # language
    if "language" in args:
        language = args.language
    else:
        language = None

    if isinstance(language, str):
        language = [language]

    # duration
    if 'duration' in args:
        if isinstance(args.duration, str):
            duration = [args.duration]
        else:
            duration = args.duration
    else:
        duration = ['1s', '10s', '120s']

    # abx Task folder
    if 'task_folder' in args:
        task_folder = args.task_folder
    else:
        task_folder = None

    # launch evaluation
    try:
        Evaluation2020(
            args.submission,
            njobs=args.njobs,
            output=args.output,
            log=log,
            edition=edition,
            track=track,
            language_choice=language,
            tasks=task_folder,
            distance=distance,
            normalize=normalize,
            duration=duration
        ).evaluate()
    except ValueError as err:
        log.error(f'fatal error: {err}')
        log.error(
            'please fix the error and try again, '
            'or contact zerospeech2020@gmail.com if you need assistance')
        sys.exit(1)


if __name__ == "__main__":
    main()
