CREATE DATABASE IF NOT EXISTS ugc;

CREATE TABLE IF NOT EXISTS ugc.movies_progress (
    user_id UUID,
    movie_id UUID,
    progress Int32,
) ENGINE = MergeTree()
ORDER BY (user_id, movie_id);
