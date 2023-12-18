class Database:
    def __init__(self):
        """
    Initializes an instance of the Database class.

    The database maintains information about shared files, including their
    availability, the host IP, and the total number of blocks.
    """
        self.files = {}

    def add_file(self, filename, ip, blocks_available, total_blocks):
        """
        Adds or updates information about a file in the database.

        :param filename: The name of the file.
        :param ip: The IP address of the host sharing the file.
        :param blocks_available: The list of available blocks for the file.
        :param total_blocks: The total number of blocks in the file.
        """
        if filename in self.files:
            self.files[filename]['ip'] = ip
            self.files[filename]['blocks_available'] = blocks_available
            self.files[filename]['total_blocks'] = total_blocks
        else:
            self.files[filename] = {
                'ip': ip,
                'blocks_available': blocks_available,
                'total_blocks': total_blocks
            }

    def get_file_info(self, filename):
        """
        Retrieves information about a specific file from the database.

        :param filename: The name of the file.
        :return: Information about the file, or None if the file is not in the database.
        """
        if filename in self.files:
            return self.files[filename]
        else:
            return None

    def delete_file(self, filename):
        """
        Deletes information about a file from the database.

        :param filename: The name of the file to be deleted.
        """
        if filename in self.files:
            del self.files[filename]

    def get_all_files_info_string(self, selected_files=None):
        """
        Retrieves a formatted string containing information about selected files.

        :param selected_files: A list of filenames to include in the string.
                              If None, includes information about all files in the database.
        :return: A formatted string with file information.
        """
        selected_files = selected_files or self.files.keys()

        return "\n".join(
            f"{file_info['ip']}:{file_info['blocks_available']}:{file_info['total_blocks']}"
            for filename in selected_files
            if (file_info := self.get_file_info(filename)) is not None
        )

    def view_database(self):
        """
        Displays information about all files in the database.

        Prints information about each file, including the file name, host IP,
        available blocks, and total blocks.
        """
        if self.files == {}:
            print("NO INFORMATION IN THE DATABASE!")
        for file, file_info in self.files.items():
            print(f"File: {file}")
            print(f"IP: {file_info['ip']}")
            print(f"Blocks Available: {file_info['blocks_available']}")
            print(f"Total Blocks: {file_info['total_blocks']}")
            print('------------------------')
