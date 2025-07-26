from binreader import BinaryReader
from io import BytesIO
import struct
import json

def get_block_by_id(block_list, id):
    for block in block_list:
        if block.get("Id") == id:
            return block
    return None

def decode(data, block_list, width, height):
    reader = BinaryReader(BytesIO(data))
    world_data = {'width': width, 'height': height, 'bg': {}, 'fg': {}, 'ol': {}, 'block_list': block_list}
    i = 0
    for l in range(3):
        if l == 0:
            layer = 'bg'
        if l == 1:
            layer = 'fg'
        if l == 2:
            layer = 'ol'
            
        for x in range(width):
            for y in range(height):
                i += 1
                id = reader.read_uint32()
                block = get_block_by_id(block_list, id)
                block_data = {'id': id, 'data': []}
                
                if not block:
                    raise ValueError(f"Id {id} is not a valid block id.")
                
                if "BlockDataArgs" in block:
                    for arg in block['BlockDataArgs']:
                        block_data['data'].append(decode_argument(arg, reader))
                if not x in world_data[layer]:
                    world_data[layer][x] = []
                world_data[layer][x].append(block_data)
                
    return world_data
    
def decode_argument(arg, reader, endian='big'):
    if arg == 0:
        size = 0
        shift = 0
        while True:
            byte = ord(reader.read(1))
            size |= (byte & 0x7F) << shift
            shift += 7
            if (byte & 0x80) == 0:
                break
        string = reader.read_string(size)
        data = string
    elif arg == 1:
        data = reader.read_bool()
    elif arg == 3:
        if endian == 'big':
            data = reader.read_uint32()
        else:
            data = int.from_bytes(reader.read(4))
    elif arg == 7:
        data = reader.read_bool()
    elif arg == 8:
        data = int.from_bytes(reader.read(reader.read_ubyte()))
    elif arg == 9:
        uint32_color = reader.read_uint32()
        red = (uint32_color >> 16) & 0xFF
        green = (uint32_color >> 8) & 0xFF
        blue = uint32_color & 0xFF

        hex_red = format(red, '02X')
        hex_green = format(green, '02X')
        hex_blue = format(blue, '02X')

        data = f"#{hex_red}{hex_green}{hex_blue}"
    else:
        raise ValueError(f"Argument id {arg} is not a valid block argument.")
    
    return data
    
def decode_block_placed_data(data):
    reader = BinaryReader(BytesIO(data))
    length = len(data)
    block_data = []
    while not reader.tell() >= length:
        arg = reader.read_ubyte()
        block_data.append(decode_argument(arg, reader, endian='little'))
    return block_data

def encode_argument(arg, data):
    if arg == 0:
        bytes = b''
        value = len(data)
        while True:
            byte = value & 0x7F
            value >>= 7
            if value > 0:
                byte |= 0x80
            bytes += byte.to_bytes(1)
            if value == 0:
                break
        bytes += data.encode('utf-8')
    elif arg == 1:
        if data:
            bytes = b'\x01'
        else:
            bytes = b'\x00'
    elif arg == 3:
        bytes = data.to_bytes(4)
    elif arg == 7:
        if data:
            bytes = b'\x01'
        else:
            bytes = b'\x00'
    elif arg == 8:
        bytes = len(data.to_bytes()).to_bytes() + data.to_bytes()
    elif arg == 9:
        if not data.startswith('#') or len(data) != 7:
            raise ValueError("Invalid hexadecimal color string format. Expected '#RRGGBB'.")

        hex_red = data[1:3]
        hex_green = data[3:5]
        hex_blue = data[5:7]

        red = int(hex_red, 16)
        green = int(hex_green, 16)
        blue = int(hex_blue, 16)

        uint32_color = (red << 16) | (green << 8) | blue
        bytes = uint32_color.to_bytes(4, byteorder='little')
    else:
        raise ValueError(f"Argument id {arg} is not a valid block argument.")
    
    return bytes

def encode_block_placed_data(id, block_list, data=None):
    block = get_block_by_id(block_list, id)
    if bool("BlockDataArgs" in block) ^ bool(data):
        raise ValueError("Block has data, but none given from user.")
        
    if "BlockDataArgs" in block:
        i = 0
        block_data = b''
        for arg in block['BlockDataArgs']:
            block_data += arg.to_bytes(1)
            block_data += encode_argument(arg, data[i])
            i += 1
    else:
        block_data = None
        
    return block_data
    