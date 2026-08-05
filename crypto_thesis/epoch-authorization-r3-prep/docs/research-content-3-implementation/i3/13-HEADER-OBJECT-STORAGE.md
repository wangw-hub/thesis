# Header Object Storage

Signed canonical Header bytes are stored as immutable `HEADER` objects through the I2 StorageGateway. Their object reference uses SHA-256 and size. Reads revalidate reference, length and digest before strict parsing.

Body and Header are distinct immutable objects. Body reference/digest is signed inside the Header. Neither object storage nor an object digest is authorization proof or a chain anchor.

