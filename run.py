#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hello
"""

import json
import re
import sys
from collections import Counter
from wordlists import hyphenated_coded_words, feminine_coded_words, masculine_coded_words


def de_hyphen_non_coded_words(word_list):
    """
    Removes hypens from coded, hyphenated words
    """
    for idx, word in enumerate(word_list):
        if not word.find('-'):
            continue
        # If non-coded, hyphenated word, split it and reinsert at list index
        if not any(word.startswith(coded_word) for coded_word in hyphenated_coded_words):
            word_list.remove(word)
            word_list[idx:idx] = word.split('-')
    return word_list


def clean_up_word_list(ad_text):
    """
    Returns cleaned up word list
    """
    cleaner_text = ''.join([
        i if ord(i) < 128 else ' ' for i in ad_text
    ])
    cleaner_text = re.sub(r'[\s]', ' ', cleaner_text, 0, 0)
    cleaned_word_list = list(filter(None, re.sub(
        r'[\.\t\,“”‘’<>\*\?\!\"\[\]\@\':;\(\)\\./&]',
        ' ', cleaner_text, 0, 0).split(' ')))
    word_list = [word.lower() for word in cleaned_word_list if word]
    return de_hyphen_non_coded_words(word_list)


def get_gendered_counts(advert_word_counts, gendered_word_list):
    """
    Counts gendered words and returns Counter
    """
    gendered_word_counts = Counter()
    for gendered_word in gendered_word_list:
        for advert_word in advert_word_counts:
            if gendered_word in advert_word:
                gendered_word_counts[advert_word] = advert_word_counts[advert_word]
    return gendered_word_counts


def extract_coded_words(advert_word_list):
    """
    Returns dict of gender coding Counters.
    """
    word_counts = Counter(advert_word_list)
    masculine_counts = get_gendered_counts(word_counts, masculine_coded_words)
    feminine_counts = get_gendered_counts(word_counts, feminine_coded_words)
    return {
        'masculine_coding': masculine_counts,
        'feminine_coding': feminine_counts,
    }


def get_coding_score(count_diff, has_feminine):
    """
    Returns a str label for a given diff (f - m)
    """
    if count_diff == 0:
        return 'neutral' if has_feminine else 'empty'

    if count_diff > 3:
        return 'strongly feminine-coded'

    if count_diff > 0:
        return 'feminine-coded'

    if count_diff < -3:
        return 'strongly masculine-coded'

    return 'masculine-coded'


def assess_coding(word_counts):
    """
    Prints gender coding assessment as a dict
    """
    feminine_count = sum(word_counts['feminine_coding'].values())
    masculine_count = sum(word_counts['masculine_coding'].values())
    word_counts['score'] = get_coding_score(feminine_count - masculine_count, bool(feminine_count))
    return (
        f'feminine-coded words: {json.dumps(word_counts["feminine_coding"], indent=4)}\n\n'
        f'masculine-coded words: {json.dumps(word_counts["masculine_coding"], indent=4)}\n\n'
        f'final score: {word_counts["score"]}'
    )


def analyse(ad_text):
    """
    Analyse the job text.
    """
    word_list = clean_up_word_list(ad_text)
    word_counts = extract_coded_words(word_list)
    return assess_coding(word_counts)


with open(sys.argv[1], 'r') as jobtext:
    print(analyse(''.join(jobtext.readlines())))
