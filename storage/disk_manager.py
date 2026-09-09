"""
Reference: Architecture of a Database System (Hellerstein et al.) - Section 3.1
The Disk Manager abstracts OS file access, treating the DB file as an array of Pages.
"""
import os
from storage.page import PAGE_SIZE

class DiskManager:
    def __init__(self, db_file: str):
        self.db_file = db_file
        # Create file if not exists
        if not os.path.exists(db_file):
            with open(db_file, 'wb') as f:
                pass
        self.file = open(db_file, 'r+b')

    def read_page(self, page_id: int) -> bytearray:
        self.file.seek(page_id * PAGE_SIZE)
        data = self.file.read(PAGE_SIZE)
        if not data:
            return bytearray(PAGE_SIZE)
        
        # Pad if less than PAGE_SIZE
        if len(data) < PAGE_SIZE:
            data += b'\x00' * (PAGE_SIZE - len(data))
        return bytearray(data)

    def write_page(self, page_id: int, page_data: bytearray):
        assert len(page_data) == PAGE_SIZE
        self.file.seek(page_id * PAGE_SIZE)
        self.file.write(page_data)
        self.file.flush()
        
    def close(self):
        self.file.close()
