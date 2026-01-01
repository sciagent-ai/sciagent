#!/usr/bin/env python3
"""
Test script for Evidence Synthesis Skill

Tests the evidence synthesis skill integration and functionality
"""

import sys
import os
from pathlib import Path

# Add sciagent to Python path
sys.path.insert(0, str(Path(__file__).parent / "sciagent"))

try:
    from sciagent.skill import SkillMetadata
    from skills.evidence_synthesis.skill import EvidenceSynthesisSkill, Domain, QueryType
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Make sure sciagent module is properly installed")
    sys.exit(1)

def test_skill_metadata():
    """Test skill metadata loading"""
    print("🔧 Testing skill metadata loading...")
    
    skill_path = Path("skills/evidence_synthesis")
    try:
        skill = EvidenceSynthesisSkill(skill_path)
        metadata = skill.metadata
        
        assert metadata.name == "evidence_synthesis"
        assert "scientific" in metadata.domain
        assert len(metadata.triggers) > 0
        assert "research" in metadata.triggers
        assert "web_search" in metadata.allowed_tools
        
        print("✅ Metadata loading successful")
        print(f"   - Name: {metadata.name}")
        print(f"   - Domain: {metadata.domain}")
        print(f"   - Triggers: {len(metadata.triggers)} triggers loaded")
        print(f"   - Tools: {len(metadata.allowed_tools)} tools allowed")
        return True
        
    except Exception as e:
        print(f"❌ Metadata test failed: {e}")
        return False

def test_domain_detection():
    """Test domain detection functionality"""
    print("\n🔬 Testing domain detection...")
    
    test_queries = [
        ("research protein folding mechanisms", Domain.BIOLOGY),
        ("analyze machine learning model performance", Domain.DATA_SCIENCE),
        ("study chemical reaction synthesis pathways", Domain.CHEMISTRY),
        ("investigate climate change impact", Domain.ENVIRONMENTAL),
        ("examine quantum physics theories", Domain.PHYSICS),
    ]
    
    skill_path = Path("skills/evidence_synthesis")
    skill = EvidenceSynthesisSkill(skill_path)
    
    passed = 0
    total = len(test_queries)
    
    for query, expected_domain in test_queries:
        detected = skill.detect_domain(query)
        if detected == expected_domain:
            print(f"✅ '{query[:30]}...' → {detected.value}")
            passed += 1
        else:
            print(f"❌ '{query[:30]}...' → Expected: {expected_domain.value}, Got: {detected.value}")
    
    print(f"\nDomain Detection: {passed}/{total} tests passed")
    return passed == total

def test_query_type_detection():
    """Test query type detection"""
    print("\n❓ Testing query type detection...")
    
    test_queries = [
        ("what is protein folding", QueryType.FACTUAL),
        ("compare machine learning vs deep learning", QueryType.COMPARATIVE),
        ("predict climate change effects", QueryType.PREDICTIVE),
        ("how does photosynthesis work", QueryType.MECHANISTIC),
        ("how to synthesize aspirin", QueryType.METHODOLOGICAL),
    ]
    
    skill_path = Path("skills/evidence_synthesis")
    skill = EvidenceSynthesisSkill(skill_path)
    
    passed = 0
    total = len(test_queries)
    
    for query, expected_type in test_queries:
        detected = skill.detect_query_type(query)
        if detected == expected_type:
            print(f"✅ '{query}' → {detected.value}")
            passed += 1
        else:
            print(f"❌ '{query}' → Expected: {expected_type.value}, Got: {detected.value}")
    
    print(f"\nQuery Type Detection: {passed}/{total} tests passed")
    return passed == total

def test_search_strategy():
    """Test search strategy generation"""
    print("\n🔍 Testing search strategy generation...")
    
    skill_path = Path("skills/evidence_synthesis")
    skill = EvidenceSynthesisSkill(skill_path)
    
    try:
        query = "research recent machine learning advances"
        strategy = skill.generate_search_strategy(query)
        
        required_keys = ["domain", "query_type", "topic", "search_queries", 
                        "priority_sources", "expected_evidence_types"]
        
        for key in required_keys:
            assert key in strategy, f"Missing key: {key}"
        
        print("✅ Search strategy generated successfully")
        print(f"   - Domain: {strategy['domain']}")
        print(f"   - Query Type: {strategy['query_type']}")
        print(f"   - Topic: {strategy['topic']}")
        print(f"   - Search Queries: {len(strategy['search_queries'])} generated")
        print(f"   - Priority Sources: {', '.join(strategy['priority_sources'][:3])}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Search strategy test failed: {e}")
        return False

def test_skill_trigger():
    """Test skill trigger mechanism"""
    print("\n🎯 Testing skill trigger detection...")
    
    skill_path = Path("skills/evidence_synthesis")
    skill = EvidenceSynthesisSkill(skill_path)
    
    # Test queries that should trigger
    trigger_queries = [
        "research recent studies on climate change",
        "analyze literature on machine learning",
        "find evidence for protein folding hypothesis",
        "synthesize research on renewable energy"
    ]
    
    # Test queries that should not trigger
    non_trigger_queries = [
        "hello world",
        "write a function",
        "debug this code",
        "create a file"
    ]
    
    passed = 0
    total = len(trigger_queries) + len(non_trigger_queries)
    
    for query in trigger_queries:
        if skill.should_trigger(query):
            print(f"✅ TRIGGER: '{query[:40]}...'")
            passed += 1
        else:
            print(f"❌ MISSED: '{query[:40]}...'")
    
    for query in non_trigger_queries:
        if not skill.should_trigger(query):
            print(f"✅ NO TRIGGER: '{query}'")
            passed += 1
        else:
            print(f"❌ FALSE TRIGGER: '{query}'")
    
    print(f"\nTrigger Detection: {passed}/{total} tests passed")
    return passed == total

def main():
    """Run all tests"""
    print("🧪 Starting Evidence Synthesis Skill Tests\n")
    
    tests = [
        test_skill_metadata,
        test_domain_detection,
        test_query_type_detection,
        test_search_strategy,
        test_skill_trigger,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                print("Test failed")
        except Exception as e:
            print(f"❌ Test error: {e}")
    
    print(f"\n{'='*50}")
    print(f"Overall Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Evidence Synthesis Skill is working correctly.")
        return 0
    else:
        print("❌ Some tests failed. Please check the implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())