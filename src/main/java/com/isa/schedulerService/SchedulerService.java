package com.isa.scheduler;

import com.isa.service.EvaluadorService;

import java.util.concurrent.*;
import java.util.logging.Logger;

public class SchedulerService {
    private static final Logger LOG = Logger.getLogger("SchedulerService");
    private final ScheduledExecutorService scheduler = Executors.newSingleThreadScheduledExecutor();
    private final EvaluadorService evaluadorService;

    public SchedulerService(EvaluadorService evaluadorService) {
        this.evaluadorService = evaluadorService;
    }

    public void start() {
        // ejemplo: cada 10 minutos recalcula o limpia
        scheduler.scheduleAtFixedRate(this::taskRecalculateRanking, 1, 10, TimeUnit.MINUTES);
        LOG.info("Scheduler iniciado.");
    }

    public void stop() {
        scheduler.shutdown();
    }

    private void taskRecalculateRanking() {
        // Aquí podrías agregar lógica para recalcular ranking, enviar reportes, etc.
        LOG.info("Scheduler: recalculando (simulado) el ranking...");
        // ejemplo: solo imprime cuántos resultados hay
        int n = evaluadorService.allResults().size();
        LOG.info("Resultados almacenados: " + n);
    }
}
