package com.isa.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.isa.model.EvalResult;

import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Instant;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.*;
import java.util.logging.Logger;

public class EvaluadorService {
    private static final Logger LOG = Logger.getLogger("EvaluadorService");

    private final HttpClient client = HttpClient.newHttpClient();
    private final ObjectMapper mapper;
    private final ConcurrentMap<String, EvalResult> results = new ConcurrentHashMap<>();
    private final ScheduledExecutorService cleaner = Executors.newSingleThreadScheduledExecutor();
    private final ExecutorService workerPool = Executors.newFixedThreadPool(4);

    // Ajusta la URL del evaluador Python si hace falta
    private final String EVALUADOR_URL = "http://127.0.0.1:8001/evaluate";

    public EvaluadorService(ObjectMapper mapper) {
        this.mapper = mapper;
        // Programar limpieza de resultados antiguos cada 5 minutos
        cleaner.scheduleAtFixedRate(this::cleanupOld, 5, 5, TimeUnit.MINUTES);
    }

    public EvalResult evaluateSync(String pregunta, String respuesta) throws IOException, InterruptedException {
        Map<String, String> payload = Map.of("pregunta", pregunta, "respuesta", respuesta);
        String json = mapper.writeValueAsString(payload);

        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(EVALUADOR_URL))
                .header("Content-Type", "application/json")
                .POST(HttpRequest.BodyPublishers.ofString(json))
                .build();

        HttpResponse<String> resp = client.send(request, HttpResponse.BodyHandlers.ofString());
        String body = resp.body();
        // parse body to EvalResult (tolerante)
        EvalResult r = mapper.readValue(body, EvalResult.class);
        r.setTimestamp(Instant.now().toEpochMilli());
        return r;
    }

    public String evaluateAsync(String pregunta, String respuesta) {
        String id = UUID.randomUUID().toString();
        // marca como processing
        EvalResult placeholder = new EvalResult();
        placeholder.setRequestId(id);
        placeholder.setStatus("processing");
        placeholder.setTimestamp(Instant.now().toEpochMilli());
        results.put(id, placeholder);

        workerPool.submit(() -> {
            try {
                EvalResult r = evaluateSync(pregunta, respuesta);
                r.setRequestId(id);
                r.setStatus("done");
                r.setTimestamp(Instant.now().toEpochMilli());
                results.put(id, r);
            } catch (Exception e) {
                EvalResult err = new EvalResult();
                err.setRequestId(id);
                err.setStatus("failed");
                err.setError(e.getMessage());
                err.setTimestamp(Instant.now().toEpochMilli());
                results.put(id, err);
                LOG.severe("Error en evaluación async: " + e.getMessage());
            }
        });

        return id;
    }

    public EvalResult getResult(String requestId) {
        return results.get(requestId);
    }

    private void cleanupOld() {
        long now = Instant.now().toEpochMilli();
        long ttl = TimeUnit.MINUTES.toMillis(30); // conserva 30 min
        results.entrySet().removeIf(e -> (now - e.getValue().getTimestamp()) > ttl);
        LOG.info("Cleanup ejecutado. Resultados actuales: " + results.size());
    }

    // usado por el scheduler externo si es necesario
    public Map<String, EvalResult> allResults() {
        return results;
    }

    public void shutdown() {
        cleaner.shutdown();
        workerPool.shutdown();
    }
}
