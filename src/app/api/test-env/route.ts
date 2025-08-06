import { NextResponse } from 'next/server'

export async function GET() {
  try {
    const envVars = {
      hasSupabaseUrl: !!process.env.NEXT_PUBLIC_SUPABASE_URL,
      hasSupabaseAnonKey: !!process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY,
      hasPostgresUrl: !!process.env.POSTGRES_URL,
      hasServiceRoleKey: !!process.env.SUPABASE_SERVICE_ROLE_KEY,
      supabaseUrl: process.env.NEXT_PUBLIC_SUPABASE_URL,
      postgresUrl: process.env.POSTGRES_URL ? 'SET' : 'NOT SET',
      serviceRoleKey: process.env.SUPABASE_SERVICE_ROLE_KEY ? 'SET' : 'NOT SET'
    }

    return NextResponse.json({
      success: true,
      message: 'Environment variables check',
      envVars
    })
  } catch (error) {
    return NextResponse.json(
      { 
        success: false, 
        error: 'Failed to check environment variables'
      },
      { status: 500 }
    )
  }
} 