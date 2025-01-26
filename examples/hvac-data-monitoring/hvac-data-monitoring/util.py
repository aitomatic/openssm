import os

# Initialize the dictionary to store the answers
ANSWER_DICT = {}

# List of markdown files
file_names = ["ans1.md", "ans2.md", "ans3.md"]

# Read each file and store its content in the dictionary
for file_name in file_names:
    if os.path.exists(file_name):  # Check if the file exists
        with open(file_name, "r", encoding="utf-8") as file:            # Extract the answer key from the file name (e.g., ans1 -> question_1)
            answer_key = f"{file_name[:-3]}"  # Dynamically set the key
            print(file_name)
            ANSWER_DICT[answer_key] = file.read()
    else:
        print(f"File {file_name} does not exist!")
    print(ANSWER_DICT)

# Print the dictionary to verify the content
print(ANSWER_DICT)
