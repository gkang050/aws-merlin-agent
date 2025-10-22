#!/usr/bin/env python3
"""Test MERLIN agent deployment"""

import os
import sys

# Set environment
os.environ['MERLIN_ENV'] = 'demo'
os.environ['MERLIN_INFERENCE_MODE'] = 'local'

try:
    from aws_merlin_agent.agent.workflows.agent_plan import MerlinAgentWorkflow
    
    print("🧙‍♂️ Testing MERLIN Agent...")
    print("=" * 50)
    print()
    
    # Initialize workflow
    print("1. Initializing workflow...")
    workflow = MerlinAgentWorkflow()
    print("   ✅ Workflow initialized")
    print()
    
    # Test performance summary
    print("2. Testing performance summary for SKU-001...")
    try:
        result = workflow.summarize_performance('SKU-001')
        print("   ✅ Summary generated:")
        print(f"   📊 {result['narrative']}")
        print(f"   📈 Data points: {len(result['rows'])}")
    except Exception as e:
        print(f"   ⚠️  Summary failed: {e}")
    print()
    
    # Test forecast
    print("3. Testing demand forecast...")
    try:
        forecast = workflow.forecast(sku='SKU-001')
        print("   ✅ Forecast generated:")
        print(f"   🔮 {forecast}")
    except Exception as e:
        print(f"   ⚠️  Forecast failed: {e}")
    print()
    
    # Test conversational query
    print("4. Testing conversational query...")
    try:
        response = workflow.conversational_query("How is SKU-001 performing?")
        print("   ✅ Query processed:")
        print(f"   💬 {response.get('response', 'No response')[:200]}...")
    except Exception as e:
        print(f"   ⚠️  Query failed: {e}")
    print()
    
    print("=" * 50)
    print("✅ Agent test complete!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Run: poetry install")
    sys.exit(1)
except Exception as e:
    print(f"❌ Test failed: {e}")
    sys.exit(1)
