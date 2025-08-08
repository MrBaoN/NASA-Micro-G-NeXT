import random

def generate_bits(file_path, total_bits=10000, pattern1="111111111111111", pattern2="000101111", pattern_prob=0.01):
    """
    Generates a text file filled with random bits (0s and 1s), randomly inserting specific patterns.

    :param file_path: The output file path.
    :param total_bits: The total number of bits to generate.
    :param pattern1: The first pattern to randomly insert.
    :param pattern2: The second pattern to randomly insert.
    :param pattern_prob: The probability of inserting a pattern at each step.
    """
    bits = []
    while len("".join(bits)) < total_bits:
        if random.random() < pattern_prob:
            pattern = random.choice([pattern1, pattern2])
            # pattern = pattern2
            if len("".join(bits)) + len(pattern) <= total_bits:
                bits.append(pattern)
        else:
            bits.append(str(random.randint(0, 1)))
    
    # Write to file
    with open(file_path, "w") as f:
        f.write("".join(bits))

if __name__ == "__main__":
    generate_bits("random_binary.txt", total_bits=100000)



# import random

# def generate_binary_file_with_pattern(filename, num_bits, pattern, pattern_interval=1000):
#     """
#     Generate a binary file with random bits and ensure the given pattern is inserted at regular intervals.
    
#     :param filename: The name of the output binary file.
#     :param num_bits: The total number of bits in the file.
#     :param pattern: The pattern to insert periodically.
#     :param pattern_interval: The interval (in bits) at which to insert the pattern.
#     """
#     with open(filename, 'w') as f:
#         # Total number of bits written so far
#         bits_written = 0
        
#         # Generate random bits until we reach num_bits
#         while bits_written < num_bits:
#             # Write random bits
#             if bits_written + len(pattern) <= num_bits and (bits_written % pattern_interval == 0 or random.random() < 0.1):
#                 # Insert the pattern at regular intervals or randomly
#                 f.write(''.join(str(bit) for bit in pattern))
#                 bits_written += len(pattern)
#             else:
#                 # Write a random bit (0 or 1)
#                 f.write(random.choice(['0', '1']))
#                 bits_written += 1

# # Parameters for file generation
# filename = "random_binary.txt"
# num_bits = 10000  # 10 million bits
# pattern = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]  # 15 consecutive 1's
# # pattern = [0, 0, 0, 1, 0, 1, 1, 1, 1]

# # Generate the file with the pattern inserted
# generate_binary_file_with_pattern(filename, num_bits, pattern)
