package com.stu.signin;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.context.properties.ConfigurationPropertiesScan;
import org.springframework.scheduling.annotation.EnableAsync;

@SpringBootApplication
@ConfigurationPropertiesScan
@EnableAsync
public class StudentSigninApplication {

    public static void main(String[] args) {
        SpringApplication.run(StudentSigninApplication.class, args);
    }
}
