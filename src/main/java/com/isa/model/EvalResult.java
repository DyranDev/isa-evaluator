package com.isa.model;

import java.util.Map;

public class EvalResult {
    private String requestId;
    private String status; // processing | done | failed
    private Map<String, Object> raw; // el JSON devuelto por FastAPI / Ollama
    private Map<String, Object> scores;
    private Double final_score;
    private String comment;
    private Double confidence;
    private String error;
    private long timestamp;

    public EvalResult() {}

    // getters / setters
    public String getRequestId() { return requestId; }
    public void setRequestId(String requestId) { this.requestId = requestId; }

    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }

    public Map<String, Object> getRaw() { return raw; }
    public void setRaw(Map<String, Object> raw) { this.raw = raw; }

    public Map<String, Object> getScores() { return scores; }
    public void setScores(Map<String, Object> scores) { this.scores = scores; }

    public Double getFinal_score() { return final_score; }
    public void setFinal_score(Double final_score) { this.final_score = final_score; }

    public String getComment() { return comment; }
    public void setComment(String comment) { this.comment = comment; }

    public Double getConfidence() { return confidence; }
    public void setConfidence(Double confidence) { this.confidence = confidence; }

    public String getError() { return error; }
    public void setError(String error) { this.error = error; }

    public long getTimestamp() { return timestamp; }
    public void setTimestamp(long timestamp) { this.timestamp = timestamp; }
}
