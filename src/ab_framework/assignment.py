"""
User assignment and bucketing logic for A/B experiments.
Implements deterministic hash-based randomization for consistent user experiences.
"""

import hashlib
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class ExperimentStatus(Enum):
    """Experiment lifecycle status"""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"


@dataclass
class ExperimentConfig:
    """Configuration for an A/B experiment"""
    experiment_id: str
    name: str
    variants: List[str]
    traffic_allocation: Dict[str, float]  # variant -> percentage (0-1)
    status: ExperimentStatus
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    
    def __post_init__(self):
        """Validate experiment configuration"""
        # Ensure traffic allocations sum to <= 1.0
        total_allocation = sum(self.traffic_allocation.values())
        if total_allocation > 1.0:
            raise ValueError(f"Traffic allocation exceeds 100%: {total_allocation}")
        
        # Ensure all variants have allocations
        for variant in self.variants:
            if variant not in self.traffic_allocation:
                raise ValueError(f"Variant {variant} missing traffic allocation")


class UserAssignment:
    """
    Handles deterministic user assignment to experiment variants.
    Uses consistent hashing to ensure users always see the same variant.
    """
    
    def __init__(self, salt: str = "experimentation_platform_v1"):
        """
        Initialize assignment engine.
        
        Args:
            salt: Salt value for hash function to prevent prediction
        """
        self.salt = salt
    
    def _hash_user(self, user_id: str, experiment_id: str) -> float:
        """
        Generate deterministic hash value for user-experiment pair.
        
        Args:
            user_id: Unique user identifier
            experiment_id: Unique experiment identifier
            
        Returns:
            Float between 0 and 1 representing hash bucket
        """
        # Create deterministic hash
        hash_input = f"{user_id}:{experiment_id}:{self.salt}"
        hash_bytes = hashlib.sha256(hash_input.encode()).digest()
        
        # Convert first 8 bytes to integer and normalize to [0, 1]
        hash_int = int.from_bytes(hash_bytes[:8], byteorder='big')
        return hash_int / (2 ** 64)
    
    def assign_variant(
        self, 
        user_id: str, 
        experiment: ExperimentConfig
    ) -> Optional[str]:
        """
        Assign user to experiment variant using consistent hashing.
        
        Args:
            user_id: Unique user identifier
            experiment: Experiment configuration
            
        Returns:
            Assigned variant name or None if user not in experiment
        """
        if experiment.status != ExperimentStatus.ACTIVE:
            return None
        
        # Get hash bucket for this user-experiment pair
        hash_value = self._hash_user(user_id, experiment.experiment_id)
        
        # Assign to variant based on traffic allocation
        cumulative_allocation = 0.0
        for variant, allocation in experiment.traffic_allocation.items():
            cumulative_allocation += allocation
            if hash_value < cumulative_allocation:
                return variant
        
        # User falls outside experiment traffic (holdout group)
        return None
    
    def bulk_assign(
        self, 
        user_ids: List[str], 
        experiment: ExperimentConfig
    ) -> Dict[str, Optional[str]]:
        """
        Assign multiple users to experiment variants.
        
        Args:
            user_ids: List of user identifiers
            experiment: Experiment configuration
            
        Returns:
            Dictionary mapping user_id to assigned variant
        """
        return {
            user_id: self.assign_variant(user_id, experiment)
            for user_id in user_ids
        }
    
    def get_assignment_distribution(
        self,
        user_ids: List[str],
        experiment: ExperimentConfig
    ) -> Dict[str, int]:
        """
        Calculate actual distribution of users across variants.
        Useful for validating randomization quality.
        
        Args:
            user_ids: List of user identifiers
            experiment: Experiment configuration
            
        Returns:
            Dictionary with variant counts
        """
        assignments = self.bulk_assign(user_ids, experiment)
        
        distribution = {variant: 0 for variant in experiment.variants}
        distribution['holdout'] = 0
        
        for variant in assignments.values():
            if variant is None:
                distribution['holdout'] += 1
            else:
                distribution[variant] += 1
        
        return distribution


class MultiExperimentAssignment:
    """
    Handles assignment when users can be in multiple experiments simultaneously.
    Prevents interaction effects between experiments.
    """
    
    def __init__(self, salt: str = "experimentation_platform_v1"):
        self.assigner = UserAssignment(salt=salt)
    
    def assign_all_experiments(
        self,
        user_id: str,
        experiments: List[ExperimentConfig]
    ) -> Dict[str, Optional[str]]:
        """
        Assign user to all active experiments.
        
        Args:
            user_id: Unique user identifier
            experiments: List of experiment configurations
            
        Returns:
            Dictionary mapping experiment_id to assigned variant
        """
        assignments = {}
        for experiment in experiments:
            variant = self.assigner.assign_variant(user_id, experiment)
            assignments[experiment.experiment_id] = variant
        
        return assignments
    
    def check_experiment_overlap(
        self,
        user_ids: List[str],
        experiment1: ExperimentConfig,
        experiment2: ExperimentConfig
    ) -> float:
        """
        Calculate percentage of users in both experiments.
        High overlap may indicate interaction effects.
        
        Args:
            user_ids: List of user identifiers
            experiment1: First experiment
            experiment2: Second experiment
            
        Returns:
            Percentage of users in both experiments (0-1)
        """
        assignments1 = self.assigner.bulk_assign(user_ids, experiment1)
        assignments2 = self.assigner.bulk_assign(user_ids, experiment2)
        
        in_both = sum(
            1 for uid in user_ids
            if assignments1[uid] is not None and assignments2[uid] is not None
        )
        
        return in_both / len(user_ids) if user_ids else 0.0
