import { NextRequest, NextResponse } from 'next/server'
import { requireAuth } from '@/lib/auth-server'
import { supabase } from '@/lib/supabase'

export async function POST(request: NextRequest) {
  try {
    // Temporarily disable authentication to debug
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
    
    const captions = lines.map((line, index) => {
      const parts = line.split(',').map(part => part.trim())
      
      // Handle different CSV formats
      let text, category, tags
      
      if (parts.length === 1) {
        // Just text
        text = parts[0]
        category = 'general'
        tags = []
      } else if (parts.length === 2) {
        // text, category
        text = parts[0]
        category = parts[1] || 'general'
        tags = []
      } else if (parts.length >= 3) {
        // text, category, tags
        text = parts[0]
        category = parts[1] || 'general'
        tags = parts[2] ? parts[2].split('|').map(t => t.trim()).filter(t => t) : []
      } else {
        // Invalid format
        console.warn(`Invalid line ${index + 1}: ${line}`)
        return null
      }
      
      // Validate text
      if (!text || text.length === 0) {
        console.warn(`Empty text in line ${index + 1}`)
        return null
      }
      
      return {
        text: text,
        category: category,
        tags: tags
      }
    }).filter(caption => caption !== null)
    
    console.log('Processed captions:', captions.length)
    console.log('Sample caption:', captions[0])
    
    if (captions.length === 0) {
      return NextResponse.json(
        { success: false, error: 'No valid captions found in CSV' },
        { status: 400 }
      )
    }
    
    // Insert into database using Supabase
    const { data, error } = await supabase
      .from('captions')
      .insert(captions)
      .select()
    
    console.log('Supabase insert response:', { data: data?.length, error })
    
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
    console.error('CSV upload error:', error)
    return NextResponse.json(
      { success: false, error: 'Internal server error' },
      { status: 500 }
    )
  }
} 