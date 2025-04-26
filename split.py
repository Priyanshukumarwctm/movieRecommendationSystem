import pickle

# Load the original file
with open('similarity.pkl', 'rb') as f:
    data = pickle.load(f)

# Calculate the size of each part
num_parts = 8
chunk_size = len(data) // num_parts

# Split the data into 8 parts
for i in range(num_parts):
    start = i * chunk_size
    end = None if i == num_parts - 1 else (i + 1) * chunk_size  # Ensure the last part gets all remaining data
    part_data = data[start:end]
    part_file = f'similarity_part{i+1}.pkl'
    with open(part_file, 'wb') as part_f:
        pickle.dump(part_data, part_f)
    print(f"Part {i+1} saved as {part_file}")
