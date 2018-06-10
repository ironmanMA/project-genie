package main.java.com.models;

import lombok.Data;

@Data
public class Items {
    private String end_time;

    private Alternatives[] alternatives;

    private String start_time;

    private String type;
}
