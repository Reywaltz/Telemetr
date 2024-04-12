CREATE TABLE users( 
    id SERIAL PRIMARY KEY, 
    username TEXT,
    telegram_id TEXT UNIQUE NOT NULL,
    auth_code TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    valid_to TIMESTAMP WITH TIME ZONE
    );

CREATE TABLE categories(
    name TEXT PRIMARY KEY
);

CREATE TABLE channels(
    id SERIAL PRIMARY KEY,
    owner SERIAL,
    name TEXT NOT NULL DEFAULT '',
    tg_link TEXT DEFAULT '',
    tg_id TEXT UNIQUE,
    category TEXT,
    sub_count INTEGER DEFAULT 0,
    avg_coverage INTEGER DEFAULT 0,
    er INTEGER NOT NULL DEFAULT 0,
    cpm INTEGER NOT NULL DEFAULT 0,
    post_price INTEGER DEFAULT 0,
    photo_path TEXT DEFAULT '',
    CONSTRAINT fk_owner FOREIGN KEY (owner) REFERENCES users(id),
    CONSTRAINT fk_category FOREIGN KEY (category) REFERENCES categories(name)
);

CREATE TABLE admin(
    id SERIAL PRIMARY KEY,
    username TEXT NOT NULL,
    password TEXT NOT NULL,
    access_token TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    valid_to TIMESTAMP WITH TIME ZONE
)


