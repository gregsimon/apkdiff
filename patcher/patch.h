
#ifndef __patch_h__
#define __patch_h__


class ApkPatcher {
public:
	ApkPatcher();
	~ApkPatcher();

	int patch(const char* fromfile, const char* destfile, const char* patchfile);

private:


};


#endif
