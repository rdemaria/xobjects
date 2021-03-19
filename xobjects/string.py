"""


TODO:
- String._to_buffer to use same context copy
- consider caching  the length
- consider using __slots__
- consider adding size in the class
"""

from .typeutils import get_a_buffer, Info, _to_slot_size
from .scalar import Int64

import logging

log = logging.getLogger(__name__)

class String:
    _size = None

    @classmethod
    def _inspect_args(cls, string_or_int):
        if isinstance(string_or_int, int):
            return Info(size=string_or_int + 8)
        elif isinstance(string_or_int, str):
            data=bytes(string_or_int,"utf8")
            size= _to_slot_size(len(data)+1 + 8)
            return Info(size=size,data=data) # add zero termination
        elif isinstance(string_or_int, cls):
            return Info(size=string_or_int._get_size())
        raise ValueError(
            f"String can accept only one integer or string and not `{string_or_int}`"
        )

    @classmethod
    def _to_buffer(cls, buffer, offset, value, info=None):
        log.debug(f"{cls} to buffer {offset}  `{value}`")
        if info is None:  # string is always dynamic therefore index is necessary
            info = cls._inspect_args(value)
        size = info.size
        string_capacity=info.size-8
        Int64._to_buffer(buffer, offset, size)
        if isinstance(value, String):
            buffer.write(offset, value.to_bytes())
        elif isinstance(value, str):
            data =info.data
            off=string_capacity-len(data)
            data += b'\x00'*off
            stored_size = Int64._from_buffer(buffer, offset)
            if size > stored_size:
                raise ValueError(f"{value} to large to fit in {size}")
            buffer.write(offset + 8, data)
        elif isinstance(value, int):
            pass
        else:
            raise ValueError(f"{value} not a string")


    @classmethod
    def _get_data(cls,buffer, offset):
        ll = Int64._from_buffer(buffer, offset)
        return buffer.read(offset + 8, ll)

    @classmethod
    def _from_buffer(cls, buffer, offset):
        return cls._get_data(buffer, offset).decode("utf8").rstrip("\x00")

    def _get_size(self):
        return Int64._from_buffer(self._buffer, self._offset)

    def __init__(self, string_or_int, _buffer=None, _offset=None, _context=None):
        new_object = False
        info = self.__class__._inspect_args(string_or_int)
        size = info.size
        self._buffer, self._offset = get_a_buffer(size, _context, _buffer, _offset)

        self.__class__._to_buffer(self._buffer, self._offset, string_or_int, info=info)

    def update(self, string):
        if isinstance(value, String):
            if value._size<self._size:
                buffer.write(offset+8, value.to_bytes()) #TODO use copy
            else:
                raise ValueError(f"{value} to large to fit in {size}")
        elif isinstance(value, str):
            info = self.__class__._inspect_args(value)
            if info > self._size:
                raise ValueError(f"{value} to large to fit in {size}")
            else:
                data =info.data
                off=_to_slot_size(size)-len(data)
                data += b'\x00'*off
                buffer.write(offset + 8, data)
        else:
            raise ValueError(f"{value} not a string")

    def to_str(self):
        return self.__class__._from_buffer(self._buffer, self._offset)

    def to_bytes(self):
        return self.__class__._get_data(self._buffer, self._offset)

