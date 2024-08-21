def read_file(file_path):
    try:
        with open(file_path, 'r') as file:
            file_content = file.read()
            print("File content read successfully.")
            # Now, 'file_content' variable contains the content of the file
            # You can use 'file_content' as needed in your script
            return file_content
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
    except Exception as e:
        print(f"Error: {e}")


def save_to_text_file(file_path, content):
    try:
        with open(file_path, 'w') as file:
            file.write(content)
        print(f"Content successfully saved to '{file_path}'.")
    except Exception as e:
        print(f"Error: {e}")