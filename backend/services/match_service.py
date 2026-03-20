from utils.embedder import embed, cosine_similarity, score_to_100
from utils.groq_client import chat_complete
import asyncio

class MatchService:

    async def score(
        self,
        resume_text: str,
        job: dict
    ) -> dict:
        """
        Scores a job against a resume.

        Steps:
          1. Embed resume text (384-dim vector)
          2. Embed job description or title fallback
          3. Cosine similarity → 0-100 score
          4. If score >= 50, call Groq for 3 bullet reasons
          5. Sleep 2s after Groq call (free tier rate limit)

        Returns:
          { score: float, reasons: str }
        """
        # Build job text for embedding
        job_text = job.get("description") or ""
        if not job_text:
            # Fallback: use title + location if no description
            job_text = (
                f"{job.get('title', '')} "
                f"{job.get('location', '')} "
                f"{job.get('company', '')}"
            )

        # Embed both
        resume_emb = embed(resume_text)
        job_emb    = embed(job_text)

        # Score
        similarity = cosine_similarity(resume_emb, job_emb)
        score      = score_to_100(similarity)

        # Only call Groq for promising matches
        # to stay within free rate limits
        reasons = ""
        if score >= 50:
            reasons = await self._get_reasons(
                resume_text, job, score
            )
            # Groq free tier: 30 req/min
            # Sleep to avoid hitting the limit
            await asyncio.sleep(2)

        return {"score": score, "reasons": reasons}

    async def _get_reasons(
        self,
        resume_text: str,
        job: dict,
        score: float
    ) -> str:
        """
        Calls Groq to generate 3 bullet match reasons.
        Truncates inputs to stay under token limits.
        """
        try:
            return await chat_complete(
                system=(
                    "You are a professional recruiter. "
                    "Be concise. Use plain text, no markdown."
                ),
                user=(
                    f"Resume (excerpt):\n"
                    f"{resume_text[:600]}\n\n"
                    f"Job: {job.get('title')} "
                    f"at {job.get('company')}\n"
                    f"Description (excerpt):\n"
                    f"{job.get('description', '')[:600]}\n\n"
                    f"Match score: {score}/100\n"
                    f"Give exactly 3 short bullet points "
                    f"explaining why this is or is not "
                    f"a good match. Start each with - "
                ),
                max_tokens=256
            )
        except Exception as e:
            print(f"[Groq] Reason generation failed: {e}")
            return ""
