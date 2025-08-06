import { NextRequest, NextResponse } from 'next/server'
import { requireAuth } from '@/lib/auth-server'
import sql from '@/lib/database'

export async function PUT(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const user = await requireAuth(request)
    const body = await request.json()
    
    const { text, category, tags, used } = body
    
    const [prompt] = await sql`
      UPDATE captions 
      SET 
        text = ${text},
        category = ${category || 'general'},
        tags = ${tags || []},
        used = ${used || false},
        updated_at = NOW()
      WHERE id = ${params.id}
      RETURNING 
        id,
        user_id,
        text,
        COALESCE(category, 'general') as category,
        COALESCE(tags, '{}') as tags,
        used,
        created_at,
        COALESCE(updated_at, created_at) as updated_at
    `
    
    if (!prompt) {
      return NextResponse.json(
        { success: false, error: 'Prompt not found' },
        { status: 404 }
      )
    }
    
    return NextResponse.json({
      success: true,
      prompt
    })
  } catch (error) {
    console.error('Error updating prompt:', error)
    if (error instanceof Error && error.message === 'Unauthorized') {
      return NextResponse.json(
        { success: false, error: 'Unauthorized' },
        { status: 401 }
      )
    }
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
    const user = await requireAuth(request)
    
    const [prompt] = await sql`
      DELETE FROM captions
      WHERE id = ${params.id}
      RETURNING 
        id,
        user_id,
        text,
        COALESCE(category, 'general') as category,
        COALESCE(tags, '{}') as tags,
        used,
        created_at,
        COALESCE(updated_at, created_at) as updated_at
    `
    
    if (!prompt) {
      return NextResponse.json(
        { success: false, error: 'Prompt not found' },
        { status: 404 }
      )
    }
    
    return NextResponse.json({
      success: true,
      message: 'Prompt deleted successfully'
    })
  } catch (error) {
    console.error('Error deleting prompt:', error)
    if (error instanceof Error && error.message === 'Unauthorized') {
      return NextResponse.json(
        { success: false, error: 'Unauthorized' },
        { status: 401 }
      )
    }
    return NextResponse.json(
      { success: false, error: 'Failed to delete prompt' },
      { status: 500 }
    )
  }
} 