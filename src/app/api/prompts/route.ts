import { NextRequest, NextResponse } from 'next/server'
import { requireAuth } from '@/lib/auth-server'
import sql from '@/lib/database'

export async function GET(request: NextRequest) {
  try {
    const user = await requireAuth(request)
    
    const prompts = await sql`
      SELECT * FROM captions 
      WHERE user_id = ${user.id}
      ORDER BY created_at DESC
    `
    
    // Transform captions to prompts format
    const transformedPrompts = (prompts || []).map(prompt => ({
      id: prompt.id,
      text: prompt.text,
      category: 'general', // Default category
      tags: [], // Default empty tags
      used: prompt.used,
      created_at: prompt.created_at
    }))
    
    return NextResponse.json({
      success: true,
      prompts: transformedPrompts
    })
  } catch (error) {
    console.error('Error fetching prompts:', error)
    if (error instanceof Error && error.message === 'Unauthorized') {
      return NextResponse.json(
        { success: false, error: 'Unauthorized' },
        { status: 401 }
      )
    }
    return NextResponse.json(
      { success: false, error: 'Failed to fetch prompts' },
      { status: 500 }
    )
  }
}

export async function POST(request: NextRequest) {
  try {
    const user = await requireAuth(request)
    const body = await request.json()
    
    const { text, category, tags } = body
    
    const [prompt] = await sql`
      INSERT INTO captions (
        user_id, text, used
      ) VALUES (
        ${user.id}, ${text}, false
      ) RETURNING *
    `
    
    return NextResponse.json({
      success: true,
      prompt: {
        id: prompt.id,
        text: prompt.text,
        category: category || 'general',
        tags: tags || [],
        used: prompt.used,
        created_at: prompt.created_at
      }
    })
  } catch (error) {
    console.error('Error creating prompt:', error)
    if (error instanceof Error && error.message === 'Unauthorized') {
      return NextResponse.json(
        { success: false, error: 'Unauthorized' },
        { status: 401 }
      )
    }
    return NextResponse.json(
      { success: false, error: 'Failed to create prompt' },
      { status: 500 }
    )
  }
} 