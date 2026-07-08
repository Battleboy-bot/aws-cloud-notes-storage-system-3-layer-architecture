CREATE DATABASE IF NOT EXISTS notes_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE notes_db;

CREATE TABLE IF NOT EXISTS files (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    title VARCHAR(150) NOT NULL,
    filename VARCHAR(255) NOT NULL,
    s3_key VARCHAR(512) NOT NULL,
    content_type VARCHAR(120) NOT NULL,
    size_bytes BIGINT UNSIGNED NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_files_s3_key (s3_key),
    KEY idx_files_title (title),
    KEY idx_files_filename (filename),
    KEY idx_files_created_at (created_at)
) ENGINE=InnoDB;
