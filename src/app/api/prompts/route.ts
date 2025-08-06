import { NextRequest, NextResponse } from 'next/server'
import { requireAuth } from '@/lib/auth-server'
import { supabase } from '@/lib/supabase'

export async function GET(request: NextRequest) {
  try {
    // Temporarily remove authentication to debug
    // const user = await requireAuth(request)
    
    console.log('Attempting to fetch captions from Supabase...')
    
    const { data: prompts, error } = await supabase
      .from('captions')
      .select('*')
      .order('created_at', { ascending: false })
    
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
    // Temporarily remove authentication to debug
    // const user = await requireAuth(request)
    const body = await request.json()
    
    const { text, category, tags } = body
    
    const { data: prompt, error } = await supabase
      .from('captions')
      .insert({
        text: text,
        category: category || 'general',
        tags: tags || [],
        used: false
      })
      .select()
      .single()
    
    if (error) {
      console.error('Supabase insert error:', error)
      return NextResponse.json(
        { success: false, error: 'Failed to create prompt' },
        { status: 500 }
      )
    }
    
    return NextResponse.json({
      success: true,
      prompt
    })
  } catch (error) {
    console.error('Error creating prompt:', error)
    return NextResponse.json(
      { success: false, error: 'Failed to create prompt' },
      { status: 500 }
    )
  }
} 