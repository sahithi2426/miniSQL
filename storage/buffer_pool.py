"""
Reference: CMU 15-445 / 645 Database Systems (Andy Pavlo) - Buffer Pool Manager
Maintains in-memory cache of pages, swapping to disk when frames are full. 
For simplicity, we use a basic dictionary with an LRU-like eviction approximation.
"""
from storage.page import Page
from storage.disk_manager import DiskManager

class BufferPoolManager:
    def __init__(self, disk_manager: DiskManager, pool_size: int = 10):
        self.disk_manager = disk_manager
        self.pool_size = pool_size
        self.pages = {} # map page_id -> Page

    def fetch_page(self, page_id: int) -> Page:
        if page_id in self.pages:
            self.pages[page_id].pin_count += 1
            return self.pages[page_id]
        
        # Evict if full
        if len(self.pages) >= self.pool_size:
            self._evict_page()

        # Load from disk
        page = Page(page_id)
        page.data = self.disk_manager.read_page(page_id)
        page.pin_count = 1
        self.pages[page_id] = page
        return page

    def unpin_page(self, page_id: int, is_dirty: bool):
        if page_id in self.pages:
            page = self.pages[page_id]
            page.pin_count -= 1
            if is_dirty:
                page.is_dirty = True

    def flush_page(self, page_id: int):
        if page_id in self.pages:
            page = self.pages[page_id]
            if page.is_dirty:
                self.disk_manager.write_page(page.page_id, page.data)
                page.is_dirty = False

    def flush_all_pages(self):
        for pid in list(self.pages.keys()):
            self.flush_page(pid)

    def _evict_page(self):
        # find a page with pin_count == 0
        for pid, p in list(self.pages.items()):
            if p.pin_count == 0:
                self.flush_page(pid)
                del self.pages[pid]
                return
        raise Exception("Buffer pool full, all pages are pinned!")
