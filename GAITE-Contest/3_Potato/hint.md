The task is based on using an embedding (vector) representation of words. The key property of these vectors is that they are semantic: embedding("banana") is more similar to embedding("apple") than to embedding("horse").

For normalized vectors, this means that: `emb("banana") * emb("apple") > emb("banana") * emb("horse")`

So if you multiply embeddings by embeddings.T, you get a full matrix of how similar the words are to each other.

You can start with a binary search over this embedding space.
