package com.isa.controller;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.isa.model.EvalRequest;
import com.isa.model.EvalResult;
import com.isa.service.EvaluadorService;
import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpHandler;

import java.io.*;
import java.net.URI;
import java.nio.charset.StandardCharsets;
import java.util.Map;
import java.util.logging.Logger;

public class EvalController {
    private static final Logger LOG = Logger.getLogger("EvalController");
    private final EvaluadorService evaluadorService;
    private final ObjectMapper mapper;

    public EvalController(EvaluadorService service, ObjectMapper mapper) {
        this.evaluadorService = service;
        this.mapper = mapper;
    }

    // Síncrono: llama al evaluador Python y devuelve resultado
    public void handleEvaluateSync(HttpExchange exchange) throws IOException {
        if (!"POST".equalsIgnoreCase(exchange.getRequestMethod())) {
            exchange.sendResponseHeaders(405, -1);
            return;
        }
        String body = new String(exchange.getRequestBody().readAllBytes(), StandardCharsets.UTF_8);
        EvalRequest req = mapper.readValue(body, EvalRequest.class);
        try {
            EvalResult result = evaluadorService.evaluateSync(req.getPregunta(), req.getRespuesta());
            byte[] out = mapper.writeValueAsBytes(result);
            exchange.getResponseHeaders().add("Content-Type", "application/json; charset=utf-8");
            exchange.sendResponseHeaders(200, out.length);
            exchange.getResponseBody().write(out);
        } catch (Exception e) {
            LOG.severe("Error evaluate_sync: " + e.getMessage());
            byte[] out = ("{\"error\":\"" + e.getMessage() + "\"}").getBytes();
            exchange.sendResponseHeaders(500, out.length);
            exchange.getResponseBody().write(out);
        } finally {
            exchange.close();
        }
    }

    // Asíncrono: desencadena evaluación en hilo, devuelve request_id
    public void handleEvaluateAsync(HttpExchange exchange) throws IOException {
        if (!"POST".equalsIgnoreCase(exchange.getRequestMethod())) {
            exchange.sendResponseHeaders(405, -1);
            return;
        }
        String body = new String(exchange.getRequestBody().readAllBytes(), StandardCharsets.UTF_8);
        EvalRequest req = mapper.readValue(body, EvalRequest.class);
        String requestId = evaluadorService.evaluateAsync(req.getPregunta(), req.getRespuesta());
        byte[] out = mapper.writeValueAsBytes(Map.of("request_id", requestId, "status", "processing"));
        exchange.getResponseHeaders().add("Content-Type", "application/json; charset=utf-8");
        exchange.sendResponseHeaders(200, out.length);
        exchange.getResponseBody().write(out);
        exchange.close();
    }

    // GET /api/result?request_id=...
    public void handleGetResult(HttpExchange exchange) throws IOException {
        if (!"GET".equalsIgnoreCase(exchange.getRequestMethod())) {
            exchange.sendResponseHeaders(405, -1);
            return;
        }
        URI uri = exchange.getRequestURI();
        String query = uri.getQuery();
        String requestId = null;
        if (query != null) {
            for (String part : query.split("&")) {
                String[] kv = part.split("=", 2);
                if (kv.length == 2 && kv[0].equals("request_id")) {
                    requestId = kv[1];
                }
            }
        }
        if (requestId == null) {
            exchange.sendResponseHeaders(400, -1);
            return;
        }
        EvalResult res = evaluadorService.getResult(requestId);
        if (res == null) {
            byte[] out = "{\"status\":\"pending\"}".getBytes();
            exchange.getResponseHeaders().add("Content-Type", "application/json; charset=utf-8");
            exchange.sendResponseHeaders(200, out.length);
            exchange.getResponseBody().write(out);
        } else {
            byte[] out = mapper.writeValueAsBytes(res);
            exchange.getResponseHeaders().add("Content-Type", "application/json; charset=utf-8");
            exchange.sendResponseHeaders(200, out.length);
            exchange.getResponseBody().write(out);
        }
        exchange.close();
    }
}
