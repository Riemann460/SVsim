# Shadowverse Simulator

This project is a Python-based implementation of the card game "Shadowverse".

## Development Philosophy

This project was developed with the following principles in mind:

*   **Modularity and Extensibility:** The code is designed to be modular and extensible. The core game logic, card data, and effects are separated to make it easy to add new cards, effects, and features in the future.
*   **Event-Driven Architecture:** The game uses an event-driven architecture to handle complex interactions between cards and effects. This makes the code more maintainable and easier to debug.
*   **Data-Driven Design:** Card data is stored in JSON files, making it easy to manage and update without changing the core game logic. The `card_data_pipeline` is designed to automate the process of collecting and processing card data.
*   **Readability and Maintainability:** The code is written to be as readable and maintainable as possible. Clear naming conventions and comments are used to make the code easy to understand and modify.