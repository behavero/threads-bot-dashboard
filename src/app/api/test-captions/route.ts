import { NextRequest, NextResponse } from 'next/server'
import { supabase } from '@/lib/supabase'

export async function POST(request: NextRequest) {
  try {
    console.log('Testing caption creation...')
    console.log('Supabase URL:', process.env.NEXT_PUBLIC_SUPABASE_URL)
    console.log('Supabase Key exists:', !!process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY)
    
    const body = await request.json()
    console.log('Test request body:', body)
    
    // Test data
    const testCaption = {
      text: 'Test caption from API',
      category: 'test',
      tags: ['test', 'api'],
      used: false
    }
    
    console.log('Inserting test caption:', testCaption)
    
    const { data: caption, error } = await supabase
      .from('captions')
      .insert(testCaption)
      .select()
      .single()
    
    console.log('Test insert response:', { data: caption, error })
    
    if (error) {
      return NextResponse.json({
        success: false,
        error: error.message,
        details: error
      })
    }
    
    // Clean up - delete the test caption
    const { error: deleteError } = await supabase
      .from('captions')
      .delete()
      .eq('id', caption.id)
    
    console.log('Test cleanup:', { deleteError })
    
    return NextResponse.json({
      success: true,
      message: 'Caption creation test successful',
      testCaption: caption
    })
    
  } catch (error) {
    console.error('Test caption creation error:', error)
    return NextResponse.json({
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error'
    })
  }
}

export async function GET(request: NextRequest) {
  try {
    console.log('Testing captions table access...')
    
    // Test basic table access
    const { data: captions, error } = await supabase
      .from('captions')
      .select('count')
      .limit(1)
    
    console.log('Captions table test:', { data: captions, error })
    
    if (error) {
      return NextResponse.json({
        success: false,
        error: error.message,
        details: error
      })
    }
    
    return NextResponse.json({
      success: true,
      message: 'Captions table accessible',
      count: captions?.length || 0
    })
    
  } catch (error) {
    console.error('Test captions access error:', error)
    return NextResponse.json({
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error'
    })
  }
} 