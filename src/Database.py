class Database:
    def __init__(self):
        self.files = {}

    def add_file(self, filename, ip, blocks_available, total_blocks):
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

    """
    def update_file_info(self, filename, ip, blocks_available, total_blocks):
        if filename in self.files:
            self.files[filename]['ip'] = ip
            self.files[filename]['blocks_available'] = blocks_available
            self.files[filename]['total_blocks'] = total_blocks
    """

    def get_file_info(self, filename):
        if filename in self.files:
            return self.files[filename]
        else:
            return None

    def delete_file(self, filename):
        if filename in self.files:
            del self.files[filename]

    def view_database(self):
        if self.files == {}:
            print("NO INFORMATION IN THE DATABASE!")
        for file, file_info in self.files.items():
            print(f"File: {file}")
            print(f"IP: {file_info['ip']}")
            print(f"Blocks Available: {file_info['blocks_available']}")
            print(f"Total Blocks: {file_info['total_blocks']}")
            print('------------------------')
