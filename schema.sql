CREATE TABLE users( 
    id SERIAL PRIMARY KEY, 
    username TEXT NOT NULL
    );

CREATE TABLE categories(
    name TEXT PRIMARY KEY
);

CREATE TABLE auth_key(
    user_id SERIAL PRIMARY KEY,
    auth_code TEXT DEFAULT 'code',
    created_at DATE DEFAULT NOW(),
    valid_to DATE DEFAULT NOW(),
    CONSTRAINT fk_user_id FOREIGN KEY (user_id) REFERENCES users(id)
    );

CREATE TABLE channels(
    id SERIAL PRIMARY KEY,
    owner SERIAL,
    name TEXT NOT NULL DEFAULT '',
    tg_link TEXT DEFAULT '',
    category TEXT,
    sub_count INTEGER DEFAULT 0,
    avg_coverage INTEGER DEFAULT 0,
    er INTEGER NOT NULL DEFAULT 0,
    cpm INTEGER NOT NULL DEFAULT 0,
    post_price INTEGER DEFAULT 0,
    CONSTRAINT fk_owner FOREIGN KEY (owner) REFERENCES users(id),
    CONSTRAINT fk_category FOREIGN KEY (category) REFERENCES categories(name)
);


