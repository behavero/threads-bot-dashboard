import { NextRequest, NextResponse } from 'next/server'
import { supabase } from '@/lib/supabase'
import sql from '@/lib/database'
import { requireAuth } from '@/lib/auth-server'

export async function DELETE(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    // Require authentication
    await requireAuth(request)
    
    const body = await request.json()
    const { filename } = body

    // Delete from Supabase Storage
    if (filename) {
      const { error: storageError } = await supabase.storage
        .from('images')
        .remove([filename])

      if (storageError) {
        console.error('Storage delete error:', storageError)
        // Continue with database deletion even if storage deletion fails
      }
    }

    // Delete from database
    try {
      await sql`
        DELETE FROM images 
        WHERE id = ${params.id}
      `
    } catch (dbError) {
      return NextResponse.json(
        { success: false, error: dbError },
        { status: 400 }
      )
    }

    return NextResponse.json({ success: true })
  } catch (error) {
    console.error('Delete image error:', error)
    return NextResponse.json(
      { success: false, error: 'Delete failed' },
      { status: 500 }
    )
  }
} 