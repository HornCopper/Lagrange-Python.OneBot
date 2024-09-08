from datetime import datetime

import hashlib
import random

def generate_message_id() -> int:
    seed_timestamp = int(datetime.now().timestamp()*1000)
    random.seed(seed_timestamp)
    
    random_number = random.randint(0, 1_000_000_000)
    
    unique_string = f"{seed_timestamp}-{random_number}"
    unique_hash = hashlib.sha256(unique_string.encode()).hexdigest()
    
    unique_integer = int(unique_hash, 16)
    
    min_range = -2_147_483_647
    max_range = 2_147_483_647
    
    range_span = max_range - min_range + 1
    
    unique_random_number = min_range + (unique_integer % range_span)
    
    return unique_random_number