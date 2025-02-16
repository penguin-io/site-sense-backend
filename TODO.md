### 0. Initial setup
- [ ] [OPTIONAL] Setup Postgres (sqlite now)
- [ ] Set up Docker for containerization
- [ ] Set up role-based access control (RBAC) ( Admins can change rulesets, "smaller" admins can only view)

### 1. Core Attendance API
- [ ] Create employee model and database schema
- [ ] Implement CRUD operations for employee management
- [ ] Develop check-in/check-out endpoints
- [ ] Create attendance log model and schema
- [ ] Implement attendance record retrieval and filtering

### 2. Biometric Processing Pipeline
- [ ] Set up endpoint to receive biometric data (face, voice)
- [ ] Implement face recognition processing (integrate with AI model)
- [ ] Create fallback mechanism for QR code-based check-in
- [ ] Implement liveness detection integration

### 3. Environmental Adaptation
- [ ] Create endpoint to receive environmental data
- [ ] Implement logic to select appropriate authentication mode based on conditions
- [ ] Develop API to update and retrieve current environmental status

### 4. Anomaly Detection
- [ ] Set up real-time data streaming for attendance logs
- [ ] Implement anomaly detection algorithm (integrate with AI model)
- [ ] Create endpoint to report and retrieve anomalies
- [ ] Develop notification system for flagged anomalies

### 5. Integration and Interoperability
- [ ] Create webhooks for third-party HRMS integration (Zoho, BambooHR)
- [ ] Implement API endpoints for data export (CSV, JSON)
- [ ] Develop a modular plugin system for easy extensibility

### 6. Offline Support and Sync
- [ ] Implement data caching mechanism for offline operation
- [ ] Create sync algorithm for reconciling offline and online data
- [ ] Develop conflict resolution strategies for data inconsistencies

### 7. Real-time Features
- [ ] Set up WebSocket connections for live updates
- [ ] Implement real-time attendance dashboard data streaming
- [ ] Create API for real-time environmental condition updates

### 8. Performance Optimization
- [ ] Implement database query optimization and indexing
- [ ] Set up caching layer (Redis recommended)
- [ ] Develop batch processing for large data operations

### 9. Testing and Documentation
- [ ] Write unit tests for all core functionalities
- [ ] Implement integration tests for API endpoints
- [ ] Create API documentation using Swagger/OpenAPI
- [ ] Develop comprehensive README and setup instructions

### 10. Deployment and DevOps (Coordinate with Akhil)
- [ ] Prepare Dockerfile for backend service
- [ ] Create docker-compose file for local development
- [ ] Set up CI/CD pipeline configuration
- [ ] Implement health check and monitoring endpoints

### 11. AI Model Integration (Coordinate with Harshan)
- [ ] Create API endpoints for AI model updates
- [ ] Implement model versioning and rollback functionality
- [ ] Develop a system for periodic model retraining with new data

### 12. Simulation Data Handling (Coordinate with Thiru)
- [ ] Create endpoints to receive and store simulation data
- [ ] Implement API for retrieving and analyzing simulation results
- [ ] Develop system to use simulation data for system improvements


# make api endpoint which takes rtsp stream and send backs the same stream with bounding boxes and hls
