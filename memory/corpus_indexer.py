#!/usr/bin/env python3
"""
AEGIS OS: Corpus Memory Indexer
Reads verified G^G physics trajectories to supply Aegis OS bodies with "memory".
"""

import os
import json
import random
from typing import Dict, Any, Optional

class CorpusMemory:
    def __init__(self, corpus_root: str):
        self.corpus_root = corpus_root
        
    def find_latest_trajectory(self, body_type: str, condition: str = "nominal") -> Optional[Dict[str, Any]]:
        """
        Scans the corpus for a recent trajectory for the specific body type.
        E.g., body_type="titanhauler", condition="sand"
        """
        body_dir = os.path.join(self.corpus_root, body_type)
        if not os.path.exists(body_dir):
            print(f"Memory Fault: No corpus found for {body_type}")
            return None
            
        json_files = []
        for root, _, files in os.walk(body_dir):
            for f in files:
                if f.endswith('.json'):
                    json_files.append(os.path.join(root, f))
                    
        # Filter files that reside in a directory matching the condition (case-insensitive)
        condition_lower = condition.lower()
        matched_files = [f for f in json_files if condition_lower in f.lower()]
        
        # If no strict matches, fallback to all JSONs but warn
        if not matched_files:
            print(f"Memory Fault: Condition '{condition}' not found for {body_type}. Falling back to general scan.")
            matched_files = json_files
            
        if not matched_files:
            return None
            
        # Get the newest file by modification time
        chosen_file = max(matched_files, key=os.path.getmtime)
        try:
            with open(chosen_file, 'r') as f:
                dataset = json.load(f)
                
            trajectories = dataset.get("trajectories", [])
            if not trajectories:
                return None
                
            # Chronologically retrieve the final generated trajectory from the sweep
            return trajectories[-1]
            
        except Exception as e:
            print(f"Memory Fault: Failed to read {chosen_file}: {e}")
            return None
