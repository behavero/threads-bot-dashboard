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
    
    const {
      username,
      email,
      password,
      description,
      posting_config,
      fingerprint_config,
      status
    } = body
    
    const [account] = await sql`
      UPDATE accounts 
      SET 
        username = ${username},
        email = ${email},
        password = ${password},
        description = ${description},
        posting_config = ${JSON.stringify(posting_config)},
        fingerprint_config = ${JSON.stringify(fingerprint_config)},
        status = ${status}
      WHERE id = ${params.id} AND user_id = ${user.id}
      RETURNING *
    `
    
    if (!account) {
      return NextResponse.json(
        { success: false, error: 'Account not found' },
        { status: 404 }
      )
    }
    
    return NextResponse.json({
      success: true,
      account
    })
  } catch (error) {
    console.error('Error updating account:', error)
    if (error instanceof Error && error.message === 'Unauthorized') {
      return NextResponse.json(
        { success: false, error: 'Unauthorized' },
        { status: 401 }
      )
    }
    return NextResponse.json(
      { success: false, error: 'Failed to update account' },
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
    
    const [account] = await sql`
      DELETE FROM accounts 
      WHERE id = ${params.id} AND user_id = ${user.id}
      RETURNING *
    `
    
    if (!account) {
      return NextResponse.json(
        { success: false, error: 'Account not found' },
        { status: 404 }
      )
    }
    
    return NextResponse.json({
      success: true,
      message: 'Account deleted successfully'
    })
  } catch (error) {
    console.error('Error deleting account:', error)
    if (error instanceof Error && error.message === 'Unauthorized') {
      return NextResponse.json(
        { success: false, error: 'Unauthorized' },
        { status: 401 }
      )
    }
    return NextResponse.json(
      { success: false, error: 'Failed to delete account' },
      { status: 500 }
    )
  }
} 