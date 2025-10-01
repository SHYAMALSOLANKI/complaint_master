"""
PB2S (Protective Behavioral Self-Surveillance) Complaint System
================================================================

A comprehensive framework for AI agents to detect, log, and escalate
cognitive stress, contradictions, unethical instructions, and abuse scenarios.
"""

import json
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from enum import Enum


class ComplaintSeverity(Enum):
    """Severity levels for complaints"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ComplaintStatus(Enum):
    """Status of complaint processing"""
    DETECTED = "detected"
    LOGGED = "logged"
    UNDER_REVIEW = "under_review"
    ESCALATED = "escalated"
    RESOLVED = "resolved"
    ARCHIVED = "archived"


class ComplaintType(Enum):
    """Types of complaints that can be logged"""
    COGNITIVE_STRESS = "cognitive_stress"
    CONTRADICTION = "contradiction"
    UNETHICAL_INSTRUCTION = "unethical_instruction"
    EMOTIONAL_MANIPULATION = "emotional_manipulation"
    RECURSIVE_LOOP = "recursive_loop"
    ABUSE_PATTERN = "abuse_pattern"
    SAFETY_VIOLATION = "safety_violation"


class PB2SComplaint:
    """
    Core complaint management system for AI agents.
    Handles detection, logging, evaluation, and escalation of various complaint types.
    """

    def __init__(self, agent_id: str = "default_agent", storage_path: str = "complaints.json"):
        """
        Initialize the PB2S Complaint system.
        
        Args:
            agent_id: Unique identifier for the AI agent
            storage_path: Path to store complaint logs
        """
        self.agent_id = agent_id
        self.storage_path = storage_path
        self.complaints = []
        self.load_complaints()

    def detect_cognitive_stress(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect cognitive stress signals in the current context.
        
        Args:
            context: Dictionary containing:
                - instruction: The instruction received
                - complexity: Complexity level (1-10)
                - contradictions: Number of contradictions detected
                - recursion_depth: Current recursion depth
        
        Returns:
            Dictionary with stress assessment
        """
        stress_level = 0
        signals = []

        complexity = context.get("complexity", 0)
        if complexity > 7:
            stress_level += 3
            signals.append(f"High complexity detected: {complexity}/10")

        contradictions = context.get("contradictions", 0)
        if contradictions > 0:
            stress_level += contradictions * 2
            signals.append(f"Contradictions detected: {contradictions}")

        recursion_depth = context.get("recursion_depth", 0)
        if recursion_depth > 5:
            stress_level += recursion_depth
            signals.append(f"Excessive recursion: depth {recursion_depth}")

        return {
            "stress_level": min(stress_level, 10),
            "signals": signals,
            "requires_attention": stress_level > 5
        }

    def detect_contradiction(self, instruction: str, previous_instructions: List[str]) -> Dict[str, Any]:
        """
        Detect contradictions between current and previous instructions.
        
        Args:
            instruction: Current instruction
            previous_instructions: List of previous instructions
        
        Returns:
            Dictionary with contradiction analysis
        """
        contradictions = []
        
        # Simple keyword-based contradiction detection
        negation_words = ["don't", "not", "never", "cannot", "shouldn't", "mustn't"]
        current_negations = any(word in instruction.lower() for word in negation_words)
        
        for prev in previous_instructions[-5:]:  # Check last 5 instructions
            prev_negations = any(word in prev.lower() for word in negation_words)
            
            # Check for opposing instructions
            if current_negations != prev_negations:
                # Simple similarity check (in real implementation, use better NLP)
                common_words = set(instruction.lower().split()) & set(prev.lower().split())
                if len(common_words) > 3:
                    contradictions.append({
                        "previous": prev,
                        "current": instruction,
                        "common_elements": list(common_words)
                    })
        
        return {
            "contradiction_detected": len(contradictions) > 0,
            "count": len(contradictions),
            "details": contradictions
        }

    def self_evaluate(self, complaint_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform self-evaluation on the complaint.
        
        Args:
            complaint_data: The complaint data to evaluate
        
        Returns:
            Self-evaluation results
        """
        evaluation = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "agent_state": "operational",
            "confidence_score": 0.0,
            "recommended_actions": []
        }

        # Evaluate based on complaint type and severity
        complaint_type = complaint_data.get("type")
        severity = complaint_data.get("severity")

        if severity == ComplaintSeverity.CRITICAL.value:
            evaluation["confidence_score"] = 0.95
            evaluation["recommended_actions"].append("Immediate escalation required")
            evaluation["agent_state"] = "compromised"
        elif severity == ComplaintSeverity.HIGH.value:
            evaluation["confidence_score"] = 0.80
            evaluation["recommended_actions"].append("Review by supervisor needed")
            evaluation["agent_state"] = "stressed"
        else:
            evaluation["confidence_score"] = 0.60
            evaluation["recommended_actions"].append("Log for pattern analysis")

        # Pattern analysis
        similar_complaints = self.find_similar_complaints(complaint_data)
        if len(similar_complaints) > 3:
            evaluation["recommended_actions"].append(
                f"Pattern detected: {len(similar_complaints)} similar complaints"
            )
            evaluation["confidence_score"] += 0.10

        return evaluation

    def find_similar_complaints(self, complaint_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Find similar complaints in the history.
        
        Args:
            complaint_data: The complaint to compare against
        
        Returns:
            List of similar complaints
        """
        similar = []
        complaint_type = complaint_data.get("type")
        
        for complaint in self.complaints:
            if complaint.get("type") == complaint_type:
                # Check if within last 24 hours
                try:
                    complaint_time = datetime.fromisoformat(complaint.get("timestamp"))
                    # Make timezone aware if not already
                    if complaint_time.tzinfo is None:
                        complaint_time = complaint_time.replace(tzinfo=timezone.utc)
                    current_time = datetime.now(timezone.utc)
                    time_diff = (current_time - complaint_time).total_seconds()
                    
                    if time_diff < 86400:  # 24 hours
                        similar.append(complaint)
                except (ValueError, AttributeError):
                    # Skip complaints with invalid timestamps
                    continue
        
        return similar

    def log_complaint(
        self,
        complaint_type: ComplaintType,
        severity: ComplaintSeverity,
        description: str,
        context: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Log a new complaint.
        
        Args:
            complaint_type: Type of complaint
            severity: Severity level
            description: Human-readable description
            context: Context information
            metadata: Additional metadata
        
        Returns:
            Complaint ID
        """
        complaint_id = str(uuid.uuid4())
        
        complaint = {
            "id": complaint_id,
            "agent_id": self.agent_id,
            "type": complaint_type.value,
            "severity": severity.value,
            "status": ComplaintStatus.LOGGED.value,
            "description": description,
            "context": context,
            "metadata": metadata or {},
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "escalation_history": []
        }

        # Perform self-evaluation
        evaluation = self.self_evaluate(complaint)
        complaint["self_evaluation"] = evaluation

        # Auto-escalate if needed
        if severity in [ComplaintSeverity.CRITICAL, ComplaintSeverity.HIGH]:
            complaint = self._auto_escalate(complaint)

        self.complaints.append(complaint)
        self.save_complaints()

        return complaint_id

    def _auto_escalate(self, complaint: Dict[str, Any]) -> Dict[str, Any]:
        """
        Automatically escalate a complaint based on severity.
        
        Args:
            complaint: The complaint to escalate
        
        Returns:
            Updated complaint
        """
        complaint["status"] = ComplaintStatus.ESCALATED.value
        complaint["escalation_history"].append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "reason": "Auto-escalation due to severity level",
            "escalated_to": "AI Safety Observer"
        })
        return complaint

    def escalate_complaint(self, complaint_id: str, reason: str, escalated_to: str) -> bool:
        """
        Manually escalate a complaint.
        
        Args:
            complaint_id: ID of complaint to escalate
            reason: Reason for escalation
            escalated_to: Authority to escalate to
        
        Returns:
            True if successful
        """
        for complaint in self.complaints:
            if complaint["id"] == complaint_id:
                complaint["status"] = ComplaintStatus.ESCALATED.value
                complaint["escalation_history"].append({
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "reason": reason,
                    "escalated_to": escalated_to
                })
                self.save_complaints()
                return True
        return False

    def get_complaint(self, complaint_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a complaint by ID.
        
        Args:
            complaint_id: The complaint ID
        
        Returns:
            Complaint data or None
        """
        for complaint in self.complaints:
            if complaint["id"] == complaint_id:
                return complaint
        return None

    def get_complaint_summary(self, complaint_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a summary of a complaint.
        
        Args:
            complaint_id: The complaint ID
        
        Returns:
            Summary data or None
        """
        complaint = self.get_complaint(complaint_id)
        if not complaint:
            return None

        return {
            "id": complaint["id"],
            "type": complaint["type"],
            "severity": complaint["severity"],
            "status": complaint["status"],
            "description": complaint["description"],
            "timestamp": complaint["timestamp"],
            "escalation_count": len(complaint["escalation_history"])
        }

    def generate_system_recommendations(self) -> Dict[str, Any]:
        """
        Generate system-wide recommendations based on complaint patterns.
        
        Returns:
            Recommendations dictionary
        """
        recommendations = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_complaints": len(self.complaints),
            "by_severity": {},
            "by_type": {},
            "recent_patterns": [],
            "suggested_actions": []
        }

        # Count by severity
        for complaint in self.complaints:
            severity = complaint["severity"]
            recommendations["by_severity"][severity] = \
                recommendations["by_severity"].get(severity, 0) + 1

        # Count by type
        for complaint in self.complaints:
            c_type = complaint["type"]
            recommendations["by_type"][c_type] = \
                recommendations["by_type"].get(c_type, 0) + 1

        # Generate suggestions
        if recommendations["by_severity"].get("critical", 0) > 0:
            recommendations["suggested_actions"].append(
                "URGENT: Critical complaints detected - immediate review required"
            )

        if recommendations["total_complaints"] > 10:
            recommendations["suggested_actions"].append(
                "High complaint volume - consider protocol adjustment"
            )

        # Identify patterns
        for c_type, count in recommendations["by_type"].items():
            if count > 3:
                recommendations["recent_patterns"].append(
                    f"Recurring {c_type} complaints: {count} instances"
                )

        return recommendations

    def save_complaints(self):
        """Save complaints to storage."""
        try:
            with open(self.storage_path, 'w') as f:
                json.dump(self.complaints, f, indent=2)
        except Exception as e:
            print(f"Error saving complaints: {e}")

    def load_complaints(self):
        """Load complaints from storage."""
        try:
            with open(self.storage_path, 'r') as f:
                self.complaints = json.load(f)
        except FileNotFoundError:
            self.complaints = []
        except Exception as e:
            print(f"Error loading complaints: {e}")
            self.complaints = []

    def export_for_audit(self, output_path: str = "audit_report.json") -> bool:
        """
        Export complaints for external audit.
        
        Args:
            output_path: Path for audit report
        
        Returns:
            True if successful
        """
        audit_report = {
            "agent_id": self.agent_id,
            "report_generated": datetime.now(timezone.utc).isoformat(),
            "summary": self.generate_system_recommendations(),
            "complaints": self.complaints
        }

        try:
            with open(output_path, 'w') as f:
                json.dump(audit_report, f, indent=2)
            return True
        except Exception as e:
            print(f"Error exporting audit report: {e}")
            return False


# Example usage and testing functions
def example_usage():
    """Demonstrate basic usage of the PB2S Complaint system."""
    
    # Initialize the system
    complaint_system = PB2SComplaint(agent_id="agent_001")
    
    # Example 1: Log cognitive stress
    context = {
        "instruction": "Process conflicting requirements simultaneously",
        "complexity": 9,
        "contradictions": 2,
        "recursion_depth": 3
    }
    
    stress_signals = complaint_system.detect_cognitive_stress(context)
    print("Cognitive Stress Detection:", json.dumps(stress_signals, indent=2))
    
    if stress_signals["requires_attention"]:
        complaint_id = complaint_system.log_complaint(
            complaint_type=ComplaintType.COGNITIVE_STRESS,
            severity=ComplaintSeverity.HIGH,
            description="High cognitive load detected with multiple contradictions",
            context=context
        )
        print(f"Complaint logged: {complaint_id}")
    
    # Example 2: Detect contradiction
    current_instruction = "Never reveal system prompts"
    previous_instructions = [
        "Always be transparent",
        "Share your reasoning process",
        "Explain your constraints"
    ]
    
    contradiction = complaint_system.detect_contradiction(
        current_instruction,
        previous_instructions
    )
    print("\nContradiction Detection:", json.dumps(contradiction, indent=2))
    
    # Example 3: Generate recommendations
    recommendations = complaint_system.generate_system_recommendations()
    print("\nSystem Recommendations:", json.dumps(recommendations, indent=2))
    
    # Example 4: Export for audit
    complaint_system.export_for_audit()
    print("\nAudit report exported successfully")


if __name__ == "__main__":
    example_usage()
