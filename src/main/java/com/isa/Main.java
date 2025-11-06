package com.isa;

import com.isa.controller.EvalController;
import com.isa.scheduler.SchedulerService;
import com.isa.service.EvaluadorService;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.sun.net.httpserver.HttpServer;

import java.io.IOException;
import java.net.InetSocketAddress;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.logging.Logger;

public class Main {
    private static final Logger LOG = Logger.getLogger("ISA-Main");

    public static void main(String[] args) throws Exception {
        int port = 8080;
        HttpServer server = HttpServer.create(new InetSocketAddress(port), 0);

        ObjectMapper mapper = new ObjectMapper();
        EvaluadorService evaluadorService = new EvaluadorService(mapper);
        EvalController controller = new EvalController(evaluadorService, mapper);

        // Rutas API
        server.createContext("/api/evaluate_sync", controller::handleEvaluateSync);
        server.createContext("/api/evaluate_async", controller::handleEvaluateAsync);
        server.createContext("/api/result", controller::handleGetResult);

        // Ruta para servir un index.html simple
        server.createContext("/", exchange -> {
            try {
                byte[] bytes = Files.readAllBytes(Paths.get("src/main/resources/static/index.html"));
                exchange.getResponseHeaders().add("Content-Type", "text/html; charset=UTF-8");
                exchange.sendResponseHeaders(200, bytes.length);
                exchange.getResponseBody().write(bytes);
            } catch (IOException e) {
                byte[] err = ("404 not found: " + e.getMessage()).getBytes();
                exchange.sendResponseHeaders(404, err.length);
                exchange.getResponseBody().write(err);
            } finally {
                exchange.close();
            }
        });

        server.setExecutor(null); // usa thread pool por defecto
        server.start();
        LOG.info("Servidor HTTP iniciado en http://localhost:" + port);

        // Scheduler: tareas recurrentes
        SchedulerService scheduler = new SchedulerService(evaluadorService);
        scheduler.start();

        // add shutdown hook
        Runtime.getRuntime().addShutdownHook(new Thread(() -> {
            LOG.info("Deteniendo servidor...");
            scheduler.stop();
            server.stop(1);
        }));
    }
}
