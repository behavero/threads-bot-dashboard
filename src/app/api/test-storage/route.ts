import { NextRequest, NextResponse } from 'next/server'
import { supabase } from '@/lib/supabase'

export async function GET(request: NextRequest) {
  try {
    console.log('Testing Supabase Storage access...')
    
    // Test 1: Check if we can list buckets
    const { data: buckets, error: bucketsError } = await supabase.storage.listBuckets()
    
    if (bucketsError) {
      console.error('Error listing buckets:', bucketsError)
      return NextResponse.json({
        success: false,
        error: 'Cannot list buckets',
        details: bucketsError.message
      })
    }
    
    console.log('Available buckets:', buckets.map(b => b.name))
    
    // Test 2: Check if 'images' bucket exists
    const imagesBucket = buckets.find(b => b.name === 'images')
    
    if (!imagesBucket) {
      console.error('Images bucket not found')
      return NextResponse.json({
        success: false,
        error: 'Images bucket not found',
        availableBuckets: buckets.map(b => b.name)
      })
    }
    
    // Test 3: Try to list files in images bucket
    const { data: files, error: filesError } = await supabase.storage
      .from('images')
      .list()
    
    if (filesError) {
      console.error('Error listing files:', filesError)
      return NextResponse.json({
        success: false,
        error: 'Cannot list files in images bucket',
        details: filesError.message
      })
    }
    
    console.log('Files in images bucket:', files)
    
    return NextResponse.json({
      success: true,
      message: 'Supabase Storage is accessible',
      buckets: buckets.map(b => b.name),
      imagesBucket: {
        name: imagesBucket.name,
        public: imagesBucket.public,
        fileCount: files.length
      }
    })
    
  } catch (error) {
    console.error('Storage test error:', error)
    return NextResponse.json({
      success: false,
      error: 'Storage test failed',
      details: error instanceof Error ? error.message : 'Unknown error'
    })
  }
} 