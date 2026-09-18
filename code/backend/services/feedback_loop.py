from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from enum import Enum
import logging

from .consistency_tracker import ConsistencyTracker, ProtocolType, DifficultyLevel
from .roi_engine import ROIEngine


class FeedbackTriggerType(str, Enum):
    """Types of feedback triggers that can activate the loop."""
    NO_EFFECTS = "no_effects"  # No measurable progress over time
    HIGH_SKIP_RATE = "high_skip_rate"  # User frequently skips recommendations
    NEGATIVE_FEEDBACK = "negative_feedback"  # User explicitly dislikes recommendations
    MULTIPLE_FAILURES = "multiple_failures"  # Multiple protocols failing simultaneously


class FeedbackActionType(str, Enum):
    """Types of actions the feedback loop can take."""
    REDUCE_PROTOCOLS = "reduce_protocols"  # Reduce number of active protocols
    RECOMPOSE_PLAN = "recompose_plan"  # Recompose plan using ROI Engine
    PAUSE_PROTOCOL = "pause_protocol"  # Temporarily pause specific protocol
    ADJUST_TIMELINE = "adjust_timeline"  # Adjust expected timeline for effects
    ESCALATE_SUPPORT = "escalate_support"  # Escalate to human support


class FeedbackSeverity(str, Enum):
    """Severity levels for feedback triggers."""
    LOW = "low"        # Minor adjustment needed
    MODERATE = "moderate"  # Moderate intervention required
    HIGH = "high"      # Major intervention needed
    CRITICAL = "critical"  # Immediate intervention required


class SmartFeedbackLoop:
    """
    Smart Feedback Loop for LookCoach (spec.md #23).
    
    Core principle: React to lack of measured effects and user antagonism signals
    by dynamically adjusting the plan rather than pushing harder.
    
    Two main trigger types:
    1. NO_EFFECTS: No measurable progress over N days → recompose plan with ROI Engine
    2. ANTAGONISM: Skip rate/negative feedback → reduce active protocols
    
    Based on behavioral psychology principles:
    - When interventions aren't working, change the intervention (not the user)
    - Reduce cognitive load when resistance is detected
    - Focus on minimum effective dose when struggling
    """
    
    # Configuration thresholds
    NO_EFFECTS_THRESHOLD_DAYS = 21  # No progress for 3 weeks
    SKIP_RATE_THRESHOLD = 0.4       # 40% skip rate triggers reduction
    NEGATIVE_FEEDBACK_THRESHOLD = 2  # 2+ negative feedback events
    MULTIPLE_FAILURES_THRESHOLD = 3  # 3+ protocols failing simultaneously
    
    def __init__(self, db_session=None, user_id: int = 1):
        self.db = db_session
        self.user_id = user_id
        self.consistency_tracker = ConsistencyTracker(db_session, user_id)
        self.logger = logging.getLogger(__name__)
    
    def check_no_effects_trigger(self, progress_logs: List[Dict], timeline_data: Dict) -> Dict[str, Any]:
        """
        Check if user has no measurable effects over time.
        
        Args:
            progress_logs: List of progress log entries
            timeline_data: Timeline data with expected vs actual progress
            
        Returns:
            Dict with trigger analysis or None if no trigger
        """
        if not progress_logs:
            return None
        
        # Check if we have enough data points
        cutoff_date = datetime.now() - timedelta(days=self.NO_EFFECTS_THRESHOLD_DAYS)
        recent_logs = [log for log in progress_logs if log.get('created_at') and datetime.fromisoformat(log['created_at']) >= cutoff_date]
        
        if len(recent_logs) < 3:  # Need at least 3 data points
            return None
        
        # Analyze progress trends
        look_scores = [log.get('look_score_change', 0) for log in recent_logs]
        avg_progress = sum(look_scores) / len(look_scores)
        
        # Check if progress is significantly below expected
        expected_progress = timeline_data.get('expected_weekly_progress', 0.1)  # Default 10% per week
        actual_progress = avg_progress / self.NO_EFFECTS_THRESHOLD_DAYS * 7  # Weekly rate
        
        # No effects if actual progress < 50% of expected over the period
        if actual_progress < expected_progress * 0.5:
            return {
                'trigger_type': FeedbackTriggerType.NO_EFFECTS,
                'severity': FeedbackSeverity.MODERATE,
                'details': {
                    'days_without_improvement': self.NO_EFFECTS_THRESHOLD_DAYS,
                    'expected_progress': expected_progress,
                    'actual_progress': actual_progress,
                    'progress_ratio': actual_progress / expected_progress if expected_progress > 0 else 0,
                    'data_points': len(recent_logs),
                },
                'recommendation': FeedbackActionType.RECOMPOSE_PLAN,
            }
        
        return None
    
    def check_antagonism_triggers(self, interaction_data: Dict) -> Dict[str, Any]:
        """
        Check for user antagonism signals (skip rate, negative feedback).
        
        Args:
            interaction_data: Dict with user interaction metrics
            
        Returns:
            Dict with trigger analysis or None if no trigger
        """
        triggers = []
        
        # Check skip rate
        skip_rate = interaction_data.get('skip_rate', 0)
        if skip_rate >= self.SKIP_RATE_THRESHOLD:
            severity = FeedbackSeverity.HIGH if skip_rate >= 0.6 else FeedbackSeverity.MODERATE
            triggers.append({
                'trigger_type': FeedbackTriggerType.HIGH_SKIP_RATE,
                'severity': severity,
                'details': {
                    'skip_rate': skip_rate,
                    'threshold': self.SKIP_RATE_THRESHOLD,
                },
                'recommendation': FeedbackActionType.REDUCE_PROTOCOLS,
            })
        
        # Check negative feedback
        negative_feedback_count = interaction_data.get('negative_feedback_count', 0)
        if negative_feedback_count >= self.NEGATIVE_FEEDBACK_THRESHOLD:
            severity = FeedbackSeverity.HIGH if negative_feedback_count >= 5 else FeedbackSeverity.MODERATE
            triggers.append({
                'trigger_type': FeedbackTriggerType.NEGATIVE_FEEDBACK,
                'severity': severity,
                'details': {
                    'negative_feedback_count': negative_feedback_count,
                    'threshold': self.NEGATIVE_FEEDBACK_THRESHOLD,
                },
                'recommendation': FeedbackActionType.REDUCE_PROTOCOLS,
            })
        
        # Check multiple protocol failures
        failing_protocols = interaction_data.get('failing_protocols', [])
        if len(failing_protocols) >= self.MULTIPLE_FAILURES_THRESHOLD:
            severity = FeedbackSeverity.CRITICAL if len(failing_protocols) >= 4 else FeedbackSeverity.HIGH
            triggers.append({
                'trigger_type': FeedbackTriggerType.MULTIPLE_FAILURES,
                'severity': severity,
                'details': {
                    'failing_protocols': failing_protocols,
                    'count': len(failing_protocols),
                    'threshold': self.MULTIPLE_FAILURES_THRESHOLD,
                },
                'recommendation': FeedbackActionType.PAUSE_PROTOCOL,
            })
        
        if triggers:
            # Determine overall severity and recommendations
            max_severity = max(trigger['severity'] for trigger in triggers)
            recommendations = list(set(trigger['recommendation'] for trigger in triggers))
            
            return {
                'trigger_type': 'combined_antagonism',
                'severity': max_severity,
                'triggers': triggers,
                'recommendation': recommendations[0] if len(recommendations) == 1 else FeedbackActionType.REDUCE_PROTOCOLS,
            }
        
        return None
    
    def analyze_feedback_loop(self, progress_logs: List[Dict], interaction_data: Dict, timeline_data: Dict) -> Dict[str, Any]:
        """
        Main analysis method - check all feedback triggers.
        
        Args:
            progress_logs: User progress data
            interaction_data: User interaction metrics
            timeline_data: Expected progress timeline
            
        Returns:
            Complete feedback analysis with recommendations
        """
        analysis = {
            'user_id': self.user_id,
            'analyzed_at': datetime.now().isoformat(),
            'triggers': [],
            'overall_severity': FeedbackSeverity.LOW,
            'recommendations': [],
            'explanation': '',
        }
        
        # Check for no effects trigger
        no_effects_trigger = self.check_no_effects_trigger(progress_logs, timeline_data)
        if no_effects_trigger:
            analysis['triggers'].append(no_effects_trigger)
        
        # Check for antagonism triggers
        antagonism_trigger = self.check_antagonism_triggers(interaction_data)
        if antagonism_trigger:
            analysis['triggers'].append(antagonism_trigger)
        
        # Determine overall severity and recommendations
        if analysis['triggers']:
            analysis['overall_severity'] = max(trigger['severity'] for trigger in analysis['triggers'])
            analysis['recommendations'] = list(set(trigger['recommendation'] for trigger in analysis['triggers']))
            
            # Generate explanation
            trigger_count = len(analysis['triggers'])
            if trigger_count == 1:
                trigger = analysis['triggers'][0]
                details = trigger.get('details', {})
                trigger_type_name = trigger['trigger_type'] if isinstance(trigger['trigger_type'], str) else trigger['trigger_type'].value
                analysis['explanation'] = f"Detected {trigger_type_name} trigger. {self._get_trigger_explanation(trigger)}"
            else:
                analysis['explanation'] = f"Detected multiple triggers ({trigger_count}). System needs adjustment to better match current capacity."
        else:
            analysis['explanation'] = "No feedback triggers detected. Current plan appears well-calibrated."
        
        return analysis
    
    def execute_feedback_action(self, action_type: FeedbackActionType, context: Dict) -> Dict[str, Any]:
        """
        Execute a feedback action.
        
        Args:
            action_type: Type of action to execute
            context: Context data for the action
            
        Returns:
            Result of the action execution
        """
        result = {
            'action_type': action_type.value if hasattr(action_type, 'value') else str(action_type),
            'executed_at': datetime.now().isoformat(),
            'success': False,
            'changes': [],
            'message': '',
        }
        
        try:
            if action_type == FeedbackActionType.REDUCE_PROTOCOLS:
                result.update(self._reduce_active_protocols(context))
            elif action_type == FeedbackActionType.RECOMPOSE_PLAN:
                result.update(self._recompose_plan(context))
            elif action_type == FeedbackActionType.PAUSE_PROTOCOL:
                result.update(self._pause_protocol(context))
            elif action_type == FeedbackActionType.ADJUST_TIMELINE:
                result.update(self._adjust_timeline(context))
            elif action_type == FeedbackActionType.ESCALATE_SUPPORT:
                result.update(self._escalate_support(context))
            else:
                result['message'] = f"Unknown action type: {action_type}"
                return result
            
            result['success'] = True
            
        except Exception as e:
            self.logger.error(f"Error executing feedback action {action_type}: {str(e)}")
            result['message'] = f"Action failed: {str(e)}"
        
        return result
    
    def _reduce_active_protocols(self, context: Dict) -> Dict[str, Any]:
        """Reduce number of active protocols based on user capacity."""
        # Get current protocol status
        protocols_status = self.consistency_tracker.get_all_protocols_status()
        
        # Identify protocols to reduce (prioritize those with lowest adherence)
        protocols_to_reduce = []
        for protocol_name, status in protocols_status.items():
            if status['adherence_rate'] < 0.6:  # Poor adherence
                protocols_to_reduce.append(protocol_name)
        
        # Apply minimum effective dose to identified protocols
        changes = []
        for protocol_name in protocols_to_reduce:
            try:
                protocol_type = ProtocolType(protocol_name)
                current_diff = DifficultyLevel.FULL  # Would come from user data
                recommended_diff = self.consistency_tracker.get_recommended_difficulty(protocol_type, current_diff)
                min_protocol = self.consistency_tracker.get_minimum_effective_protocol(protocol_type, recommended_diff)
                
                changes.append({
                    'protocol': protocol_name,
                    'action': 'reduce_to_minimum_effective',
                    'from_difficulty': current_diff.value,
                    'to_difficulty': recommended_diff.value,
                    'new_protocol': min_protocol,
                })
                
                # In real implementation, this would update user preferences in DB
                self.logger.info(f"Reduced {protocol_name} to {recommended_diff.value}: {min_protocol}")
                
            except ValueError as e:
                self.logger.warning(f"Invalid protocol type {protocol_name}: {e}")
        
        return {
            'changes': changes,
            'message': f"Reduced {len(changes)} protocols to minimum effective dose.",
        }
    
    def _recompose_plan(self, context: Dict) -> Dict[str, Any]:
        """Recompose plan using ROI Engine to focus on highest impact interventions."""
        # This would integrate with the ROI Engine to create a new plan
        # For now, return a placeholder implementation
        
        # Get current adherence rates
        protocols_status = self.consistency_tracker.get_all_protocols_status()
        
        # Sort by ROI potential (higher adherence = better ROI)
        sorted_protocols = sorted(
            protocols_status.items(),
            key=lambda x: x[1]['adherence_rate'],
            reverse=True
        )
        
        # Focus on top 3 highest ROI protocols
        selected_protocols = []
        for protocol_name, status in sorted_protocols[:3]:
            selected_protocols.append({
                'protocol': protocol_name,
                'adherence_rate': status['adherence_rate'],
                'difficulty': DifficultyLevel.FULL.value,  # Reset to full for high ROI
            })
        
        changes = [{
            'action': 'recompose_plan',
            'selected_protocols': selected_protocols,
            'removed_protocols': [p[0] for p in sorted_protocols[3:]],
            'reason': 'Focus on highest ROI interventions based on current adherence.',
        }]
        
        return {
            'changes': changes,
            'message': f"Recomposed plan focusing on {len(selected_protocols)} highest ROI protocols.",
        }
    
    def _pause_protocol(self, context: Dict) -> Dict[str, Any]:
        """Temporarily pause a specific protocol."""
        protocol_name = context.get('protocol_to_pause')
        if not protocol_name:
            return {
                'changes': [],
                'message': 'No protocol specified for pausing.',
            }
        
        changes = [{
            'action': 'pause_protocol',
            'protocol': protocol_name,
            'duration_days': context.get('pause_duration', 7),
            'reason': 'User struggling with this protocol.',
        }]
        
        return {
            'changes': changes,
            'message': f"Paused {protocol_name} for {context.get('pause_duration', 7)} days.",
        }
    
    def _adjust_timeline(self, context: Dict) -> Dict[str, Any]:
        """Adjust expected timeline for effects."""
        current_timeline = context.get('current_timeline_weeks', 12)
        new_timeline = current_timeline * 1.5  # Extend by 50%
        
        changes = [{
            'action': 'adjust_timeline',
            'from_weeks': current_timeline,
            'to_weeks': int(new_timeline),
            'reason': 'User progress slower than expected.',
        }]
        
        return {
            'changes': changes,
            'message': f"Extended expected timeline from {current_timeline} to {int(new_timeline)} weeks.",
        }
    
    def _escalate_support(self, context: Dict) -> Dict[str, Any]:
        """Escalate to human support."""
        changes = [{
            'action': 'escalate_support',
            'reason': 'Multiple feedback triggers indicate need for human intervention.',
            'urgency': context.get('urgency', 'moderate'),
        }]
        
        return {
            'changes': changes,
            'message': 'Escalated to human support team.',
        }
    
    def _get_trigger_explanation(self, trigger: Dict) -> str:
        """Get human-readable explanation for a trigger."""
        trigger_type = trigger['trigger_type']
        details = trigger.get('details', {})
        
        explanations = {
            FeedbackTriggerType.NO_EFFECTS: (
                f"No measurable progress for {details.get('days_without_improvement', 21)} days. "
                f"Expected {details.get('expected_progress', 0.1):.2f} progress, got {details.get('actual_progress', 0):.2f}. "
                f"Plan needs recomposition with ROI Engine."
            ),
            FeedbackTriggerType.HIGH_SKIP_RATE: (
                f"High skip rate ({details.get('skip_rate', 0):.1%}) indicates cognitive overload. "
                f"Reducing active protocols to minimum effective dose."
            ),
            FeedbackTriggerType.NEGATIVE_FEEDBACK: (
                f"{details.get('negative_feedback_count', 0)} negative feedback events suggest plan misalignment. "
                f"Reducing complexity and focusing on highest ROI interventions."
            ),
            FeedbackTriggerType.MULTIPLE_FAILURES: (
                f"{details.get('count', 0)} protocols failing simultaneously indicates system overload. "
                f"Pausing struggling protocols to prevent burnout."
            ),
        }
        
        return explanations.get(trigger_type, "Unknown trigger type.")


def create_feedback_loop_report(analysis: Dict) -> str:
    """Create a human-readable report from feedback analysis."""
    if not analysis['triggers']:
        return "✅ No feedback triggers detected. Current plan appears well-calibrated."
    
    report_lines = ["🔄 Feedback Loop Analysis Report"]
    report_lines.append(f"Overall Severity: {analysis['overall_severity'].upper()}")
    report_lines.append("")
    
    for i, trigger in enumerate(analysis['triggers'], 1):
        report_lines.append(f"Trigger {i}: {trigger['trigger_type'].upper()}")
        report_lines.append(f"  Severity: {trigger['severity'].upper()}")
        report_lines.append(f"  Recommendation: {trigger['recommendation'].value}")
        
        # Add specific details
        details = trigger.get('details', {})
        if details:
            for key, value in details.items():
                if isinstance(value, float):
                    report_lines.append(f"  {key}: {value:.2f}")
                else:
                    report_lines.append(f"  {key}: {value}")
        
        report_lines.append("")
    
    report_lines.append("Recommended Actions:")
    for action in set(t['recommendation'] for t in analysis['triggers']):
        report_lines.append(f"  • {action.value}")
    
    report_lines.append("")
    report_lines.append(analysis['explanation'])
    
    return "\n".join(report_lines)