import { NextRequest, NextResponse } from 'next/server'
import { requireAuth } from '@/lib/auth-server'
import { supabase } from '@/lib/supabase'

export async function POST(request: NextRequest) {
  try {
    // Temporarily remove authentication to debug
    // const user = await requireAuth(request)
    console.log('CSV upload started')
    
    const formData = await request.formData()
    const file = formData.get('file') as File
    
    console.log('File received:', file ? { name: file.name, size: file.size, type: file.type } : 'No file')
    
    if (!file) {
      return NextResponse.json(
        { success: false, error: 'No file provided' },
        { status: 400 }
      )
    }
    
    const text = await file.text()
    console.log('File content preview:', text.substring(0, 200))
    
    const lines = text.split('\n').filter(line => line.trim())
    console.log('Number of lines:', lines.length)
    
    const captions = lines.map(line => {
      const [text, category = 'general', tags = ''] = line.split(',').map(s => s.trim())
      return {
        text: text,
        category: category,
        tags: tags ? tags.split('|').map(t => t.trim()) : []
      }
    })
    
    console.log('Processed captions:', captions.length)
    console.log('Sample caption:', captions[0])
    
    // Insert into database using Supabase
    const { data, error } = await supabase
      .from('captions')
      .insert(captions)
      .select()
    
    console.log('Supabase insert response:', { data, error })
    
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