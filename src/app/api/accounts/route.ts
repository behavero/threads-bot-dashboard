import { NextRequest, NextResponse } from 'next/server'
import { requireAuth } from '@/lib/auth-server'
import sql from '@/lib/database'

export async function GET(request: NextRequest) {
  try {
    const user = await requireAuth(request)
    
    const accounts = await sql`
      SELECT * FROM accounts 
      WHERE user_id = ${user.id}
      ORDER BY created_at DESC
    `
    
    return NextResponse.json({
      success: true,
      accounts: accounts || []
    })
  } catch (error) {
    console.error('Error fetching accounts:', error)
    if (error instanceof Error && error.message === 'Unauthorized') {
      return NextResponse.json(
        { success: false, error: 'Unauthorized' },
        { status: 401 }
      )
    }
    return NextResponse.json(
      { success: false, error: 'Failed to fetch accounts' },
      { status: 500 }
    )
  }
}

export async function POST(request: NextRequest) {
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
      INSERT INTO accounts (
        user_id, username, email, password, description, 
        posting_config, fingerprint_config, status
      ) VALUES (
        ${user.id}, ${username}, ${email}, ${password}, ${description},
        ${JSON.stringify(posting_config)}, ${JSON.stringify(fingerprint_config)}, ${status}
      ) RETURNING *
    `
    
    return NextResponse.json({
      success: true,
      account
    })
  } catch (error) {
    console.error('Error creating account:', error)
    if (error instanceof Error && error.message === 'Unauthorized') {
      return NextResponse.json(
        { success: false, error: 'Unauthorized' },
        { status: 401 }
      )
    }
    return NextResponse.json(
      { success: false, error: 'Failed to create account' },
      { status: 500 }
    )
  }
} 