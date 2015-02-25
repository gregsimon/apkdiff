#!/usr/bin/python

import sys, os, filecmp, shutil, bsdiff4


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
    global g_output_dir; g_output_dir = "out"

    try:
    	a_folder = sys.argv[1]
    	b_folder = sys.argv[2]
        a_files = collect_files(a_folder)
        b_files = collect_files(b_folder)

        compute_delta(a_folder, a_files, b_folder, b_files)
        
    except:
        print('Usage: {} <dir1> <dir2>'.format(os.path.basename(sys.argv[0])))
        raise


def compute_delta_brut(a_folder, a_files, b_folder, b_files):
	# just walk through the dst files and diff them with EVERYTHING
	# from the src. We'll only compare things with the same file ext
	# to save time.
	result_files = []

	for dst in b_files:
		#for elt in a_files:
			#src_filename = a_folder+'/'+elt
		dst_filename = b_folder+'/'+dst
		best_src_diff = find_best_diff(dst_filename, a_folder, a_files)
		result_files.append([dst, best_src_diff])

	print('now compute all the diffs')
	
	shutil.rmtree(g_output_dir)
	os.makedirs(g_output_dir)
	
	unique_fileid = 0

	for elt in result_files:
		bsdiff4.file_diff(elt[1], elt[2], '%s/f%s' % (g_output_dir, unique_fileid))
		unique_fileid = unique_fileid + 1


def compute_delta(a_folder, a_files, b_folder, b_files):
	print('Going from %d files %d files' % (len(a_files), len(b_files)))

	# First let's fill up these categories
	files_new = []
	files_removed = []
	files_changed = []
	files_unchanged = []
	files_renamed = []

	# First, let's remove the .so files since we're going to treat
	# them special.
	a_files_so = []
	b_files_so = []
	for elt in a_files:
		if elt.endswith('.so'):
			a_files_so.append(elt)
			a_files.remove(elt)
	for elt in b_files:
		if elt.endswith('.so'):
			b_files_so.append(elt)
			b_files.remove(elt)


	# What files appear in B but not in A?
	for elt in b_files:
		if elt not in a_files:
			if not elt.endswith('.so'):
				files_new.append(elt)
	
    # What files appear in A but not in B?
	for elt in a_files:
		if elt not in b_files:
			files_removed.append(elt)
	
	# What files have changed contents but not name/path?
	for elt in b_files:
		if elt in a_files:
			if not filecmp.cmp(a_folder+'/'+elt, b_folder+'/'+elt):
				files_changed.append(elt)
			else:
				files_unchanged.append(elt)



	# Now, handle the so files special.
	#
	# We ultimately want to diff .so files that are built from
	# the same source even if the names have slightly changed.
	# It looks like for clank, they stamp the build #s into 
	# the names, so we'll use that heuristic.

	for elt in b_files_so:
		if elt in a_files_so:
			# this file is the same name in both!
			files_changed.append(elt)
		else:
			# This one is new, but we can probably bsdiff it with one
			# of the other .so's since it was likely renamed.
			a_best_choice_diff = find_best_diff(b_folder+'/'+elt, a_folder, a_files_so)

			# this will be a 'rename' record in the TOC
			files_renamed.append([elt, a_best_choice_diff])

	

	print('%d .so files to diff' % (len(b_files_so) + len(a_files_so)))
	print('%d new files' % len(files_new))
	print('%d removed files' % len(files_removed))
	print('%d files changed' % len(files_changed))
	print('%d files unchanged' % len(files_unchanged))
	print('%d files files_renamed' % len(files_renamed))


	# Ok, now let's write out the patch. The patch is two major sections:
	#  
	#   - TOC.txt, which contains the instructions of what files to add, 
	#			remove, and patch
	# 	- f0, f1, ...  the files themselves
	# 
	#   Legend:
	#   -<filename>         					// This file should be REMOVED
	#   +<id> <dst_filename>         			// This file should be ADDED
	#	c<id> <filename>						// This file shouldb be patched, same name
	#   r<id> <src_filename> <dst_filename>		// this file should be patched to 
	#												src_filename and named dst_filename

	# temp dir where we're assembling the patch
	shutil.rmtree(g_output_dir)
	os.makedirs(g_output_dir)

	unique_fileid = 0


	toc = open(g_output_dir+'/TOC.txt','w')
	# TODO write MD5 of result
	toc.write('md5 a82da2f761d6f63ddd7181a7c8c764ea\n')

	for elt in files_removed:
		toc.write('-%s\n' % elt)

	for elt in files_new:
		# write an entry for the file
		toc.write('+%d %s\n' % (unique_fileid, elt))
		
		# copy the file contents itself into the folder.
		shutil.copy(b_folder+'/'+elt, '%s/f%d' % (g_output_dir, unique_fileid))
		unique_fileid = unique_fileid + 1

	print("writing diff'ed changed files...")
	for elt in files_changed:
		toc.write('c%d %s\n' % (unique_fileid, elt))
		bsdiff4.file_diff(b_folder+'/'+elt, a_folder+'/'+elt, 
							'%s/f%d' % (g_output_dir, unique_fileid))
		unique_fileid = unique_fileid + 1

	for elt in files_renamed:
		# these files are diffed against a src file with a different name
		src_file = a_folder+'/'+elt[1]
		dst_file = b_folder+'/'+elt[0]
		toc.write('C%d %s %s\n' % (unique_fileid, src_file, dst_file))
		bsdiff4.file_diff(src_file, dst_file, 
			'%s/f%d' % (g_output_dir, unique_fileid))
		unique_fileid = unique_fileid + 1

	toc.close()

def find_best_diff(dst, prefix, filelist):
	print('Finding the best file from original apk to diff %s with:' % dst)
	winning_patch_sz = sys.maxint
	for elt in filelist:
		src_file = prefix+'/'+elt
		src_sz = os.path.getsize(src_file)
		if (src_sz > 0) and os.path.splitext(src_file)[1] == os.path.splitext(dst)[1]:
			print('trying %s (%d bytes) -> %s' % (src_file, src_sz, dst))
			diff_sz = measure_two_filediffs(src_file, dst)
			if diff_sz < winning_patch_sz:
				winning_patch_sz = diff_sz
				winning_file = elt

	print('   Best is to diff with %s, patch is only %d k!' % (winning_file, 
					winning_patch_sz/1024))
	return winning_file

def measure_two_filediffs(src, dst):
	k_patch_filename = 'temp.patch'
	bsdiff4.file_diff(src, dst, k_patch_filename)
	result_size = os.path.getsize(k_patch_filename)
	os.remove(k_patch_filename)
	return result_size

def collect_files(path):
    dirs, files = listdir(path)[:2]
    all_files = []
    return walk(path, dirs, files, all_files, path)

def walk(root, dirs, files, all_files, path_prefix_to_remove, prefix=''):
    file_prefix = prefix + ('|' if dirs else ' ') + '   '
    for name in files:
        all_files.append(os.path.relpath(root+'/'+name, path_prefix_to_remove))
        

    dir_prefix, walk_prefix = prefix + '+---', prefix + '|   '
    for pos, neg, name in enumerate2(dirs):
        if neg == -1:
            dir_prefix, walk_prefix = prefix + '\\---', prefix + '    '
        path = os.path.join(root, name)
        try:
            dirs, files = listdir(path)[:2]
        except:
            pass
        else:
            walk(path, dirs, files, all_files, path_prefix_to_remove, walk_prefix)

    return all_files

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
