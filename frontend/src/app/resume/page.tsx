"use client"
import { useState, useRef, useEffect } from "react"
import { api } from "@/lib/api"
import { useUserId } from "@/lib/hooks"

export default function ResumePage() {
  const userId               = useUserId()
  const [mounted, setMounted] = useState(false)
  const [resume, setResume]  = useState<any>(null)
  const [uploading, setUploading] = useState(false)
  const [dragOver, setDragOver]   = useState(false)
  const [message, setMessage]     = useState("")
  const [error, setError]         = useState("")
  const inputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    setMounted(true)
  }, [])

  useEffect(() => {
    if (!userId) return
    api.getResume(userId)
      .then(setResume)
      .catch(() => setResume(null))
  }, [userId])

  const handleUpload = async (file: File) => {
    if (!userId) {
      setError("Create an account first in Settings")
      return
    }
    if (!file.name.endsWith(".pdf")) {
      setError("Only PDF files are accepted")
      return
    }
    if (file.size > 10 * 1024 * 1024) {
      setError("File too large — max 10MB")
      return
    }

    setError("")
    setUploading(true)
    setMessage("")

    try {
      const result = await api.uploadResume(userId, file)
      if (result.status === "uploaded") {
        setResume(result)
        setMessage(
          `Uploaded successfully — ${result.char_count?.toLocaleString()} characters extracted`
        )
      } else {
        setError(result.detail || "Upload failed")
      }
    } catch (e: any) {
      setError(e.message || "Upload failed")
    } finally {
      setUploading(false)
    }
  }

  const onDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setDragOver(false)
    const file = e.dataTransfer.files[0]
    if (file) handleUpload(file)
  }

  if (!mounted) return null

  return (
    <div className="max-w-2xl mx-auto py-4">
      <div className="flex items-center gap-4 mb-2">
        <div className="w-12 h-12 bg-indigo-50 text-indigo-600 rounded-2xl flex items-center justify-center">
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        </div>
        <div>
          <h1 className="text-3xl font-bold text-slate-900 tracking-tight">
            Resume
          </h1>
          <p className="text-sm font-medium text-slate-400">
            AI Profile & Application Documents
          </p>
        </div>
      </div>
      
      <p className="text-sm text-slate-500 mb-10 leading-relaxed max-w-md">
        Your resume is the core of Jobly's AI matching. Upload your latest
        PDF to sync your experience with 24/7 job discovery.
      </p>

      {/* Upload zone */}
      <div
        onDrop={onDrop}
        onDragOver={(e) => {
          e.preventDefault()
          setDragOver(true)
        }}
        onDragLeave={() => setDragOver(false)}
        onClick={() => inputRef.current?.click()}
        className={`border-2 border-dashed rounded-3xl
                     p-16 text-center cursor-pointer
                     transition-all duration-300 mb-8 overflow-hidden relative ${
          dragOver
            ? "border-indigo-400 bg-indigo-50/50 shadow-lg shadow-indigo-100/50"
            : "border-slate-200 hover:border-indigo-300 hover:bg-slate-50/50"
        }`}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".pdf"
          className="hidden"
          onChange={(e) => {
            const f = e.target.files?.[0]
            if (f) handleUpload(f)
          }}
        />
        
        {uploading ? (
          <div className="py-2">
            <div className="w-12 h-12 border-4
                             border-slate-200
                             border-t-indigo-600
                             rounded-full animate-spin
                             mx-auto mb-4" />
            <p className="text-base font-bold text-slate-700">
              Analyzing Experience...
            </p>
            <p className="text-xs text-slate-400 mt-1">
              Extracting text and generating embeddings
            </p>
          </div>
        ) : (
          <div>
            <div className="w-16 h-16 bg-white
                             rounded-2xl flex items-center shadow-sm border border-slate-100
                             justify-center mx-auto mb-6 text-indigo-600 group-hover:scale-110 transition-transform">
              <svg
                className="w-8 h-8"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={1.5}
                  d="M12 16V4m0 0l-4 4m4-4l4 4
                     M4 20h16"
                />
              </svg>
            </div>
            <p className="text-lg font-bold text-slate-900">
              {dragOver ? "Drop to sync" : "Select your Resume"}
            </p>
            <p className="text-sm text-slate-400 mt-1">
              PDF files only · up to 10MB
            </p>
          </div>
        )}
      </div>

      {/* Messages */}
      {message && (
        <div className="bg-emerald-50 border border-emerald-100 text-emerald-700
                         text-sm font-medium rounded-2xl px-6 py-4 mb-8 flex items-center gap-3 animate-in fade-in slide-in-from-top-2">
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
          {message}
        </div>
      )}
      {error && (
        <div className="bg-rose-50 border border-rose-100 text-rose-600 text-sm
                         font-medium rounded-2xl px-6 py-4 mb-8 flex items-center gap-3 animate-in fade-in slide-in-from-top-2">
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          {error}
        </div>
      )}

      {/* Current resume info */}
      {resume && (
        <div className="card-premium p-8">
          <div className="flex items-start
                           justify-between mb-8">
            <div className="flex items-start gap-4">
              <div className="w-12 h-12 bg-slate-50 rounded-xl border border-slate-100 flex items-center justify-center text-slate-400">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 00-2 2z" />
                </svg>
              </div>
              <div>
                <p className="text-lg font-bold text-slate-900">
                  {resume.filename || "resume.pdf"}
                </p>
                <div className="flex items-center gap-3 mt-1 text-xs font-bold uppercase tracking-tight">
                  <span className="text-slate-400">
                    {resume.char_count?.toLocaleString() || "—"} Chars
                  </span>
                  <div className="w-1 h-1 rounded-full bg-slate-200" />
                  {resume.has_embedding !== false ? (
                    <span className="text-emerald-600 flex items-center gap-1">
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                      AI Embedding Active
                    </span>
                  ) : (
                    <span className="text-amber-500">Processing...</span>
                  )}
                </div>
              </div>
            </div>
            {resume.file_url && (
              <a
                href={resume.file_url}
                target="_blank"
                rel="noopener noreferrer"
                className="px-4 py-2 bg-slate-50 text-slate-600 rounded-xl text-xs font-bold hover:bg-slate-100 transition-colors border border-slate-100"
              >
                View PDF
              </a>
            )}
          </div>

          {resume.parsed_text_preview && (
            <div className="space-y-3">
              <h4 className="text-[10px] font-bold text-slate-400
                             uppercase tracking-widest px-1">
                Content Intelligence Preview
              </h4>
              <div className="relative group">
                <p className="text-xs text-slate-500
                                leading-relaxed bg-slate-50/80 backdrop-blur-sm
                                rounded-2xl p-6 border border-slate-100/50 italic">
                  "{resume.parsed_text_preview}..."
                </p>
                <div className="absolute inset-x-0 bottom-0 h-12 bg-gradient-to-t from-slate-50/80 to-transparent rounded-b-2xl" />
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
