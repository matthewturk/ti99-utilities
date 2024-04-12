import numpy as np
import struct
import sys
import csv

# Hey I hate this
fn = sys.argv[-1]
if fn.endswith(".py"):
    print("Gimme the data file")
    raise RuntimeError

commands, tokens = {}, {}

with open("commands.csv", "r") as f:
    header = next(f)
    for command, token, _ in csv.reader(f):
        tokens[int(token, base=16)] = command
        commands[command] = int(token, base=16)

def read_struct(f, fmt):
    s = struct.calcsize(fmt)
    return struct.unpack(fmt, f.read(s))

def unpack_line(line):
    # This gets a set of bytes.  We read them one at a time ...
    i = 0
    lt = []
    while i < len(line) - 1:
        b = line[i]
        if b >= ord(' ') and b <= ord('~'):
            s = ""
            while line[i] >= ord(' ') and line[i] <= ord('~'):
                s = s + chr(line[i])
                i += 1
                if i == len(line): break
            lt.append(s)
        elif b >= 0 and b <= 9 and i < len(line):
            s = ""
            while line[i] >= 0 and line[i] <= 9:
                s = s + str(line[i])
                i += 1
                if i == len(line): break
            lt.append(s)
        elif b in (0xc7, 0xc8):
            string_length = int(line[i+1])
            string_content = line[i+2:i+2+string_length].decode('ASCII')
            if b == 0xc7:
                string_content = f"\"{string_content}\""
            i += string_length + 2
            lt.append(string_content)
        elif b == 0xc9:
            ln = int.from_bytes(line[i+1:i+3], byteorder='big')
            lt.append(f"LINE:{ln}")
            i += 3
        else:
            lt.append(tokens[b])
            i += 1
    return " ".join(lt)

with open(fn, "rb") as f:
    f.seek(0x80)
    checksum, line_table_start, line_table_end, end_of_memory = read_struct(f, ">4h")
    #print(end_of_memory)

    #print(bin(checksum), bin(line_table_start), bin(line_table_end), bin(line_table_start^line_table_end), checksum==(line_table_start^line_table_end))

    lnt_size = line_table_start - line_table_end + 1
    lnt = f.read(lnt_size)
    lnt_np = np.frombuffer(lnt, dtype='>u2').reshape((-1, 2)).copy()
    lnt_np[:,1] -= (line_table_start + 2)

    basic_code = f.read()
    lines = {}
    decoded_lines = {}
    for line, offset in lnt_np:
        #offset -= 1
        length = basic_code[offset]
        lines[line] = basic_code[offset+1:offset+1+length]
        #print(line, length, lines[line][-1])
        decoded_lines[line] = unpack_line(lines[line])

for i in sorted(decoded_lines):
    print(f"{i:04d}:  {decoded_lines[i]}")
