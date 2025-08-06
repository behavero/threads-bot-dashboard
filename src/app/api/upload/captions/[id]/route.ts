import { NextRequest, NextResponse } from 'next/server'
import sql from '@/lib/database'
import { requireAuth } from '@/lib/auth-server'

export async function DELETE(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    // Require authentication
    await requireAuth(request)
    
    const result = await sql`
      DELETE FROM captions 
      WHERE id = ${params.id}
    `

    return NextResponse.json({ success: true })
  } catch (error) {
    console.error('Delete caption error:', error)
    return NextResponse.json(
      { success: false, error: 'Delete failed' },
      { status: 500 }
    )
  }
} 