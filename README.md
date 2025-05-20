# 🌿 Find a Fragrance — Smarter Scent Discovery

Welcome to **Find a Fragrance**, an intelligent fragrance recommendation engine that understands **what you're looking for** — even when you don't know the name. This project uses **semantic search**, powered by AI-generated **vector embeddings**, to help users find fragrances based on style, mood, and descriptive intent.

---

## 🧠 How It Works

Instead of relying on keyword matching, FragranceFinder uses **semantic embeddings** to represent both user queries and fragrance profiles in high-dimensional vector space.

### ✨ Example

> User query:  
> *"I'm looking for something fresh and woody, but not too strong."*

Even if those exact words don’t appear in any fragrance description, the system understands the **intent** and recommends colognes that match the vibe — like crisp green notes or light cedar blends.

---

## 🔍 Under the Hood

### 🧬 1. Text Embedding
User input is passed into a **Sentence Transformer** model (e.g., `all-MiniLM-L6-v2`), which converts text into a vector embedding.

### 🧱 2. Vector Storage
Each fragrance in our database has a precomputed embedding, generated from its **description**, **notes**, and **style**.

### 📐 3. Semantic Similarity Search
We use **cosine similarity** to compare the user’s embedding against every stored fragrance vector.

### 🏆 4. Ranking & Recommendations
The top matches are returned based on highest similarity — with the option to include filters like price, gender, or season.

---

## 💡 Why This Matters

Semantic search provides a **human-like** way to find fragrances. It's not about guessing the right keywords — it's about **expressing what you want** and letting AI interpret it.

---

## ⚠️ Current Limitations

- **All results displayed**: When looking at specific brands, or scents based off a season, all available fragrances are displayed. Adding a 'see more' button is desired for a more user-friendly UI in the front-end application.
- **In-memory similarity**: Not optimized for very large datasets.
- **No hybrid filtering yet**: Can’t combine vector search with metadata filtering (e.g., price or season).
- **Embeddings are static**: Based only on initial descriptions.
- **Explainability is low**: Hard to show why a result is relevant.

---

## 🚀 Future Plans

- ✅ Integrate **pgvector** or **FAISS** for scalable vector indexing  
- ✅ Support hybrid search (e.g., vector + filter by season/gender)  
- ✅ Use **multi-modal embeddings** (notes + tone + metadata)  
- ✅ Rerank results with **user behavior** (clicks, favorites)  
- ✅ Add confidence or similarity scores to increase transparency  

---

## 📦 Tech Stack

- **Backend**: Python + Flask  
- **Embedding Model**: Sentence Transformers  
- **Vector Math**: Numpy + Cosine Similarity  
- **Frontend**: HTML/CSS/JS/Bootstrap 

---

## 🧰 Installation

```bash
git clone https://github.com/your-username/fragrancefinder.git
cd fragrancefinder
python3 -m venv venv
source venv/bin/activate
```

Run locally:
```bash
flask run

```
Note: .env data is not included for the database configuration (secrey key), API to populate database, or links in the footer.

---


## 🤝 Contributing

Have fragrance data, design ideas, or feature suggestions? Pull requests and issues are welcome!
