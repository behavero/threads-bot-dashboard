import { NextRequest, NextResponse } from 'next/server'
import { supabase } from '@/lib/supabase'

export async function GET(request: NextRequest) {
  try {
    // Test 1: Check if we can access storage
    console.log('Testing Supabase Storage access...')
    
    // Test 2: List buckets
    const { data: buckets, error: bucketsError } = await supabase.storage.listBuckets()
    console.log('Buckets:', buckets)
    console.log('Buckets error:', bucketsError)
    
    // Test 3: Try to list files in images bucket
    const { data: files, error: filesError } = await supabase.storage
      .from('images')
      .list()
    console.log('Files in images bucket:', files)
    console.log('Files error:', filesError)
    
    // Test 4: Check environment variables
    const envCheck = {
      hasSupabaseUrl: !!process.env.NEXT_PUBLIC_SUPABASE_URL,
      hasSupabaseAnonKey: !!process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY,
      supabaseUrl: process.env.NEXT_PUBLIC_SUPABASE_URL,
      anonKeyLength: process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY?.length || 0
    }
    
    return NextResponse.json({
      success: true,
      buckets: buckets || [],
      bucketsError: bucketsError?.message || null,
      files: files || [],
      filesError: filesError?.message || null,
      envCheck
    })
  } catch (error) {
    console.error('Test upload error:', error)
    return NextResponse.json(
      { success: false, error: 'Test failed' },
      { status: 500 }
    )
  }
} 

export async function POST(request: NextRequest) {
  try {
    console.log('Testing file upload to Supabase Storage...')
    
    const formData = await request.formData()
    const file = formData.get('file') as File
    
    if (!file) {
      return NextResponse.json({
        success: false,
        error: 'No file provided'
      })
    }
    
    console.log('Test file:', { name: file.name, size: file.size, type: file.type })
    
    // Test upload to images bucket
    const fileName = `test-${Date.now()}-${file.name}`
    
    const { data: uploadData, error: uploadError } = await supabase.storage
      .from('images')
      .upload(fileName, file, {
        cacheControl: '3600',
        upsert: false
      })
    
    console.log('Upload test response:', { uploadData, uploadError })
    
    if (uploadError) {
      return NextResponse.json({
        success: false,
        error: uploadError.message,
        details: uploadError
      })
    }
    
    // Get public URL
    const { data: urlData } = supabase.storage
      .from('images')
      .getPublicUrl(fileName)
    
    console.log('Public URL:', urlData.publicUrl)
    
    return NextResponse.json({
      success: true,
      message: 'Test upload successful',
      fileName,
      publicUrl: urlData.publicUrl,
      uploadData
    })
  } catch (error) {
    console.error('Test upload error:', error)
    return NextResponse.json({
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error'
    })
  }
} 