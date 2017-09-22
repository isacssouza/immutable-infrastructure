package xyz.isouza.controller;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController("/hello")
public class HelloController {

    @PostMapping
    public String sayHello() {
        return "Hello, world!";
    }
}
