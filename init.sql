CREATE TABLE utenti (
    email VARCHAR(100) NOT NULL PRIMARY KEY,
    ticker VARCHAR(5) NOT NULL,
    high_value FLOAT(10),
    low_value FLOAT(10)
);

CREATE TABLE data (
    email VARCHAR(100) NOT NULL,
    ticker VARCHAR(5) NOT NULL,
    valore FLOAT(10),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (email) REFERENCES utenti(email)
);