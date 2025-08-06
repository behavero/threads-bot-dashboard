import { NextRequest, NextResponse } from 'next/server'
import { requireAuth } from '@/lib/auth-server'
import { supabase } from '@/lib/supabase'

export async function PUT(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    // Temporarily remove authentication to debug
    // const user = await requireAuth(request)
    const body = await request.json()
    
    const { text, category, tags, used } = body
    
    const { data: prompt, error } = await supabase
      .from('captions')
      .update({
        text: text,
        category: category || 'general',
        tags: tags || [],
        used: used || false,
        updated_at: new Date().toISOString()
      })
      .eq('id', params.id)
      .select()
      .single()
    
    if (error) {
      console.error('Supabase update error:', error)
      return NextResponse.json(
        { success: false, error: 'Failed to update prompt' },
        { status: 500 }
      )
    }
    
    // Process the data to ensure all fields have default values
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
    
    return NextResponse.json({
      success: true,
      prompt: processedPrompt
    })
  } catch (error) {
    console.error('Error updating prompt:', error)
    return NextResponse.json(
      { success: false, error: 'Failed to update prompt' },
      { status: 500 }
    )
  }
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    // Temporarily remove authentication to debug
    // const user = await requireAuth(request)
    
    const { data: prompt, error } = await supabase
      .from('captions')
      .delete()
      .eq('id', params.id)
      .select()
      .single()
    
    if (error) {
      console.error('Supabase delete error:', error)
      return NextResponse.json(
        { success: false, error: 'Failed to delete prompt' },
        { status: 500 }
      )
    }
    
    // Process the data to ensure all fields have default values
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
    
    return NextResponse.json({
      success: true,
      prompt: processedPrompt
    })
  } catch (error) {
    console.error('Error deleting prompt:', error)
    return NextResponse.json(
      { success: false, error: 'Failed to delete prompt' },
      { status: 500 }
    )
  }
} 