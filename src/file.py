class File:
    def __init__(self, name, size, num_blocks, block_size):
        self.name = name
        self.size = size
        self.num_blocks = num_blocks
        self.block_size = 1000
        self.blocks_available = list(range(1, num_blocks + 1)) #//TODO Deste modo todos os blocos estão diponiveis, o que não é o melhor
    
    def __str__(self):
        return f"File(name={self.name}, size={self.size} bytes, num_blocks={self.num_blocks}, block_size={self.block_size}"
     
    def get_file_info(self):
        return{
            'name': self.name,
            'size': self.size,
            'num_blocks': self.num_blocks,
            'block_size': self.block_size,
            'blocks_available': self.blocks_available
        }
        
    def mark_block_unavailable(self, block_number):
        if block_number in self.blocks_available:
            self.blocks_available.remove(block_number)
            return True
        else:
            return False

    def mark_block_available(self, block_number):
        if block_number not in self.blocks_available:
            self.blocks_available.append(block_number)
            return True
        else:
            return False
    