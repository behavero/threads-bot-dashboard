import { NextRequest, NextResponse } from 'next/server'
import { requireAuth } from '@/lib/auth-server'
import { supabase } from '@/lib/supabase'

export async function POST(request: NextRequest) {
  try {
    // Temporarily remove authentication to debug
    // const user = await requireAuth(request)
    const formData = await request.formData()
    const file = formData.get('file') as File
    
    if (!file) {
      return NextResponse.json(
        { success: false, error: 'No file provided' },
        { status: 400 }
      )
    }
    
    const text = await file.text()
    const lines = text.split('\n').filter(line => line.trim())
    
    const captions = lines.map(line => {
      const [text, category = 'general', tags = ''] = line.split(',').map(s => s.trim())
      return {
        text: text,
        category: category,
        tags: tags ? tags.split('|').map(t => t.trim()) : []
      }
    })
    
    // Insert into database using Supabase
    const { data, error } = await supabase
      .from('captions')
      .insert(captions)
      .select()
    
    if (error) {
      console.error('Supabase insert error:', error)
      return NextResponse.json(
        { success: false, error: 'Failed to upload captions' },
        { status: 500 }
      )
    }
    
    return NextResponse.json({
      success: true,
      message: `Successfully uploaded ${captions.length} captions`,
      captions: data
    })
  } catch (error) {
    console.error('Error uploading CSV:', error)
    return NextResponse.json(
      { success: false, error: 'Failed to upload CSV' },
      { status: 500 }
    )
  }
} 