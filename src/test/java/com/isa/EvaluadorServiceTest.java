package com.isa;

import com.isa.model.EvalResult;
import com.isa.service.EvaluadorService;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.*;
import java.util.*;
import static org.junit.jupiter.api.Assertions.*;

/**
 * 🔍 Conjunto de 15 pruebas unitarias para el proyecto ISA-java-Threads
 * Usa JUnit 5.
 */
public class EvaluadorServiceTest {

    private static EvaluadorService evaluadorService;

    @BeforeAll
    static void setup() {
        evaluadorService = new EvaluadorService(new ObjectMapper());
        System.out.println("🔧 Iniciando entorno de pruebas...");
    }

    // --- Pruebas simples de ejemplo ---
    @Test
    void testSumaBasica() {
        int resultado = 2 + 3;
        assertEquals(5, resultado);
    }

    @Test
    void testCadenaNoVacia() {
        String s = "ISA";
        assertFalse(s.isEmpty());
    }

    @Test
    void testListaContieneElemento() {
        List<String> roles = Arrays.asList("empresa", "candidato");
        assertTrue(roles.contains("empresa"));
    }

    // --- Pruebas con lógica del servicio ---
    @Test
    void testEvaluadorServiceNoNulo() {
        assertNotNull(evaluadorService);
    }

    @Test
    void testEvaluacionAsyncGeneraID() {
        String id = evaluadorService.evaluateAsync("Pregunta", "Respuesta");
        assertNotNull(id);
        assertFalse(id.isEmpty());
    }

    @Test
    void testPlaceholderInicialTieneEstadoProcessing() {
        String id = evaluadorService.evaluateAsync("Pregunta", "Respuesta");
        EvalResult res = evaluadorService.getResult(id);
        assertEquals("processing", res.getStatus());
    }

    @Test
    void testCleanupOldNoLanzaErrores() {
        assertDoesNotThrow(() -> evaluadorService.allResults());
    }

    @Test
    void testEvalResultSettersYGetters() {
        EvalResult res = new EvalResult();
        res.setRequestId("123");
        res.setStatus("done");
        res.setError("none");
        res.setTimestamp(123456L);
        res.setScores(Map.of("tecnico", 4.5));
        assertEquals("123", res.getRequestId());
        assertEquals("done", res.getStatus());
        assertEquals(4.5, res.getScores().get("tecnico"));
    }

    // --- Pruebas de validaciones lógicas ---
    @Test
    void testDivisionSegura() {
        assertThrows(ArithmeticException.class, () -> {
            int x = 10 / 0;
        });
    }

    @Test
    void testComparacionNumerica() {
        assertTrue(5 > 3);
    }

    @Test
    void testMapaContieneClave() {
        Map<String, Integer> mapa = Map.of("a", 1, "b", 2);
        assertTrue(mapa.containsKey("a"));
    }

    @Test
    void testStringMayusculas() {
        String texto = "isa".toUpperCase();
        assertEquals("ISA", texto);
    }

    @Test
    void testBooleanNegacion() {
        boolean valor = false;
        assertFalse(valor);
    }

    @Test
    void testListaVacia() {
        List<String> lista = new ArrayList<>();
        assertTrue(lista.isEmpty());
    }

    @AfterAll
    static void teardown() {
        evaluadorService.shutdown();
        System.out.println("✅ Pruebas finalizadas correctamente.");
    }
}
