import { API_CONFIG } from '@/config/api.config'

const API_BASE = API_CONFIG.BASE_URL

const tryJson = async (res: Response) => {
	const ct = res.headers.get('content-type') || ''
	return ct.includes('application/json') ? await res.json() : null
}

export type QuizListItem = {
	id: number
	title: string
	description: string
	difficulty: number
	icon?: string
	color?: string
	stars?: number
	image_url?: string | null
}


export class QuizService {
	// Centralized quizzes endpoint
	static QUIZ_BASE = `${API_BASE}/quiz/quizzes`

	static async getAll(): Promise<QuizListItem[]> {
		const p = `${QuizService.QUIZ_BASE}/`
		const res = await fetch(p, { method: 'GET', headers: { 'Content-Type': 'application/json' } })
		if (!res.ok) throw new Error(`Could not fetch quizzes list: ${res.status}`)
		let raw: any = await tryJson(res) || []
		if (!Array.isArray(raw)) raw = Array.isArray(raw.results) ? raw.results : []

		return raw.map((r: any, idx: number) => ({
			id: r.quiz_id ?? r.id ?? r.pk ?? idx,
			title: r.title ?? r.name ?? `Quiz ${idx + 1}`,
			description: r.description ?? r.summary ?? '',
			difficulty: r.difficulty_level ?? r.difficulty ?? undefined,
			icon: r.icon ?? undefined,
			color: (r.color ?? undefined),
			stars: r.stars ?? undefined,
			image_url: r.image_url ?? r.image ?? null,
		}))
	}

	static async getById(id: string | number): Promise<any> {
		const p = `${QuizService.QUIZ_BASE}/${id}/`
		const res = await fetch(p, { method: 'GET', headers: { 'Content-Type': 'application/json' } })
		if (!res.ok) throw new Error(`Could not fetch quiz ${id}: ${res.status}`)
		return await tryJson(res)
	}

	static async submitAnswer(quizId: string | number, payload: any): Promise<any> {
		const p = `${QuizService.QUIZ_BASE}/${quizId}/answers/`
		const res = await fetch(p, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) })
		if (!res.ok) {
			const txt = await res.text()
			throw new Error(`Submit answer failed: ${res.status} ${txt}`)
		}
		return await tryJson(res)
	}
}

