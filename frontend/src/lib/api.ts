const BASE = process.env.NEXT_PUBLIC_API_URL || 
             "http://localhost:8000"

export const api = {
    get: (path: string) =>
        fetch(`${BASE}${path}`).then(r => r.json()),
    post: (path: string, body: unknown) =>
        fetch(`${BASE}${path}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(body)
        }).then(r => r.json()),
}
