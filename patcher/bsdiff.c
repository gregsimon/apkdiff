

#include <sys/types.h>

#include "bsdiff.h"


/*

split
qsufsort
matchlen
search

(ext)
diff
patch
encode_int64
decode_int64
*/

#define MIN(x, y)  (((x) < (y)) ? (x) : (y))

static void split(off_t *I, off_t *V, off_t start, off_t len, off_t h);
static void qsufsort(off_t *I, off_t *V, unsigned char *old, off_t oldsize);
static off_t matchlen(unsigned char *old, off_t oldsize,
                      unsigned char *new, off_t newsize);
static off_t search(off_t *I,
                    unsigned char *old, off_t oldsize,
                    unsigned char *new, off_t newsize,
                    off_t st, off_t en, off_t *pos);

int bsdiff_patch(const char* srcpath, const char* dstpath, const char* patchpath)
{
    return 0;
}


static void split(off_t *I, off_t *V, off_t start, off_t len, off_t h)
{
    off_t i, j, k, x, tmp, jj, kk;

    if (len < 16) {
        for (k = start; k < start + len; k += j) {
            j = 1;
            x = V[I[k] + h];
            for (i = 1; k + i < start + len; i++) {
                if (V[I[k + i] + h] < x) {
                    x = V[I[k + i] + h];
                    j = 0;
                }
                if (V[I[k + i] + h] == x) {
                    tmp = I[k + j];
                    I[k + j] = I[k + i];
                    I[k + i] = tmp;
                    j++;
                }
            }
            for (i = 0; i < j; i++)
                V[I[k + i]] = k + j - 1;
            if (j == 1)
                I[k] = -1;
        }

    } else {

        jj = 0;
        kk = 0;
        x = V[I[start + len / 2] + h];
        for (i = start; i < start + len; i++) {
            if (V[I[i] + h] < x)
                jj++;
            if (V[I[i] + h] == x)
                kk++;
        }
        jj += start;
        kk += jj;

        j = 0;
        k = 0;
        i = start;
        while (i < jj) {
            if (V[I[i] + h] < x) {
                i++;
            } else if (V[I[i] + h] == x) {
                tmp = I[i];
                I[i] = I[jj + j];
                I[jj + j] = tmp;
                j++;
            } else {
                tmp = I[i];
                I[i] = I[kk + k];
                I[kk + k] = tmp;
                k++;
            }
        }

        while (jj + j < kk) {
            if (V[I[jj + j] + h] == x) {
                j++;
            } else {
                tmp = I[jj + j];
                I[jj + j] = I[kk + k];
                I[kk + k] = tmp;
                k++;
            }
        }

        if (jj > start)
            split(I, V, start, jj - start, h);

        for (i = 0; i < kk - jj; i++)
            V[I[jj + i]] = kk - 1;
        if (jj == kk - 1)
            I[jj] = -1;
        if (start + len > kk)
            split(I, V, kk, start + len - kk, h);
    }
}


static void qsufsort(off_t *I, off_t *V, unsigned char *old, off_t oldsize)
{
    off_t buckets[256], i, h, len;

    for (i = 0; i < 256; i++)
        buckets[i] = 0;
    for (i = 0; i < oldsize; i++)
        buckets[old[i]]++;
    for (i = 1; i < 256; i++)
        buckets[i] += buckets[i - 1];
    for (i = 255; i > 0; i--)
        buckets[i] = buckets[i - 1];
    buckets[0] = 0;

    for (i = 0; i < oldsize; i++)
        I[++buckets[old[i]]] = i;
    I[0] = oldsize;
    for (i = 0; i < oldsize; i++)
        V[i] = buckets[old[i]];
    V[oldsize] = 0;
    for (i = 1; i < 256; i++)
        if (buckets[i] == buckets[i - 1] + 1)
            I[buckets[i]] = -1;
    I[0] = -1;

    for (h = 1; I[0] != -(oldsize + 1); h += h) {
        len = 0;
        for (i = 0; i < oldsize + 1;) {
            if (I[i] < 0) {
                len -= I[i];
                i -= I[i];
            } else {
                if (len)
                    I[i - len] = -len;
                len = V[I[i]] + 1 - i;
                split(I, V, i, len, h);
                i += len;
                len=0;
            }
        }
        if (len)
            I[i - len] = -len;
    }

    for (i = 0; i < oldsize + 1; i++)
        I[V[i]] = i;
}


static off_t matchlen(unsigned char *old, off_t oldsize,
                      unsigned char *new, off_t newsize)
{
    off_t i;

    for (i = 0; (i < oldsize) && (i < newsize); i++)
        if (old[i] != new[i])
            break;
    return i;
}


static off_t search(off_t *I,
                    unsigned char *old, off_t oldsize,
                    unsigned char *new, off_t newsize,
                    off_t st, off_t en, off_t *pos)
{
    off_t x, y;

    if (en - st < 2) {
        x = matchlen(old + I[st], oldsize - I[st], new, newsize);
        y = matchlen(old + I[en], oldsize - I[en], new, newsize);

        if (x > y) {
            *pos = I[st];
            return x;
        } else {
            *pos = I[en];
            return y;
        }
    }

    x = st + (en - st) / 2;
    if (memcmp(old + I[x], new, MIN(oldsize - I[x], newsize)) < 0) {
        return search(I, old, oldsize, new, newsize, x, en, pos);
    } else {
        return search(I, old, oldsize, new, newsize, st, x, pos);
    }
}
