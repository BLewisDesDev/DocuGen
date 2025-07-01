# DocuGen - Document Generator CLI

A Python CLI tool that processes Excel data through Word templates to generate personalized documents with future LLM enhancement capabilities.

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Virtual environment recommended

### Installation

1. **Clone and setup environment**:

   ```bash
   git clone <repository-url>
   cd DocuGen
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Verify installation**:

   ```bash
   python main.py --help
   ```

## 📋 Usage

### Basic Commands

#### **Validate Configuration**

```bash
python main.py validate --config mappers/care_plans_mapper.yaml
```

**Purpose**: Validate template and configuration files before processing

#### **Preview Data (Dry Run)**

```bash
python main.py process --config mappers/care_plans_mapper.yaml --data data/sample_clients.xlsx --dry-run
```

**Purpose**: Preview data mapping without generating documents

#### **Generate Documents**

```bash
python main.py process --config mappers/care_plans_mapper.yaml --data data/sample_clients.xlsx
```

**Purpose**: Generate Word and PDF documents for all records

### Advanced Options

#### **Process Specific Rows**

```bash
python main.py process --config mappers/care_plans_mapper.yaml --data data/sample_clients.xlsx --start-row 10 --end-row 50
```

#### **Verbose Logging**

```bash
python main.py process --config mappers/care_plans_mapper.yaml --data data/sample_clients.xlsx --verbose
```

#### **Skip PDF Generation**

```bash
python main.py process --config mappers/care_plans_mapper.yaml --data data/sample_clients.xlsx --no-pdf
```

#### **Custom Output Directory**

```bash
python main.py process --config mappers/care_plans_mapper.yaml --data data/sample_clients.xlsx --output /path/to/output
```

## 📁 Project Structure

```text
DocuGen/
├── config/
│   └── app_config.yaml         # Application settings
├── mappers/
│   └── care_plans_mapper.yaml  # Data mapping configurations
├── templates/
│   └── care_plan_template.docx # Word templates
├── data/
│   └── sample_clients.xlsx     # Input Excel files
├── output/                     # Generated documents
├── logs/                       # Application logs
├── src/
│   ├── cli/                    # Command-line interface
│   ├── core/                   # Core business logic
│   ├── importers/              # Data input handlers
│   ├── generators/             # Document output handlers
│   ├── templates/              # Template processing
│   └── utils/                  # Utilities
└── main.py                     # Entry point
```

## 🔧 Configuration

### Application Configuration (`config/app_config.yaml`)

```yaml
logging:
  level: INFO
  file_pattern: "logs/docugen_{date}.log"
  console_output: true

processing:
  batch_size: 100

paths:
  templates_dir: "templates"
  output_dir: "output"
  data_dir: "data"

output:
  formats: ["docx", "pdf"]
  naming_pattern: "{client_name}_{date_processed}"
  duplicate_handling: "rename" # rename, overwrite, skip
```

### Mapper Configuration (`mappers/project_mapper.yaml`)

```yaml
project_name: "care_plans"
template_file: "care_plan_template.docx"

# Excel column to template variable mapping
field_mappings:
  "ACN": "ACN"
  "GivenName": "FirstName"
  "FamilyName": "LastName"
  "BirthDate": "DOB"

# Fixed values to add to every document
fixed_values:
  "DateOfPlan": "15/11/24"
  "ReviewDate": "14/11/25"

# Data transformations
transformations:
  "DOB": "date_format:%d/%m/%Y"
  "FirstName": "clean_nan"

# Required fields (warnings if missing)
required_fields:
  - "ACN"
  - "FirstName"
```

## 📊 Excel Data Format

Your Excel file should contain columns that match the `field_mappings` in your mapper configuration.

**Example Excel Structure**:

| ACN  | GivenName | FamilyName | BirthDate  | GenderCode | Type |
| ---- | --------- | ---------- | ---------- | ---------- | ---- |
| C001 | John      | Smith      | 1985-03-15 | Male       | HM   |
| C002 | Jane      | Doe        | 1990-07-22 | Female     | DA   |

## 📝 Template Format

Templates use Jinja2 syntax with Word documents:

```text
**CLIENT DETAILS**
Name: {{ FirstName }} {{ LastName }}
DOB: {{ DOB }}
Address: {{ Address1 }}

**SERVICES**
{% if Type == "HM" %}☑ Home Maintenance{% else %}☐ Home Maintenance{% endif %}
{% if Type == "DA" %}☑ Domestic Assistance{% else %}☐ Domestic Assistance{% endif %}
```

## 🎯 Adding New Document Types

DocuGen is designed for plug-and-play operation. To add a new document type:

1. **Create template**: `templates/invoice_template.docx`
2. **Create mapper**: `mappers/invoice_mapper.yaml`
3. **Run command**:

   ```bash
   python main.py process --config invoice_mapper.yaml --data invoice_data.xlsx
   ```

**No code changes required!**

## 🐛 Troubleshooting

### Common Issues

#### **Template not found**

```text
FileNotFoundError: Template file not found: templates/template.docx
```

**Solution**: Verify template file exists and path is correct in mapper config

#### **Missing columns**

```text
Required column not found: ClientName
```

**Solution**: Check Excel column names match `field_mappings` in mapper config

#### **PDF generation fails**

```text
docx2pdf failed: [error message]
```

**Solution**: Install LibreOffice as fallback:

- macOS: `brew install libreoffice`
- Ubuntu: `sudo apt-get install libreoffice`
- Windows: Download from libreoffice.org

### Debugging

#### **Verbose logging**

```bash
python main.py process --config mapper.yaml --data data.xlsx --verbose
```

#### **Check logs**

```bash
tail -f logs/docugen_2025-07-01.log
```

#### **Validate before processing**

```bash
python main.py validate --config mapper.yaml
```

## 📈 Performance

### Current Benchmarks

- **Target**: 100 documents in <5 minutes
- **Memory**: <1GB for 1000-row datasets
- **Success rate**: 99%+ document generation

### Optimization Tips

- Use `--start-row` and `--end-row` for large datasets
- Monitor memory usage with verbose logging
- Use `--no-pdf` to skip PDF generation if not needed

## 🔄 Development Status

### Phase 1: Core System ✅

- ✅ Modular architecture
- ✅ CLI interface
- ✅ Template processing
- ✅ Excel import/mapping
- ✅ Document generation

### Phase 1b: Testing 🔄

- 🔄 Service type logic
- 🔄 Scale testing
- 🔄 Performance validation

### Phase 2: LLM Enhancement 📋

- 📋 Local LLM integration
- 📋 Intelligent content generation
- 📋 Dynamic field enhancement

## 🤝 Contributing

1. Follow the modular architecture patterns
2. Add tests for new features
3. Update documentation
4. Use configuration-driven approach (no hardcoded values)

## 📄 License

[Add your license information here]

## 🆘 Support

- **Issues**: Create GitHub issues for bugs or feature requests
- **Documentation**: Check `docs/` folder for detailed guides
- **Logs**: Check `logs/` folder for debugging information

---

**Ready to generate some documents? Start with the validation command!**

```bash
python main.py validate --config mappers/care_plans_mapper.yaml
```
