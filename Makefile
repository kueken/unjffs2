all: unjffs2

OBJECTS = crc32.o mini_inflate.o unjffs2.o

unjffs2: $(OBJECTS)
	$(CXX) $(OBJECTS) -o unjffs2

clean:
	rm -f *.o unjffs2
