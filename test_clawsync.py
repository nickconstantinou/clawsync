#!/usr/bin/env python3
"""Tests for clawsync"""
import pytest
from pathlib import Path

DIR = Path(__file__).parent

def test_has_sync_script():
    """Test sync.sh exists"""
    assert (DIR / "sync.sh").exists()

def test_has_restore_script():
    """Test restore.sh exists"""
    assert (DIR / "restore.sh").exists()

def test_has_skill():
    """Test SKILL.md exists"""
    assert (DIR / "SKILL.md").exists()

def test_has_github_workflow():
    """Test .github/workflows exists"""
    assert (DIR / ".github").is_dir()

def test_has_gitignore():
    """Test .gitignore exists"""
    assert (DIR / ".gitignore").exists()
