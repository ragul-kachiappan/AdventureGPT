# AdventureGPT

A modern CLI text adventure game powered by GenAI. This project aims to recreate the classic text-based adventure experience with modern enhancements and AI-driven interactions.

## Tech Stack

- **CLI Interface**: Built with Textual and Prompt Toolkit for a rich text user interface.
- **Backend**: Starlette for handling internal API requests.
- **Database**: PostgreSQL with asyncpg and Tortoise ORM for data management.
- **Caching**: Redis for caching mechanisms.
- **Vector Database**: ChromaDB for storing embeddings and supporting AI features.
- **Containerization**: Docker and Docker Compose for environment management.

## How to Run the Project

1. **Build the Docker containers**:
   ```bash
   docker-compose build
   ```

2. **Start the Docker containers**:
   ```bash
   docker-compose up -d
   ```

3. **Attach to the CLI interface**:
   ```bash
   docker attach colossal_adventure
   ```

4. **Stop the Docker containers**:
   ```bash
   docker-compose down
   ```

## Pending Tasks

- [ ] Fix terminal issue
- [ ] Implement game logic and mechanics
- [ ] Add AI-driven interactions
- [ ] Enhance CLI interface with additional commands
- [ ] Write unit tests for core components
- [ ] Improve documentation and add usage examples
