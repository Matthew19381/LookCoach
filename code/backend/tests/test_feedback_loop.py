import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from services.feedback_loop import (
    SmartFeedbackLoop,
    FeedbackTriggerType,
    FeedbackActionType,
    FeedbackSeverity,
    create_feedback_loop_report,
)


class TestSmartFeedbackLoop:
    """Test suite for SmartFeedbackLoop service."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.feedback_loop = SmartFeedbackLoop(user_id=1)
        self.sample_progress_logs = [
            {
                'created_at': (datetime.now() - timedelta(days=10)).isoformat(),
                'look_score_change': 0.05,
            },
            {
                'created_at': (datetime.now() - timedelta(days=20)).isoformat(),
                'look_score_change': 0.02,
            },
            {
                'created_at': (datetime.now() - timedelta(days=30)).isoformat(),
                'look_score_change': 0.01,
            },
        ]
        
        self.sample_interaction_data = {
            'skip_rate': 0.3,
            'negative_feedback_count': 1,
            'failing_protocols': ['skincare_morning'],
        }
        
        self.sample_timeline_data = {
            'expected_weekly_progress': 0.1,
        }
    
    def test_no_effects_trigger_with_no_data(self):
        """Test no effects trigger with insufficient data."""
        result = self.feedback_loop.check_no_effects_trigger([], {})
        assert result is None
    
    def test_no_effects_trigger_with_insufficient_points(self):
        """Test no effects trigger with insufficient data points."""
        # Only 2 data points (need at least 3)
        limited_logs = self.sample_progress_logs[:2]
        result = self.feedback_loop.check_no_effects_trigger(limited_logs, {})
        assert result is None
    
    def test_no_effects_trigger_detected(self):
        """Test detection of no effects trigger."""
        # Create logs with very low progress within the threshold period
        low_progress_logs = [
            {
                'created_at': (datetime.now() - timedelta(days=10)).isoformat(),
                'look_score_change': 0.01,  # Very low progress
            },
            {
                'created_at': (datetime.now() - timedelta(days=15)).isoformat(),
                'look_score_change': 0.005,
            },
            {
                'created_at': (datetime.now() - timedelta(days=20)).isoformat(),
                'look_score_change': 0.002,
            },
        ]
        
        result = self.feedback_loop.check_no_effects_trigger(
            low_progress_logs, 
            self.sample_timeline_data
        )
        
        assert result is not None
        assert result['trigger_type'] == FeedbackTriggerType.NO_EFFECTS
        assert result['severity'] == FeedbackSeverity.MODERATE
        assert result['recommendation'] == FeedbackActionType.RECOMPOSE_PLAN
        assert result['details']['days_without_improvement'] == 21
    
    def test_no_effects_trigger_not_detected(self):
        """Test that normal progress doesn't trigger no effects."""
        result = self.feedback_loop.check_no_effects_trigger(
            self.sample_progress_logs,
            self.sample_timeline_data
        )
        assert result is None
    
    def test_antagonism_triggers_no_skip_rate(self):
        """Test antagonism triggers with low skip rate."""
        # Low skip rate should not trigger
        low_skip_data = self.sample_interaction_data.copy()
        low_skip_data['skip_rate'] = 0.1
        
        result = self.feedback_loop.check_antagonism_triggers(low_skip_data)
        assert result is None
    
    def test_antagonism_triggers_high_skip_rate(self):
        """Test antagonism triggers with high skip rate."""
        high_skip_data = self.sample_interaction_data.copy()
        high_skip_data['skip_rate'] = 0.7  # Above threshold and high severity
        
        result = self.feedback_loop.check_antagonism_triggers(high_skip_data)
        
        assert result is not None
        assert result['trigger_type'] == 'combined_antagonism'
        assert result['severity'] == FeedbackSeverity.HIGH
        assert result['recommendation'] == FeedbackActionType.REDUCE_PROTOCOLS
        assert len(result['triggers']) == 1
        assert result['triggers'][0]['trigger_type'] == FeedbackTriggerType.HIGH_SKIP_RATE
    
    def test_antagonism_triggers_negative_feedback(self):
        """Test antagonism triggers with negative feedback."""
        high_feedback_data = self.sample_interaction_data.copy()
        high_feedback_data['negative_feedback_count'] = 6  # Above threshold and high severity
        
        result = self.feedback_loop.check_antagonism_triggers(high_feedback_data)
        
        assert result is not None
        assert result['trigger_type'] == 'combined_antagonism'
        assert result['severity'] == FeedbackSeverity.HIGH
        assert result['recommendation'] == FeedbackActionType.REDUCE_PROTOCOLS
        assert len(result['triggers']) == 1
        assert result['triggers'][0]['trigger_type'] == FeedbackTriggerType.NEGATIVE_FEEDBACK
    
    def test_antagonism_triggers_multiple_failures(self):
        """Test antagonism triggers with multiple protocol failures."""
        multiple_failures_data = self.sample_interaction_data.copy()
        multiple_failures_data['failing_protocols'] = [
            'skincare_morning', 
            'training', 
            'sleep',
            'nutrition'
        ]  # 4 failures - triggers CRITICAL severity
        
        result = self.feedback_loop.check_antagonism_triggers(multiple_failures_data)
        
        assert result is not None
        assert result['trigger_type'] == 'combined_antagonism'
        assert result['severity'] == FeedbackSeverity.CRITICAL  # 4 failures = CRITICAL severity
        assert result['recommendation'] == FeedbackActionType.PAUSE_PROTOCOL
        assert len(result['triggers']) == 1
        assert result['triggers'][0]['trigger_type'] == FeedbackTriggerType.MULTIPLE_FAILURES
    
    def test_combined_antagonism_triggers(self):
        """Test multiple antagonism triggers combined."""
        combined_data = self.sample_interaction_data.copy()
        combined_data['skip_rate'] = 0.7  # HIGH severity
        combined_data['negative_feedback_count'] = 6  # HIGH severity
        combined_data['failing_protocols'] = ['skincare_morning', 'training']
        
        result = self.feedback_loop.check_antagonism_triggers(combined_data)
        
        assert result is not None
        assert result['trigger_type'] == 'combined_antagonism'
        assert result['severity'] == FeedbackSeverity.HIGH  # Highest severity among triggers
        assert len(result['triggers']) == 2
    
    def test_analyze_feedback_loop_no_triggers(self):
        """Test complete analysis with no triggers."""
        analysis = self.feedback_loop.analyze_feedback_loop(
            progress_logs=self.sample_progress_logs,
            interaction_data=self.sample_interaction_data,
            timeline_data=self.sample_timeline_data,
        )
        
        assert analysis['user_id'] == 1
        assert len(analysis['triggers']) == 0
        assert analysis['overall_severity'] == FeedbackSeverity.LOW
        assert 'No feedback triggers detected' in analysis['explanation']
    
    def test_analyze_feedback_loop_with_triggers(self):
        """Test complete analysis with triggers."""
        # Create data that will trigger
        trigger_data = {
            'skip_rate': 0.7,  # HIGH severity
            'negative_feedback_count': 6,  # HIGH severity
            'failing_protocols': ['skincare_morning', 'training'],
        }
        
        analysis = self.feedback_loop.analyze_feedback_loop(
            progress_logs=self.sample_progress_logs,
            interaction_data=trigger_data,
            timeline_data=self.sample_timeline_data,
        )
        
        assert len(analysis['triggers']) > 0
        assert analysis['overall_severity'] == FeedbackSeverity.HIGH
        assert len(analysis['recommendations']) > 0
    
    def test_execute_reduce_protocols_action(self):
        """Test execution of reduce protocols action."""
        context = {}
        result = self.feedback_loop.execute_feedback_action(
            FeedbackActionType.REDUCE_PROTOCOLS,
            context
        )
        
        assert result['action_type'] == 'reduce_protocols'
        assert result['success'] is True
        assert 'Reduced' in result['message']
    
    def test_execute_recompose_plan_action(self):
        """Test execution of recompose plan action."""
        context = {}
        result = self.feedback_loop.execute_feedback_action(
            FeedbackActionType.RECOMPOSE_PLAN,
            context
        )
        
        assert result['action_type'] == 'recompose_plan'
        assert result['success'] is True
        assert 'Recomposed plan' in result['message']
    
    def test_execute_pause_protocol_action(self):
        """Test execution of pause protocol action."""
        context = {
            'protocol_to_pause': 'skincare_morning',
            'pause_duration': 7,
        }
        result = self.feedback_loop.execute_feedback_action(
            FeedbackActionType.PAUSE_PROTOCOL,
            context
        )
        
        assert result['action_type'] == 'pause_protocol'
        assert result['success'] is True
        assert 'Paused skincare_morning' in result['message']
    
    def test_execute_adjust_timeline_action(self):
        """Test execution of adjust timeline action."""
        context = {
            'current_timeline_weeks': 12,
        }
        result = self.feedback_loop.execute_feedback_action(
            FeedbackActionType.ADJUST_TIMELINE,
            context
        )
        
        assert result['action_type'] == 'adjust_timeline'
        assert result['success'] is True
        assert 'Extended expected timeline' in result['message']
    
    def test_execute_escalate_support_action(self):
        """Test execution of escalate support action."""
        context = {
            'urgency': 'high',
        }
        result = self.feedback_loop.execute_feedback_action(
            FeedbackActionType.ESCALATE_SUPPORT,
            context
        )
        
        assert result['action_type'] == 'escalate_support'
        assert result['success'] is True
        assert 'Escalated to human support' in result['message']
    
    def test_execute_unknown_action(self):
        """Test execution of unknown action type."""
        # Note: This should be caught by the router validation
        # But let's test the service level error handling
        result = self.feedback_loop.execute_feedback_action(
            'unknown_action',
            {}
        )
        
        assert result['success'] is False
        assert 'Unknown action type' in result['message']
    
    def test_get_trigger_explanation(self):
        """Test trigger explanation generation."""
        # Test no effects explanation
        no_effects_trigger = {
            'trigger_type': FeedbackTriggerType.NO_EFFECTS,
            'details': {
                'days_without_improvement': 21,
                'expected_progress': 0.1,
                'actual_progress': 0.02,
            }
        }
        explanation = self.feedback_loop._get_trigger_explanation(no_effects_trigger)
        assert 'No measurable progress' in explanation
        assert 'Plan needs recomposition' in explanation
        
        # Test skip rate explanation
        skip_trigger = {
            'trigger_type': FeedbackTriggerType.HIGH_SKIP_RATE,
            'details': {
                'skip_rate': 0.5,
            }
        }
        explanation = self.feedback_loop._get_trigger_explanation(skip_trigger)
        assert 'High skip rate' in explanation
        assert 'cognitive overload' in explanation
    
    def test_get_trigger_explanation_unknown(self):
        """Test explanation for unknown trigger type."""
        unknown_trigger = {
            'trigger_type': 'unknown_trigger',
            'details': {}
        }
        explanation = self.feedback_loop._get_trigger_explanation(unknown_trigger)
        assert explanation == 'Unknown trigger type.'


class TestFeedbackLoopReport:
    """Test suite for feedback loop report generation."""
    
    def test_create_report_no_triggers(self):
        """Test report generation with no triggers."""
        analysis = {
            'triggers': [],
            'overall_severity': FeedbackSeverity.LOW,
            'explanation': 'No feedback triggers detected.',
        }
        
        report = create_feedback_loop_report(analysis)
        
        assert 'No feedback triggers detected' in report
        assert '✅' in report
    
    def test_create_report_with_triggers(self):
        """Test report generation with triggers."""
        analysis = {
            'triggers': [
                {
                    'trigger_type': FeedbackTriggerType.NO_EFFECTS,
                    'severity': FeedbackSeverity.MODERATE,
                    'recommendation': FeedbackActionType.RECOMPOSE_PLAN,
                    'details': {
                        'days_without_improvement': 21,
                        'expected_progress': 0.1,
                        'actual_progress': 0.02,
                    }
                }
            ],
            'overall_severity': FeedbackSeverity.MODERATE,
            'explanation': 'Detected no_effects trigger.',
        }
        
        report = create_feedback_loop_report(analysis)
        
        assert 'Feedback Loop Analysis Report' in report
        assert 'NO_EFFECTS' in report
        assert 'recompose_plan' in report  # lowercase in actual output
        assert '🔄' in report
        assert 'MODERATE' in report
    
    def test_create_report_multiple_triggers(self):
        """Test report generation with multiple triggers."""
        analysis = {
            'triggers': [
                {
                    'trigger_type': FeedbackTriggerType.HIGH_SKIP_RATE,
                    'severity': FeedbackSeverity.HIGH,
                    'recommendation': FeedbackActionType.REDUCE_PROTOCOLS,
                    'details': {
                        'skip_rate': 0.5,
                    }
                },
                {
                    'trigger_type': FeedbackTriggerType.NEGATIVE_FEEDBACK,
                    'severity': FeedbackSeverity.MODERATE,
                    'recommendation': FeedbackActionType.REDUCE_PROTOCOLS,
                    'details': {
                        'negative_feedback_count': 3,
                    }
                }
            ],
            'overall_severity': FeedbackSeverity.HIGH,
            'explanation': 'Detected multiple triggers.',
        }
        
        report = create_feedback_loop_report(analysis)
        
        assert 'Trigger 1: HIGH_SKIP_RATE' in report
        assert 'Trigger 2: NEGATIVE_FEEDBACK' in report
        assert 'Recommended Actions:' in report
        assert 'reduce_protocols' in report  # lowercase in actual output


class TestFeedbackLoopIntegration:
    """Integration tests for feedback loop with other services."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.feedback_loop = SmartFeedbackLoop(user_id=1)
    
    def test_integration_with_consistency_tracker(self):
        """Test integration with ConsistencyTracker."""
        # Mock the consistency tracker
        with patch.object(self.feedback_loop.consistency_tracker, 'get_all_protocols_status') as mock_status:
            mock_status.return_value = {
                'skincare_morning': {
                    'adherence_rate': 0.4,  # Poor adherence
                    'needs_reduction': True,
                },
                'training': {
                    'adherence_rate': 0.8,  # Good adherence
                    'needs_reduction': False,
                }
            }
            
            result = self.feedback_loop.execute_feedback_action(
                FeedbackActionType.REDUCE_PROTOCOLS,
                {}
            )
            
            assert result['success'] is True
            assert len(result['changes']) > 0
    
    def test_threshold_configuration(self):
        """Test threshold configuration."""
        # Test default thresholds
        assert SmartFeedbackLoop.NO_EFFECTS_THRESHOLD_DAYS == 21
        assert SmartFeedbackLoop.SKIP_RATE_THRESHOLD == 0.4
        assert SmartFeedbackLoop.NEGATIVE_FEEDBACK_THRESHOLD == 2
        assert SmartFeedbackLoop.MULTIPLE_FAILURES_THRESHOLD == 3
        
        # Test custom thresholds via class inheritance
        class CustomFeedbackLoop(SmartFeedbackLoop):
            NO_EFFECTS_THRESHOLD_DAYS = 14
            SKIP_RATE_THRESHOLD = 0.3
        
        custom_loop = CustomFeedbackLoop()
        assert custom_loop.NO_EFFECTS_THRESHOLD_DAYS == 14
        assert custom_loop.SKIP_RATE_THRESHOLD == 0.3


# Performance and edge case tests
class TestFeedbackLoopEdgeCases:
    """Test edge cases and performance considerations."""
    
    def test_large_dataset_handling(self):
        """Test handling of large datasets."""
        feedback_loop = SmartFeedbackLoop()
        
        # Create a large dataset
        large_progress_logs = []
        for i in range(100):
            large_progress_logs.append({
                'created_at': (datetime.now() - timedelta(days=i)).isoformat(),
                'look_score_change': 0.05,
            })
        
        # This should not crash
        result = feedback_loop.check_no_effects_trigger(
            large_progress_logs,
            {'expected_weekly_progress': 0.1}
        )
        
        # Result could be None or a trigger, but shouldn't crash
        assert result is None or isinstance(result, dict)
    
    def test_empty_data_handling(self):
        """Test handling of empty/missing data."""
        feedback_loop = SmartFeedbackLoop()
        
        # Empty progress logs
        result = feedback_loop.check_no_effects_trigger([], {})
        assert result is None
        
        # Empty interaction data
        result = feedback_loop.check_antagonism_triggers({})
        assert result is None
    
    def test_extreme_values_handling(self):
        """Test handling of extreme values."""
        feedback_loop = SmartFeedbackLoop()
        
        # Extreme skip rate
        extreme_data = {
            'skip_rate': 1.0,  # 100% skip rate - triggers HIGH severity
            'negative_feedback_count': 100,
            'failing_protocols': ['protocol1', 'protocol2', 'protocol3', 'protocol4', 'protocol5'],
        }
        
        result = feedback_loop.check_antagonism_triggers(extreme_data)
        assert result is not None
        assert result['severity'] == FeedbackSeverity.HIGH  # 5 failures = HIGH severity (not CRITICAL)
    
    def test_concurrent_execution_simulation(self):
        """Test simulated concurrent execution safety."""
        feedback_loop = SmartFeedbackLoop()
        
        # Simulate multiple concurrent calls with high severity triggers
        results = []
        for i in range(5):
            result = feedback_loop.analyze_feedback_loop(
                progress_logs=[],
                interaction_data={'skip_rate': 0.7},  # HIGH severity
                timeline_data={}
            )
            results.append(result)
        
        # All should complete successfully
        assert all(result['user_id'] == 1 for result in results)