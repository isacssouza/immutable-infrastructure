package xyz.isouza.controller;

import static org.junit.Assert.*;

import org.junit.Test;

public class HelloControllerTest {
    @Test
    public void shouldSayHello() {
        HelloController controller = new HelloController();
        assertEquals("Hello, world!", controller.sayHello());
    }

}