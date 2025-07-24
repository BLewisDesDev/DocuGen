# LLM Care Plan Generation Integration Plan

## Current State Analysis

**✅ What's Working:**

- Complete document processing pipeline (Excel → Word templates)
- Robust LLM testing framework in `scripts/test_care_plan_llm.py`
- JSON-structured LLM output format defined
- Template variables mapped and identified
- Ollama integration tested and working

**❌ Missing Integration:**

- LLM functionality exists only in test scripts
- No production LLM processor in main pipeline
- Mapper configuration has empty `llm_fields: []`
- No database connection for client data

## Implementation Tasks

### 1. Create LLM Processor Component

- **File:** `src/core/llm_processor.py`
- **Purpose:** Production-ready LLM integration
- **Features:**
  - Migrate prompt engineering from test script
  - JSON parsing and validation
  - Error handling and fallbacks
  - Model configuration management

### 2. Update Mapper Configuration

- **File:** `mappers/care_plans_mapper.yaml`
- **Changes:**
  - Add 15-20 LLM-generated fields to `llm_fields` section
  - Include goals (Goal1-3), care needs (CareNeed1-3), interventions (Intervention1-3)
  - Add WHS fields, assistance tasks, and other LLM-generated content
  - Configure fallback values for LLM failures

### 3. Database Integration Layer

- **File:** `src/data/client_data_loader.py`
- **Purpose:** Connect to your external client database
- **Features:**
  - Load client data from your database folder
  - Transform database format to DocuGen expected format
  - Handle missing data gracefully

### 4. Enhanced Care Plan Generator

- **File:** `src/generators/care_plan_generator.py` (update existing)
- **Changes:**
  - Integrate LLM processor into generation pipeline
  - Add LLM data enrichment step
  - Handle LLM failures with appropriate fallbacks
  - Maintain existing Excel processing capabilities

### 5. CLI Integration

- **File:** `src/cli/main.py` (update existing)
- **Changes:**
  - Add `--enable-llm` flag for LLM processing
  - Add database connection options
  - Provide status feedback for LLM processing

### 6. Configuration & Testing

- **Files:** Config updates and test scripts
- **Purpose:**
  - Update template to use `chsp_care_plan_template_updated.docx`
  - Create integration tests
  - Add error handling documentation

## Critical LLM Fields to Generate

**High Priority (Core Care Planning):**

- `Goal1`, `Goal2`, `Goal3` - Wellness-focused client goals
- `CareNeed1-3` - Specific care needs identification
- `Intervention1-3` - CHSP-compliant interventions
- `WHSIssues` - Work health and safety risk assessment
- `RiskMitigation` - Safety risk mitigation strategies

**Medium Priority (Service Tasks):**

- `Task1-4` - Specific assistance tasks
- `WellnessApproach` - Tailored wellness approach
- `EmergencyPlanDetails` - Emergency response planning

**Low Priority (Compliance):**

- Various boolean flags and system status fields

## Today's Implementation Order

1. **Create LLM Processor** (30 mins)
2. **Update Mapper Config** (15 mins)
3. **Database Connection** (45 mins)
4. **Integration Testing** (30 mins)
5. **End-to-end Test** (30 mins)

**Total Estimated Time:** 2.5 hours

## Risk Mitigation

- **LLM Failures:** Default to template placeholders
- **Database Issues:** Fallback to Excel import
- **JSON Parsing Errors:** Structured error handling
- **Model Availability:** Configurable model selection

This plan leverages your existing working LLM test code and integrates it into the production pipeline with minimal architectural changes.
