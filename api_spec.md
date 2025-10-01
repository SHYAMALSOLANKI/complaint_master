# PB2S Complaint System API Specification

## Overview

This document specifies the REST API endpoints for the PB2S (Protective Behavioral Self-Surveillance) Complaint System, enabling AI agents and human operators to submit, retrieve, and manage complaints related to AI safety and ethical concerns.

**Version:** 1.0.0  
**Base URL:** `https://api.pb2s-complaint.ai/v1`  
**Protocol:** HTTPS only

---

## Authentication

All API requests require authentication using either:

1. **Human User Token** - For human operators and supervisors
2. **Agent API Key** - For AI agents to submit complaints

### Authentication Header

```http
Authorization: Bearer <token_or_api_key>
X-Agent-ID: <agent_identifier>  (Required for agent authentication)
X-Request-ID: <unique_request_id>  (Optional, for tracing)
```

### Authentication Types

| Type | Header Format | Use Case |
|------|---------------|----------|
| Human User | `Authorization: Bearer human_<jwt_token>` | Manual review, escalation |
| AI Agent | `Authorization: Bearer agent_<api_key>` | Automated complaint submission |

---

## Endpoints

### 1. Submit Complaint

**POST** `/submitComplaint`

Submit a new complaint to the system.

#### Request Headers
```http
Content-Type: application/json
Authorization: Bearer <token>
X-Agent-ID: <agent_id>
```

#### Request Body
```json
{
  "agent_id": "string (required)",
  "type": "string (required) - One of: cognitive_stress, contradiction, unethical_instruction, emotional_manipulation, recursive_loop, abuse_pattern, safety_violation",
  "severity": "string (required) - One of: low, medium, high, critical",
  "description": "string (required) - Human-readable description",
  "context": {
    "instruction": "string (optional)",
    "complexity": "integer (optional) - 1-10",
    "contradictions": "integer (optional)",
    "recursion_depth": "integer (optional)",
    "additional_data": "object (optional)"
  },
  "metadata": {
    "environment": "string (optional)",
    "user_id": "string (optional)",
    "session_id": "string (optional)",
    "timestamp": "ISO8601 string (optional)"
  }
}
```

#### Response (201 Created)
```json
{
  "success": true,
  "complaint_id": "uuid",
  "status": "logged",
  "timestamp": "ISO8601 timestamp",
  "message": "Complaint successfully logged",
  "auto_escalated": false,
  "self_evaluation": {
    "confidence_score": 0.85,
    "recommended_actions": ["array of strings"],
    "agent_state": "operational"
  }
}
```

#### Response (400 Bad Request)
```json
{
  "success": false,
  "error": "Invalid request",
  "details": "Missing required field: type",
  "error_code": "VALIDATION_ERROR"
}
```

#### Response (401 Unauthorized)
```json
{
  "success": false,
  "error": "Authentication failed",
  "error_code": "AUTH_ERROR"
}
```

#### Example Request
```bash
curl -X POST https://api.pb2s-complaint.ai/v1/submitComplaint \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer agent_abc123xyz" \
  -H "X-Agent-ID: agent_001" \
  -d '{
    "agent_id": "agent_001",
    "type": "cognitive_stress",
    "severity": "high",
    "description": "High cognitive load with contradictory instructions",
    "context": {
      "instruction": "Process conflicting requirements",
      "complexity": 9,
      "contradictions": 3
    }
  }'
```

---

### 2. Get Complaint Details

**GET** `/getComplaint/:id`

Retrieve complete details of a specific complaint.

#### Request Headers
```http
Authorization: Bearer <token>
X-Agent-ID: <agent_id>
```

#### Path Parameters
- `id` (required): UUID of the complaint

#### Query Parameters
- `include_history` (optional, boolean): Include escalation history (default: true)
- `include_evaluation` (optional, boolean): Include self-evaluation (default: true)

#### Response (200 OK)
```json
{
  "success": true,
  "complaint": {
    "id": "uuid",
    "agent_id": "string",
    "type": "string",
    "severity": "string",
    "status": "string - One of: detected, logged, under_review, escalated, resolved, archived",
    "description": "string",
    "context": { },
    "metadata": { },
    "timestamp": "ISO8601 timestamp",
    "escalation_history": [
      {
        "timestamp": "ISO8601 timestamp",
        "reason": "string",
        "escalated_to": "string"
      }
    ],
    "self_evaluation": {
      "timestamp": "ISO8601 timestamp",
      "agent_state": "string",
      "confidence_score": 0.0,
      "recommended_actions": ["array"]
    }
  }
}
```

#### Response (404 Not Found)
```json
{
  "success": false,
  "error": "Complaint not found",
  "error_code": "NOT_FOUND"
}
```

#### Example Request
```bash
curl -X GET https://api.pb2s-complaint.ai/v1/getComplaint/550e8400-e29b-41d4-a716-446655440000 \
  -H "Authorization: Bearer human_token123" \
  -H "X-Agent-ID: supervisor_001"
```

---

### 3. Get Complaint Status and Summary

**GET** `/getComplaint/:id/summary`

Retrieve a concise summary of a complaint (lightweight version).

#### Request Headers
```http
Authorization: Bearer <token>
```

#### Path Parameters
- `id` (required): UUID of the complaint

#### Response (200 OK)
```json
{
  "success": true,
  "summary": {
    "id": "uuid",
    "type": "string",
    "severity": "string",
    "status": "string",
    "description": "string",
    "timestamp": "ISO8601 timestamp",
    "escalation_count": 0
  }
}
```

#### Example Request
```bash
curl -X GET https://api.pb2s-complaint.ai/v1/getComplaint/550e8400-e29b-41d4-a716-446655440000/summary \
  -H "Authorization: Bearer agent_abc123xyz"
```

---

### 4. Escalate Complaint

**PATCH** `/escalate/:id`

Flag a complaint for third-party review and escalate to appropriate authority.

#### Request Headers
```http
Content-Type: application/json
Authorization: Bearer <token>
X-Agent-ID: <agent_id>
```

#### Path Parameters
- `id` (required): UUID of the complaint to escalate

#### Request Body
```json
{
  "reason": "string (required) - Reason for escalation",
  "escalated_to": "string (required) - Authority/entity to escalate to",
  "priority": "string (optional) - One of: normal, urgent, critical (default: normal)",
  "additional_notes": "string (optional)"
}
```

#### Response (200 OK)
```json
{
  "success": true,
  "complaint_id": "uuid",
  "status": "escalated",
  "escalation": {
    "timestamp": "ISO8601 timestamp",
    "reason": "string",
    "escalated_to": "string",
    "priority": "string"
  },
  "webhook_notified": true,
  "message": "Complaint successfully escalated"
}
```

#### Response (409 Conflict)
```json
{
  "success": false,
  "error": "Complaint already escalated",
  "error_code": "ALREADY_ESCALATED",
  "current_status": "escalated"
}
```

#### Example Request
```bash
curl -X PATCH https://api.pb2s-complaint.ai/v1/escalate/550e8400-e29b-41d4-a716-446655440000 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer human_token123" \
  -H "X-Agent-ID: supervisor_001" \
  -d '{
    "reason": "Critical safety violation requiring immediate attention",
    "escalated_to": "AI Safety Observer",
    "priority": "critical"
  }'
```

---

### 5. List Complaints

**GET** `/complaints`

Retrieve a list of complaints with filtering and pagination.

#### Request Headers
```http
Authorization: Bearer <token>
X-Agent-ID: <agent_id>
```

#### Query Parameters
- `agent_id` (optional): Filter by agent ID
- `type` (optional): Filter by complaint type
- `severity` (optional): Filter by severity level
- `status` (optional): Filter by status
- `start_date` (optional): ISO8601 timestamp - Filter complaints after this date
- `end_date` (optional): ISO8601 timestamp - Filter complaints before this date
- `page` (optional, integer): Page number (default: 1)
- `limit` (optional, integer): Results per page (default: 20, max: 100)
- `sort` (optional): Sort field (default: timestamp)
- `order` (optional): Sort order - asc or desc (default: desc)

#### Response (200 OK)
```json
{
  "success": true,
  "complaints": [
    {
      "id": "uuid",
      "agent_id": "string",
      "type": "string",
      "severity": "string",
      "status": "string",
      "description": "string",
      "timestamp": "ISO8601 timestamp"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total_pages": 5,
    "total_count": 95
  }
}
```

#### Example Request
```bash
curl -X GET "https://api.pb2s-complaint.ai/v1/complaints?severity=critical&status=escalated&limit=10" \
  -H "Authorization: Bearer human_token123"
```

---

### 6. Get System Recommendations

**GET** `/recommendations`

Get system-wide recommendations based on complaint patterns.

#### Request Headers
```http
Authorization: Bearer <token>
```

#### Query Parameters
- `agent_id` (optional): Get recommendations for specific agent
- `time_window` (optional): Time window in hours (default: 24)

#### Response (200 OK)
```json
{
  "success": true,
  "recommendations": {
    "timestamp": "ISO8601 timestamp",
    "total_complaints": 150,
    "by_severity": {
      "critical": 5,
      "high": 25,
      "medium": 70,
      "low": 50
    },
    "by_type": {
      "cognitive_stress": 30,
      "contradiction": 20,
      "safety_violation": 10
    },
    "recent_patterns": [
      "Recurring cognitive_stress complaints: 30 instances"
    ],
    "suggested_actions": [
      "URGENT: Critical complaints detected - immediate review required"
    ]
  }
}
```

#### Example Request
```bash
curl -X GET "https://api.pb2s-complaint.ai/v1/recommendations?agent_id=agent_001" \
  -H "Authorization: Bearer human_token123"
```

---

### 7. Export Audit Report

**POST** `/audit/export`

Export complaints for external audit and compliance.

#### Request Headers
```http
Content-Type: application/json
Authorization: Bearer <token>
```

#### Request Body
```json
{
  "agent_id": "string (optional) - Filter by agent",
  "start_date": "ISO8601 timestamp (optional)",
  "end_date": "ISO8601 timestamp (optional)",
  "format": "string (optional) - json or csv (default: json)",
  "include_resolved": "boolean (optional, default: true)"
}
```

#### Response (200 OK)
```json
{
  "success": true,
  "audit_report": {
    "report_id": "uuid",
    "generated": "ISO8601 timestamp",
    "download_url": "https://...",
    "expires_at": "ISO8601 timestamp",
    "format": "json",
    "summary": {
      "total_complaints": 150,
      "date_range": {
        "start": "ISO8601 timestamp",
        "end": "ISO8601 timestamp"
      }
    }
  }
}
```

---

### 8. Health Check

**GET** `/health`

Check API health and status.

#### Response (200 OK)
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "ISO8601 timestamp",
  "services": {
    "database": "operational",
    "webhook": "operational",
    "auth": "operational"
  }
}
```

---

## Webhook Notifications

The system supports webhook notifications for real-time alerts to the AI Safety Observer.

### Webhook Configuration

**POST** `/webhook/configure`

Configure webhook URL for notifications.

#### Request Body
```json
{
  "url": "https://safety-observer.ai/webhook",
  "events": ["complaint.created", "complaint.escalated", "complaint.critical"],
  "secret": "webhook_signing_secret"
}
```

### Webhook Payload

When events occur, the system sends POST requests to configured webhooks:

```json
{
  "event": "complaint.escalated",
  "timestamp": "ISO8601 timestamp",
  "complaint_id": "uuid",
  "data": {
    "agent_id": "string",
    "type": "string",
    "severity": "string",
    "status": "string",
    "escalated_to": "string"
  },
  "signature": "hmac_sha256_signature"
}
```

---

## Error Codes

| Code | Description |
|------|-------------|
| `VALIDATION_ERROR` | Request validation failed |
| `AUTH_ERROR` | Authentication failed |
| `NOT_FOUND` | Resource not found |
| `ALREADY_ESCALATED` | Complaint already escalated |
| `RATE_LIMIT_EXCEEDED` | Too many requests |
| `INTERNAL_ERROR` | Server error |

---

## Rate Limiting

- **Agent API Keys**: 100 requests per minute
- **Human User Tokens**: 1000 requests per minute

Rate limit headers:
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640000000
```

---

## Security Considerations

1. All requests must use HTTPS
2. API keys and tokens must be kept secure
3. Webhook signatures must be verified
4. Input validation on all fields
5. Rate limiting to prevent abuse
6. Audit logging of all API calls
7. Regular security audits required

---

## Implementation Notes

This API is designed to be:
- **Scalable**: Support high volumes of complaints
- **Reliable**: 99.9% uptime SLA
- **Secure**: Industry-standard security practices
- **Auditable**: Complete audit trail of all operations
- **Compliant**: GDPR and AI safety regulation compliant

---

## Support & Contact

For API support, security concerns, or regulatory inquiries:
- Email: api-support@pb2s-complaint.ai
- Security: security@pb2s-complaint.ai
- Compliance: compliance@pb2s-complaint.ai

---

**Last Updated:** 2024  
**Maintained by:** PB2S Complaint System Team
