# :closed_lock_with_key: CryptoContainer
Python module for secure, encrypted file storage


## :computer: Install
> pip install CryptoContainer


## :mega: Example
``` python
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
        # Write 'image.png' to partition
        partition.handle.write('image.png')
        # Extract files to 'out' directory
        partition.handle.extractall('out')
        # Print files list
        print(partition.handle.filelist)
        partition.export_zip("export.zip")
        # Delete partition with all files
        container.erase_partition(partition)
```
