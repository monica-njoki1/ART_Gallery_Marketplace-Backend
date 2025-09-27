# Art Gallery Marketplace — Backend

**Live API Base URL:**  

https://art-gallery-marketplace-backend.onrender.com/  


## Table of Contents

- [About](#about)  
- [Features](#features)  
- [Tech Stack](#tech-stack)  
- [API Endpoints](#api-endpoints)  
- [Getting Started](#getting-started)  
  - [Prerequisites](#prerequisites)  
  - [Installation](#installation)  
  - [Running Locally](#running-locally)  
- [Environment Variables](#environment-variables)  
- [Database & Migrations](#database--migrations)  
- [Authentication / Authorization](#authentication--authorization)  
- [Error Handling & Validation](#error-handling--validation)  
- [Testing](#testing)  
- [Deployment](#deployment)  
- [Contributing](#contributing)  
- [License](#license)  
- [Contact](#contact)  

## About

This is the backend API for the **Art Gallery Marketplace** application.  
It provides endpoints to manage artworks, user accounts, transactions, galleries/collections, and other business logic.  

## Features

- CRUD operations on artworks, artists, collections/galleries, categories  
- User registration, login, password reset, profile management  
- Roles/permissions (e.g. admin/curator vs normal user)  
- Purchase / order processing, payment integration  
- Image upload / asset storage  
- Pagination, filtering, sorting  
- Data validation, error handling  
- Logging, security (input sanitization, rate-limiting, etc.)  
- API versioning (if applicable)  

## Tech Stack

- Language / Runtime: e.g. **Node.js / TypeScript** or **Python / Django / Flask** or **Go**  
- Web Framework / Router: e.g. Express, Fastify, Django REST Framework, Flask  
- Database: e.g. PostgreSQL, MySQL, MongoDB  
- ORM / Database Library: e.g. TypeORM, Sequelize, Prisma, Mongoose, Django ORM  
- Authentication: JWT, OAuth2, session-based auth  
- File / Asset Storage: Local / Cloud (e.g. AWS S3, Cloudinary)  
- Hosting / Deployment: Render (since backend is on `onrender.com`)  
- Logging & Monitoring: Winston, Morgan, Sentry, etc.  
- Testing: Jest, Mocha, Pytest, etc.  

## API Endpoints

> Below is a sample (illustrative) list of typical endpoints. Adjust to match your implementation.

| Method | Path | Description | Auth Required |
|---|---|---|---|
| `GET` | / | API root / health check | — |
| `POST` | /auth/register | Register a new user | No |
| `POST` | /auth/login | Log in user, return token | No |
| `POST` | /auth/refresh | Refresh JWT / session | Yes / token |
| `GET` | /users/me | Get current user profile | Yes |
| `PUT` | /users/me | Update user profile | Yes |
| `GET` | /artworks | List artworks (pagination, filters) | No / optional |
| `POST` | /artworks | Create a new artwork (admin / curator) | Yes |
| `GET` | /artworks/:id | Get a specific artwork | No |
| `PUT` | /artworks/:id | Update an artwork | Yes (owner / admin) |
| `DELETE` | /artworks/:id | Delete an artwork | Yes (owner / admin) |
| `POST` | /orders | Create an order / purchase | Yes |
| `GET` | /orders/:id | Get order detail | Yes |
| `GET` | /orders | List user's orders | Yes |
| `GET` | /gallery/:id` or `/collections/:id` | List artworks in a collection | No |
| `POST` | /upload | Upload image / asset | Yes |

Include any versioning prefix (e.g. `/api/v1`) if your API uses that.

### Request & Response Format

- Requests and responses use **JSON** format.
- Standard structure for error responses:

  ```json
  {
    "error": {
      "message": "Descriptive error message",
      "code": "BAD_REQUEST",
      "details": { ... }
    }
  }
