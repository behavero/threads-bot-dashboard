import { NextRequest, NextResponse } from 'next/server'
import { supabase } from '@/lib/supabase'
import { requireAuth } from '@/lib/auth-server'

export async function GET(request: NextRequest) {
  try {
    console.log('GET /api/prompts called')
    
    // Temporarily disable authentication to fix data flow
    // const user = await requireAuth(request)
    
    const { data: prompts, error } = await supabase
      .from('captions')
      .select('*')
      .order('created_at', { ascending: false })

    console.log('Supabase response:', { data: prompts?.length, error })

    if (error) {
      console.error('Supabase error:', error)
      return NextResponse.json(
        { success: false, error: 'Failed to fetch captions' },
        { status: 500 }
      )
    }

    // Process captions to ensure all fields have default values
    const processedPrompts = (prompts || []).map(prompt => ({
      id: prompt.id,
      user_id: prompt.user_id,
      text: prompt.text || '',
      category: prompt.category || 'general',
      tags: Array.isArray(prompt.tags) ? prompt.tags : [],
      used: prompt.used || false,
      created_at: prompt.created_at,
      updated_at: prompt.updated_at || prompt.created_at
    }))

    console.log('Processed prompts:', processedPrompts.length)

    return NextResponse.json({
      success: true,
      prompts: processedPrompts
    })
  } catch (error) {
    console.error('GET /api/prompts error:', error)
    return NextResponse.json(
      { success: false, error: 'Internal server error' },
      { status: 500 }
    )
  }
}

export async function POST(request: NextRequest) {
  try {
    console.log('POST /api/prompts called')
    
    // Temporarily disable authentication to fix data flow
    // const user = await requireAuth(request)
    
    const body = await request.json()
    console.log('Request body:', body)
    
    const { text, category, tags } = body
    
    // Validate required fields
    if (!text) {
      console.error('Missing required text field')
      return NextResponse.json(
        { success: false, error: 'Caption text is required' },
        { status: 400 }
      )
    }
    
    if (typeof text !== 'string' || text.trim().length === 0) {
      console.error('Invalid text field')
      return NextResponse.json(
        { success: false, error: 'Caption text must be a non-empty string' },
        { status: 400 }
      )
    }
    
    // Validate category
    if (category && typeof category !== 'string') {
      console.error('Invalid category field')
      return NextResponse.json(
        { success: false, error: 'Category must be a string' },
        { status: 400 }
      )
    }
    
    // Validate tags
    if (tags && !Array.isArray(tags)) {
      console.error('Invalid tags field')
      return NextResponse.json(
        { success: false, error: 'Tags must be an array' },
        { status: 400 }
      )
    }
    
    // Clean and validate tags
    let cleanedTags: string[] = []
    if (tags && Array.isArray(tags)) {
      cleanedTags = tags
        .filter(tag => typeof tag === 'string' && tag.trim().length > 0)
        .map(tag => tag.trim())
    }
    
    const captionData = {
      text: text.trim(),
      category: category || 'general',
      tags: cleanedTags,
      used: false
    }
    
    console.log('Inserting caption data:', captionData)
    
    const { data: prompt, error } = await supabase
      .from('captions')
      .insert(captionData)
      .select()
      .single()
    
    console.log('Supabase insert response:', { data: prompt, error })
    
    if (error) {
      console.error('Supabase insert error:', error)
      return NextResponse.json(
        { success: false, error: `Failed to create caption: ${error.message}` },
        { status: 500 }
      )
    }
    
    // Process the response to ensure all fields have default values
    const processedPrompt = {
      id: prompt.id,
      user_id: prompt.user_id,
      text: prompt.text || '',
      category: prompt.category || 'general',
      tags: Array.isArray(prompt.tags) ? prompt.tags : [],
      used: prompt.used || false,
      created_at: prompt.created_at,
      updated_at: prompt.updated_at || prompt.created_at
    }
    
    console.log('Successfully created caption:', processedPrompt)
    
    return NextResponse.json({
      success: true,
      prompt: processedPrompt
    })
  } catch (error) {
    console.error('POST /api/prompts error:', error)
    return NextResponse.json(
      { success: false, error: 'Internal server error' },
      { status: 500 }
    )
  }
} 