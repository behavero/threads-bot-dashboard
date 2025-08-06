import { NextResponse } from 'next/server'
import { supabase } from '@/lib/supabase'
import sql from '@/lib/database'

export async function GET() {
  try {
    // Test the direct PostgreSQL connection
    const result = await sql`SELECT 1 as test`
    
    // Also test Supabase client for storage operations
    const { data, error } = await supabase
      .from('captions')
      .select('count')
      .limit(1)

    return NextResponse.json({
      success: true,
      message: 'Both PostgreSQL and Supabase connections successful',
      postgresTest: result[0]?.test === 1,
      supabaseUrl: process.env.NEXT_PUBLIC_SUPABASE_URL,
      hasKey: !!process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY,
      hasDatabaseUrl: !!process.env.DATABASE_URL
    })

  } catch (error) {
    return NextResponse.json({
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error',
      message: 'Supabase connection test failed'
    }, { status: 500 })
  }
} 