import { NextResponse } from 'next/server'
import { supabase } from '@/lib/supabase'

export async function GET() {
  try {
    console.log('Testing images API...')
    
    // Test environment variables
    const envCheck = {
      hasSupabaseUrl: !!process.env.NEXT_PUBLIC_SUPABASE_URL,
      hasSupabaseKey: !!process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY,
      supabaseUrl: process.env.NEXT_PUBLIC_SUPABASE_URL?.substring(0, 20) + '...',
      supabaseKey: process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY?.substring(0, 20) + '...'
    }
    
    console.log('Environment check:', envCheck)

    // Test database connection
    const { data: dbResult, error: dbError } = await supabase
      .from('images')
      .select('count', { count: 'exact', head: true })
    
    console.log('Database test result:', { dbResult, dbError })

    // Test Supabase storage
    const { data: storageData, error: storageError } = await supabase.storage
      .from('images')
      .list('', { limit: 1 })

    console.log('Storage test result:', { storageData, storageError })

    return NextResponse.json({
      success: true,
      message: 'Images API test successful',
      environment: envCheck,
      database: {
        connection: dbError ? 'ERROR' : 'OK',
        error: dbError?.message || null
      },
      storage: {
        bucket: 'images',
        connection: storageError ? 'ERROR' : 'OK',
        error: storageError?.message || null
      }
    })

  } catch (error) {
    console.error('Test failed:', error)
    return NextResponse.json({
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error',
      message: 'Images API test failed'
    }, { status: 500 })
  }
} 