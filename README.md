# Find a Fragrance

An intelligent cologne recommendation platform that uses semantic search and natural language processing (NLP) to match users with fragrances. Users can describe their scent preferences in everyday language (e.g., “I’m looking for something sweet but masculine”), and the system returns personalized suggestions by comparing the query’s vector embedding against stored embeddings of colognes. These embeddings are generated using structured scent data like notes, accords, and brand context. The goal was to blend conversational AI with semantic vector similarity to create an intuitive, expressive, and highly personalized fragrance discovery experience for users. 

# Technical Explination

- Text Embedding:
  User input is passed into a machine learning model called a Sentence Transformer, which converts the user sentence into a high-dimensional vector embedding, a list of numbers that represents the meaning of your query.

 - Vector Storage:
Each cologne in the database has its own precomputed embedding, based on its description, notes, and accords.

- Similarity Search:
  The user-query embedding is compared against every cologne embedding using cosine similarity: a metric that measures how close the meanings are in vector space.

- Top Matches:
The system ranks the colognes by similarity and returns the most relevant matches, even if they don't share exact words with your input (limited to top 9 results).

Why This Matters:
This approach allows a request to be matched based on intent and style, not just text. Whether you’re looking for “a clean, office-safe scent” or “something smoky and romantic,” fragrances are recommended that fit the vibe, not just the words.
