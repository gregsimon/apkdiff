#!/usr/bin/python

import sys, os, filecmp

FILES = True

'''
 Diff two APK files and create a patch which can be applied
 gregsimon@chromium.org

 Rather than diff the entire file, we're going to uncompress
 the APK files, and diff everything we find separately. 

     B.apk - A.apk = patch

     A.apk + patch = B.apk

 1. Create a list of files in each APK, with paths included
 2. These files will fall into one of three categories:
    1) file exists only in A (to be deleted)
	2) file exists only in B (new)	
	3) file exists in both and has the same contents (push)
	4) file exists in both and is different. (diff!)

	Note this does not account for files that are moved around, 
	but that is a feature for later.

'''

def main():
    global FILES; FILES = True

    try:
        a_files = collect_files(sys.argv[1])
        b_files = collect_files(sys.argv[2])
    except:
        print('Usage: {} <dir1> <dir2>'.format(os.path.basename(sys.argv[0])))

def collect_files(path):
    path = os.path.abspath(path)
    dirs, files = listdir(path)[:2]
    print(path)
    walk(path, dirs, files)
    if not dirs:
        print('No subfolders exist')

def walk(root, dirs, files, prefix=''):
    if FILES and files:
        file_prefix = prefix + ('|' if dirs else ' ') + '   '
        for name in files:
            print(file_prefix + name)
        print(file_prefix)
    dir_prefix, walk_prefix = prefix + '+---', prefix + '|   '
    for pos, neg, name in enumerate2(dirs):
        if neg == -1:
            dir_prefix, walk_prefix = prefix + '\\---', prefix + '    '
        print(dir_prefix + name)
        path = os.path.join(root, name)
        try:
            dirs, files = listdir(path)[:2]
        except:
            pass
        else:
            walk(path, dirs, files, walk_prefix)

def listdir(path):
    dirs, files, links = [], [], []
    for name in os.listdir(path):
        path_name = os.path.join(path, name)
        if os.path.isdir(path_name):
            dirs.append(name)
        elif os.path.isfile(path_name):
            files.append(name)
        elif os.path.islink(path_name):
            links.append(name)
    return dirs, files, links

def enumerate2(sequence):
    length = len(sequence)
    for count, value in enumerate(sequence):
        yield count, count - length, value

if __name__ == '__main__':
    main()
