import unittest
import os
import sqlite3
from backend.app.database import init_db, save_project, save_experience, get_projects, get_experiences, delete_project, delete_experience

class TestVaultDatabase(unittest.TestCase):
    def setUp(self):
        # Enforce db initialization
        init_db()

    def test_save_and_retrieve_experience(self):
        exp_data = {
            "company_name": "Test Company Corp",
            "role_title": "Senior Backend Developer",
            "start_date": "2026-01",
            "end_date": "2026-05",
            "employment_type": "Full-time"
        }
        
        # Save experience
        exp_id = save_experience(exp_data)
        self.assertIsNotNone(exp_id)
        
        # Verify retrieve
        experiences = get_experiences()
        saved_exp = next((e for e in experiences if e["id"] == exp_id), None)
        self.assertIsNotNone(saved_exp)
        self.assertEqual(saved_exp["company_name"], "Test Company Corp")
        self.assertEqual(saved_exp["role_title"], "Senior Backend Developer")
        self.assertEqual(saved_exp["employment_type"], "Full-time")
        
        # Delete experience
        delete_success = delete_experience(exp_id)
        self.assertTrue(delete_success)

    def test_save_and_retrieve_project_with_achievements(self):
        project_data = {
            "title": "Autonomous Drone Navigation",
            "description": "Built neural pathfinding routines for obstacle bypass.",
            "repository_url": "github.com/test/drone",
            "achievements": [
                {
                    "action_taken": "Engineered real-time depth mapping using OpenCV",
                    "outcome_metric": "reduced collision rate by 45%",
                    "raw_bullet_text": "Engineered real-time depth mapping using OpenCV, reducing collision rate by 45%.",
                    "technologies": ["OpenCV", "Python"],
                    "skills": ["Computer Vision", "Python Programming"]
                }
            ]
        }
        
        # Save project
        proj_id = save_project(project_data)
        self.assertIsNotNone(proj_id)
        
        # Verify retrieve
        projects = get_projects()
        saved_proj = next((p for p in projects if p["id"] == proj_id), None)
        self.assertIsNotNone(saved_proj)
        self.assertEqual(saved_proj["title"], "Autonomous Drone Navigation")
        
        # Verify achievements and nested skills/tech
        self.assertEqual(len(saved_proj["achievements"]), 1)
        ach = saved_proj["achievements"][0]
        self.assertEqual(ach["action_taken"], "Engineered real-time depth mapping using OpenCV")
        self.assertIn("OpenCV", ach["technologies"])
        self.assertIn("Computer Vision", ach["skills"])
        
        # Delete project
        delete_success = delete_project(proj_id)
        self.assertTrue(delete_success)
        
        # Confirm cascading deletes cleared the child achievements
        projects_after_delete = get_projects()
        self.assertFalse(any(p["id"] == proj_id for p in projects_after_delete))

if __name__ == "__main__":
    unittest.main()
