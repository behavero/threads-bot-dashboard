import { NextRequest, NextResponse } from 'next/server'
import { requireAuth } from '@/lib/auth-server'
import sql from '@/lib/database'

export async function GET(request: NextRequest) {
  try {
    // Temporarily remove authentication to debug
    // const user = await requireAuth(request)
    
    const prompts = await sql`
      SELECT 
        id,
        user_id,
        text,
        COALESCE(category, 'general') as category,
        COALESCE(tags, '{}') as tags,
        used,
        created_at,
        COALESCE(updated_at, created_at) as updated_at
      FROM captions 
      ORDER BY created_at DESC
    `
    
    return NextResponse.json({
      success: true,
      prompts: prompts || []
    })
  } catch (error) {
    console.error('Error fetching prompts:', error)
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
    
    const [prompt] = await sql`
      INSERT INTO captions (
        text, category, tags, used
      ) VALUES (
        ${text}, ${category || 'general'}, ${tags || []}, false
      ) RETURNING *
    `
    
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