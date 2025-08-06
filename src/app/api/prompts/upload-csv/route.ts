import { NextRequest, NextResponse } from 'next/server'
import { requireAuth } from '@/lib/auth-server'
import sql from '@/lib/database'

export async function POST(request: NextRequest) {
  try {
    const user = await requireAuth(request)
    const formData = await request.formData()
    const file = formData.get('file') as File

    if (!file) {
      return NextResponse.json(
        { success: false, error: 'No file provided' },
        { status: 400 }
      )
    }

    // Read the file content
    const text = await file.text()
    const lines = text.split('\n').filter(line => line.trim())

    let successCount = 0
    let errorCount = 0
    const errors: string[] = []

    // Process each line
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i].trim()
      if (!line) continue

      try {
        // Parse CSV line (simple comma-separated)
        const parts = line.split(',').map(part => part.trim())
        const text = parts[0] || ''
        const category = parts[1] || 'general'
        const tags = parts[2] ? parts[2].split(';').map(tag => tag.trim()).filter(tag => tag) : []

        if (!text) {
          errorCount++
          errors.push(`Line ${i + 1}: Empty text`)
          continue
        }

        // Insert into database
        await sql`
          INSERT INTO prompts (
            user_id, text, category, tags, used
          ) VALUES (
            ${user.id}, ${text}, ${category}, ${tags}, false
          )
        `

        successCount++
      } catch (error) {
        errorCount++
        errors.push(`Line ${i + 1}: ${error}`)
      }
    }

    return NextResponse.json({
      success: true,
      count: successCount,
      errors: errors.length > 0 ? errors : undefined
    })

  } catch (error) {
    console.error('Error uploading CSV:', error)
    if (error instanceof Error && error.message === 'Unauthorized') {
      return NextResponse.json(
        { success: false, error: 'Unauthorized' },
        { status: 401 }
      )
    }
    return NextResponse.json(
      { success: false, error: 'Failed to upload CSV' },
      { status: 500 }
    )
  }
} 