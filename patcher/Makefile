

SOURCES=patch.cpp main.cpp bsdiff.c
HEADERS=patch.h bsdiff.h

patcher: $(SOURCES) $(HEADERS)
	g++ -o patcher $(SOURCES) -lz 




clean:
	rm -f patcher

