import { NextRequest, NextResponse } from 'next/server'
import { supabase } from '@/lib/supabase'

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
          const { data, error } = await supabase
            .from('captions')
            .insert([
              {
                text: caption.trim(),
                created_at: new Date().toISOString()
              }
            ])
            .select()

          if (error) {
            results.errors.push(`Caption error: ${error.message}`)
          } else {
            results.captions.push(data[0])
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
        const { data: imageData, error: insertError } = await supabase
          .from('images')
          .insert([
            {
              filename: fileName,
              url: urlData.publicUrl,
              size: image.size,
              type: image.type,
              created_at: new Date().toISOString()
            }
          ])
          .select()

        if (insertError) {
          results.errors.push(`Image insert error: ${insertError.message}`)
        } else {
          results.images.push(imageData[0])
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
    const [captionsResult, imagesResult] = await Promise.all([
      supabase.from('captions').select('*').order('created_at', { ascending: false }),
      supabase.from('images').select('*').order('created_at', { ascending: false })
    ])

    return NextResponse.json({
      success: true,
      data: {
        captions: captionsResult.data || [],
        images: imagesResult.data || []
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