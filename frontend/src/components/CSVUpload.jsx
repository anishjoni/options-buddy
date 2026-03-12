import { useState, useRef } from "react"
import { api } from "../api/client"

export default function CSVUpload({ onImportComplete }) {
  const [dragging, setDragging] = useState(false)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const inputRef = useRef()

  const handleFile = async (file) => {
    if (!file) return
    setLoading(true)
    setResult(null)
    try {
      const res = await api.uploadCSV(file)
      setResult(res)
      if (onImportComplete) onImportComplete(res)
    } catch (e) {
      setResult({ status: "failed", errors: [e.message], trades_added: 0, wheel_suggestions: [] })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <div
        onDragOver={e => { e.preventDefault(); setDragging(true) }}
        onDragLeave={() => setDragging(false)}
        onDrop={e => { e.preventDefault(); setDragging(false); handleFile(e.dataTransfer.files[0]) }}
        onClick={() => inputRef.current.click()}
        className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors
          ${dragging ? "border-blue-500 bg-blue-950/20" : "border-slate-600 hover:border-slate-400"}`}
      >
        <input ref={inputRef} type="file" accept=".csv" className="hidden"
          onChange={e => handleFile(e.target.files[0])} />
        {loading
          ? <p className="text-slate-400">Importing...</p>
          : <p className="text-slate-400">Drop Wealthsimple CSV here, or click to browse</p>
        }
      </div>
      {result && (
        <div className={`mt-3 p-3 rounded-lg text-sm ${result.status === "failed" ? "bg-red-950 text-red-300" : "bg-emerald-950 text-emerald-300"}`}>
          {result.status !== "failed"
            ? `✓ ${result.trades_added} trades imported`
            : `✗ Import failed`}
          {result.errors?.length > 0 && (
            <ul className="mt-1 text-xs text-slate-400">
              {result.errors.map((e, i) => <li key={i}>• {e}</li>)}
            </ul>
          )}
          {result.wheel_suggestions?.length > 0 && (
            <div className="mt-2 text-xs text-blue-300">
              {result.wheel_suggestions.length} Wheel pattern(s) detected — visit Campaigns to link them.
            </div>
          )}
        </div>
      )}
    </div>
  )
}
