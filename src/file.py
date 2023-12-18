import logging
import os

class File:
    def __init__(self, name="", block_size=1024):
        """
        Initializes a File object.

        :param name: The name of the file.
        :param block_size: The size of each block in bytes.
        """
        self.block_size = block_size
        self.name = name
        self.size = os.path.getsize(name) if name else 0
        self.num_blocks = self.calculate_blocks(self.size, self.block_size)
        self.blocks_available = list(range(1, self.num_blocks + 1))
        self.block_data = self.divide_into_blocks() if name else []

    def __str__(self):
        """
        Returns a string representation of the File object.

        :return: A string representation of the File object.
        """
        return f"File(name={self.name}, size={self.size} bytes, num_blocks={self.num_blocks}, block_size={self.block_size}, 'blocks_data'={self.block_size}"

    def set_values(self, name, size):
        """
        Sets the values of the file.

        :param name: The name of the file.
        :param size: The size of the file in bytes.
        """
        self.name = name
        self.size = size
        self.num_blocks = self.calculate_blocks(self.size, self.block_size)

    def add_blockdata(self, data, block_number):
        """
        Adds block data to the file.

        :param data: The data to be added.
        :param block_number: The block number.
        """
        self.block_data.append({'block_number': block_number, 'data': data})
        self.blocks_available.append(block_number)

    def build_file(self):
        """
        Builds the file from block data and saves it.
        """
        file = open(self.name[:-4] + "transfered.txt", "wb")
        sorted_blocks = sorted(self.block_data, key=lambda x: x['block_number'])
        file_bytes = b""
        for block in sorted_blocks:
            if isinstance(block['data'], str):
                file_bytes += block['data'].encode("utf-8")
            elif isinstance(block['data'], bytes):
                file_bytes += block['data']
            else:
                # Handle the case where the data type is not bytes or str
                pass
        file.write(file_bytes)
        file.close()

    def calculate_blocks(self, size, block_size):
        """
        Calculates the number of blocks needed for the given size and block size.

        :param size: The size of the file in bytes.
        :param block_size: The size of each block in bytes.
        :return: The number of blocks needed.
        """
        if size % block_size == 0:
            return int(size / block_size)
        else:
            return int(size / block_size + 1)

    def divide_into_blocks(self):
        """
        Divides the file into blocks.

        :return: A list of blocks, each containing block number and data.
        """
        blocks = []

        with open(self.name, 'rb') as file:
            block_number = 1
            while True:
                data = file.read(self.block_size)
                if not data:
                    break
                blocks.append({'block_number': block_number, 'data': data})
                block_number += 1

        return blocks

    def get_file_info(self):
        """
        Retrieves information about the file.

        :return: A dictionary containing information about the file.
        """
        return {
            'name': self.name,
            'size': self.size,
            'num_blocks': self.num_blocks,
            'block_size': self.block_size,
            'blocks_available': self.blocks_available,
            'blocks_data': self.block_data
        }

    def mark_blocks_unavailable(self, block_numbers):
        """
        Marks specified blocks as unavailable.

        :param block_numbers: A list of block numbers to be marked as unavailable.
        """
        for block_number in block_numbers:
            if self.mark_block_unavailable(block_number):
                logging.debug(f"Marked block {block_number} as unavailable for file {self.name}")

    def mark_blocks_available(self, block_numbers):
        """
        Marks specified blocks as available.

        :param block_numbers: A list of block numbers to be marked as available.
        """
        for block_number in block_numbers:
            if self.mark_block_available(block_number):
                logging.debug(f"Marked block {block_number} as available for file {self.name}")
