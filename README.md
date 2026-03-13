## About
Link Forge is a minimal URL shortener service with user authentication.
Each user can create and manage their own short links, which redirect to target URLs.
The project exposes an HTTP API for authentication and link management, backed by a relational database.

## Showcase
![Showcase](https://github.com/Kalebe16/link-forge/blob/main/showcase.png)


## How to run
```bash
cd link-forge

cp -rf ./backend/.env.example ./backend/.env
cp -rf ./frontend/.env.example ./frontend/.env
cp -rf ./db/.env.example ./db/.env

cd docker
docker compose up --build --force-recreate
```


