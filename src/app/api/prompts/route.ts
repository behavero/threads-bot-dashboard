import { NextRequest, NextResponse } from 'next/server'
import { requireAuth } from '@/lib/auth-server'
import { supabase } from '@/lib/supabase'

export async function GET(request: NextRequest) {
  try {
    // Temporarily remove authentication to debug
    // const user = await requireAuth(request)
    
    console.log('Attempting to fetch captions from Supabase...')
    console.log('Supabase URL:', process.env.NEXT_PUBLIC_SUPABASE_URL)
    console.log('Supabase Key exists:', !!process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY)
    
    const { data: prompts, error } = await supabase
      .from('captions')
      .select('*')
      .order('created_at', { ascending: false })
    
    console.log('Supabase response:', { data: prompts, error })
    
    if (error) {
      console.error('Supabase error:', error)
      return NextResponse.json(
        { success: false, error: 'Failed to fetch prompts' },
        { status: 500 }
      )
    }
    
    // Process the data to ensure all fields have default values
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
    
    console.log('Successfully fetched captions:', processedPrompts.length)
    console.log('Sample caption:', processedPrompts[0])
    
    return NextResponse.json({
      success: true,
      prompts: processedPrompts
    })
  } catch (error) {
    console.error('Error fetching prompts:', error)
    console.error('Error details:', {
      message: error instanceof Error ? error.message : 'Unknown error',
      stack: error instanceof Error ? error.stack : undefined
    })
    return NextResponse.json(
      { success: false, error: 'Failed to fetch prompts' },
      { status: 500 }
    )
  }
}

export async function POST(request: NextRequest) {
  try {
    console.log('POST /api/prompts called')
    console.log('Supabase URL:', process.env.NEXT_PUBLIC_SUPABASE_URL)
    console.log('Supabase Key exists:', !!process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY)
    
    // Temporarily remove authentication to debug
    // const user = await requireAuth(request)
    
    const body = await request.json()
    console.log('Request body:', body)
    
    const { text, category, tags } = body
    
    if (!text) {
      console.error('Missing required text field')
      return NextResponse.json(
        { success: false, error: 'Caption text is required' },
        { status: 400 }
      )
    }
    
    const captionData = {
      text: text,
      category: category || 'general',
      tags: Array.isArray(tags) ? tags : (tags ? tags.split(',').map((t: string) => t.trim()) : []),
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
        { success: false, error: `Failed to create prompt: ${error.message}` },
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
    console.error('Error creating prompt:', error)
    console.error('Error details:', {
      message: error instanceof Error ? error.message : 'Unknown error',
      stack: error instanceof Error ? error.stack : undefined
    })
    return NextResponse.json(
      { success: false, error: `Failed to create prompt: ${error instanceof Error ? error.message : 'Unknown error'}` },
      { status: 500 }
    )
  }
} 