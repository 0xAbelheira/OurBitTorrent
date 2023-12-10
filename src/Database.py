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

    def get_file_info(self, filename):
        if filename in self.files:
            return self.files[filename]
        else:
            return None

    def delete_file(self, filename):
        if filename in self.files:
            del self.files[filename]
            
    def get_all_files_info_string(self, selected_files=None):
        selected_files = selected_files or self.files.keys()

        return "\n".join(
            f"{file_info['ip']}:{file_info['blocks_available']}:{file_info['total_blocks']}"
            for filename in selected_files
            if (file_info := self.get_file_info(filename)) is not None
        )

    def view_database(self):
        if self.files == {}:
            print("NO INFORMATION IN THE DATABASE!")
        for file, file_info in self.files.items():
            print(f"File: {file}")
            print(f"IP: {file_info['ip']}")
            print(f"Blocks Available: {file_info['blocks_available']}")
            print(f"Total Blocks: {file_info['total_blocks']}")
            print('------------------------')
