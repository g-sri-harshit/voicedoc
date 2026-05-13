def compute_trust_score(answer: str, context_chunks: list) -> dict:
    """
    Compute a trust score for a model-generated diagnostic answer.

    Scoring starts at 100 and deductions are applied based on heuristics
    that indicate low reliability (uncertainty phrases, short answers,
    no source context, or signs of hallucination).

    Args:
        answer: The LLM-generated answer string.
        context_chunks: List of retrieved context strings used to generate the answer.

    Returns:
        dict with keys:
            score (int): 0–100 trust score.
            label (str): "High", "Medium", or "Low".
            color (str): "green", "yellow", or "red".
            flags (list[str]): Human-readable descriptions of any issues found.
    """
    score = 100
    flags = []
    answer_lower = answer.lower() if answer else ""

    # --- Penalty: model expressed uncertainty ---
    uncertainty_phrases = [
        "i don't know",
        "i'm not sure",
        "i am not sure",
        "cannot determine",
        "not certain",
        "unclear",
        "i cannot say",
    ]
    for phrase in uncertainty_phrases:
        if phrase in answer_lower:
            score -= 30
            flags.append("Model expressed uncertainty")
            break  # apply once

    # --- Penalty: answer is too short to be useful ---
    if answer and len(answer.strip()) < 50:
        score -= 20
        flags.append("Answer is unusually short")

    # --- Penalty: no context documents matched ---
    if not context_chunks:
        score -= 40
        flags.append("No source documents matched this query")

    # --- Penalty: potential hallucination detected ---
    if "hallucin" in answer_lower:
        score -= 50
        flags.append("Potential hallucination detected")

    # --- Penalty: empty or missing answer ---
    if not answer or not answer.strip():
        score -= 60
        flags.append("Empty answer returned by model")

    # Clamp to valid range
    score = max(0, min(100, score))

    # Determine label and color
    if score >= 70:
        label = "High"
        color = "green"
    elif score >= 40:
        label = "Medium"
        color = "yellow"
    else:
        label = "Low"
        color = "red"

    return {
        "score": score,
        "label": label,
        "color": color,
        "flags": flags,
    }


