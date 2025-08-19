PRAGMA journal_mode=WAL;

CREATE TABLE IF NOT EXISTS movies (
  movieId INTEGER PRIMARY KEY,
  title TEXT NOT NULL,
  year INTEGER,
  genres TEXT
);

CREATE TABLE IF NOT EXISTS ratings (
  userId INTEGER,
  movieId INTEGER,
  rating REAL,
  timestamp INTEGER,
  PRIMARY KEY (userId, movieId)
);

CREATE TABLE IF NOT EXISTS tags (
  userId INTEGER,
  movieId INTEGER,
  tag TEXT,
  timestamp INTEGER,
  PRIMARY KEY (userId, movieId, tag)
);

CREATE TABLE IF NOT EXISTS meta (
  key TEXT PRIMARY KEY,
  value TEXT
);

-- Cache of precomputed artifacts
CREATE TABLE IF NOT EXISTS cache (
  key TEXT PRIMARY KEY,
  value BLOB
);
