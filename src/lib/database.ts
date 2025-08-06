import postgres from 'postgres'

// Use the new Supabase-Vercel integration variables
const connectionString = process.env.POSTGRES_URL || process.env.DATABASE_URL!
const sql = postgres(connectionString, {
  ssl: 'require',
  max: 10,
  idle_timeout: 20,
  connect_timeout: 10
})

export default sql 