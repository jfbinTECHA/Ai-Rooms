-- Initialize database for AI Rooms

-- Create database
CREATE DATABASE ai_rooms;

-- Connect to database
\c ai_rooms;

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS vector;

-- Create tables
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email TEXT UNIQUE NOT NULL,
    display_name TEXT,
    password_hash TEXT,
    created_at timestamptz DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE nomis (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    name TEXT,
    persona JSONB,        -- instructions, system prompt, traits
    default_model TEXT,   -- e.g. "gpt-5-mini" or "local-bert-v2"
    avatar_url TEXT,
    visibility TEXT,      -- private/public
    created_at timestamptz DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE rooms (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT,
    owner_id UUID REFERENCES users(id),
    is_group BOOL,
    created_at timestamptz DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE room_members (
    room_id UUID REFERENCES rooms(id),
    nomi_id UUID REFERENCES nomis(id),
    role TEXT,
    PRIMARY KEY (room_id, nomi_id)
);

CREATE TABLE chat_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    title VARCHAR(200),
    created_at timestamptz DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    room_id UUID REFERENCES rooms(id),
    nomi_id UUID REFERENCES nomis(id),  -- who sent
    text TEXT,
    content JSONB,
    embeddings_id UUID,        -- link to vector entry
    created_at timestamptz DEFAULT CURRENT_TIMESTAMP
);

-- Vector table for embeddings
CREATE TABLE embeddings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_id UUID,        -- e.g. message id
    text TEXT NOT NULL,
    embedding vector(384), -- Assuming 384 dimensions for all-MiniLM-L6-v2
    nomi_id UUID REFERENCES nomis(id),
    room_id UUID REFERENCES rooms(id),
    created_at timestamptz DEFAULT CURRENT_TIMESTAMP
);

-- Index for vector similarity search
CREATE INDEX ON embeddings USING ivfflat (embedding vector_cosine_ops);