from queue import PriorityQueue

class PeekableQueue(PriorityQueue):
    # priority queue is minheap
    # which mean the fist (top) item of priority queue is the smallest
    # thsu the last element should be the biggest

    def _init(self, maxsize):
        super()._init(maxsize)
        self.last = None

    def _put(self, item):
        super()._put(item)
        if self.last is None:
            self.last = item
        else:
            self.last = item if self.last < item else self.last # new bigger item is added, update last
    
    def _get(self):
        ret = super()._get()
        with self.mutex:
            if not self.queue:  # no element in queue => no last
                self.last = None
        return ret

    def decrease(self, sub):
        "decrease the all priority values in the queue by sub"
        with self.mutex:
            for item in self.queue:
                if item:
                    item -= sub

    def peek_first(self):
        with self.mutex:
            if self.queue:
                return self.queue[0]
        return None
    
    def peek_last(self):
        with self.mutex:
            return self.last

