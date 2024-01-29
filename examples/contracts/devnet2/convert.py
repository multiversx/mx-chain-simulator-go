import json

# Load the original JSON data from the file
with open('output.json', 'r') as file:
    original_data = json.load(file)

# Extract relevant data from the original JSON
address = "erd1lllllllllllllllllllllllllllllllllllllllllllllllllllllsckry7t"
balance = "0"
pairs_data = original_data["data"]["pairs"]

# Create the new JSON structure
new_data = [
    {
        "address": address,
        "balance": balance,
        "keys": pairs_data
    }
]

# Save the new JSON data to a new file
with open('state_2.json', 'w') as new_file:
    json.dump(new_data, new_file, indent=2)

print("Conversion successful. New JSON data saved to 'your_new_file.json'")