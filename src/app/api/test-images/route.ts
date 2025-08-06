import { NextResponse } from 'next/server'
import { supabase } from '@/lib/supabase'
import sql from '@/lib/database'

export async function GET() {
  try {
    // Test database connection
    const dbResult = await sql`SELECT COUNT(*) as count FROM images`
    
    // Test Supabase storage
    const { data: storageData, error: storageError } = await supabase.storage
      .from('images')
      .list('', { limit: 1 })

    return NextResponse.json({
      success: true,
      message: 'Images API test successful',
      database: {
        imageCount: dbResult[0]?.count || 0,
        connection: 'OK'
      },
      storage: {
        bucket: 'images',
        connection: storageError ? 'ERROR' : 'OK',
        error: storageError?.message || null
      },
      env: {
        hasSupabaseUrl: !!process.env.NEXT_PUBLIC_SUPABASE_URL,
        hasSupabaseKey: !!process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY,
        hasDatabaseUrl: !!process.env.DATABASE_URL
      }
    })

  } catch (error) {
    return NextResponse.json({
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error',
      message: 'Images API test failed'
    }, { status: 500 })
  }
} 