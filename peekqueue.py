from queue import Queue

class PeekableQueue(Queue):
    def peek_first(self):
        with self.mutex:
            if self.queue:
                return self.queue[0]
        return None
    
    def peek_last(self):
        with self.mutex:
            if self.queue:
                return self.queue[-1]
        return None