# Shadowverse Clone

This project is a Python-based implementation of the card game "Shadowverse". It includes a game engine, card data management, and a simple text-based UI.

## Features

*   Card game logic (playing cards, attacking, evolving, etc.)
*   Card data pipeline for crawling card information from `shadowverse.gg`.
*   Effect system with an event manager.
*   Text-based GUI for user interaction.

## How to Run

To run the game, execute the following command in your terminal:

```bash
python main.py
```

## Project Structure

*   `main.py`: Main entry point of the game.
*   `main_game_logic.py`: Contains the core game logic.
*   `card.py`, `deck.py`, `player.py`, etc.: Core components of the game.
*   `card_data.py`: Loads and manages card data.
*   `card_data_pipeline/`: A data pipeline to crawl and process card data.
    *   `1_data_acquisition/card_data_crawl.py`: Crawls card data from `shadowverse.gg`.
*   `card_database/`: Contains the card data in JSON format.
