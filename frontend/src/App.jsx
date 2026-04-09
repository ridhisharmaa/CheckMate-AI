import { useState, useRef } from 'react'

const API_BASE = 'http://localhost:8000'

/* ─── STYLES ─────────────────────────────────────────────── */
const s = {
  page: {
    minHeight: '100vh',
    background: '#faf9f6',
    padding: '0 0 80px',
  },

  /* Header */
  header: {
    borderBottom: '1px solid #e8e5df',
    padding: '28px 48px',
    display: 'flex',
    alignItems: 'center',
    gap: 16,
    background: '#ffffff',
    position: 'sticky', top: 0, zIndex: 100,
  },
  logo: {
    width: 36, height: 36,
    background: '#c8402a',
    borderRadius: 8,
    display: 'flex', alignItems: 'center', justifyContent: 'center',
    color: '#fff', fontSize: 18, fontWeight: 700,
  },
  title: {
    fontFamily: "'Playfair Display', serif",
    fontSize: 24, fontWeight: 900,
    color: '#0f0e0c', letterSpacing: '-0.5px',
  },
  tagline: {
    fontSize: 13, color: '#7a7874',
    marginLeft: 'auto',
    fontStyle: 'italic',
  },

  /* Main container */
  container: {
    maxWidth: 900,
    margin: '0 auto',
    padding: '48px 24px 0',
  },

  /* Step badge */
  stepBadge: {
    display: 'inline-flex', alignItems: 'center', gap: 8,
    background: '#fdf1ef', color: '#c8402a',
    fontSize: 12, fontWeight: 500,
    padding: '4px 12px', borderRadius: 20,
    marginBottom: 12,
    letterSpacing: '0.5px', textTransform: 'uppercase',
  },

  sectionTitle: {
    fontFamily: "'Playfair Display', serif",
    fontSize: 20, fontWeight: 700,
    color: '#0f0e0c', marginBottom: 6,
  },

  sectionSub: {
    fontSize: 14, color: '#7a7874', marginBottom: 24,
  },

  /* Upload cards */
  uploadGrid: {
    display: 'grid',
    gridTemplateColumns: '1fr 1fr',
    gap: 20, marginBottom: 32,
  },

  uploadCard: (active, hasFile) => ({
    border: `2px dashed ${hasFile ? '#2d6a4f' : active ? '#c8402a' : '#d4d0c8'}`,
    borderRadius: 12,
    padding: '32px 24px',
    textAlign: 'center',
    cursor: 'pointer',
    background: hasFile ? '#edf6f1' : active ? '#fdf1ef' : '#ffffff',
    transition: 'all 0.2s ease',
  }),

  uploadIcon: (hasFile) => ({
    fontSize: 32,
    marginBottom: 12,
    display: 'block',
  }),

  uploadLabel: { fontSize: 15, fontWeight: 500, color: '#0f0e0c', marginBottom: 4 },
  uploadSub: { fontSize: 13, color: '#7a7874' },
  uploadFile: { fontSize: 13, color: '#2d6a4f', fontWeight: 500, marginTop: 8 },

  /* Divider */
  divider: {
    border: 'none', borderTop: '1px solid #e8e5df',
    margin: '36px 0',
  },

  /* Marks scheme */
  marksGrid: {
    display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(160px, 1fr))',
    gap: 12, marginBottom: 24,
  },

  marksCard: {
    background: '#ffffff',
    border: '1px solid #e8e5df',
    borderRadius: 10, padding: '12px 14px',
    display: 'flex', flexDirection: 'column', gap: 6,
  },

  marksLabel: { fontSize: 12, color: '#7a7874', fontWeight: 500 },

  marksInput: {
    border: '1px solid #e8e5df', borderRadius: 6,
    padding: '6px 10px', fontSize: 14,
    fontFamily: "'DM Mono', monospace",
    color: '#0f0e0c', background: '#faf9f6',
    width: '100%', outline: 'none',
  },

  addQBtn: {
    border: '1px dashed #d4d0c8',
    borderRadius: 10, padding: '12px 14px',
    background: 'transparent',
    cursor: 'pointer', fontSize: 13, color: '#7a7874',
    display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6,
  },

  removeBtn: {
    background: 'none', border: 'none',
    cursor: 'pointer', color: '#c8402a',
    fontSize: 16, lineHeight: 1, marginLeft: 'auto',
  },

  marksRow: { display: 'flex', alignItems: 'center', gap: 6 },

  /* Submit */
  submitBtn: (loading) => ({
    width: '100%', padding: '16px',
    background: loading ? '#7a7874' : '#c8402a',
    color: '#ffffff', border: 'none',
    borderRadius: 10, fontSize: 16, fontWeight: 500,
    cursor: loading ? 'not-allowed' : 'pointer',
    fontFamily: "'DM Sans', sans-serif",
    display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 10,
    transition: 'background 0.2s',
    letterSpacing: '-0.2px',
  }),

  /* Progress */
  progressWrap: {
    background: '#ffffff', border: '1px solid #e8e5df',
    borderRadius: 12, padding: '24px 28px', marginTop: 24,
  },
  progressTitle: { fontSize: 15, fontWeight: 500, marginBottom: 16 },
  progressStep: (active, done) => ({
    display: 'flex', alignItems: 'center', gap: 12,
    padding: '10px 0',
    opacity: done ? 1 : active ? 1 : 0.4,
    borderBottom: '1px solid #f0ede7',
  }),
  progressDot: (active, done) => ({
    width: 28, height: 28, borderRadius: '50%', flexShrink: 0,
    display: 'flex', alignItems: 'center', justifyContent: 'center',
    fontSize: 13, fontWeight: 500,
    background: done ? '#2d6a4f' : active ? '#c8402a' : '#e8e5df',
    color: done || active ? '#fff' : '#7a7874',
  }),
  progressText: { fontSize: 14, color: '#0f0e0c' },

  /* Results */
  resultsHeader: {
    background: '#0f0e0c',
    borderRadius: 14, padding: '32px 36px',
    marginBottom: 24, color: '#ffffff',
    display: 'flex', alignItems: 'center', gap: 32,
  },
  bigScore: {
    fontFamily: "'Playfair Display', serif",
    fontSize: 64, fontWeight: 900, lineHeight: 1,
    color: '#ffffff',
  },
  bigScoreSub: { fontSize: 14, color: '#7a7874', marginTop: 4 },
  gradeBadge: (grade) => {
    const colors = {
      'A+': '#b8860b', A: '#2d6a4f', B: '#1e6091', C: '#6b4c11', D: '#92400e', F: '#c8402a'
    }
    return {
      fontFamily: "'Playfair Display', serif",
      fontSize: 48, fontWeight: 900,
      color: colors[grade] || '#c8402a',
      marginLeft: 'auto',
    }
  },

  metaGrid: {
    display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)',
    gap: 12, marginBottom: 24,
  },
  metaCard: {
    background: '#ffffff', border: '1px solid #e8e5df',
    borderRadius: 10, padding: '16px 20px',
  },
  metaVal: { fontSize: 22, fontWeight: 700, color: '#0f0e0c' },
  metaLabel: { fontSize: 12, color: '#7a7874', marginTop: 2 },

  /* Question cards */
  qCard: (pct) => ({
    background: '#ffffff', border: '1px solid #e8e5df',
    borderRadius: 12, marginBottom: 16, overflow: 'hidden',
  }),
  qHeader: {
    padding: '16px 20px',
    display: 'flex', alignItems: 'center', gap: 12,
    cursor: 'pointer', userSelect: 'none',
  },
  qNum: {
    fontFamily: "'DM Mono', monospace",
    fontSize: 13, fontWeight: 500,
    background: '#f0ede7', borderRadius: 6,
    padding: '4px 10px', color: '#4a4844',
  },
  qMarks: { fontSize: 15, fontWeight: 500, color: '#0f0e0c' },
  qMax: { fontSize: 13, color: '#7a7874' },
  qSimilarity: (pct) => ({
    marginLeft: 'auto', fontSize: 13,
    color: pct >= 70 ? '#2d6a4f' : pct >= 40 ? '#92400e' : '#c8402a',
    fontWeight: 500,
  }),
  qChevron: (open) => ({
    fontSize: 12, color: '#7a7874',
    transform: open ? 'rotate(180deg)' : 'rotate(0deg)',
    transition: 'transform 0.2s',
    marginLeft: 8,
  }),

  qBody: {
    borderTop: '1px solid #f0ede7',
    padding: '16px 20px',
  },

  progressBar: (pct) => ({
    height: 6, borderRadius: 3,
    background: '#f0ede7', overflow: 'hidden',
    marginBottom: 12,
  }),
  progressFill: (pct) => ({
    height: '100%',
    width: `${pct}%`,
    background: pct >= 70 ? '#2d6a4f' : pct >= 40 ? '#b8860b' : '#c8402a',
    borderRadius: 3,
    transition: 'width 0.8s ease',
  }),

  scoreRow: {
    display: 'flex', gap: 20, marginBottom: 12,
    fontSize: 13,
  },

  scoreItem: { display: 'flex', flexDirection: 'column', gap: 2 },
  scoreVal: { fontWeight: 500, color: '#0f0e0c', fontFamily: "'DM Mono', monospace" },
  scoreLabel: { color: '#7a7874', fontSize: 12 },

  tags: { display: 'flex', gap: 6, marginBottom: 12 },
  tag: (color) => ({
    fontSize: 11, fontWeight: 500,
    padding: '3px 8px', borderRadius: 4,
    background: color === 'diagram' ? '#e9f5fb' : color === 'table' ? '#f0f4fe' : '#f5f0fe',
    color: color === 'diagram' ? '#1e6091' : color === 'table' ? '#3730a3' : '#6d28d9',
  }),

  feedbackBox: {
    background: '#faf9f6', borderRadius: 8,
    padding: '12px 14px', fontSize: 14,
    color: '#4a4844', lineHeight: 1.6,
    borderLeft: '3px solid #e8e5df',
  },

  previewBox: {
    background: '#f0ede7', borderRadius: 8,
    padding: '10px 14px', fontSize: 13,
    color: '#4a4844', lineHeight: 1.5,
    fontFamily: "'DM Mono', monospace",
    marginTop: 10, whiteSpace: 'pre-wrap',
  },

  /* Error */
  errorBox: {
    background: '#fef2f2', border: '1px solid #fecaca',
    borderRadius: 10, padding: '16px 20px',
    color: '#991b1b', fontSize: 14, marginTop: 16,
  },
}

/* ─── UPLOAD DROPZONE ─────────────────────────────────────── */
function DropZone({ label, subLabel, file, onFile }) {
  const [drag, setDrag] = useState(false)
  const ref = useRef()

  const handleDrop = (e) => {
    e.preventDefault(); setDrag(false)
    const f = e.dataTransfer.files[0]
    if (f && f.type === 'application/pdf') onFile(f)
  }

  return (
    <div
      style={s.uploadCard(drag, !!file)}
      onClick={() => ref.current.click()}
      onDragOver={(e) => { e.preventDefault(); setDrag(true) }}
      onDragLeave={() => setDrag(false)}
      onDrop={handleDrop}
    >
      <input ref={ref} type="file" accept=".pdf" style={{ display: 'none' }}
        onChange={(e) => { if (e.target.files[0]) onFile(e.target.files[0]) }} />
      <span style={s.uploadIcon(!!file)}>
        {file ? '✅' : '📄'}
      </span>
      <div style={s.uploadLabel}>{label}</div>
      <div style={s.uploadSub}>{subLabel}</div>
      {file && <div style={s.uploadFile}>{file.name}</div>}
    </div>
  )
}

/* ─── QUESTION CARD ───────────────────────────────────────── */
function QuestionCard({ q }) {
  const [open, setOpen] = useState(false)
  const pct = q.combined_score_pct ?? ((q.marks_awarded / q.max_marks) * 100)

  return (
    <div style={s.qCard(pct)}>
      <div style={s.qHeader} onClick={() => setOpen(o => !o)}>
        <span style={s.qNum}>{q.question}</span>
        <span style={s.qMarks}>{q.marks_awarded} / {q.max_marks}</span>
        <span style={s.qMax}>marks</span>
        <span style={s.qSimilarity(q.similarity_score)}>
          {q.similarity_score?.toFixed(0)}% match
        </span>
        <span style={s.qChevron(open)}>▼</span>
      </div>

      {/* Progress bar always visible */}
      <div style={{ padding: '0 20px 14px' }}>
        <div style={s.progressBar(pct)}>
          <div style={s.progressFill(pct)} />
        </div>
      </div>

      {open && (
        <div style={s.qBody}>
          <div style={s.scoreRow}>
            <div style={s.scoreItem}>
              <span style={s.scoreVal}>{q.similarity_score?.toFixed(1)}%</span>
              <span style={s.scoreLabel}>Semantic similarity</span>
            </div>
            <div style={s.scoreItem}>
              <span style={s.scoreVal}>{q.llm_score?.toFixed(1)}%</span>
              <span style={s.scoreLabel}>AI rubric score</span>
            </div>
            <div style={s.scoreItem}>
              <span style={s.scoreVal}>{pct.toFixed(1)}%</span>
              <span style={s.scoreLabel}>Combined score</span>
            </div>
            <div style={s.scoreItem}>
              <span style={s.scoreVal}>{q.marks_awarded} / {q.max_marks}</span>
              <span style={s.scoreLabel}>Marks awarded</span>
            </div>
          </div>

          {(q.has_diagram || q.has_table || q.has_code) && (
            <div style={s.tags}>
              {q.has_diagram && <span style={s.tag('diagram')}>📊 Diagram detected</span>}
              {q.has_table && <span style={s.tag('table')}>📋 Table detected</span>}
              {q.has_code && <span style={s.tag('code')}>💻 Code detected</span>}
            </div>
          )}

          <div style={s.feedbackBox}>{q.feedback}</div>

          {q.student_answer_preview && (
            <div style={s.previewBox}>
              <strong style={{ fontSize: 11, color: '#7a7874', display: 'block', marginBottom: 6 }}>
                STUDENT ANSWER (OCR preview)
              </strong>
              {q.student_answer_preview}
              {q.student_answer_preview.length >= 300 && '...'}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

/* ─── MAIN APP ────────────────────────────────────────────── */
const STAGES = [
  'CV preprocessing — deskew, denoise, enhance',
  'Gemini Vision OCR — handwriting to text',
  'LLM answer mapping — matching questions',
  'Semantic + AI scoring — evaluating answers',
]

export default function App() {
  const [studentFile, setStudentFile] = useState(null)
  const [teacherFile, setTeacherFile] = useState(null)
  const [questions, setQuestions] = useState([
    { id: 1, label: 'Q1', marks: 2 },
    { id: 2, label: 'Q2', marks: 5 },
    { id: 3, label: 'Q3', marks: 10 },
  ])
  const [nextId, setNextId] = useState(4)
  const [loading, setLoading] = useState(false)
  const [stage, setStage] = useState(-1)
  const [results, setResults] = useState(null)
  const [error, setError] = useState(null)

  const addQuestion = () => {
    setQuestions(q => [...q, { id: nextId, label: `Q${nextId}`, marks: 5 }])
    setNextId(n => n + 1)
  }

  const removeQuestion = (id) => {
    setQuestions(q => q.filter(x => x.id !== id))
  }

  const updateQuestion = (id, field, value) => {
    setQuestions(q => q.map(x => x.id === id ? { ...x, [field]: value } : x))
  }

  const handleSubmit = async () => {
    if (!studentFile || !teacherFile) {
      setError('Please upload both PDF files before grading.'); return
    }
    if (questions.length === 0) {
      setError('Please add at least one question.'); return
    }

    setError(null); setResults(null); setLoading(true); setStage(0)

    // Build marks scheme JSON
    const marksScheme = {}
    questions.forEach(q => { marksScheme[q.label.trim() || `Q${q.id}`] = Number(q.marks) || 1 })

    const formData = new FormData()
    formData.append('student_pdf', studentFile)
    formData.append('teacher_pdf', teacherFile)
    formData.append('marks_scheme', JSON.stringify(marksScheme))

    // Simulate stage progress (real progress needs WebSocket — this approximates it)
    const stageInterval = setInterval(() => {
      setStage(s => s < STAGES.length - 1 ? s + 1 : s)
    }, 12000)   // Each stage ~12 seconds

    try {
      const res = await fetch(`${API_BASE}/grade`, {
        method: 'POST', body: formData,
      })
      clearInterval(stageInterval)
      setStage(STAGES.length)

      if (!res.ok) {
        const err = await res.json()
        throw new Error(err.detail || 'Grading failed')
      }
      const data = await res.json()
      setResults(data.results)
    } catch (e) {
      clearInterval(stageInterval)
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  const reset = () => {
    setStudentFile(null); setTeacherFile(null)
    setResults(null); setError(null)
    setStage(-1); setLoading(false)
  }

  return (
    <div style={s.page}>
      {/* Header */}
      <header style={s.header}>
        <div style={s.logo}>✓</div>
        <h1 style={s.title}>CheckMate</h1>
        <p style={s.tagline}>AI-powered answer sheet grading</p>
      </header>

      <div style={s.container}>

        {!results ? (
          <>
            {/* STEP 1: Upload */}
            <div style={s.stepBadge}>Step 1</div>
            <h2 style={s.sectionTitle}>Upload Answer Sheets</h2>
            <p style={s.sectionSub}>Student handwritten PDF + Teacher's model answer PDF</p>
            <div style={s.uploadGrid}>
              <DropZone
                label="Student Answer Sheet"
                subLabel="Handwritten PDF — scanned or photographed"
                file={studentFile}
                onFile={setStudentFile}
              />
              <DropZone
                label="Teacher's Q&A Reference"
                subLabel="Printed question paper with model answers"
                file={teacherFile}
                onFile={setTeacherFile}
              />
            </div>

            <hr style={s.divider} />

            {/* STEP 2: Marks scheme */}
            <div style={s.stepBadge}>Step 2</div>
            <h2 style={s.sectionTitle}>Marks Scheme</h2>
            <p style={s.sectionSub}>Set the question label and maximum marks for each question</p>

            <div style={s.marksGrid}>
              {questions.map(q => (
                <div key={q.id} style={s.marksCard}>
                  <div style={s.marksRow}>
                    <span style={s.marksLabel}>Question label</span>
                    <button style={s.removeBtn} onClick={() => removeQuestion(q.id)}>✕</button>
                  </div>
                  <input
                    style={s.marksInput}
                    value={q.label}
                    onChange={e => updateQuestion(q.id, 'label', e.target.value)}
                    placeholder="e.g. Q1"
                  />
                  <span style={{ ...s.marksLabel, marginTop: 6 }}>Max marks</span>
                  <input
                    style={s.marksInput}
                    type="number" min="1" max="100"
                    value={q.marks}
                    onChange={e => updateQuestion(q.id, 'marks', e.target.value)}
                  />
                </div>
              ))}
              <button style={s.addQBtn} onClick={addQuestion}>
                + Add question
              </button>
            </div>

            <hr style={s.divider} />

            {/* STEP 3: Grade */}
            <div style={s.stepBadge}>Step 3</div>
            <h2 style={s.sectionTitle}>Grade</h2>
            <p style={s.sectionSub}>
              Pipeline: CV preprocessing → Gemini OCR → Answer mapping → AI scoring
            </p>

            <button style={s.submitBtn(loading)} onClick={handleSubmit} disabled={loading}>
              {loading ? '⏳ Grading in progress...' : '🎯 Grade Answer Sheet'}
            </button>

            {error && <div style={s.errorBox}>⚠️ {error}</div>}

            {/* Progress */}
            {loading && (
              <div style={s.progressWrap}>
                <p style={s.progressTitle}>Processing your answer sheet...</p>
                {STAGES.map((label, i) => (
                  <div key={i} style={s.progressStep(stage === i, stage > i)}>
                    <div style={s.progressDot(stage === i, stage > i)}>
                      {stage > i ? '✓' : i + 1}
                    </div>
                    <span style={s.progressText}>{label}</span>
                    {stage === i && (
                      <span style={{ marginLeft: 'auto', fontSize: 12, color: '#c8402a' }}>
                        Running...
                      </span>
                    )}
                  </div>
                ))}
              </div>
            )}
          </>
        ) : (
          <>
            {/* RESULTS */}
            <div style={s.resultsHeader}>
              <div>
                <div style={{ fontSize: 13, color: '#7a7874', marginBottom: 8, textTransform: 'uppercase', letterSpacing: '1px' }}>
                  Final Score
                </div>
                <div style={s.bigScore}>
                  {results.total_scored} <span style={{ fontSize: 32, color: '#7a7874' }}>/ {results.total_possible}</span>
                </div>
                <div style={s.bigScoreSub}>{results.percentage}% overall</div>
              </div>
              <div style={{ marginLeft: 'auto', textAlign: 'right' }}>
                <div style={{ fontSize: 13, color: '#7a7874', marginBottom: 4 }}>Grade</div>
                <div style={s.gradeBadge(results.grade)}>{results.grade}</div>
              </div>
            </div>

            {/* Meta cards */}
            <div style={s.metaGrid}>
              <div style={s.metaCard}>
                <div style={s.metaVal}>{results.questions.length}</div>
                <div style={s.metaLabel}>Questions graded</div>
              </div>
              <div style={s.metaCard}>
                <div style={s.metaVal}>{results.percentage}%</div>
                <div style={s.metaLabel}>Overall accuracy</div>
              </div>
              <div style={s.metaCard}>
                <div style={s.metaVal}>
                  {results.questions.filter(q => q.has_diagram || q.has_table || q.has_code).length}
                </div>
                <div style={s.metaLabel}>Questions with visuals</div>
              </div>
            </div>

            {/* Question breakdown */}
            <h2 style={{ ...s.sectionTitle, marginBottom: 16 }}>Question-wise Breakdown</h2>
            {results.questions.map((q, i) => (
              <QuestionCard key={i} q={q} />
            ))}

            <button
              style={{ ...s.submitBtn(false), marginTop: 32, background: '#2a2825' }}
              onClick={reset}
            >
              ← Grade Another Sheet
            </button>
          </>
        )}
      </div>
    </div>
  )
}
