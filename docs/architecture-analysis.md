# DocuGen Architecture Map & Modularity Analysis

## Current Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                                DocuGen System                                       │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│   ┌─────────────┐    ┌──────────────────────────────────────────────────────────┐   │
│   │   main.py   │────┤                CLI Layer                                 │   │
│   │ Entry Point │    │                                                          │   │
│   └─────────────┘    │  ┌─────────────────┐  ┌─────────────────────────────┐    │   │
│                      │  │  process cmd    │  │     validate cmd            │    │   │
│                      │  │ • config file   │  │ • config validation         │    │   │
│                      │  │ • data file     │  │ • template validation       │    │   │
│                      │  │ • output opts   │  │                             │    │   │
│                      │  └─────────────────┘  └─────────────────────────────┘    │   │
│                      └──────────────────────────────────────────────────────────┘   │
│                                                │                                    │
│   ┌─────────────────────────────────────────────────────────────────────────────┐   │
│   │                     Configuration Layer                                     │   │
│   │                                                                             │   │
│   │  ┌─────────────────┐           ┌─────────────────────────────────────────┐  │   │
│   │  │  ConfigLoader   │           │        Configuration Files              │  │   │
│   │  │ • app_config    │◄──────────┤ • config/app_config.yaml                │  │   │
│   │  │ • mapper_config │           │ • mappers/care_plans_mapper.yaml        │  │   │
│   │  │ • validation    │           │ • mappers/[your_new_mapper].yaml        │  │   │
│   │  └─────────────────┘           └─────────────────────────────────────────┘  │   │
│   └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                │                                    │
│   ┌─────────────────────────────────────────────────────────────────────────────┐   │
│   │                      Core Processing Layer                                  │   │
│   │                                                                             │   │
│   │  ┌─────────────────────────────────────────────────────────────────────┐    │   │
│   │  │                    DocumentProcessor                                │    │   │
│   │  │ • Main orchestrator                                                 │    │   │
│   │  │ • Validation & preview                                              │    │   │
│   │  │ • Document processing pipeline                                      │    │   │
│   │  │ • Error handling & logging                                          │    │   │
│   │  └─────────────────────────────────────────────────────────────────────┘    │   │
│   └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                │                                    │
│   ┌─────────────────────────────────────────────────────────────────────────────┐   │
│   │                      Data Processing Layer                                  │   │
│   │                                                                             │   │
│   │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────────┐  │   │
│   │  │  ExcelImporter  │  │ JinjaProcessor  │  │     CarePlanGenerator       │  │   │
│   │  │ • Read Excel    │  │ • Extract vars  │  │ • Document generation       │  │   │
│   │  │ • Map fields    │  │ • Validate      │  │ • PDF conversion            │  │   │
│   │  │ • Transform     │  │ • Process       │  │ • File naming               │  │   │
│   │  │ • Validate      │  │                 │  │ • Duplicate handling        │  │   │
│   │  └─────────────────┘  └─────────────────┘  └─────────────────────────────┘  │   │
│   └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                     │
│   ┌─────────────────────────────────────────────────────────────────────────────┐   │
│   │                         Utilities Layer                                     │   │
│   │                                                                             │   │
│   │  ┌─────────────────┐                                                        │   │
│   │  │     Logger      │                                                        │   │
│   │  │ • Setup logging │                                                        │   │
│   │  │ • File/console  │                                                        │   │
│   │  │ • Level control │                                                        │   │
│   │  └─────────────────┘                                                        │   │
│   └─────────────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

## Current Data Flow Pipeline

```
┌─────────────┐    ┌─────────────┐    ┌─────────────────┐
│   User      │───►│   CLI       │───►│  ConfigLoader   │
│ Commands    │    │ Interface   │    │                 │
└─────────────┘    └─────────────┘    └─────────────────┘
                                                │
                                                ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    DocumentProcessor (Main Orchestrator)                        │
└─────────────────────────────────────────────────────────────────────────────────┘
                                                │
                                                ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────────┐    ┌───────────────────┐
│   Excel     │───►│   Excel     │───►│    Mapper       │───►│   Transformed     │
│   File      │    │  Importer   │    │  Processing     │    │   Data Records    │
│             │    │             │    │                 │    │                   │
└─────────────┘    └─────────────┘    └─────────────────┘    └───────────────────┘
                                                                        │
                                                                        ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────────┐    ┌───────────────────┐
│   Word      │◄───│   Jinja     │◄───│   Template      │◄───│   For Each        │
│ Document    │    │ Processor   │    │   Processing    │    │   Record          │
│             │    │             │    │                 │    │                   │
└─────────────┘    └─────────────┘    └─────────────────┘    └───────────────────┘
       │
       ▼
┌─────────────┐    ┌─────────────┐
│     PDF     │◄───│  CarePlan   │
│ Conversion  │    │  Generator  │
│             │    │             │
└─────────────┘    └─────────────┘
       │
       ▼
┌─────────────┐
│   Output    │
│ Documents   │
│             │
└─────────────┘
```

## Current Modularity Issues (Breaking Points)

### 🔴 Critical Hardcoded Dependencies

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           MODULARITY BLOCKERS                                   │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  1. DocumentProcessor → CarePlanGenerator (HARDCODED)                           │
│     ┌─────────────────────────────────────────────────────────────────────┐     │
│     │ src/core/document_processor.py:28                                   │     │
│     │ self.generator = CarePlanGenerator(self.output_dir, app_config)     │     │
│     │                                                                     │     │
│     │ 🚫 BLOCKS: Adding invoices, contracts, reports, etc.                │     │
│     └─────────────────────────────────────────────────────────────────────┘     │
│                                                                                 │
│  2. ExcelImporter → Care Plan Service Logic (HARDCODED)                         │
│     ┌─────────────────────────────────────────────────────────────────────┐     │
│     │ src/importers/excel_importer.py:94-106                              │     │
│     │ # Process service types for checkbox logic                          │     │
│     │ service_types = mapper_config.get('service_types', {})              │     │
│     │ current_service = mapped_row.get('ServiceType', '').strip()         │     │
│     │ for service_code, service_name in service_types.items():            │     │
│     │     mapped_row[f'{service_code}_selected'] = (current_service       │     │
│     │                                             == service_code)        │     │
│     │                                                                     │     │
│     │ 🚫 BLOCKS: Non-service-based documents (invoices, contracts)        │     │
│     └─────────────────────────────────────────────────────────────────────┘     │
│                                                                                 │
│  3. ExcelImporter → Client Name Generation (HARDCODED)                          │
│     ┌─────────────────────────────────────────────────────────────────────┐     │
│     │ src/importers/excel_importer.py:86-92                               │     │
│     │ # Create client_name from FirstName + LastName                      │     │
│     │ first_name = mapped_row.get('FirstName', '').strip()                │     │
│     │ last_name = mapped_row.get('LastName', '').strip()                  │     │
│     │ if first_name or last_name:                                         │     │
│     │     mapped_row['client_name'] = f"{first_name} {last_name}".strip() │     │
│     │                                                                     │     │
│     │ 🚫 BLOCKS: Documents without FirstName/LastName                     │     │
│     └─────────────────────────────────────────────────────────────────────┘     │
│                                                                                 │
│  4. CarePlanGenerator → Template Name Hardcoding                                │
│     ┌─────────────────────────────────────────────────────────────────────┐     │
│     │ src/generators/care_plan_generator.py:62                            │     │
│     │ 'template_name': 'care_plan'                                        │     │
│     │                                                                     │     │
│     │ 🚫 BLOCKS: Different document types                                 │     │
│     └─────────────────────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### ⚠️ Specific Problem Scenarios

**Adding an Invoice Template:**

```
❌ CURRENT: Cannot add invoice template because:
   • DocumentProcessor only creates CarePlanGenerator
   • ExcelImporter assumes FirstName/LastName for client_name
   • Service type logic assumes care plan services
   • Generator hardcodes 'care_plan' template name

✅ WOULD NEED: Code changes in 3+ files
```

**Adding a Contract Template:**

```
❌ CURRENT: Cannot add contract template because:
   • All same issues as invoice, plus:
   • Contract data might use CompanyName instead of client names
   • Different field transformations needed
   • No service type logic needed

✅ WOULD NEED: Code changes in 3+ files
```

## Enhanced Modular Architecture Design

### 🎯 Proposed Modular Architecture

```
┌────────────────────────────────────────────────────────────────────────────────────┐
│                            ENHANCED DocuGen System                                 │
├────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                    │
│   ┌─────────────┐    ┌─────────────────────────────────────────────────────────┐   │
│   │   main.py   │────┤                CLI Layer (UNCHANGED)                    │   │
│   │ Entry Point │    │                                                         │   │
│   └─────────────┘    │  ┌─────────────────┐  ┌──────────────────────────────┐  │   │
│                      │  │  process cmd    │  │     validate cmd             │  │   │
│                      │  │ • config file   │  │ • config validation          │  │   │
│                      │  │ • data file     │  │ • template validation        │  │   │
│                      │  │ • output opts   │  │                              │  │   │
│                      │  └─────────────────┘  └──────────────────────────────┘  │   │
│                      └─────────────────────────────────────────────────────────┘   │
│                                                │                                   │
│   ┌────────────────────────────────────────────────────────────────────────────┐   │
│   │                  ENHANCED Configuration Layer                              │   │
│   │                                                                            │   │
│   │  ┌─────────────────┐           ┌────────────────────────────────────────┐  │   │
│   │  │  ConfigLoader   │           │        Enhanced Configuration Files    │  │   │
│   │  │ • app_config    │◄──────────┤ • config/app_config.yaml               │  │   │
│   │  │ • mapper_config │           │ • mappers/care_plans_mapper.yaml       │  │   │
│   │  │ • generator_cfg │           │ • mappers/invoice_mapper.yaml          │  │   │
│   │  │ • plugin_loader │           │ • mappers/contract_mapper.yaml         │  │   │
│   │  └─────────────────┘           │ • generators/[type]_generator.yaml     │  │   │
│   │                                └────────────────────────────────────────┘  │   │
│   └────────────────────────────────────────────────────────────────────────────┘   │
│                                                │                                   │
│   ┌────────────────────────────────────────────────────────────────────────────┐   │
│   │                   ENHANCED Core Processing Layer                           │   │
│   │                                                                            │   │
│   │  ┌─────────────────────────────────────────────────────────────────────┐   │   │
│   │  │              DocumentProcessor (ENHANCED)                           │   │   │
│   │  │ • Dynamic generator loading                                         │   │   │
│   │  │ • Plugin architecture support                                       │   │   │
│   │  │ • Generic validation & preview                                      │   │   │
│   │  │ • Configurable processing pipeline                                  │   │   │
│   │  └─────────────────────────────────────────────────────────────────────┘   │   │
│   │                                                                            │   │
│   │  ┌─────────────────────────────────────────────────────────────────────┐   │   │
│   │  │                GeneratorFactory (NEW)                               │   │   │
│   │  │ • Dynamic generator creation                                        │   │   │
│   │  │ • Plugin registration system                                        │   │   │
│   │  │ • Generator type detection                                          │   │   │
│   │  └─────────────────────────────────────────────────────────────────────┘   │   │
│   └────────────────────────────────────────────────────────────────────────────┘   │
│                                                │                                   │
│   ┌────────────────────────────────────────────────────────────────────────────┐   │
│   │                  ENHANCED Data Processing Layer                            │   │
│   │                                                                            │   │
│   │  ┌─────────────────┐  ┌─────────────────┐  ┌────────────────────────────┐  │   │
│   │  │  DataImporter   │  │ JinjaProcessor  │  │    DocumentGenerator       │  │   │
│   │  │   (ENHANCED)    │  │  (UNCHANGED)    │  │      (GENERIC)             │  │   │
│   │  │ • Generic       │  │ • Extract vars  │  │ • Generic generation       │  │   │
│   │  │   importing     │  │ • Validate      │  │ • PDF conversion           │  │   │
│   │  │ • Configurable  │  │ • Process       │  │ • Configurable naming      │  │   │
│   │  │   transformers  │  │                 │  │ • Duplicate handling       │  │   │
│   │  │ • Pluggable     │  │                 │  │                            │  │   │
│   │  │   validators    │  │                 │  │                            │  │   │
│   │  └─────────────────┘  └─────────────────┘  └────────────────────────────┘  │   │
│   │                                                                            │   │
│   │  ┌─────────────────────────────────────────────────────────────────────┐   │   │
│   │  │                    DataTransformer (NEW)                            │   │   │
│   │  │ • Configurable transformation pipeline                              │   │   │
│   │  │ • Built-in transformers (dates, strings, numbers)                   │   │   │
│   │  │ • Custom transformer registration                                   │   │   │
│   │  │ • Conditional logic support                                         │   │   │
│   │  └─────────────────────────────────────────────────────────────────────┘   │   │
│   └────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                    │
│   ┌────────────────────────────────────────────────────────────────────────────┐   │
│   │                      Plugin System (NEW)                                   │   │
│   │                                                                            │   │
│   │  ┌─────────────────┐  ┌─────────────────┐  ┌────────────────────────────┐  │   │
│   │  │  PluginManager  │  │ GeneratorPlugin │  │      TransformerPlugin     │  │   │
│   │  │ • Plugin loader │  │ • Custom gens   │  │ • Custom transformers      │  │   │
│   │  │ • Registry      │  │ • Type specific │  │ • Field processors         │  │   │
│   │  │ • Lifecycle     │  │ • Inheritance   │  │ • Validation rules         │  │   │
│   │  └─────────────────┘  └─────────────────┘  └────────────────────────────┘  │   │
│   └────────────────────────────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────────────────────────────┘
```

### 🔧 Enhanced Configuration Schema

```yaml
# Enhanced Mapper Configuration
# mappers/invoice_mapper.yaml
project_name: "invoices"
document_type: "invoice" # NEW: Document type identifier
template_file: "invoice_template.docx"

# Enhanced field mappings with transformations
field_mappings:
  "InvoiceNumber": "invoice_id"
  "CompanyName": "company_name"
  "Amount": "total_amount"
  "DueDate": "due_date"

# NEW: Document-specific configuration
document_config:
  generator_type: "invoice" # Specifies which generator to use
  naming_strategy: "invoice_number" # How to name output files
  required_fields: ["invoice_id", "company_name", "total_amount"]

# NEW: Advanced transformations
transformations:
  "total_amount":
    type: "currency"
    format: "USD"
  "due_date":
    type: "date"
    format: "%B %d, %Y"
  "company_name":
    type: "string"
    operations: ["trim", "title_case"]

# NEW: Custom field generation
computed_fields:
  "invoice_filename":
    template: "Invoice_{invoice_id}_{company_name}"
    sanitize: true
  "formatted_total":
    template: "${total_amount:.2f}"

# NEW: Conditional logic
conditional_processing:
  - condition: "total_amount > 1000"
    add_fields:
      "priority": "high"
  - condition: "due_date < today"
    add_fields:
      "status": "overdue"

# NEW: Custom validation rules
validation_rules:
  - field: "invoice_id"
    type: "regex"
    pattern: "^INV-\\d{4,6}$"
    message: "Invoice ID must be in format INV-XXXX"
  - field: "total_amount"
    type: "numeric"
    min: 0
    message: "Total amount must be positive"
```

### 🚀 Enhanced Data Flow

```
┌─────────────┐    ┌─────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User      │───►│   CLI       │───►│  ConfigLoader   │───►│ GeneratorFactory│
│ Commands    │    │ Interface   │    │                 │    │                 │
└─────────────┘    └─────────────┘    └─────────────────┘    └─────────────────┘
                                                │                       │
                                                ▼                       ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    DocumentProcessor (Enhanced)                                 │
│  • Dynamic generator loading based on document_type                             │
│  • Configurable processing pipeline                                             │
│  • Plugin architecture integration                                              │
└─────────────────────────────────────────────────────────────────────────────────┘
                                                │
                                                ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────────┐    ┌───────────────────┐
│   Excel     │───►│   Data      │───►│  DataTransformer│───►│   Enhanced        │
│   File      │    │  Importer   │    │  (Configurable) │    │   Data Records    │
│             │    │ (Generic)   │    │                 │    │                   │
└─────────────┘    └─────────────┘    └─────────────────┘    └───────────────────┘
                                                                        │
                                                                        ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────────┐    ┌───────────────────┐
│   Word      │◄───│   Jinja     │◄───│   Template      │◄───│   For Each        │
│ Document    │    │ Processor   │    │   Processing    │    │   Record          │
│             │    │             │    │                 │    │                   │
└─────────────┘    └─────────────┘    └─────────────────┘    └───────────────────┘
       │
       ▼
┌─────────────┐    ┌─────────────┐
│     PDF     │◄───│  Generic    │
│ Conversion  │    │ Document    │
│             │    │ Generator   │
└─────────────┘    └─────────────┘
       │
       ▼
┌─────────────┐
│   Output    │
│ Documents   │
│             │
└─────────────┘
```

### 🔄 Implementation Strategy

#### Phase 1: Core Refactoring (Immediate)

```
1. Replace CarePlanGenerator with GenericDocumentGenerator
2. Move hardcoded logic to configuration
3. Create DataTransformer class
4. Enhance mapper configuration schema
```

#### Phase 2: Plugin Architecture (Future)

```
1. Implement GeneratorFactory
2. Create PluginManager
3. Add custom transformer registration
4. Support external generator plugins
```

### ✅ True Modularity Achievement

**With Enhanced Architecture:**

```
✅ ADD INVOICE TEMPLATE:
   1. Create templates/invoice_template.docx
   2. Create mappers/invoice_mapper.yaml
   3. Run: python main.py process --config invoice_mapper.yaml --data invoice_data.xlsx
   ✅ NO CODE CHANGES NEEDED!

✅ ADD CONTRACT TEMPLATE:
   1. Create templates/contract_template.docx
   2. Create mappers/contract_mapper.yaml
   3. Run: python main.py process --config contract_mapper.yaml --data contract_data.xlsx
   ✅ NO CODE CHANGES NEEDED!

✅ ADD REPORT TEMPLATE:
   1. Create templates/report_template.docx
   2. Create mappers/report_mapper.yaml
   3. Run: python main.py process --config report_mapper.yaml --data report_data.xlsx
   ✅ NO CODE CHANGES NEEDED!
```

### 📊 Comparison: Current vs Enhanced

| Feature                  | Current System                | Enhanced System            |
| ------------------------ | ----------------------------- | -------------------------- |
| **New Templates**        | ❌ Requires code changes      | ✅ Config-only             |
| **Data Transformations** | ❌ Hardcoded in importer      | ✅ Configurable pipeline   |
| **Field Validation**     | ❌ Basic column checking      | ✅ Custom validation rules |
| **File Naming**          | ❌ Hardcoded patterns         | ✅ Configurable strategies |
| **Document Types**       | ❌ Care plans only            | ✅ Any document type       |
| **Generator Logic**      | ❌ Single hardcoded class     | ✅ Dynamic loading         |
| **Extensibility**        | ❌ Code modification required | ✅ Plugin architecture     |

This enhanced architecture would make the system **truly plug-and-play** as originally intended, requiring only configuration files for new document types without any code changes.

## Component Details

### 1. Entry Point: main.py

- **Role**: Simple entry point that delegates to CLI module
- **Dependencies**: `src.cli`
- **Data Flow**: Entry point → CLI module

### 2. CLI Interface: src/cli/commands.py

- **Main Classes**: Click-based command functions
- **Key Methods**:
  - `cli()`: Main Click group command
  - `process()`: Primary document processing command
  - `validate()`: Configuration and template validation command
- **Dependencies**: `click`, `ConfigLoader`, `ExcelImporter`, `DocumentProcessor`
- **Data Flow**: CLI commands → ConfigLoader → DocumentProcessor → Output

### 3. Core Processor: src/core/document_processor.py

- **Main Classes**: `DocumentProcessor` (Main orchestrator class)
- **Key Methods**:
  - `validate_and_preview()`: Validation without generation
  - `process_documents()`: Main processing pipeline
  - `validate_template()`: Template validation
- **Dependencies**: `ExcelImporter`, `JinjaProcessor`, `CarePlanGenerator`
- **Data Flow**: Excel data → Import → Map → Template processing → Document generation

### 4. Configuration Management: src/core/config_loader.py

- **Main Classes**: `ConfigLoader` (Configuration file loader and validator)
- **Key Methods**:
  - `load_app_config()`: Load application configuration
  - `load_mapper_config()`: Load field mapping configuration
  - `get_setting()`: Get nested configuration values
- **Dependencies**: `yaml`, `pathlib`
- **Data Flow**: YAML files → Validation → Configuration objects → Other components

### 5. Data Import: src/importers/excel_importer.py

- **Main Classes**: `ExcelImporter` (Excel file reader and data mapper)
- **Key Methods**:
  - `read_file()`: Read Excel file
  - `map_data()`: Map DataFrame to template variables
  - `validate_columns()`: Column validation
- **Dependencies**: `pandas`, `datetime`
- **Data Flow**: Excel file → DataFrame → Column mapping → Data transformation → Mapped data list

### 6. Template Processing: src/templates/jinja_processor.py

- **Main Classes**: `JinjaProcessor` (Jinja2 template processor for Word documents)
- **Key Methods**:
  - `extract_template_variables()`: Extract Jinja2 variables from Word template
  - `validate_template_syntax()`: Validate Jinja2 syntax
  - `process_template()`: Process template with data
- **Dependencies**: `docx`, `jinja2`, `re`
- **Data Flow**: Word template + Data → Jinja2 processing → Rendered Word document

### 7. Document Generation: src/generators/care_plan_generator.py

- **Main Classes**: `CarePlanGenerator` (Document generation and PDF conversion)
- **Key Methods**:
  - `generate_document()`: Generate single document
  - `_generate_filename()`: Create filename from data
  - `_generate_pdf()`: Convert Word to PDF
- **Dependencies**: `docx2pdf`, `subprocess`, `pathlib`
- **Data Flow**: Template + Data → Word document → PDF conversion → Output files

### 8. Logging Utilities: src/utils/logger.py

- **Key Methods**: `setup_logging()`: Configure logging system
- **Dependencies**: `logging`, `pathlib`, `datetime`
- **Data Flow**: Configuration → Logger setup → All components use configured logging
