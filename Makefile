all: dump

OBJECTS = crc32.o mini_inflate.o dump.o

dump: $(OBJECTS)
	g++ $(OBJECTS) -o dump
