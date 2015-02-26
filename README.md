# apkdiff
APK Diff

This python script diffs two Android APKs creating a patch for reducing OTA update size.

It works by creating instructions to re-write the old apk on the client into the new apk using a combination
of simple file manipulation and bsdiff when appropriate.

There are many more optimizations to make, like

- write the 'patcher' in C/C++ for memory and speed improvements
- reduce the memory required by bsdiff (is this an issue? need to measure)
- Use courgette instead of bsdiff for executables

Experiments still to try

- When diffing load everything into RAM and do brut-force 'bsdiff' to see if that results in further reductions



Using

https://github.com/ilanschnell/bsdiff4

for the bsdiff implementation.
