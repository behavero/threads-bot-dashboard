import { NextRequest, NextResponse } from 'next/server'
import { supabase } from '@/lib/supabase'

export async function GET(request: NextRequest) {
  try {
    console.log('Testing Supabase Storage...')
    console.log('Supabase URL:', process.env.NEXT_PUBLIC_SUPABASE_URL)
    console.log('Supabase Key exists:', !!process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY)
    
    // Test bucket listing
    const { data: buckets, error: bucketError } = await supabase.storage.listBuckets()
    console.log('Buckets response:', { buckets, error: bucketError })
    
    if (bucketError) {
      return NextResponse.json({
        success: false,
        error: bucketError.message,
        details: bucketError
      })
    }
    
    // Check if images bucket exists
    const imagesBucket = buckets?.find(b => b.name === 'images')
    console.log('Images bucket found:', !!imagesBucket)
    
    if (!imagesBucket) {
      return NextResponse.json({
        success: false,
        error: 'Images bucket not found',
        availableBuckets: buckets?.map(b => b.name) || []
      })
    }
    
    // Test listing files in images bucket
    const { data: files, error: filesError } = await supabase.storage
      .from('images')
      .list('', { limit: 10 })
    
    console.log('Files in images bucket:', { files, error: filesError })
    
    return NextResponse.json({
      success: true,
      message: 'Supabase Storage connection successful',
      bucketExists: true,
      filesCount: files?.length || 0,
      availableBuckets: buckets?.map(b => b.name) || []
    })
  } catch (error) {
    console.error('Storage test error:', error)
    return NextResponse.json({
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error'
    })
  }
} 