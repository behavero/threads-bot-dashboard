import { NextRequest, NextResponse } from 'next/server'
import { supabase } from '@/lib/supabase'
import sql from '@/lib/database'

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData()
    const captions = formData.get('captions') as string
    const images = formData.getAll('images') as File[]

    const results: {
      captions: any[];
      images: any[];
      errors: string[];
    } = {
      captions: [],
      images: [],
      errors: []
    }

    // Handle captions
    if (captions && captions.trim()) {
      const captionList = captions.split('\n').filter(caption => caption.trim())
      
      for (const caption of captionList) {
        try {
          const [data] = await sql`
            INSERT INTO captions (text, created_at)
            VALUES (${caption.trim()}, ${new Date().toISOString()})
            RETURNING *
          `

          if (data) {
            results.captions.push(data)
          }
        } catch (error) {
          results.errors.push(`Caption error: ${error}`)
        }
      }
    }

    // Handle images
    for (const image of images) {
      try {
        // Upload to Supabase Storage
        const fileName = `${Date.now()}-${image.name}`
        const { data: uploadData, error: uploadError } = await supabase.storage
          .from('images')
          .upload(fileName, image)

        if (uploadError) {
          results.errors.push(`Image upload error: ${uploadError.message}`)
          continue
        }

        // Get public URL
        const { data: urlData } = supabase.storage
          .from('images')
          .getPublicUrl(fileName)

        // Insert into images table
        try {
          const [imageData] = await sql`
            INSERT INTO images (filename, url, size, type, created_at)
            VALUES (${fileName}, ${urlData.publicUrl}, ${image.size}, ${image.type}, ${new Date().toISOString()})
            RETURNING *
          `

          if (imageData) {
            results.images.push(imageData)
          }
        } catch (insertError) {
          results.errors.push(`Image insert error: ${insertError}`)
        }
      } catch (error) {
        results.errors.push(`Image error: ${error}`)
      }
    }

    return NextResponse.json({
      success: true,
      data: results
    })

  } catch (error) {
    console.error('Upload error:', error)
    return NextResponse.json(
      { success: false, error: 'Upload failed' },
      { status: 500 }
    )
  }
}

export async function GET() {
  try {
    // Fetch existing captions and images
    const [captions, images] = await Promise.all([
      sql`SELECT * FROM captions ORDER BY created_at DESC`,
      sql`SELECT * FROM images ORDER BY created_at DESC`
    ])

    return NextResponse.json({
      success: true,
      data: {
        captions: captions || [],
        images: images || []
      }
    })
  } catch (error) {
    console.error('Fetch error:', error)
    return NextResponse.json(
      { success: false, error: 'Fetch failed' },
      { status: 500 }
    )
  }
} 