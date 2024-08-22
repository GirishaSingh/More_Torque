# More Torque API

Welcome to the More Torque API project! This API allows you to manage vehicle and organization data, decode VINs, and more.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [API Endpoints](#api-endpoints)
  - [GET /vehicles/:vin](#get-vehiclesvin)
  - [POST /vehicles](#post-vehicles)
- [Usage](#usage)
- [Video Demo](#video-demo)


## Overview

The More Torque API is designed to help you interact with vehicle and organization data. It includes endpoints to fetch and manage vehicle records, decode VINs, and handle organization details.

## Features

- **Decode VIN**: Retrieve vehicle details from a VIN.
- **Add Vehicle**: Add new vehicles to the system with associated organizations.
- **Manage Organizations**: Create and update organizations.

## API Endpoints

### GET /vehicles/:vin

Fetches the vehicle corresponding to the VIN and returns the details.

#### Validations
- VIN should be a valid 17-digit alphanumeric string.
- The given VIN should be present in the system.

#### Response
- **Success**: Returns a 200 status code with the vehicle details.
- **Error**: Returns a 400 status code for invalid input or a 404 status code if the vehicle doesn’t exist.

### POST /vehicles

Adds a vehicle to the system. The body of the request should include the VIN and the organization to which the vehicle belongs.

#### Request Body
{
  "vin": "xxxxxxxx",
  "org": "yyyyyy"
}

## Video Demo
Check out the demo video 
[![Video Demo](https://link-to-your-thumbnail-image.com)](https://link-to-your-video-demo.com)




