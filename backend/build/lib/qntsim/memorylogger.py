import logging

def get_memory_logger():
    # create a logger object
    logger = logging.getLogger('my_logger')
    logger.setLevel(logging.DEBUG)

    # create a MemoryHandler object with a capacity of 1000 log records
    memory_handler = logging.handlers.MemoryHandler(capacity=1000, flushLevel=logging.WARNING)

    # add the MemoryHandler object to the logger
    logger.addHandler(memory_handler)
    
    return logger
