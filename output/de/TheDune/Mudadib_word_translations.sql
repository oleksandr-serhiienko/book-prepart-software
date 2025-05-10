
CREATE TABLE IF NOT EXISTS word_translations (
    id INTEGER PRIMARY KEY,
    translations TEXT,
    word TEXT                  
);

CREATE TABLE IF NOT EXISTS word_contexts (
    word_id INTEGER,
    context_id INTEGER,
    original_text TEXT,
    translated_text TEXT,
    PRIMARY KEY (word_id, context_id),
    FOREIGN KEY (word_id) REFERENCES word_translations(id)
);

CREATE TABLE IF NOT EXISTS word_info (
    word_id INTEGER PRIMARY KEY,
    info TEXT,
    FOREIGN KEY (word_id) REFERENCES word_translations(id)
);
