create table if not exists accounts (
  id uuid default uuid_generate_v4() primary key,
  username text not null,
  password text not null,
  active boolean default true,
  created_at timestamptz default now()
);

create table if not exists captions (
  id uuid default uuid_generate_v4() primary key,
  text text not null,
  used boolean default false,
  created_at timestamptz default now()
);

create table if not exists images (
  id uuid default uuid_generate_v4() primary key,
  url text not null,
  used boolean default false,
  created_at timestamptz default now()
);

create table if not exists posting_history (
  id uuid default uuid_generate_v4() primary key,
  account_id uuid references accounts(id),
  caption_id uuid references captions(id),
  image_id uuid references images(id),
  timestamp timestamptz default now(),
  status text
);