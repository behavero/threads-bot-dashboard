import { NextRequest, NextResponse } from 'next/server'
import { requireAuth } from '@/lib/auth-server'
import { supabase } from '@/lib/supabase'

export async function GET(request: NextRequest) {
  try {
    console.log('Attempting to fetch accounts from Supabase...')
    console.log('Supabase URL:', process.env.NEXT_PUBLIC_SUPABASE_URL)
    console.log('Supabase Key exists:', !!process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY)
    
    // Temporarily remove authentication to debug
    // const user = await requireAuth(request)
    
    const { data: accounts, error } = await supabase
      .from('accounts')
      .select('*')
      .order('created_at', { ascending: false })
    
    console.log('Supabase accounts response:', { data: accounts, error })
    
    if (error) {
      console.error('Supabase error:', error)
      return NextResponse.json(
        { success: false, error: 'Failed to fetch accounts' },
        { status: 500 }
      )
    }
    
    // Process accounts to match expected interface
    const processedAccounts = (accounts || []).map(account => ({
      id: account.id,
      username: account.username || '',
      email: account.email || '',
      password: account.password || '',
      description: account.description || '',
      posting_config: account.posting_config || {},
      fingerprint_config: account.fingerprint_config || {},
      status: account.active ? 'enabled' : 'disabled',
      last_posted: account.last_posted,
      created_at: account.created_at
    }))
    
    console.log('Successfully fetched accounts:', processedAccounts.length)
    console.log('Sample account:', processedAccounts[0])
    
    return NextResponse.json({
      success: true,
      accounts: processedAccounts
    })
  } catch (error) {
    console.error('Error fetching accounts:', error)
    return NextResponse.json(
      { success: false, error: 'Failed to fetch accounts' },
      { status: 500 }
    )
  }
}

export async function POST(request: NextRequest) {
  try {
    console.log('POST /api/accounts called')
    
    // Temporarily remove authentication to debug
    // const user = await requireAuth(request)
    
    const body = await request.json()
    console.log('Account data:', body)
    
    const {
      username,
      email,
      password,
      description,
      posting_config,
      fingerprint_config,
      status
    } = body
    
    // Convert to match database schema
    const accountData = {
      username: username,
      email: email || '',
      password: password,
      description: description || '',
      posting_config: posting_config || {},
      fingerprint_config: fingerprint_config || {},
      active: status === 'enabled',
      last_posted: null
    }
    
    console.log('Inserting account data:', accountData)
    
    const { data: account, error } = await supabase
      .from('accounts')
      .insert(accountData)
      .select()
      .single()
    
    console.log('Supabase insert response:', { data: account, error })
    
    if (error) {
      console.error('Supabase insert error:', error)
      return NextResponse.json(
        { success: false, error: 'Failed to create account' },
        { status: 500 }
      )
    }
    
    // Process the response to match expected interface
    const processedAccount = {
      id: account.id,
      username: account.username,
      email: account.email || '',
      password: account.password,
      description: account.description || '',
      posting_config: account.posting_config || {},
      fingerprint_config: account.fingerprint_config || {},
      status: account.active ? 'enabled' : 'disabled',
      last_posted: account.last_posted,
      created_at: account.created_at
    }
    
    return NextResponse.json({
      success: true,
      account: processedAccount
    })
  } catch (error) {
    console.error('Error creating account:', error)
    return NextResponse.json(
      { success: false, error: 'Failed to create account' },
      { status: 500 }
    )
  }
} 