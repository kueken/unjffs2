#!/usr/bin/python

fs_size = 60 * 1024 # 60MB for the ext2 partition

import sys, os, struct

if len(sys.argv) < 2:
	raise "please give NFI file as argument!"
	
print """ripimage.py tries to unpack an NFI file and turns it into a compact
flash image. it requires the jffs2_dump tool and genext2fs."""

os.system("rm -rf root boot")
file = open(sys.argv[1], "r")
header = file.read(32)

if header[:4] != "NFI1":
	print "old NFI format detected!"
	machine_type = "dm7020"
	file.seek(0)
else:
	machine_type = header[4:4+header[4:].find("\0")]

endianess = {"dm7025": "1234", "dm7020": "4321"}

print "machine type:", machine_type

(total_size, ) = struct.unpack("!L", file.read(4))

p = 0
while file.tell() < total_size:
	(size, ) = struct.unpack("!L", file.read(4))
	
	output_names = {2: "boot", 3: "root"}
	if p not in output_names:
		file.seek(size, 1)
	else:
		print "extracting", output_names[p]
		output_filename = output_names[p] + ".jffs2" 
		output_directory = output_names[p]
		output = open(output_filename, "wb")
		for sector in range(size / 528):
			d = file.read(528)
			output.write(d[:512])
		output.close()
		print "unpacking", p, "(ignore errors about mknod, chown)"
		if os.system("./dump %s %s %s" % (output_filename, output_directory, endianess[machine_type])):
			raise "unpacking jffs2 failed!"
		print "ok"
		os.unlink(output_filename)
		
	p += 1

print "generating ext2fs"
if os.system("genext2fs -d root -D root.devtab root.ext2 -b %d" % (fs_size)):
	raise "genext2fs failed! do you have it installed?"
else:
	print "removing temporary files.."
	os.system("rm -rf root root.devtab boot.devtab")

a = open("boot/autorun.bat", "wb")
a.write("/cf/bootlogo.elf\n")
a.write("/cf/vmlinux.gz root=/dev/hdc2 console=ttyS0,115200 rw\n")
a.close()

print "done! you now should have a root.ext2 file and a boot/ directory"
print "prepare a CF disc with following layout:"
print "partition 1: MSDOS (~4MB)"
print "partition 2: Linux (%d MB)" % (fs_size / 1024)
print "copy the files from boot/ into the first partition."
print "write the root.ext into the second partition."
