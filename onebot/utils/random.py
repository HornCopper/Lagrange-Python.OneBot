import cityhash

def generate_message_id(uni_num: int, seq: int) -> int:
    hash_value = cityhash.CityHash32(str(uni_num) + str(seq))
    return hash_value