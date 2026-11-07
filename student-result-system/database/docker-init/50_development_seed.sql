-- Docker-only development administrator. Password: admin123
-- This data is for local development only; never use it in production.
INSERT INTO users (username, email, password_hash, name, is_admin)
VALUES (
    'admin',
    'admin@example.com',
    '$argon2id$v=19$m=65536,t=3,p=4$MRxVAvtSZo2Q3xOn6+X+2Q$iVhBFW9X21y2if8D8bDtyBm5Gb9TsPzhivL09Lj1NhY',
    'Development Administrator',
    TRUE
);
