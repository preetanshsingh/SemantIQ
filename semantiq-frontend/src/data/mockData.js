// Mock data — shaped exactly like the future FastAPI responses will be.
// When the backend is live, each of these gets replaced by a fetch() call
// to the matching endpoint (see comments below).

// Replace with: GET /api/recommendations?keyword=...
export const MOCK_RECOMMENDATIONS = [
  { word: 'insulin resistance', ig: 89, category: 'Core', points: 6 },
  { word: 'blood glucose levels', ig: 85, category: 'Core', points: 5 },
  { word: 'HbA1c test', ig: 78, category: 'Semantic', points: 5 },
  { word: 'glycemic index', ig: 72, category: 'Semantic', points: 4 },
  { word: 'pancreatic beta cells', ig: 68, category: 'Entity', points: 4 },
  { word: 'fasting blood sugar', ig: 65, category: 'Semantic', points: 4 },
  { word: 'endocrinologist', ig: 61, category: 'Entity', points: 3 },
]

// Replace with: GET /api/paa?keyword=...
export const MOCK_PAA = [
  { question: 'What are the early signs of diabetes?', answered: false, points: 6 },
  { question: 'How is type 2 different from type 1?', answered: true },
  { question: 'Can diabetes be reversed with diet?', answered: false, points: 6 },
  { question: 'What is a normal blood sugar level?', answered: true },
  { question: 'What foods should diabetics avoid?', answered: false, points: 5 },
]

// Replace with: GET /api/entities?content=...
export const MOCK_ENTITIES = [
  { entity: 'insulin', type: 'Protein', inKG: true, count: 3 },
  { entity: 'pancreas', type: 'Organ', inKG: true, count: 2 },
  { entity: 'blood sugar', type: 'Biomarker', inKG: true, count: 5 },
  { entity: 'metformin', type: 'Drug', inKG: false, count: 0 },
  { entity: 'HbA1c', type: 'Biomarker', inKG: false, count: 0 },
]

// Replace with: GET /api/readability?content=...
export const MOCK_READABILITY = [
  { label: 'Flesch Reading Ease', value: '64.2', grade: 'Standard', good: true },
  { label: 'FK Grade Level', value: '8.4', grade: 'Grade 8', good: true },
  { label: 'Passive Voice', value: '14%', grade: 'Moderate', good: false },
  { label: 'Avg Sentence Length', value: '18 words', grade: 'Optimal', good: true },
  { label: 'Burstiness Index', value: '0.71', grade: 'Human-like', good: true },
  { label: 'AI Probability', value: '31%', grade: 'Likely human', good: true },
]

// Replace with: GET /api/brief?keyword=...
export const MOCK_BRIEF = {
  h1: 'Complete Guide to Diabetes Management: Symptoms, Treatment & Prevention',
  h2s: [
    'What Is Diabetes? Types, Causes, Risk Factors',
    'Early Warning Signs You Should Not Ignore',
    'How Diabetes Is Diagnosed: Tests & Procedures',
    'Managing Blood Sugar: Diet, Exercise, Medication',
    'HbA1c and Key Biomarkers Explained',
    'Can Type 2 Diabetes Be Reversed?',
  ],
}

// Replace with: POST /api/score  { content, keyword }
export const MOCK_SCORE_BREAKDOWN = [
  { label: 'Keyword relevance', score: 78 },
  { label: 'Entity coverage', score: 62 },
  { label: 'Readability', score: 84 },
  { label: 'Content depth', score: 70 },
  { label: 'Heading structure', score: 58 },
  { label: 'PAA coverage', score: 40 },
]

export const DEMO_CONTENT = `Diabetes is a metabolic disease that causes high blood sugar. The hormone insulin moves sugar from the blood into your cells to be stored or used for energy. With diabetes, your body either doesn't make enough insulin or can't effectively use the insulin it does make.

Untreated high blood sugar from diabetes can damage your nerves, eyes, kidneys, and other organs.`

export const ANALYSIS_STEPS = [
  { label: 'Fetching SERP top 10 results', icon: '🔍' },
  { label: 'Scraping competitor pages', icon: '📄' },
  { label: 'Running SBERT semantic analysis', icon: '🧠' },
  { label: 'Extracting NER + KG entities', icon: '🏷️' },
  { label: 'Ranking by Information Gain', icon: '📊' },
  { label: 'Analysis complete!', icon: '✅' },
]
