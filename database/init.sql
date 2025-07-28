-- =============================================================================
--  Database Initialization Script for Semantic Network Indexer
--  Target Database: PostgreSQL
--  Version: 1.0
-- =============================================================================
--  This script sets up the required tables, indexes, and extensions for the
--  application. It is designed to be idempotent.
-- =============================================================================


-- === 1. ENABLE EXTENSIONS ===
-- These extensions provide necessary functionality for the application.
--
-- 'uuid-ossp': For generating UUIDs, which are used as primary keys.
-- 'vector': The pgvector extension for storing and searching embeddings.
-------------------------------------------------------------------------------
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS vector;


-- === 2. CREATE CORE TABLES ===
-- These tables form the core of the file indexing system.
-------------------------------------------------------------------------------

--
-- Table: Files
-- Purpose: The central table holding the identity and core metadata for every
--          indexed file. This is the "source of truth" for file existence.
--
CREATE TABLE IF NOT EXISTS Files (
    -- The unique identifier for this file within our system.
    ID              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- The full, canonical path to the file on the network drive.
    Path            TEXT NOT NULL UNIQUE,

    -- The filesystem-level unique ID (e.g., inode on Linux, MFT ID on Windows).
    -- This is critical for reliably tracking files across renames and moves.
    FsID            TEXT NOT NULL,

    -- The SHA256 hash of the file's content, used for change detection
    -- and identifying duplicate files.
    SHA256          CHAR(64) NOT NULL,

    -- The size of the file in bytes.
    SizeBytes       BIGINT NOT NULL,

    -- The 'last modified' timestamp from the operating system.
    -- TIMESTAMPTZ is used to store the timestamp with timezone information.
    LastModified    TIMESTAMPTZ NOT NULL,

    -- The timestamp when this record was first created in our database.
    CreatedAt       TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- The timestamp when this file was last processed by our indexer.
    LastIndexed     TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- The semantic vector embedding. This column is nullable as the primary
    -- vector store might be external (like Weaviate), or embedding might fail.
    -- The dimension (e.g., 768) MUST match your embedding model's output.
    Embedding       vector(768)
);

COMMENT ON TABLE Files IS 'Central repository for file identity and core OS metadata.';
COMMENT ON COLUMN Files.FsID IS 'Filesystem-level unique ID for tracking renames.';
COMMENT ON COLUMN Files.Embedding IS 'Semantic vector. Dimension must match the ML model.';


--
-- Table: Keywords
-- Purpose: Stores a unique list of all manually added keywords or tags.
--
CREATE TABLE IF NOT EXISTS Keywords (
    ID      SERIAL PRIMARY KEY,
    Word    TEXT NOT NULL UNIQUE
);

COMMENT ON TABLE Keywords IS 'Stores a unique list of user-defined keywords or tags.';


--
-- Table: File_Keyword_Xref
-- Purpose: A junction table to create a many-to-many relationship between
--          Files and Keywords, allowing a file to have multiple tags.
--
CREATE TABLE IF NOT EXISTS File_Keyword_Xref (
    FileID      UUID REFERENCES Files(ID) ON DELETE CASCADE,
    KeywordID   INTEGER REFERENCES Keywords(ID) ON DELETE CASCADE,
    PRIMARY KEY (FileID, KeywordID) -- Prevents duplicate tags on the same file.
);

COMMENT ON TABLE File_Keyword_Xref IS 'Junction table linking files to their keywords.';


--
-- Table: Flagged_Content
-- Purpose: Tracks files that users have flagged with the "Doesn't look right?"
--          button, creating a queue for manual review.
--
CREATE TABLE IF NOT EXISTS Flagged_Content (
    FlagID      SERIAL PRIMARY KEY,
    FileID      UUID NOT NULL REFERENCES Files(ID) ON DELETE CASCADE,
    UserID      TEXT, -- Placeholder for user identifier (e.g., email, username)
    FlaggedAt   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    Reason      TEXT, -- Optional comment from the user.
    Status      TEXT NOT NULL DEFAULT 'Pending' CHECK (Status IN ('Pending', 'Reviewed', 'Resolved'))
);

COMMENT ON TABLE Flagged_Content IS 'Tracks user-submitted flags for content review.';


-- === 3. CREATE INDEXES ===
-- Indexes are critical for ensuring fast query performance, especially as the
-- number of files grows into the millions.
-------------------------------------------------------------------------------

-- Indexes for fast lookups on the Files table based on common query patterns.
CREATE INDEX IF NOT EXISTS idx_files_path ON Files (Path);
CREATE INDEX IF NOT EXISTS idx_files_fsid ON Files (FsID);
CREATE INDEX IF NOT EXISTS idx_files_sha256 ON Files (SHA256);

-- A HNSW (Hierarchical Navigable Small World) index for vector similarity search.
-- This is the key to making semantic search fast within PostgreSQL.
-- Use 'vector_l2_ops' for Euclidean distance, 'vector_ip_ops' for inner product,
-- or 'vector_cosine_ops' for cosine distance, depending on your model.
CREATE INDEX IF NOT EXISTS idx_files_embedding_hnsw ON Files USING hnsw (Embedding vector_l2_ops);

-- Index on the Keywords table for fast tag lookups.
CREATE INDEX IF NOT EXISTS idx_keywords_word ON Keywords (Word);


-- =============================================================================
--  End of Script
-- =============================================================================