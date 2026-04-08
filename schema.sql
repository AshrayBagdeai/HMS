
CREATE TABLE IF NOT EXISTS patients (
    Pid INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    dob TEXT NOT NULL,
    email TEXT  NOT NULL,
    pnum TEXT ,
    username TEXT ,
    password TEXT,
    age INTEGER,
    gender TEXT,
    city Text,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS doctor (
    Did INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    dob TEXT NOT NULL,
    email TEXT  NOT NULL,
    pnum TEXT ,
    username TEXT UNIQUE,
    password TEXT,
    age INTEGER,
    gender TEXT,
    available TEXT,
    timing TEXT NOT NULL,
    Hid INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    specifications text,
    FOREIGN KEY (Hid) REFERENCES hospitals(Hid) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS hospitals (
    Hid INTEGER PRIMARY KEY AUTOINCREMENT,
    hname TEXT not null unique,
    address TEXT NOT NULL,
    city TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    contact_number TEXT
);

CREATE TABLE IF NOT EXISTS appointments (
    Aid INTEGER PRIMARY KEY AUTOINCREMENT,
    Hid INTEGER NOT NULL,
    Pid INTEGER NOT NULL,
    Did INTEGER NOT NULL,
    date TEXT NOT NULL,
    time TEXT NOT NULL,
    status TEXT NOT NULL,
    prescription TEXT,
    diagnosis TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (Pid) REFERENCES patients(Pid),
    FOREIGN KEY (Hid) REFERENCES hospitals(Hid),
    FOREIGN KEY (Did) REFERENCES doctor(Did)
);
