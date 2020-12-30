

# Import packages
from CryptoContainer import CryptoContainer

# Encryption key
key = b"nhQ0JPN1X0aaNIal"

# Create container
with CryptoContainer("secure_storage.dat") as container:

    # Create new empty partition if not exists
    if not container.contains_partition(key):
        partition = container.create_partition(key)
        partition.close() # Close (save all changes)

    # Open partition
    with container.open_partition(key) as partition:
        # Write 'test.py' to partition
        partition.handle.write('test.py')
        # Extract files to 'out' directory
        partition.handle.extractall('out')
        # Print files list
        print(partition.handle.filelist)
        partition.export_zip("1.zip")
        # Delete partition with all files
        # container.erase_partition(partition)
