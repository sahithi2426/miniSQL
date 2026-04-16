"""
Reference: Database Management Systems (Ramakrishnan & Gehrke) - Chapter 9.6: Page Formats
The TableHeap manages the collection of physical Pages that make up a table.
To keep the disk format natively understandable:
- Byte 0-3: Next Page ID (integer, -1 if none)
- Remaining bytes: 128-byte tuple slots.
Slot layout: 1 byte marker (1=used, 0=empty) + UTF-8 JSON.
"""
import json
import struct
from storage.buffer_pool import BufferPoolManager
from storage.page import PAGE_SIZE

TUPLE_SIZE = 128
HEADER_SIZE = 4
TUPLES_PER_PAGE = (PAGE_SIZE - HEADER_SIZE) // TUPLE_SIZE

class TableHeap:
    def __init__(self, buffer_pool: BufferPoolManager, first_page_id: int):
        self.buffer_pool = buffer_pool
        self.first_page_id = first_page_id
        
        # Initialize first page if it is freshly created
        page = self.buffer_pool.fetch_page(self.first_page_id)
        # Check if header is uninitialized (all 0s commonly, or rather we should explicitly set to -1)
        next_page = struct.unpack('<i', page.data[0:4])[0]
        if next_page == 0 and all(b == 0 for b in page.data[4:20]): # crude check for empty
            page.data[0:4] = struct.pack('<i', -1)
            self.buffer_pool.unpin_page(self.first_page_id, is_dirty=True)
        else:
            self.buffer_pool.unpin_page(self.first_page_id, is_dirty=False)

    def insert_tuple(self, tuple_dict: dict):
        current_page_id = self.first_page_id
        while True:
            page = self.buffer_pool.fetch_page(current_page_id)
            
            # Find an empty slot
            inserted = False
            for i in range(TUPLES_PER_PAGE):
                offset = HEADER_SIZE + (i * TUPLE_SIZE)
                if page.data[offset] == 0: # 0 means empty
                    encoded = json.dumps(tuple_dict).encode('utf-8')
                    if len(encoded) > TUPLE_SIZE - 2:
                        raise Exception("Tuple too large for 128-byte slot!")
                    
                    page.data[offset] = 1 # Mark used
                    page.data[offset+1:offset+1+len(encoded)] = encoded
                    for j in range(offset+1+len(encoded), offset+TUPLE_SIZE):
                        page.data[j] = 0
                    inserted = True
                    break

            if inserted:
                self.buffer_pool.unpin_page(current_page_id, is_dirty=True)
                break
            
            # Page is full, check next page
            next_page_id = struct.unpack('<i', page.data[0:4])[0]
            if next_page_id == -1:
                # Ask OS for file size to get new page ID...
                # For simplicity, let's just use a crude file size check
                self.buffer_pool.disk_manager.file.seek(0, 2)
                new_page_id = self.buffer_pool.disk_manager.file.tell() // PAGE_SIZE
                
                page.data[0:4] = struct.pack('<i', new_page_id)
                self.buffer_pool.unpin_page(current_page_id, is_dirty=True)
                
                # Fetch new page to initialize it
                new_page = self.buffer_pool.fetch_page(new_page_id)
                new_page.data[0:4] = struct.pack('<i', -1)
                self.buffer_pool.unpin_page(new_page_id, is_dirty=True)
                
                current_page_id = new_page_id
            else:
                self.buffer_pool.unpin_page(current_page_id, is_dirty=False)
                current_page_id = next_page_id

    def iterator(self):
        return TableIterator(self, self.first_page_id)

class TableIterator:
    def __init__(self, table_heap: TableHeap, first_page_id: int):
        self.table_heap = table_heap
        self.current_page_id = first_page_id
        self.current_slot = 0

    def get_next(self):
        while self.current_page_id != -1:
            page = self.table_heap.buffer_pool.fetch_page(self.current_page_id)
            
            offset = HEADER_SIZE + (self.current_slot * TUPLE_SIZE)
            slot_data = page.data[offset:offset+TUPLE_SIZE]
            
            self.current_slot += 1
            is_used = slot_data[0] == 1
            
            # Check if we exhausted page slots
            if self.current_slot >= TUPLES_PER_PAGE:
                next_page_id = struct.unpack('<i', page.data[0:4])[0]
                self.table_heap.buffer_pool.unpin_page(self.current_page_id, is_dirty=False)
                self.current_page_id = next_page_id
                self.current_slot = 0
            else:
                self.table_heap.buffer_pool.unpin_page(self.current_page_id, is_dirty=False)

            if is_used:
                end_idx = 1
                while end_idx < TUPLE_SIZE and slot_data[end_idx] != 0:
                    end_idx += 1
                encoded = slot_data[1:end_idx]
                tup = json.loads(encoded.decode('utf-8'))
                return tup
            
            # If not used, we continue to check next slots in while loop
                
        return None # Hits -1
