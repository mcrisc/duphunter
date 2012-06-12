#!/usr/bin/python
#coding: utf-8
#
# Hunt Duplicated files
# Copyright (c) 2012 Marcelo Criscuolo (criscuolo[dot]marcelo[at]gmail.com)
# Open Source software. Released under the terms of the MIT License.

import argparse
import hashlib
import os


def _compute_digest(filename):
    digest = ''
    with open(filename, 'rb') as fd:
        digest = hashlib.md5(fd.read()).hexdigest()
    return digest

def _scan(root):
    for dirpath, dirnames, filenames in os.walk(root):
        for f in (os.path.join(dirpath, f) for f in filenames):
            size = os.path.getsize(f)
            if size > 0:
                yield f, size

_SINGLE_FILE = 'FAKE_DIGEST'
def hunt(root):
    candidates = {}
    # analysing all files
    for filename, size in _scan(root):
        if size in candidates:
            groups = candidates[size]
            if _SINGLE_FILE in groups:
                prev_file = groups[_SINGLE_FILE][0]
                del groups[_SINGLE_FILE]
                groups[_compute_digest(prev_file)] = [prev_file]
            groups.setdefault(_compute_digest(filename), []).append(filename)
        else:
            # defers digest computing
            candidates[size] = {_SINGLE_FILE: [filename]}
    # identifying duplicated
    result = []
    for size, groups in candidates.items():
        for filenames in groups.values():
            if len(filenames) > 1:
                filenames.sort()
                result.append((size, filenames))
    result.sort(key=lambda v: v[0], reverse=True)
    return result

UNITS = ((1024 ** 3, 'GB'), 
        (1024 ** 2, 'MB'), 
        (1024 ** 1, 'KB'),
        (1, 'bytes'))

def format_size(size, raw):
    if raw:
        return '%d bytes' % size
    for s, u in UNITS:
        if size >= s:
            return '%d %s' % (round(float(size)) / s, u)
    if size == 0:
        return '0 bytes'

def show_report(duplicated, raw):
    wasted = 0
    for size, files in duplicated:
        wasted += size * (len(files) - 1)
        print
        print format_size(size, raw)
        for f in files: 
            print f
        print '-' * 5
    print
    print '%s wasted' % format_size(wasted, raw)
    print

def main():
    parser = argparse.ArgumentParser(description='Find duplicated files')
    parser.add_argument('rootdir', help='Directory to start hunting')
    parser.add_argument('--bytes', action='store_true', default=False, required=False, 
            help='Output size in bytes. Do not format sizes in KB, MB...', dest='raw')
    args = parser.parse_args()
    if os.path.isdir(args.rootdir):
        dups = hunt(args.rootdir)
        show_report(dups, raw=args.raw)
    else:
        print "Invalid directory: %s" % args.rootdir

if __name__ == '__main__':
    main()

