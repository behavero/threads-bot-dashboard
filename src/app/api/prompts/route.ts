import { NextRequest, NextResponse } from 'next/server'
import { requireAuth } from '@/lib/auth-server'
import sql from '@/lib/database'

export async function GET(request: NextRequest) {
  try {
    const user = await requireAuth(request)
    
    const prompts = await sql`
      SELECT * FROM prompts 
      WHERE user_id = ${user.id}
      ORDER BY created_at DESC
    `
    
    return NextResponse.json({
      success: true,
      prompts: prompts || []
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
      INSERT INTO prompts (
        user_id, text, category, tags, used
      ) VALUES (
        ${user.id}, ${text}, ${category || 'general'}, ${tags || []}, false
      ) RETURNING *
    `
    
    return NextResponse.json({
      success: true,
      prompt
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