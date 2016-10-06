drop table if exists entries;
create table entries (
  id integer primary key autoincrement,
  title text not null,
  'text' text not null,
  name text not null,
  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
create table users (
      name text not null primary key,
      password text not null,
      timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
