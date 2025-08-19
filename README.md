# Local Movie Recommendation System with LLaMA 3

A local, privacy-friendly movie recommendation web app that uses the **MovieLens dataset**, **SQLite**, **pandas**, and a **locally hosted LLaMA 3 model** to interpret natural language queries.  
You can ask in plain English (e.g., *"Recommend me a sci-fi movie after 2010 that’s not horror"*) and get back personalized recommendations with explanations.

---

## Features

- **Natural language queries** parsed by a local LLaMA 3 model (via `llama-cpp-python`).
- **Content-based recommendations** using genres, tags, and TF-IDF similarity.
- **Popularity weighting** with average rating and rating count from MovieLens.
- **Offline storage** with SQLite (no external database required).
- **Web interface** built with Flask + Tailwind styling.
- **Explanations**: LLaMA generates short justifications for why each movie fits.

---

## Setup
### 1. Clone the repository

```bash
git clone https://github.com/yourusername/movie-recs-llm.git
cd movie-recs-llm
```
### 2. **Create a virtual environment & install dependencies**

   - Create a virtual environment:

     ```bash
     python -m venv .venv
     ```

   - Activate the virtual environment:

     - On macOS/Linux:  
       ```bash
       source .venv/bin/activate
       ```
     - On Windows:  
       ```bash
       .venv\Scripts\activate
       ```

   - Install the required packages:

     ```bash
     pip install -r requirements.txt
     ```
### 3. **Download MovieLens dataset**

   - Go to the [MovieLens dataset page](https://grouplens.org/datasets/movielens/) and download **ml-latest-small** (recommended for testing).
   - Extract the files into `data/movielens/` so the folder contains:
     - `movies.csv`
     - `ratings.csv`
     - `tags.csv`
     - `links.csv` (optional)
### 4. **Add a local LLaMA 3 model**

   - Download a `.gguf` build of **Meta LLaMA 3 Instruct** (e.g., from Hugging Face).  
   - Place the model file in the `models/` folder, for example:  
     ```
     models/llama-3.gguf
     ```
### 5. **Configure paths**

   - Copy the example configuration file:

     ```bash
     cp config.example.toml config.toml
     ```

   - Open `config.toml` and set the following paths:
     - `movielens_dir` → path to your MovieLens CSV files  
     - `sqlite_path` → path to your SQLite database file  
     - `model_path` → path to your `.gguf` LLaMA model
### 6. **Run the app**

   - Start the Flask application:

     ```bash
     python app.py
     ```

   - Open your browser and go to:  
     [http://127.0.0.1:5000](http://127.0.0.1:5000)
    
