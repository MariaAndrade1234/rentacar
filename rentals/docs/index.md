# Rentals API Documentation

## Overview
This module handles rental management for the RentACar system.

## Endpoints

### List/Create Rentals
- **GET** `/api/rentals/` - List all rentals
- **POST** `/api/rentals/` - Create a new rental

### Rental Details
- **GET** `/api/rentals/{id}/` - Get rental details
- **PUT** `/api/rentals/{id}/` - Update rental
- **DELETE** `/api/rentals/{id}/` - Cancel rental

### Rental Status
- **PATCH** `/api/rentals/{id}/status/` - Update rental status
- **GET** `/api/rentals/user/{user_id}/` - Get user rentals
- **GET** `/api/rentals/car/{car_id}/` - Get rentals for a car

## Models
- Rental information
- Customer details
- Rental dates (start/end)
- Vehicle assignment
- Total cost calculation
- Payment status
- Additional services (insurance, GPS, etc)
