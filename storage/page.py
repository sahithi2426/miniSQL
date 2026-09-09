"""
Reference: Database Management Systems (Ramakrishnan & Gehrke) - Chapter 9
A Page represents a fixed block of 4096 bytes read from or written to disk.
"""
PAGE_SIZE = 4096

class Page:
    def __init__(self, page_id: int):
        self.page_id = page_id
        self.data = bytearray(PAGE_SIZE)
        self.is_dirty = False
        self.pin_count = 0
