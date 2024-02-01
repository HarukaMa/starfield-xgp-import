import math
import os.path
import zlib
from collections import namedtuple
from io import BytesIO
from typing import BinaryIO, NamedTuple

from utils import NotSupportedError, read_u32, read_u64, write_u32, write_u64


class SaveFileChunk(NamedTuple):
    size: int
    data: bytes

class SaveFile:
    def __init__(self, *, filename: str, header_size: int, real_header_size: int, uncompressed_size: int, chunks: list[SaveFileChunk], unknown: int):
        self.filename = filename
        self.header_size = header_size
        self.real_header_size = real_header_size
        self.uncompressed_size = uncompressed_size
        self.chunks = chunks
        self.unknown = unknown

    @classmethod
    def from_stream(cls, stream: BinaryIO):
        filename = os.path.basename(stream.name)
        magic = stream.read(4)
        if magic != b"BCPS":
            raise NotSupportedError(f"invalid magic: {magic} != BCPS")
        # check various fields to ensure the version has not changed
        value = read_u32(stream)
        if value != 1:
            raise NotSupportedError(f"unexpected value: {value} != 1")
        value = read_u32(stream)
        if value != 0x48:
            raise NotSupportedError(f"unexpected value: {value} != 0x48")
        stream.seek(0x18, os.SEEK_SET)
        header_size = read_u64(stream)
        uncompressed_size = read_u64(stream)
        value = read_u64(stream)
        if value != 0x40000000:
            raise NotSupportedError(f"unexpected value: {value} != 0x40000000")
        chunk_size = read_u64(stream)
        if chunk_size != 0x40000:
            raise NotSupportedError(f"unexpected chunk size: {value} != 0x40000")
        chunk_count = math.ceil(uncompressed_size / chunk_size)
        value = read_u64(stream)
        if value != 0x10:
            raise NotSupportedError(f"unexpected value: {value} != 0x10")
        unknown = read_u32(stream)
        magic = stream.read(4)
        if magic != b"ZIP ":
            raise NotSupportedError(f"invalid magic: {magic} != \"ZIP \"")
        # read the chunks
        chunks = []
        header_ptr = stream.tell()
        body_ptr = header_size
        for _ in range(chunk_count):
            chunk_size = read_u32(stream)
            header_ptr += 4
            stream.seek(body_ptr, os.SEEK_SET)
            chunks.append(SaveFileChunk(chunk_size, stream.read(chunk_size)))
            if chunk_size % 0x10 != 0:
                padding = 0x10 - (chunk_size % 0x10)
                stream.seek(padding, os.SEEK_CUR)
            body_ptr = stream.tell()
            stream.seek(header_ptr, os.SEEK_SET)
        real_header_size = stream.tell()
        # safety check
        total_uncompressed_size = sum(len(zlib.decompress(chunk.data)) for chunk in chunks)
        if total_uncompressed_size != uncompressed_size:
            raise NotSupportedError(f"unexpected uncompressed size: {total_uncompressed_size} != {uncompressed_size}")
        return cls(filename=filename, header_size=header_size, real_header_size=real_header_size, uncompressed_size=uncompressed_size, chunks=chunks, unknown=unknown)

    def header_bytes(self):
        output = BytesIO()
        output.write(b"BCPS")
        write_u32(output, 1)
        write_u32(output, 0x48)
        output.write(b"\0" * 0xc)
        write_u64(output, self.header_size)
        write_u64(output, self.uncompressed_size)
        write_u64(output, 0x40000000)
        write_u64(output, 0x40000)
        write_u64(output, 0x10)
        write_u32(output, self.unknown)
        output.write(b"ZIP ")
        for chunk in self.chunks:
            write_u32(output, chunk.size)
        return output.getvalue()


