# Shadowverse Simulator

## Development Philosophy

This project was developed with the following principles in mind:

*   **Modularity and Extensibility:** The code is designed to be modular and extensible. The core game logic, card data, and effects are separated to make it easy to add new cards, effects, and features in the future.
*   **Event-Driven Architecture:** The game uses an event-driven architecture to handle complex interactions between cards and effects. This makes the code more maintainable and easier to debug.
*   **Data-Driven Design:** Card data is stored in JSON files, making it easy to manage and update without changing the core game logic. The `card_data_pipeline` is designed to automate the process of collecting and processing card data.
*   **Readability and Maintainability:** The code is written to be as readable and maintainable as possible. Clear naming conventions and comments are used to make the code easy to understand and modify.

## Features

This project is a Python-based implementation of the card game "Shadowverse".

### Implemented Features
*   **Core Game Logic:** A full 2-player game loop is implemented, including turn progression, resource management (PP, EP, SEP), card draws, and combat.
*   **Player vs. Player:** Supports local two-player matches.
*   **Mulligan System:** Players can perform a mulligan at the start of the game.
*   **Evolution System:** Both standard **Evolution** (using EP) and **Super Evolution** (using SEP) mechanics are functional.
*   **Card Effects & Keywords:** A robust, event-driven `EffectProcessor` handles a wide variety of effects:
    - **Triggers:** Fanfare, Last Words, On-Evolve, On-Super-Evolve, Turn End triggers, etc.
    - **Keywords:** `Aura`, `Ambush`, `Bane`, `Drain`, `Barrier`, `Countdown`, `Spellboost`, etc.
    - **Targeting:** Supports complex targeting (choice, random, conditional) and player choices for "Choose" effects.
*   **Functional GUI:** A `tkinter`-based GUI provides a visual representation of the game state, including each player's hand, field, and stats. It also facilitates user interactions like mulligan and effect choices.

### Planned Features
*   **AI Opponent:** Implement an AI that can play against a human player.
*   **Crest Effects:** Add support for the "Crest" keyword, which grants passive effects to the player.
*   **Deck Building:** Create a feature that allows players to build and save their own decks.
*   **Full Card Database Integration:** Integrate the entire processed card database from `card_database/` for deck creation and gameplay.
*   **Advanced GUI:** Enhance the user interface with:
    - Graphical card assets instead of text descriptions.
    - Drag-and-drop controls for a more intuitive experience.
    - Animations and visual effects for card actions.
*   **Network Play:** Implement networking to allow players to compete over the internet.

## Card Data Pipeline

The project includes a data pipeline (`card_data_pipeline/`) responsible for building and maintaining the game's card database. It automates crawling data from external sources, processing it through various refinement stages, and producing the final JSON database used by the game engine.