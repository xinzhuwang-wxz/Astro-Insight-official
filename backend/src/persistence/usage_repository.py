from src.persistence.database import connect

def save_usage(model: str, tokens: int):
    conn = connect()
    conn.execute(
        "INSERT INTO usage_logs(model,tokens) VALUES (?,?)",
        (model, tokens)
    )
    conn.commit()
    conn.close()

def usage_summary():
    conn = connect()
    rows = conn.execute(
        "SELECT model, SUM(tokens), COUNT(*) FROM usage_logs GROUP BY model"
    ).fetchall()
    conn.close()

    return {
        "models": [
            {
                "model": r[0],
                "tokens": r[1],
                "requests": r[2]
            }
            for r in rows
        ]
    }