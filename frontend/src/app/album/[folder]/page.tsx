import fs from 'fs'
import path from 'path'
import CalendarAlbum from '../../../components/CalendarAlbum'
import Link from 'next/link'

type Props = {
  params: { folder: string }
  searchParams?: { [key: string]: string | string[] | undefined }
}

export default function Page({ params, searchParams }: Props) {
  const folder = params.folder
  const dayParam = searchParams?.day ? String(searchParams.day) : null
  const rawTitle = searchParams?.title ? (Array.isArray(searchParams.title) ? searchParams.title[0] : String(searchParams.title)) : null
  const decodedTitle = rawTitle ? decodeURIComponent(rawTitle) : null
  const publicDir = path.join(process.cwd(), 'public', 'images', folder)
  let images: string[] = []
  // image -> label mapping (basename -> label)
  let labelsMap: { [key: string]: string } = {}
  try {
    const files = fs.readdirSync(publicDir)
    const imageFiles = files.filter(f => /\.(png|jpe?g|gif|webp|svg)$/i.test(f)).sort()
    images = imageFiles.map(f => `/images/${folder}/${f}`)

    // try to parse gz2_label_slice.csv if present
    const csvPath = path.join(process.cwd(), 'public', 'images', folder, 'gz2_label_slice.csv')
    if (fs.existsSync(csvPath)) {
      try {
        const raw = fs.readFileSync(csvPath, 'utf8')
        const rows = raw.split(/\r?\n/).map(r => r.trim()).filter(Boolean)
        // Map assumption: rows order corresponds to sorted imageFiles order
        rows.forEach((label, idx) => {
          const fname = imageFiles[idx]
          if (fname) labelsMap[fname] = label
        })
      } catch (e) {
        // ignore parse errors
        console.warn('failed to parse csv for', folder, e)
      }
    }
  } catch (e) {
    images = []
  }

  // build folder list from manifest or by scanning
  let folders: string[] = []
  try {
    const manifestPath = path.join(process.cwd(), 'public', 'images', 'manifest.json')
    if (fs.existsSync(manifestPath)) {
      const raw = fs.readFileSync(manifestPath, 'utf8')
      const list = JSON.parse(raw)
      if (Array.isArray(list)) folders = list
    }
    if (folders.length === 0) {
      const imagesRoot = path.join(process.cwd(), 'public', 'images')
      const entries = fs.readdirSync(imagesRoot, { withFileTypes: true })
      folders = entries.filter(e => e.isDirectory()).map(d => d.name)
    }
  } catch (e) {
    folders = [folder]
  }

  return (
    <div className="min-h-screen bg-[radial-gradient(ellipse_at_bottom,_var(--tw-gradient-stops))] from-[#01020a] via-[#070919] to-[#020214] text-white py-12">
      <div className="max-w-6xl mx-auto px-6">
        {/* breadcrumb: 首页 / 日历 / {folder} */}
        <div className="mb-4 text-sm text-slate-300">
          <Link href="/" className="text-sky-300 hover:underline">首页</Link>
          <span className="mx-2">/</span>
          <Link href="/" className="text-sky-300 hover:underline">日历</Link>
          <span className="mx-2">/</span>
          <span className="font-medium">{folder}</span>
        </div>

        {/* folder switcher */}
        <div className="mb-4 flex items-center space-x-3">
          {folders.map((f) => (
            <Link key={f} href={`/album/${f}`} className={`px-3 py-1 rounded text-sm ${f === folder ? 'bg-white/6 text-white' : 'text-slate-300 hover:bg-white/3'}`}>
              {/* special icon for HB */}
              <span className="mr-2">{f === 'HB' ? '📁' : '🖼️'}</span>
              <span>{f}</span>
            </Link>
          ))}
        </div>

        {dayParam && (
          <div className="mb-4 inline-flex items-center space-x-3 bg-white/6 py-2 px-3 rounded">
            <span className="text-sm text-sky-200">来自日历：</span>
            <span className="font-medium">{`9月${dayParam}日`}</span>
            {decodedTitle && <span className="ml-3 text-sm text-slate-200">· 实验：<span className="font-medium">{decodedTitle}</span></span>}
            <a href={`/album/${folder}/manage`} className="ml-4 text-xs text-slate-200 hover:underline">管理图片</a>
          </div>
        )}
      </div>

  <CalendarAlbum folder={folder} images={images} labels={labelsMap} />
    </div>
  )
}

// For static export (output: 'export'), Next.js requires generateStaticParams
// so all dynamic routes are known at build time. We scan `public/images` and
// return a list of folders found there as the possible `folder` params.
export async function generateStaticParams() {
  // Prefer a committed manifest for fully-static dev/build scenarios.
  try {
    const manifestPath = path.join(process.cwd(), 'public', 'images', 'manifest.json')
    if (fs.existsSync(manifestPath)) {
      try {
        const raw = fs.readFileSync(manifestPath, 'utf8')
        const list = JSON.parse(raw)
        if (Array.isArray(list)) return list.map((folder) => ({ folder }))
      } catch (err) {
        console.warn('generateStaticParams: failed to parse manifest.json', err)
      }
    }

    // Fallback: scan the public/images folder for subdirectories
    const imagesRoot = path.join(process.cwd(), 'public', 'images')
    const entries = fs.readdirSync(imagesRoot, { withFileTypes: true })
    const folders = entries.filter(e => e.isDirectory()).map(d => d.name)
    return folders.map((folder) => ({ folder }))
  } catch (e) {
    console.warn('generateStaticParams: failed to read public/images', e)
    return []
  }
}
