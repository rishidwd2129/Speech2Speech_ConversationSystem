import threading
import time
import random

# Shared state between producer and consumer
class SharedState:
    def __init__(self, max_buffer_size=5):
        self.buffer = []
        self.lock = threading.Lock()
        self.condition = threading.Condition()
        self.production_complete = False
        self.max_buffer_size = max_buffer_size

def producer_function(state):
    """Produces data and adds it to the shared buffer"""
    for i in range(1, 11):  # Produce 10 items
        # Simulate variable production time
        time.sleep(random.uniform(0.1, 0.5))
        
        # Generate data
        data = f"Item {i}"
        
        with state.condition:
            # Wait if buffer is full
            while len(state.buffer) >= state.max_buffer_size:
                state.condition.wait()
            
            state.buffer.append(data)
            print(f"Produced: {data}")
            state.condition.notify()

    # Signal production completion
    with state.condition:
        state.production_complete = True
        state.condition.notify_all()

def consumer_function(state):
    """Consumes data from the shared buffer"""
    while True:
        with state.condition:
            # Wait for data or production completion
            while not state.buffer and not state.production_complete:
                state.condition.wait()
            
            if not state.buffer and state.production_complete:
                break  # Exit when production is complete and buffer is empty
            
            data = state.buffer.pop(0)
            print(f"Buffer size: {len(state.buffer)}")
            state.condition.notify()  # Notify producer space is available

        # Process data (outside the lock)
        time.sleep(random.uniform(0.2, 0.7))  # Simulate processing time
        print(f"Consumed: {data}")

# Usage example
if __name__ == "__main__":
    shared_state = SharedState(max_buffer_size=3)
    
    producer = threading.Thread(target=producer_function, args=(shared_state,))
    consumer = threading.Thread(target=consumer_function, args=(shared_state,))

    producer.start()
    consumer.start()

    producer.join()
    consumer.join()

    print("All tasks completed")