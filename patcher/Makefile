
all: patcher

SOURCES_CPP=patch.cpp main.cpp 
SOURCES_C=bsdiff.c
HEADERS=patch.h bsdiff.h
C_FLAGS=

bsdiff.o: bsdiff.c bsdiff.h
	gcc $(C_FLAGS) bsdiff.c -c -o bsdiff.o

patcher: $(SOURCES_CPP) $(SOURCES_C) $(HEADERS) bsdiff.o
	g++ $(SOURCES_CPP) bsdiff.o -lz -o patcher



clean:
	rm -f patcher
	rm -f *.o
